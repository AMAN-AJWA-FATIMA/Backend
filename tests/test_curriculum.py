
from uuid import uuid4

import pytest

from app.dependencies.authentication import get_current_user
from app.models.user import User


def set_role(client, role):
    def override_current_user():
        return User(
            id=1,
            full_name="Curriculum Test User",
            email=f"{role}@example.com",
            role=role,
        )

    client.app.dependency_overrides[get_current_user] = override_current_user


def create_record(client, resource, payload):
    response = client.post(
        f"/curriculum/admin/{resource}",
        json=payload,
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_hierarchy(client, published=True):
    """Create a complete grade-to-page hierarchy for tests."""
    set_role(client, "admin")

    grade = create_record(
        client,
        "grades",
        {"name": f"Grade {uuid4()}"},
    )

    subject = create_record(
        client,
        "subjects",
        {
            "grade_id": grade["id"],
            "name": f"Subject {uuid4()}",
        },
    )

    book = create_record(
        client,
        "books",
        {
            "subject_id": subject["id"],
            "title": f"Book {uuid4()}",
            "published": published,
        },
    )

    chapter = create_record(
        client,
        "chapters",
        {
            "book_id": book["id"],
            "chapter_no": 1,
            "title": "Test Chapter",
        },
    )

    page = create_record(
        client,
        "pages",
        {
            "book_id": book["id"],
            "chapter_id": chapter["id"],
            "page_no": 1,
            "text": "Test page content",
        },
    )

    return {
        "grade": grade,
        "subject": subject,
        "book": book,
        "chapter": chapter,
        "page": page,
    }


def test_public_can_list_grades(client):
    response = client.get("/curriculum/grades")

    assert response.status_code == 200
    assert set(response.json()) == {
        "items",
        "total",
        "page",
        "page_size",
        "pages",
    }


def test_public_hierarchy_endpoints_use_same_pagination_format(client):
    records = create_hierarchy(client, published=True)
    grade = records["grade"]
    subject = records["subject"]
    book = records["book"]
    chapter = records["chapter"]

    set_role(client, "student")

    endpoints = [
        "/curriculum/grades",
        f"/curriculum/grades/{grade['id']}/subjects",
        f"/curriculum/subjects/{subject['id']}/books",
        f"/curriculum/books/{book['id']}/chapters",
        f"/curriculum/chapters/{chapter['id']}/pages",
    ]

    expected_keys = {
        "items",
        "total",
        "page",
        "page_size",
        "pages",
    }

    for endpoint in endpoints:
        response = client.get(endpoint)

        assert response.status_code == 200, response.text
        assert set(response.json()) == expected_keys
        assert response.json()["page"] == 1
        assert response.json()["page_size"] == 20


def test_public_pagination_parameters_are_validated(client):
    invalid_page = client.get("/curriculum/grades?page=0")
    invalid_page_size = client.get("/curriculum/grades?page_size=101")

    assert invalid_page.status_code == 422
    assert invalid_page_size.status_code == 422


def test_student_cannot_access_admin_crud_operations(client):
    set_role(client, "student")
    record_id = str(uuid4())

    for resource in (
        "grades",
        "subjects",
        "books",
        "chapters",
        "pages",
        "topics",
    ):
        create_response = client.post(
            f"/curriculum/admin/{resource}",
            json={},
        )
        update_response = client.patch(
            f"/curriculum/admin/{resource}/{record_id}",
            json={"name": "Unauthorized"},
        )
        delete_response = client.delete(
            f"/curriculum/admin/{resource}/{record_id}"
        )

        assert create_response.status_code == 403
        assert update_response.status_code == 403
        assert delete_response.status_code == 403


@pytest.mark.parametrize(
    ("resource", "payload_factory", "update_payload"),
    [
        (
            "grades",
            lambda h: {"name": f"New Grade {uuid4()}"},
            {"name": "Updated Grade"},
        ),
        (
            "subjects",
            lambda h: {
                "grade_id": h["grade"]["id"],
                "name": f"New Subject {uuid4()}",
            },
            {"name": "Updated Subject"},
        ),
        (
            "books",
            lambda h: {
                "subject_id": h["subject"]["id"],
                "title": f"New Book {uuid4()}",
                "published": False,
            },
            {"title": "Updated Book"},
        ),
        (
            "chapters",
            lambda h: {
                "book_id": h["book"]["id"],
                "chapter_no": 99,
                "title": "New Chapter",
            },
            {"title": "Updated Chapter"},
        ),
        (
            "pages",
            lambda h: {
                "book_id": h["book"]["id"],
                "chapter_id": h["chapter"]["id"],
                "page_no": 99,
                "text": "Original page text",
            },
            {"text": "Updated page text"},
        ),
        (
            "topics",
            lambda h: {
                "chapter_id": h["chapter"]["id"],
                "tag": "original-tag",
            },
            {"tag": "updated-tag"},
        ),
    ],
)
def test_admin_can_create_update_and_delete_all_resources(
    client,
    resource,
    payload_factory,
    update_payload,
):
    hierarchy = create_hierarchy(client)

    set_role(client, "admin")
    record = create_record(
        client,
        resource,
        payload_factory(hierarchy),
    )

    record_id = record["id"]

    update_response = client.patch(
        f"/curriculum/admin/{resource}/{record_id}",
        json=update_payload,
    )

    assert update_response.status_code == 200, update_response.text

    for field, expected_value in update_payload.items():
        assert update_response.json()[field] == expected_value

    delete_response = client.delete(
        f"/curriculum/admin/{resource}/{record_id}"
    )

    assert delete_response.status_code == 204


@pytest.mark.parametrize(
    ("resource", "field"),
    [
        ("grades", "name"),
        ("subjects", "grade_id"),
        ("books", "subject_id"),
        ("chapters", "book_id"),
        ("pages", "chapter_id"),
        ("topics", "chapter_id"),
    ],
)
def test_patch_rejects_null_required_fields(client, resource, field):
    hierarchy = create_hierarchy(client)

    set_role(client, "admin")

    payloads = {
        "grades": {"name": f"Patch Grade {uuid4()}"},
        "subjects": {
            "grade_id": hierarchy["grade"]["id"],
            "name": f"Patch Subject {uuid4()}",
        },
        "books": {
            "subject_id": hierarchy["subject"]["id"],
            "title": f"Patch Book {uuid4()}",
            "published": False,
        },
        "chapters": {
            "book_id": hierarchy["book"]["id"],
            "chapter_no": 99,
            "title": "Patch Chapter",
        },
        "pages": {
            "book_id": hierarchy["book"]["id"],
            "chapter_id": hierarchy["chapter"]["id"],
            "page_no": 99,
            "text": "Patch page",
        },
        "topics": {
            "chapter_id": hierarchy["chapter"]["id"],
            "tag": "patch-tag",
        },
    }

    record = create_record(client, resource, payloads[resource])

    response = client.patch(
        f"/curriculum/admin/{resource}/{record['id']}",
        json={field: None},
    )

    assert response.status_code == 422


def test_unpublished_books_are_hidden_from_public_book_listing(client):
    hierarchy = create_hierarchy(client, published=False)

    set_role(client, "student")

    response = client.get(
        f"/curriculum/subjects/{hierarchy['subject']['id']}/books"
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []


def test_unpublished_books_hide_chapters_and_pages(client):
    hierarchy = create_hierarchy(client, published=False)

    set_role(client, "student")

    chapters_response = client.get(
        f"/curriculum/books/{hierarchy['book']['id']}/chapters"
    )

    pages_response = client.get(
        f"/curriculum/chapters/{hierarchy['chapter']['id']}/pages"
    )

    assert chapters_response.status_code == 404
    assert pages_response.status_code == 404


def test_admin_cannot_create_subject_with_invalid_grade(client):
    set_role(client, "admin")

    response = client.post(
        "/curriculum/admin/subjects",
        json={
            "grade_id": str(uuid4()),
            "name": "Invalid Subject",
        },
    )

    assert response.status_code == 404


def test_admin_cannot_create_page_with_mismatched_book_and_chapter(client):
    hierarchy = create_hierarchy(client, published=True)

    set_role(client, "admin")

    other_book = create_record(
        client,
        "books",
        {
            "subject_id": hierarchy["subject"]["id"],
            "title": f"Other Book {uuid4()}",
            "published": True,
        },
    )

    response = client.post(
        "/curriculum/admin/pages",
        json={
            "book_id": other_book["id"],
            "chapter_id": hierarchy["chapter"]["id"],
            "page_no": 50,
            "text": "Invalid relationship",
        },
    )

    assert response.status_code == 422


def test_admin_cannot_update_page_to_mismatched_book_and_chapter(client):
    hierarchy = create_hierarchy(client, published=True)

    set_role(client, "admin")

    other_book = create_record(
        client,
        "books",
        {
            "subject_id": hierarchy["subject"]["id"],
            "title": f"Other Book {uuid4()}",
            "published": True,
        },
    )

    response = client.patch(
        f"/curriculum/admin/pages/{hierarchy['page']['id']}",
        json={"book_id": other_book["id"]},
    )

    assert response.status_code == 422

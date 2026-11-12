def create_user(client, email="aman@example.com"):
    response = client.post(
        "/users/",
        json={
            "full_name": "Aman Ajwa",
            "email": email,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_task(client, user_id, title="Learn FastAPI", is_completed=False):
    return client.post(
        "/tasks/",
        json={
            "title": title,
            "description": "Backend development practice.",
            "user_id": user_id,
            "is_completed": is_completed,
        },
    )


def test_create_task(client):
    user = create_user(client)

    response = create_task(client, user["id"])

    assert response.status_code == 201
    assert response.json()["title"] == "Learn FastAPI"
    assert response.json()["user_id"] == user["id"]


def test_create_task_for_nonexistent_user(client):
    response = create_task(client, 9999)

    assert response.status_code == 404


def test_get_task(client):
    user = create_user(client)
    created_task = create_task(client, user["id"]).json()

    response = client.get(f"/tasks/{created_task['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_task["id"]


def test_get_nonexistent_task(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404


def test_list_tasks_with_filters(client):
    first_user = create_user(client, "first@example.com")
    second_user = create_user(client, "second@example.com")

    create_task(client, first_user["id"], "Pending task", False)
    create_task(client, first_user["id"], "Completed task", True)
    create_task(client, second_user["id"], "Another task", False)

    response = client.get(f"/tasks/?user_id={first_user['id']}&is_completed=true")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Completed task"


def test_list_tasks_with_pagination(client):
    user = create_user(client)

    create_task(client, user["id"], "First task")
    create_task(client, user["id"], "Second task")

    response = client.get("/tasks/?skip=0&limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_task(client):
    user = create_user(client)
    created_task = create_task(client, user["id"]).json()

    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={
            "title": "Learn SQLAlchemy",
            "is_completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Learn SQLAlchemy"
    assert response.json()["is_completed"] is True


def test_update_task_with_empty_body(client):
    user = create_user(client)
    created_task = create_task(client, user["id"]).json()

    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={},
    )

    assert response.status_code == 422


def test_delete_task(client):
    user = create_user(client)
    created_task = create_task(client, user["id"]).json()

    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204

    get_response = client.get(f"/tasks/{created_task['id']}")
    assert get_response.status_code == 404

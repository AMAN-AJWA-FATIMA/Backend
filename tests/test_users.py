def create_user(client, email="aman@example.com"):
    return client.post(
        "/users/",
        json={
            "full_name": "Aman Ajwa",
            "email": email,
        },
    )


def test_create_user(client):
    response = create_user(client)

    assert response.status_code == 201
    assert response.json()["full_name"] == "Aman Ajwa"
    assert response.json()["email"] == "aman@example.com"
    assert "id" in response.json()


def test_create_user_with_invalid_email(client):
    response = client.post(
        "/users/",
        json={
            "full_name": "Aman Ajwa",
            "email": "invalid-email",
        },
    )

    assert response.status_code == 422


def test_create_user_with_duplicate_email(client):
    first_response = create_user(client)
    second_response = create_user(client)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_get_user(client):
    created_user = create_user(client).json()

    response = client.get(f"/users/{created_user['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_user["id"]


def test_get_nonexistent_user(client):
    response = client.get("/users/9999")

    assert response.status_code == 404


def test_list_users_with_pagination(client):
    create_user(client, "first@example.com")
    create_user(client, "second@example.com")

    response = client.get("/users/?skip=0&limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_user(client):
    created_user = create_user(client).json()

    response = client.delete(f"/users/{created_user['id']}")

    assert response.status_code == 204

    get_response = client.get(f"/users/{created_user['id']}")
    assert get_response.status_code == 404


def test_delete_user_with_existing_tasks(client):
    created_user = create_user(client).json()

    task_response = client.post(
        "/tasks/",
        json={
            "title": "Complete backend API",
            "description": "Implement user and task endpoints.",
            "user_id": created_user["id"],
        },
    )

    assert task_response.status_code == 201

    response = client.delete(f"/users/{created_user['id']}")

    assert response.status_code == 409

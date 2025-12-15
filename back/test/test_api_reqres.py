from playwright.sync_api import APIRequestContext

def test_api_responds(api_context: APIRequestContext):
    #Fetch a list of users with pagination
    response = api_context.get("/api/users")

    assert response.status == 200
    assert response.ok

    data = response.json()

    assert "data" in data
    assert len(data["data"]) > 0

    print(f"\n Total number of users: {data['total']}")
    print(f"\n Users on page: {len(data['data'])}")


def test_get_single_user(api_context: APIRequestContext):
    #Fetch a single user by ID
    user_id = 1
    response = api_context.get(f"/api/users/{user_id}")

    assert response.status == 200

    user = response.json()["data"]
    print(f"\n User: {user['first_name']} {user['last_name']}")
    print(f"\n Email: {user['email']}")

    # Check ID matches
    assert user["id"] == user_id

    assert "first_name" in user
    assert len(user["first_name"]) > 0

    assert "last_name" in user
    assert len(user["last_name"]) > 0

    assert "email" in user
    assert "@" in user["email"] #Redundant but let be

    assert "avatar" in user
    assert isinstance(user["avatar"], str)
    assert user["avatar"].startswith("http")


def test_create_user(api_context: APIRequestContext, created_user):
    #Create a new user
    response = created_user["response"]
    body = created_user["body"]
    user_id = body["id"]

    assert response.status == 201

    assert body["name"] == "Jeffrey Lebowski"
    assert body["job"] == "The Dude"
    assert "id" in body
    assert "createdAt" in body

    print(f"\nCreated user ID: {user_id}")
    print(f"\nNew user data: {body}")


def test_dynamic_delete_user(api_context: APIRequestContext, created_user):
    #Delete a user (created above)
    body = created_user["body"]
    user_id = body["id"]

    delete_response = api_context.delete(f"/api/users/{user_id}")
    assert delete_response.status == 204

    print(f"\nUser with ID {user_id} deleted successfully")


def test_delete_user_by_id(api_context: APIRequestContext):
    #Removing user by hardcoded id
    user_id = 1

    delete_response = api_context.delete(f"/api/users/{user_id}")
    assert delete_response.status == 204
    print(f"\n User {user_id} deleted")

    get_response = api_context.get(f"/api/users/{user_id}")
    assert get_response.status == 200  # Still exists (expected)
    print(f"\n⚠ User still EXISTS!!! - ReqRes doesn't persist deletions")


def test_update_user(api_context: APIRequestContext):
    #Update an existing user
    user_id = 1

    updated_data = {
        "name": "Michael Kovalchuk",
        "job": "Backend Tester"
    }

    response = api_context.put(
        f"/api/users/{user_id}",
        data=updated_data
    )

    assert response.status == 200
    body = response.json()

    assert body["name"] == updated_data["name"]
    assert body["job"] == updated_data["job"]
    assert "updatedAt" in body

    print(f"\n Updated user ID: {user_id}")
    print(f"\n Updated user data: {body}")


def test_login_user(api_context: APIRequestContext, sample_register_data):
    #Authenticate a user
    response = api_context.post("/api/login", data=sample_register_data)

    assert response.status == 200
    assert "token" in response.json()

    print(f"\n Token received: {response.json()['token']}")

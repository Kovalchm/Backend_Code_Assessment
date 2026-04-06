import pytest
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
    assert "token" in response.json() #response.json()["token"]

    print(f"\n Token received: {response.json()['token']}")

def test_token_returned_on_login(api_context: APIRequestContext, sample_register_data):
    response = api_context.post("/api/login", data=sample_register_data)

    assert response.status == 200
    body = response.json()

    assert "token" in body, "No token in response"

    #Basic token assertions
    token = body["token"]
    assert isinstance(token, str), "Token should be a string"
    assert len(token) > 0,         "Token should not be empty"

    print(f"\n Token received: {token}")
    print(f"\n Token length: {len(token)}")

def test_missing_token_rejected(api_context: APIRequestContext):
    # No authorization header
    response = api_context.fetch(
        "/api/users",
        method="GET",
        headers={
            "Content-Type": "application/json"
            # Omitting authorization intentionally
        }
    )

    print(f"\n No token status: {response.status}")
    assert response.status in [200, 401], \
        f"Unexpected status without token: {response.status}"

    if response.status == 200:
        print("\n ⚠️  reqres.in serves data without any token")
        print("\n     This is by design — it is a public demo API")

def test_login_wrong_password_no_token(api_context: APIRequestContext):
    response = api_context.post("/api/login", data={
        "email":    "eve.holt@reqres.in",
        "password": "wrongpassword"
    })

    print(f"\n Wrong password status: {response.status}")
    body = response.json()
    print(f"\n Response body: {body}")

    # reqres.in is a read-only demo API - returns a token for ANY password — by design
    # _meta.message confirms: "This is a read-only demo endpoint"
    if response.status == 200 and "token" in body:
        print("\n ⚠️  KNOWN LIMITATION: reqres.in accepts any password")
        print(f"\n     API message: {body['_meta']['message']}")
        pytest.skip("reqres.in does not enforce password validation — demo API")

    # this block runs only on a REAL API that validates properly
    assert response.status == 400
    assert "token" not in body
    assert "error" in body
    print(f"\n Error: {body['error']}")

def test_head_users(api_context: APIRequestContext):
    # HEAD returns same headers as GET but without body, useful to check: content-type, server,
    # cache headers without downloading the full response body

    head_response = api_context.fetch( # fetch works for any HTTP method
        "/api/users",
        method="HEAD"
    )
    get_response = api_context.get("/api/users")

    # HEAD must return 200
    assert head_response.status == 200

    # HEAD must have NO body
    assert head_response.body() == b"", \
        "HEAD response must return empty body"

    # HEAD headers must match GET headers
    assert head_response.headers.get("content-type") == \
           get_response.headers.get("content-type"), \
        "HEAD and GET must return same Content-Type"

    # useful headers to inspect
    print(f"\n Content-Type:  {head_response.headers.get('content-type')}")
    print(f"\n Server:        {head_response.headers.get('server')}")
    print(f"\n Cache-Control: {head_response.headers.get('cache-control')}")
    print(f"\n All headers:   {dict(head_response.headers)}")


def test_head_single_user_exists(api_context: APIRequestContext):
    # practical use of HEAD — check if resource EXISTS without fetching the full body
    # useful when body is large (image, file, big JSON)

    existing_user    = api_context.fetch("/api/users/3",  method="HEAD")
    nonexistent_user = api_context.fetch("/api/users/11", method="HEAD")

    # existing user — should be 200
    assert existing_user.status == 200, \
        f"Expected 200 for existing user, got {existing_user.status}"

    # non-existing user — should be 404 or 403 cause reqres.in changed behaviour (likely)
    assert nonexistent_user.status in [403,404], \
        f"Expected 403 or 404 for missing user, got {nonexistent_user.status}"

    print(f"\n User 1 exists:   {existing_user.status == 200}")
    print(f"\n User 11 exists: {nonexistent_user.status == 200}")

def test_options_users(api_context: APIRequestContext):
    # OPTIONS returns what methods the server allows also used for CORS preflight — browser sends OPTIONS
    # before actual request to check if cross-origin is allowed

    response = api_context.fetch(
        "/api/users",
        method="OPTIONS"
    )

    print(f"\n OPTIONS status: {response.status}")
    print(f"\n All headers: {dict(response.headers)}")

    # OPTIONS typically returns 200 or 204
    assert response.status in [200, 204], \
        f"Expected 200 or 204, got {response.status}"

    # check Allow header — lists supported methods
    allow_header = response.headers.get("allow", "")
    access_control = response.headers.get("access-control-allow-methods", "")

    # one of these should contain allowed methods
    allowed_methods = allow_header or access_control

    print(f"\n Allow header:                  {allow_header}")
    print(f"\n Access-Control-Allow-Methods:  {access_control}")
    print(f"\n Allowed methods:               {allowed_methods}")

    # reqres.in supports at least GET and POST on /api/users
    if allowed_methods:
        assert "GET"  in allowed_methods.upper(), "GET should be allowed"
        assert "POST" in allowed_methods.upper(), "POST should be allowed"


def test_options_cors_headers(api_context: APIRequestContext):
    # CORS specific test — what origins and headers are allowed
    # browsers check this before sending cross-origin requests

    response = api_context.fetch(
        "/api/users",
        method="OPTIONS",
        headers={
            "Origin":                         "https://myapp.com",
            "Access-Control-Request-Method":  "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }
    )

    print(f"\n Status: {response.status}")

    cors_origin  = response.headers.get("access-control-allow-origin",  "not set")
    cors_methods = response.headers.get("access-control-allow-methods", "not set")
    cors_headers = response.headers.get("access-control-allow-headers", "not set")
    cors_max_age = response.headers.get("access-control-max-age",       "not set")

    print(f"\n Access-Control-Allow-Origin:  {cors_origin}")
    print(f"\n Access-Control-Allow-Methods: {cors_methods}")
    print(f"\n Access-Control-Allow-Headers: {cors_headers}")
    print(f"\n Access-Control-Max-Age:       {cors_max_age}")

    # reqres.in is a public API — should allow all origins
    assert cors_origin in ["*", "https://myapp.com", "not set"], \
        f"Unexpected CORS origin: {cors_origin}"

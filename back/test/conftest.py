from typing import Generator, Iterator
import pytest
from playwright.sync_api import Playwright, APIRequestContext

REQRES_BASE_URL = "https://reqres.in"


@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    request_context = playwright.request.new_context(
        base_url=REQRES_BASE_URL,
        extra_http_headers={
            "x-api-key": "reqres_ca4092081b5e4bdf8fe102d3054edd8f",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def sample_user():
    return {
        "name": "Jeffrey Lebowski",
        "job": "The Dude"
    }

@pytest.fixture
def created_user(api_context: APIRequestContext, sample_user) -> Iterator[dict]:
    response = api_context.post("/api/users", data=sample_user)
    body = response.json()
    yield {"body": body, "response": response}


@pytest.fixture
def sample_register_data():
    return {
        "email": "eve.holt@reqres.in",
        "password": "pistol"
    }
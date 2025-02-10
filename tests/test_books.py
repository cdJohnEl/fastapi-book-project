from tests import client
import os
import pytest
from fastapi.testclient import TestClient
from main import app


# Get the base URL from an environment variable, defaulting to the local server
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Use TestClient for local testing, and requests for deployed testing
if BASE_URL == "http://localhost:8000":
    client = TestClient(app)
else:
    import requests
    class DeployedTestClient:
        def __init__(self, base_url):
            self.base_url = base_url
        def get(self, url, **kwargs):
            return requests.get(f"{self.base_url}{url}", **kwargs)
        def post(self, url, **kwargs):
            return requests.post(f"{self.base_url}{url}", **kwargs)
        def put(self, url, **kwargs):
            return requests.put(f"{self.base_url}{url}", **kwargs)
        def delete(self, url, **kwargs):
            return requests.delete(f"{self.base_url}{url}", **kwargs)
    client = DeployedTestClient(BASE_URL)


def test_get_all_books():
    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_single_book():
    response = client.get("/books/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Hobbit"
    assert data["author"] == "J.R.R. Tolkien"


def test_create_book():
    new_book = {
        "id": 4,
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "publication_year": 1997,
        "genre": "Fantasy",
    }
    response = client.post("/books/", json=new_book)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["title"] == "Harry Potter and the Sorcerer's Stone"


def test_update_book():
    updated_book = {
        "id": 1,
        "title": "The Hobbit: An Unexpected Journey",
        "author": "J.R.R. Tolkien",
        "publication_year": 1937,
        "genre": "Fantasy",
    }
    response = client.put("/books/1", json=updated_book)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Hobbit: An Unexpected Journey"


def test_delete_book():
    response = client.delete("/books/3")
    assert response.status_code == 204

    response = client.get("/books/3")
    assert response.status_code == 404


def test_get_all_books():
    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_get_nonexistent_book():
    response = client.get("/books/999")  # Assuming 999 is an invalid book ID
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}
from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_create_category(client):
    response = await client.post("/categories", json={"name": "Test Category", "is_active": True})
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == "Test Category"
    assert "category_id" in category


@pytest.mark.asyncio
async def test_list_active_categories(client):
    response = await client.get("/categories/active")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        for item in data:
            assert isinstance(item, dict)
            assert "category_id" in item
            assert "name" in item
            assert "is_active" in item


@pytest.mark.asyncio
async def test_get_category_by_id(client):
    response = await client.post("/categories", json={"name": "get by id", "is_active": True})
    category_id = response.json().get("category_id")

    response = await client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    category = response.json()
    assert category["category_id"] == category_id
    assert category["name"] == "get by id"


@pytest.mark.asyncio
async def test_update_category(client):
    response = await client.post("/categories", json={"name": "Update", "is_active": True})
    category_id = response.json().get("category_id")

    response = await client.put(f"/categories/{category_id}", json={"name": "Updated Category", "is_active": False})
    assert response.status_code == 200
    category = response.json()
    assert category["category_id"] == category_id
    assert category["name"] == "Updated Category"
    assert category["is_active"] is False


@pytest.mark.asyncio
async def test_mark_category_as_inactive(client):
    response = await client.post("/categories", json={"name": "mark inactive", "is_active": True})
    category_id = response.json().get("category_id")

    response = await client.patch(f"/categories/{category_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_category_by_name(client):
    response = await client.post("/categories", json={"name": "named", "is_active": True})

    response = await client.get("/categories/by-name/named")
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == "named"
    assert "category_id" in category


@pytest.mark.asyncio
async def test_create_duplicate_category(client):
    response = await client.post("/categories", json={"name": "Test Category", "is_active": True})
    dup_response = await client.post("/categories", json={"name": "Test Category", "is_active": True})
    assert dup_response.status_code == 400


@pytest.mark.asyncio
async def test_create_category_invalid_data(client):
    response = await client.post("/categories", json={"name": ""})
    assert response.status_code == 422

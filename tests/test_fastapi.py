import ast

import pytest
from app.models import Recipe
from sqlalchemy import select

from tests.sample_recipes import one_more_recipe


@pytest.mark.asyncio
async def test_get_all_recipes(client, new_db, sample_data):
    """Проверяет получение таблицы со всеми рецептами"""
    response = client.get("/recipes")
    response_dict = ast.literal_eval(response.text)
    assert response.status_code == 200
    for recipe in response_dict:
        assert recipe["name"] is not None
        assert recipe["cooking_time"] is not None
        assert recipe["rating"] is not None


@pytest.mark.asyncio
async def test_get_one_recipe(client, new_db, sample_data):
    """Проверяет получение конкретного существующего рецепта по его id"""
    response = client.get("/recipes/1")
    response_dict = ast.literal_eval(response.text)
    assert response.status_code == 200
    assert response_dict["name"] is not None
    assert response_dict["ingredients"] is not None
    assert response_dict["cooking_process"] is not None
    assert response_dict["cooking_time"] is not None


@pytest.mark.asyncio
async def test_rating_increase(client, db_session, new_db, sample_data):
    """Проверяет изменение рейтинга рецепта"""
    recipe_id = 1
    async with db_session() as session:
        initial_recipe = await session.execute(
            select(Recipe).where(Recipe.id == recipe_id)
        )
        initial_recipe = initial_recipe.scalars().first()
        initial_rating = initial_recipe.rating

    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200

    async with db_session() as session:
        updated_recipe = await session.execute(
            select(Recipe).where(Recipe.id == recipe_id)
        )
        updated_recipe = updated_recipe.scalars().first()

        new_rating = updated_recipe.rating
        assert new_rating == initial_rating + 1


@pytest.mark.asyncio
async def test_get_one_nonexistent_recipe(client, new_db, sample_data):
    """Проверяет получение ошибки 404 при запросе несуществующего id"""
    response = client.get("/recipes/7")
    assert response.status_code == 404
    assert "Recipe not found" in response.text


@pytest.mark.asyncio
async def test_post_one_recipe(client, new_db, sample_data):
    """Проверяет добавления валидного рецепта в базу данных"""
    data = one_more_recipe
    response = client.post("/recipes", json=data)
    assert response.status_code == 200
    response_dict = ast.literal_eval(response.text)
    assert response_dict["name"] == data["name"]
    assert response_dict["id"] is not None


@pytest.mark.asyncio
async def test_post_recipe_duplicate(client, new_db, sample_data):
    """Проверяет получение ошибки при попытке повторного
    добавления рецепта в базу"""
    data = one_more_recipe
    client.post("/recipes", json=data)
    response = client.post("/recipes", json=data)
    assert response.status_code == 400
    assert "Recipe with this name already exists." in response.text


@pytest.mark.asyncio
async def test_post_incomplete_recipe(client, new_db, sample_data):
    """Проверяет получение ошибки при попытке добавления неполного рецепта"""
    data = one_more_recipe
    del data["name"]
    response = client.post("/recipes", json=data)
    assert response.status_code == 422
    assert "field required" in response.text


@pytest.mark.asyncio
async def test_post_corrupted_recipe(client, new_db, sample_data):
    """Проверяет получение ошибки при попытке добавления невалидного рецепта"""
    data = one_more_recipe
    data["name"] = ["Invalid", "Type"]
    response = client.post("/recipes", json=data)
    assert response.status_code == 422
    assert '"str type expected","type":"type_error.str"' in response.text

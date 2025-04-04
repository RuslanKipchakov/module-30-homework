from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app import models, schemas
from app.database import async_session, engine, init_db

app = FastAPI()


async def get_session() -> AsyncSession:
    """Создаёт объект сессии для асинхронной работы с базой данных"""
    async with async_session() as session:
        return session


get_db_session = Depends(get_session)


@app.on_event("startup")
async def startup() -> None:
    """Создаёт базу данных при запуске приложения"""
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    """Прекращает соединение с базой данных при завершении работы приложения"""
    await engine.dispose()


@app.get("/recipes", response_model=List[schemas.TableRecipeOut])
async def all_recipes(
    session: AsyncSession = get_db_session,
) -> List[schemas.TableRecipeOut]:
    """Получает список всех рецептов из базы
    данных и представляет их в виде таблицы."""
    try:
        query = select(models.Recipe).order_by(
            models.Recipe.rating.desc(), models.Recipe.cooking_time.asc()
        )
        result = await session.execute(query)
        recipes = result.scalars().all()

        if not recipes:
            raise HTTPException(status_code=404, detail="No recipes yet")

        await session.commit()
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving recipes: {str(e)}"
        )


@app.get("/recipes/{recipe_id}", response_model=schemas.DetailedRecipeOut)
async def one_recipe(
    recipe_id: int, session: AsyncSession = get_db_session
) -> schemas.DetailedRecipeOut:
    """Получает рецепт из базы данных по его id и представляет пользователю.
    С каждым обращением к рецепту, увеличивается его рейтинг."""
    result = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe = result.scalars().first()

    if not recipe:
        await session.commit()
        raise HTTPException(status_code=404, detail="Recipe not found")

    await session.execute(
        update(models.Recipe.__table__)
        .where(models.Recipe.id == recipe_id)
        .values(rating=recipe.rating + 1)
    )
    await session.commit()

    updated_result = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    updated_recipe = updated_result.scalars().first()

    await session.commit()
    return updated_recipe


@app.post("/recipes", response_model=schemas.RecipeOut)
async def post_new_recipe(
    recipe: schemas.RecipeIn, session: AsyncSession = get_db_session
) -> schemas.RecipeOut:
    """Получает рецепт в теле POST-запроса и добавляет его в базу данных.
    Возвращает пользователю объект этого рецепта."""

    existing_recipe = await session.execute(
        select(models.Recipe).where(models.Recipe.name == recipe.name)
    )
    existing_recipe = existing_recipe.scalars().first()

    if existing_recipe:
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe with this name already exists.",
        )

    insert_query = insert(models.Recipe.__table__).values(**recipe.dict())
    await session.execute(insert_query)
    await session.commit()
    new_recipe = await session.execute(
        select(models.Recipe).where(models.Recipe.name == recipe.name)
    )

    new_recipe = new_recipe.scalars().first()
    await session.commit()
    return schemas.RecipeOut.from_orm(new_recipe)

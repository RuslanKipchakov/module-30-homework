from pydantic import BaseModel


class BaseRecipe(BaseModel):
    """Базовая схема отдельного рецепта"""

    name: str
    ingredients: str
    cooking_process: str
    cooking_time: int
    rating: int = 0


class RecipeIn(BaseRecipe):
    """Схема для внесения рецепта в базу данных (повторяет BaseRecipe)"""

    ...


class RecipeOut(BaseRecipe):
    """Полная схема рецепта, взятого из базы данных"""

    id: int
    rating: int

    class Config:
        orm_mode = True


class TableRecipeOut(RecipeOut):
    """Схема рецепта для таблицы, получаемой по эндпоинту '/recipes'
    Включает поля name, cooking_time, rating."""

    class Config:
        fields = {
            "ingredients": {"exclude": True},
            "id": {"exclude": True},
            "cooking_process": {"exclude": True},
        }


class DetailedRecipeOut(RecipeOut):
    """Схема рецепта получаемого по эндпоинту '/recipes/{recipe_id}'
    Включает поля name, ingredients, cooking_process, cooking_time."""

    class Config:
        fields = {"id": {"exclude": True}, "rating": {"exclude": True}}

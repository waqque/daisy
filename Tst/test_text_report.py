import pytest
from Src.Core.exceptions import argument_exception
from Src.Logics.storage_manager import storage_manager
from Src.Logics.text_report import text_report


# Проверка формирования текстового отчета по рецепту
def test_text_report_build_with_recipe():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]

    # Действие
    result = text_report().build(recipe)

    # Проверка
    assert result.text.startswith("Код|Наименование|Брутто|Нетто")
    assert len(result.text.split("\n")) == len(recipe.items) + 1
    assert "Молоко" in result.text


# Проверка валидации некорректного источника данных
def test_text_report_invalid_source():
    # Действие и проверка
    with pytest.raises(argument_exception):
        text_report().build(None)

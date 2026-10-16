import pytest
from Src.Core.exceptions import argument_exception
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.storage_manager import storage_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report


# 1. Проверка состава данных CSV отчета по рецепту
def test_csv_report_recipe_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]

    # Действие
    result = csv_report().build(recipe)

    # Проверка
    assert result.text.startswith("Код,Наименование,Брутто,Нетто")
    assert isinstance(result.data, bytes)
    assert len(result.text.split("\n")) == len(recipe.items) + 1
    assert "Молоко" in result.text


# 2. Проверка состава данных CSV отчета по номенклатуре
def test_csv_report_nomenclature_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    nom = storage.nomenclatures[0]

    # Действие
    result = csv_report().build(nom)

    # Проверка
    assert result.text.startswith("Код,Наименование,Полное наименование,Группа,Единица измерения")
    assert nom.name in result.text
    assert nom.full_name in result.text


# 3. Проверка состава данных CSV отчета по единице измерения
def test_csv_report_range_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    rng = storage.ranges[1]

    # Действие
    result = csv_report().build(rng)

    # Проверка
    assert result.text.startswith("Код,Наименование,Коэффициент,Базовая единица")
    assert rng.name in result.text
    assert str(rng.conversion_factor) in result.text


# 4. Проверка состава данных Markdown отчета по рецепту
def test_markdown_report_recipe_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]

    # Действие
    result = markdown_report().build(recipe)

    # Проверка
    assert "| Код | Наименование | Брутто | Нетто |" in result.text
    assert "| --- | --- | --- | --- |" in result.text
    assert isinstance(result.data, bytes)
    assert "Молоко" in result.text


# 5. Проверка состава данных XML отчета по рецепту
def test_xml_report_recipe_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]

    # Действие
    result = xml_report().build(recipe)

    # Проверка
    assert result.text.startswith("<?xml")
    assert f'<recipe name="{recipe.name}"' in result.text
    assert "<items>" in result.text
    assert "Молоко" in result.text


# 6. Проверка состава данных XML отчета по номенклатуре и единице измерения
def test_xml_report_nomenclature_and_range_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    nom = storage.nomenclatures[0]
    rng = storage.ranges[0]

    # Действие
    res_nom = xml_report().build(nom)
    res_rng = xml_report().build(rng)

    # Проверка
    assert f'<name>{nom.name}</name>' in res_nom.text
    assert f'<name>{rng.name}</name>' in res_rng.text


# 7. Проверка состава данных HTML отчета по рецепту
def test_html_report_recipe_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]

    # Действие
    result = html_report().build(recipe)

    # Проверка
    assert "<!DOCTYPE html>" in result.text
    assert f"<h1>{recipe.name}</h1>" in result.text
    assert "<th>Код</th>" in result.text
    assert "Молоко" in result.text


# 8. Проверка состава данных текстового отчета по номенклатуре и единице измерения
def test_text_report_nomenclature_and_range_data():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    nom = storage.nomenclatures[0]
    rng = storage.ranges[0]

    # Действие
    res_nom = text_report().build(nom)
    res_rng = text_report().build(rng)

    # Проверка
    assert res_nom.text.startswith("Код|Наименование|Полное наименование")
    assert nom.name in res_nom.text
    assert res_rng.text.startswith("Код|Наименование|Коэффициент")
    assert rng.name in res_rng.text


# 9. Проверка вызова исключения при передаче некорректного источника данных
def test_reports_invalid_source_raises_exception():
    # Подготовка
    reports = [csv_report(), markdown_report(), xml_report(), html_report(), text_report()]

    # Действие и проверка
    for report in reports:
        with pytest.raises(argument_exception):
            report.build(None)
        with pytest.raises(argument_exception):
            report.build("некорректный_источник")

import pytest
from main import api, storage
from Src.Dtos.report_type_dto import report_type_enum
from Src.Logics.settings_manager import settings_manager


@pytest.fixture
def client():
    # Настройка тестового клиента Flask
    storage.init_data()
    api.app.config["TESTING"] = True
    with api.app.test_client() as test_client:
        yield test_client


# 1. Проверка получения отчета по рецепту в формате Markdown со скачиванием файла
def test_api_get_report_markdown_download(client):
    # Подготовка
    recipe = storage.recipes[0]

    # Действие
    response = client.get(f"/api/report/recipe/{recipe.unique_code}?format=markdown")

    # Проверка
    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert ".md" in response.headers.get("Content-Disposition", "")
    assert "text/markdown" in response.headers.get("Content-Type", "")
    assert recipe.name in response.data.decode("utf-8")


# 2. Проверка получения отчета по номенклатуре в формате CSV со скачиванием файла
def test_api_get_report_csv_download(client):
    # Подготовка
    nom = storage.nomenclatures[0]

    # Действие
    response = client.get(f"/api/report/nomenclature/{nom.unique_code}?format=csv")

    # Проверка
    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert ".csv" in response.headers.get("Content-Disposition", "")
    assert "text/csv" in response.headers.get("Content-Type", "")
    assert nom.name in response.data.decode("utf-8")


# 3. Проверка получения отчета по единице измерения в формате XML
def test_api_get_report_xml(client):
    # Подготовка
    rng = storage.ranges[0]

    # Действие
    response = client.get(f"/api/report/range/{rng.unique_code}?format=xml")

    # Проверка
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("Content-Type", "")
    assert rng.name in response.data.decode("utf-8")


# 4. Проверка получения отчета в формате HTML
def test_api_get_report_html(client):
    # Подготовка
    recipe = storage.recipes[0]

    # Действие
    response = client.get(f"/api/report/recipe/{recipe.unique_code}?format=html")

    # Проверка
    assert response.status_code == 200
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "<!DOCTYPE html>" in response.data.decode("utf-8")
    assert recipe.name in response.data.decode("utf-8")


# 5. Проверка формирования отчета по умолчанию через create_default
def test_api_get_report_default(client):
    # Подготовка
    manager = settings_manager()
    manager.convert({"response_format": "XML"})
    recipe = storage.recipes[0]

    # Действие
    response = client.get(f"/api/report/default/recipe/{recipe.unique_code}")

    # Проверка
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("Content-Type", "")
    assert f'<recipe name="{recipe.name}"' in response.data.decode("utf-8")

    # Возврат настроек к TXT
    manager.convert({"response_format": "TXT"})


# 6. Проверка ошибки 404 при ненайденном коде сущности
def test_api_get_report_not_found(client):
    # Действие
    response = client.get("/api/report/recipe/non_existing_code_123")

    # Проверка
    assert response.status_code == 404


# 7. Проверка ошибки 400 при некорректном типе сущности или формате
def test_api_get_report_invalid_params(client):
    # Действие и проверка
    res_type = client.get("/api/report/unknown_type/123")
    assert res_type.status_code == 400

    res_format = client.get(f"/api/report/recipe/{storage.recipes[0].unique_code}?format=INVALID")
    assert res_format.status_code == 400

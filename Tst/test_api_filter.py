import json
import pytest
from main import api
from Src.Logics.storage_manager import storage_manager


@pytest.fixture
def client():
    storage = storage_manager()
    storage.init_data()
    api.app.config["TESTING"] = True
    with api.app.test_client() as test_client:
        yield test_client


def test_api_filter_nomenclatures_by_name_equals(client):
    # Точное совпадение по имени номенклатуры
    payload = {
        "filters": [
            {"field_name": "name", "filter_type": "EQUALS", "value": "Сахар"}
        ]
    }
    response = client.post(
        "/api/filter/nomenclatures",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Сахар"


def test_api_filter_nomenclatures_by_name_like(client):
    payload = {
        "field_name": "name",
        "filter_type": "LIKE",
        "value": "масло",
    }
    response = client.post(
        "/api/filter/nomenclatures",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert "масло" in data[0]["name"].lower()


def test_api_filter_ranges_nested_base_unit(client):
    payload = {
        "field_name": "name",
        "filter_type": "EQUALS",
        "value": "грамм",
    }
    response = client.post(
        "/api/filter/ranges",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    names = [r["name"] for r in data]
    assert "кг" in names or "грамм" in names


def test_api_filter_by_unique_code(client):
    storage = storage_manager()
    target_sugar = next(n for n in storage.nomenclatures if n.name == "Сахар")

    payload = {
        "field_name": "unique_code",
        "filter_type": "EQUALS",
        "value": target_sugar.unique_code,
    }
    response = client.post(
        "/api/filter/nomenclatures",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Сахар"


def test_api_filter_invalid_domain_type_returns_400(client):
    response = client.post(
        "/api/filter/unknown_entity_type",
        data=json.dumps({"name": "тест"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_filter_invalid_filter_type_returns_400(client):
    payload = {
        "field_name": "name",
        "filter_type": "INVALID_MODE",
        "value": "Сахар",
    }
    response = client.post(
        "/api/filter/nomenclatures",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_api_reports_osv_all(client):
    response = client.post(
        "/api/reports/osv",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "storage" in first
    assert "nomenclature" in first
    assert "opening_balance" in first
    assert "income" in first
    assert "outcome" in first
    assert "closing_balance" in first


def test_api_reports_osv_filtered_by_nomenclature(client):
    # По сахару в стартовых данных: приход 100, расход 25 -> остаток 75
    payload = {
        "field_name": "name",
        "filter_type": "EQUALS",
        "value": "Сахар",
    }
    response = client.post(
        "/api/reports/osv",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["nomenclature"]["name"] == "Сахар"
    assert data[0]["closing_balance"] == 75.0


def test_api_reports_osv_filtered_by_storage(client):
    payload = {
        "field_name": "name",
        "filter_type": "LIKE",
        "value": "Холодильная",
    }
    response = client.post(
        "/api/reports/osv",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert all("Холодильная" in row["storage"]["name"] for row in data)

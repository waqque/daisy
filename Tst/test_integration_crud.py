import json
import pytest
from main import api, service, storage
from Src.Dtos.report_type_dto import report_type_enum
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


@pytest.fixture
def client():
    # Настройка тестового клиента перед каждым тестом
    storage.init_data()
    api.app.config["TESTING"] = True
    with api.app.test_client() as test_client:
        yield test_client


# 1. Проверка получения списка доступных форматов отчетов в формате JSON (GET /api/reports/formats)
def test_success_get_report_formats_returns_json_list(client):
    # Действие
    response = client.get("/api/reports/formats")

    # Проверка
    assert response.status_code == 200
    assert response.is_json
    formats = response.get_json()
    assert isinstance(formats, list)
    expected_formats = [e.name for e in report_type_enum]
    assert set(formats) == set(expected_formats)


# 2. Проверка получения списка типов сущностей (GET /api/entities)
def test_success_get_entities_returns_domain_entity_keys(client):
    # Действие
    response = client.get("/api/entities")

    # Проверка
    assert response.status_code == 200
    assert response.is_json
    entities = response.get_json()
    assert "ranges" in entities
    assert "groups" in entities
    assert "nomenclatures" in entities
    assert "storages" in entities
    assert "recipes" in entities


# 3. Проверка получения списка сущностей указанного типа (GET /api/entities/{entity_type})
def test_success_get_entities_by_type(client):
    # Действие
    response = client.get("/api/entities/storages")

    # Проверка
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(item["name"] == "Главный склад" for item in data)


# 4. Проверка ошибки 400 при запросе сущностей неподдерживаемого типа
def test_error_get_entities_by_unknown_type(client):
    # Действие
    response = client.get("/api/entities/unknown_entities")

    # Проверка
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


# 5. Проверка получения конкретной сущности по идентификатору (GET /api/entities/{type}/{id})
def test_success_get_entity_by_id(client):
    # Подготовка
    st = storage.storages[0]

    # Действие
    response = client.get(f"/api/entities/storages/{st.id}")

    # Проверка
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == st.id
    assert data["name"] == st.name


# 6. Проверка ошибки 404 при получении несуществующей сущности
def test_error_get_entity_by_id_not_found(client):
    # Действие
    response = client.get("/api/entities/storages/non_existent_id_9999")

    # Проверка
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


# 7. Интеграционный тест: создание новой доменной сущности (POST /api/entities/{type})
def test_success_create_entity(client):
    # Подготовка
    new_storage_payload = {
        "name": "Новый буферный склад",
    }

    # Действие
    response = client.post(
        "/api/entities/storages",
        data=json.dumps(new_storage_payload),
        content_type="application/json",
    )

    # Проверка
    assert response.status_code == 201
    created_item = response.get_json()
    assert created_item["name"] == "Новый буферный склад"
    assert "id" in created_item

    # Проверка сохранения в хранилище
    stored_entity = storage.get_by_code("storages", created_item["id"])
    assert stored_entity is not None
    assert stored_entity.name == "Новый буферный склад"


# 8. Проверка ошибки валидации при создании сущности с некорректными данными (POST)
def test_error_create_entity_validation_failure(client):
    # Подготовка (пустое наименование вызывает ошибку валидации модели)
    invalid_payload = {
        "name": "   ",
    }

    # Действие
    response = client.post(
        "/api/entities/storages",
        data=json.dumps(invalid_payload),
        content_type="application/json",
    )

    # Проверка
    assert response.status_code == 400
    assert "error" in response.get_json()


# 9. Проверка ошибки создания дубликата сущности (POST)
def test_error_create_entity_duplicate_name(client):
    # Подготовка
    existing_name = storage.storages[0].name
    payload = {"name": existing_name}

    # Действие
    response = client.post(
        "/api/entities/storages",
        data=json.dumps(payload),
        content_type="application/json",
    )

    # Проверка
    assert response.status_code == 400
    assert "error" in response.get_json()


# 10. Интеграционный тест: успешное обновление сущности (PUT /api/entities/{type}/{id})
def test_success_update_entity(client):
    # Подготовка: создаем склад, не связанный с другими объектами
    temp_st = storage_model.create("Склад для модификации")
    storage.add_entity("storages", temp_st)

    update_payload = {
        "name": "Склад переименованный",
        "id": temp_st.id,
    }

    # Действие
    response = client.put(
        f"/api/entities/storages/{temp_st.id}",
        data=json.dumps(update_payload),
        content_type="application/json",
    )

    # Проверка
    assert response.status_code == 200
    updated_data = response.get_json()
    assert updated_data["name"] == "Склад переименованный"
    assert updated_data["id"] == temp_st.id


# 11. Проверка запрета изменения кода (id) сущности, если сущность связана с другой (PUT)
def test_error_update_entity_code_when_referenced(client):
    # Подготовка: группа "Сырье" связана с номенклатурой ("Сахар", "Мука" и т.д.)
    raw_group = storage.groups[0]
    assert len(service.get_dependencies(raw_group)) > 0

    invalid_update_payload = {
        "name": "Сырье с измененным кодом",
        "id": "new-code-prohibited-12345",
    }

    # Действие: попытка изменить уникальный код связанной группы
    response = client.put(
        f"/api/entities/groups/{raw_group.id}",
        data=json.dumps(invalid_update_payload),
        content_type="application/json",
    )

    # Проверка: запрос отклонен с кодом 400 и пояснением
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Запрещено изменять код" in data["error"]


# 12. Разрешено менять код (id) несвязанной сущности при обновлении (PUT)
def test_success_update_entity_code_when_not_referenced(client):
    # Подготовка: создаем временный склад, на который никто не ссылается
    temp_st = storage_model.create("Свободный склад")
    storage.add_entity("storages", temp_st)
    new_target_id = "allowed-custom-id-999"

    update_payload = {
        "name": "Свободный склад обновленный",
        "id": new_target_id,
    }

    # Действие
    response = client.put(
        f"/api/entities/storages/{temp_st.id}",
        data=json.dumps(update_payload),
        content_type="application/json",
    )

    # Проверка
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == new_target_id
    assert data["name"] == "Свободный склад обновленный"


# 13. Проверка запрета удаления сущности, если на нее ссылаются другие (DELETE)
def test_error_delete_entity_when_referenced(client):
    # Подготовка: единица измерения "грамм" связана с номенклатурой ("Мука", "Молоко") и кг (base_range)
    gram_range = next(r for r in storage.ranges if r.name == "грамм")
    assert len(service.get_dependencies(gram_range)) > 0

    # Действие: попытка удалить связанную единицу измерения
    response = client.delete(f"/api/entities/ranges/{gram_range.id}")

    # Проверка: отклонено с кодом 400
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Невозможно удалить сущность" in data["error"]
    assert "так как на нее ссылаются" in data["error"]


# 14. Интеграционный тест: успешное удаление несвязанной сущности (DELETE)
def test_success_delete_entity_when_not_referenced(client):
    # Подготовка: создаем изолированный склад
    temp_st = storage_model.create("Склад под снос")
    storage.add_entity("storages", temp_st)
    initial_count = len(storage.storages)

    # Действие
    response = client.delete(f"/api/entities/storages/{temp_st.id}")

    # Проверка
    assert response.status_code == 200
    assert response.get_json() == {"result": True}
    assert len(storage.storages) == initial_count - 1
    assert storage.get_by_code("storages", temp_st.id) is None


# 15. Проверка ошибки 404 при удалении несуществующей сущности (DELETE)
def test_error_delete_entity_not_found(client):
    # Действие
    response = client.delete("/api/entities/storages/non_existent_code_0000")

    # Проверка
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


# 16. Проверка успешного обновления связанной сущности без изменения её кода (PUT)
def test_success_update_referenced_entity_when_code_unchanged(client):
    # Подготовка: группа "Сырье" связана с номенклатурой
    raw_group = storage.groups[0]
    orig_id = raw_group.id
    update_payload = {
        "name": "Сырье и полуфабрикаты",
        "id": orig_id,
    }

    # Действие
    response = client.put(
        f"/api/entities/groups/{orig_id}",
        data=json.dumps(update_payload),
        content_type="application/json",
    )

    # Проверка: обновление разрешено, так как id не изменился
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == orig_id
    assert data["name"] == "Сырье и полуфабрикаты"


# 17. Проверка сохранения id при обновлении без явного указания id в теле запроса (PUT)
def test_success_update_entity_without_id_in_body_preserves_id(client):
    # Подготовка
    temp_st = storage_model.create("Склад без id в теле")
    storage.add_entity("storages", temp_st)
    orig_id = temp_st.id

    # Действие: передаем только новое имя без id
    response = client.put(
        f"/api/entities/storages/{orig_id}",
        data=json.dumps({"name": "Склад с сохраненным id"}),
        content_type="application/json",
    )

    # Проверка: сущность обновлена, исходный id сохранен
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == orig_id
    assert data["name"] == "Склад с сохраненным id"


# 18. Проверка доступности Swagger UI документации и редиректа /swagger
def test_swagger_endpoints_accessible(client):
    # Проверка редиректа с /swagger на /ui/
    resp_redirect = client.get("/swagger")
    assert resp_redirect.status_code in (301, 302, 308)
    assert "/ui/" in resp_redirect.headers.get("Location", "")


# 19. Проверка корректности структуры спецификации openapi.yaml
def test_openapi_specification_structure():
    import yaml
    with open("openapi.yaml", "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    assert spec is not None
    assert spec.get("openapi", "").startswith("3.")
    assert "paths" in spec
    paths = spec["paths"]
    assert "/api/reports/formats" in paths
    assert "/api/entities" in paths
    assert "/api/entities/{entity_type}" in paths
    assert "/api/entities/{entity_type}/{entity_id}" in paths
    assert "get" in paths["/api/reports/formats"]
    assert "get" in paths["/api/entities/{entity_type}"]
    assert "post" in paths["/api/entities/{entity_type}"]
    assert "put" in paths["/api/entities/{entity_type}/{entity_id}"]
    assert "delete" in paths["/api/entities/{entity_type}/{entity_id}"]



import pytest
from main import api, create_response, storage
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.convert_factory import convert_factory
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.osv_convertor import osv_convertor
from Src.Logics.storage_manager import storage_manager
from Src.Logics.storage_service import storage_service
from Src.Logics.text_report import text_report
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.osv_row_model import osv_row_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


@pytest.fixture
def client():
    storage.init_data()
    api.app.config["TESTING"] = True
    with api.app.test_client() as test_client:
        yield test_client


def test_storage_service_o1_id_and_code_lookup():
    # Поиск сущности в индексе по id, unique_code и имени
    manager = storage_manager()
    manager.init_data()
    srv = storage_service(manager)
    sugar = next(n for n in manager.nomenclatures if n.name == "Сахар")

    assert srv.get_by_code("nomenclatures", sugar.id) is sugar
    assert srv.get_by_code("nomenclatures", sugar.unique_code) is sugar
    assert srv.get_by_code("nomenclatures", sugar.name) is sugar
    assert srv.get_by_code("nomenclatures", "non_existing_code_999") is None


def test_storage_service_reverse_dependency_index_lookup():
    manager = storage_manager()
    manager.init_data()
    srv = storage_service(manager)
    gram_unit = next(r for r in manager.ranges if r.name == "грамм")

    deps = srv.get_dependencies(gram_unit)

    assert len(deps) > 0
    dep_names = [d.name for d in deps]
    assert "кг" in dep_names
    assert any(d.name in ("Молоко 3.2%", "Мука", "Соль", "Масло растительное") for d in deps)


def test_storage_service_indexes_updated_on_create_entity():
    manager = storage_manager()
    manager.init_data()
    srv = storage_service(manager)
    new_storage_data = {"name": "Новый индексируемый склад"}

    created = srv.create_entity("storages", new_storage_data)
    found = srv.get_by_code("storages", created.id)

    assert found is not None
    assert found.name == "Новый индексируемый склад"
    assert srv.get_by_code("storages", "Новый индексируемый склад") is created


def test_storage_service_indexes_updated_on_delete_entity():
    manager = storage_manager()
    manager.init_data()
    srv = storage_service(manager)
    temp_st = storage_model.create("Изолированный склад для удаления")
    manager.add_entity("storages", temp_st)
    srv._build_indexes()
    assert srv.get_by_code("storages", temp_st.id) is not None

    srv.delete_entity("storages", temp_st.id)
    assert srv.get_by_code("storages", temp_st.id) is None


def test_storage_service_reverse_dependency_index_updated_on_new_dependent_entity():
    manager = storage_manager()
    manager.init_data()
    srv = storage_service(manager)
    raw_group = next(g for g in manager.groups if g.name == "Сырье")
    pcs_unit = next(r for r in manager.ranges if r.name == "шт")
    initial_deps_count = len(srv.get_dependencies(raw_group))

    new_nom_data = {
        "name": "Новая позиция сырья",
        "full_name": "Новая позиция сырья ГОСТ",
        "group": {"id": raw_group.id, "name": raw_group.name, "type": "nomenclature_group_model"},
        "range": {"id": pcs_unit.id, "name": pcs_unit.name, "conversion_factor": 1.0, "type": "range_model"},
    }
    created_nom = srv.create_entity("nomenclatures", new_nom_data)
    new_deps = srv.get_dependencies(raw_group)

    assert len(new_deps) == initial_deps_count + 1
    assert created_nom in new_deps


def test_reports_pure_logic_without_flask_context():
    # Отчеты должны собираться без активного контекста Flask
    manager = storage_manager()
    manager.init_data()
    recipe = manager.recipes[0]
    txt_rep = text_report()
    csv_rep = csv_report()
    md_rep = markdown_report()

    txt_res = txt_rep.build(recipe)
    csv_res = csv_rep.build(recipe)
    md_res = md_rep.build(recipe)

    assert isinstance(txt_res, report_result_dto)
    assert isinstance(csv_res, report_result_dto)
    assert isinstance(md_res, report_result_dto)
    assert txt_rep.as_attachment is False
    assert csv_rep.as_attachment is True
    assert md_rep.as_attachment is True
    assert "Код|Наименование" in txt_res.text
    assert "Код,Наименование" in csv_res.text
    assert "| Код | Наименование |" in md_res.text


def test_web_create_response_delegation(client):
    text_content = "Тестовый отчет"
    dto = report_result_dto(text=text_content, data=text_content.encode("utf-8"))
    csv_rep = csv_report()

    with api.app.test_request_context():
        resp = create_response(csv_rep, dto, filename="custom_report")

    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("Content-Type", "")
    assert "custom_report.csv" in resp.headers.get("Content-Disposition", "")


def test_osv_convertor_direct_and_factory_conversion():
    st = storage_model.create("Склад №1")
    grp = nomenclature_group_model.create("Сырье")
    unit = range_model.create_gram("грамм")
    nom = nomenclature_model.create("Мука", "Мука пшеничная", grp, unit)
    row = osv_row_model(st, nom, unit, opening_balance=5.0, income=20.0, outcome=10.0, closing_balance=15.0)

    factory_dict = convert_factory().convert(row)
    convertor_dict = osv_convertor().convert(row)
    model_delegated_dict = row.to_dict()

    assert factory_dict == convertor_dict
    assert model_delegated_dict == factory_dict
    assert factory_dict["storage"]["name"] == "Склад №1"
    assert factory_dict["nomenclature"]["name"] == "Мука"
    assert factory_dict["opening_balance"] == 5.0
    assert factory_dict["closing_balance"] == 15.0


def test_api_osv_endpoint_uses_convert_factory(client):
    response = client.post("/api/reports/osv", json={})

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "closing_balance" in data[0]
    assert "storage" in data[0]
    assert "nomenclature" in data[0]


def test_storage_manager_has_no_service_delegates():
    manager = storage_manager()

    assert not hasattr(manager, "get_by_code") or "get_by_code" not in manager.__class__.__dict__
    assert not hasattr(manager, "is_valid_type") or "is_valid_type" not in manager.__class__.__dict__


def test_storage_manager_version_tracking():
    manager = storage_manager()
    initial_version = manager.version
    unit = range_model("тестовая мера", 1.0)

    manager.add_entity("ranges", unit)
    updated_version = manager.version
    manager.remove_entity("ranges", unit)
    final_version = manager.version

    assert updated_version == initial_version + 1
    assert final_version == initial_version + 2


def test_storage_service_get_default_recipe():
    manager = storage_manager()
    manager.init_data()
    srv = storage_service(manager)
    first_recipe = manager.recipes[0]

    default_rec = srv.get_default_recipe()
    named_rec = srv.get_default_recipe(first_recipe.name)
    unknown_rec = srv.get_default_recipe("несуществующий_рецепт_999")

    assert default_rec is first_recipe
    assert named_rec is first_recipe
    assert unknown_rec is first_recipe


def test_api_get_report_with_recipe_query_parameter(client):
    recipe = storage.recipes[0]

    response = client.get(f"/api/get_report?recipe={recipe.name}&format=TXT")

    assert response.status_code == 200
    assert "text/plain" in response.headers.get("Content-Type", "")
    assert "Код|Наименование" in response.data.decode("utf-8")

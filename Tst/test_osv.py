import datetime
import pytest
from Src.Core.exceptions import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.osv_service import osv_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.osv_row_model import osv_row_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model


def test_transaction_model_create_and_properties():
    st = storage_model.create("Главный склад")
    grp = nomenclature_group_model.create("Сырье")
    unit = range_model.create_gram("грамм")
    nom = nomenclature_model.create("Мука", "Мука в/с", grp, unit)
    dt = datetime.datetime(2026, 11, 15, 10, 0)

    tx = transaction_model.create(st, nom, unit, 50.0, dt)
    assert tx.storage == st
    assert tx.nomenclature == nom
    assert tx.range == unit
    assert tx.value == 50.0
    assert tx.period == dt

    with pytest.raises(argument_exception):
        tx.value = 0

    with pytest.raises(argument_exception):
        transaction_model.create(st, nom, unit, 0.0, dt)


def test_osv_row_model_to_dict():
    st = storage_model.create("Склад 1")
    grp = nomenclature_group_model.create("Сырье")
    unit = range_model.create_gram("грамм")
    nom = nomenclature_model.create("Сахар", "Сахар ГОСТ", grp, unit)

    row = osv_row_model(st, nom, unit, opening_balance=10.0, income=100.0, outcome=40.0, closing_balance=70.0)
    assert row.opening_balance == 10.0
    assert row.income == 100.0
    assert row.outcome == 40.0
    assert row.closing_balance == 70.0

    d = row.to_dict()
    assert d["storage"]["name"] == "Склад 1"
    assert d["nomenclature"]["name"] == "Сахар"
    assert d["opening_balance"] == 10.0
    assert d["closing_balance"] == 70.0


def test_osv_service_build_all():
    manager = storage_manager()
    manager.init_data()

    service = osv_service(manager)
    rows = service.build_osv()

    assert len(rows) > 0
    sugar_row = next((r for r in rows if r.nomenclature.name == "Сахар"), None)
    assert sugar_row is not None
    assert sugar_row.income == 100.0
    assert sugar_row.outcome == 25.0
    assert sugar_row.closing_balance == 75.0


def test_osv_service_build_with_filter_by_nomenclature():
    manager = storage_manager()
    manager.init_data()

    service = osv_service(manager)
    f = filter_dto()
    f.add("name", filter_type_enum.EQUALS, "Сахар")

    filtered_rows = service.build_osv(f)
    assert len(filtered_rows) == 1
    assert filtered_rows[0].nomenclature.name == "Сахар"


def test_osv_service_build_with_filter_by_storage():
    manager = storage_manager()
    manager.init_data()

    service = osv_service(manager)
    f = filter_dto()
    f.add("name", filter_type_enum.LIKE, "Холодильная")

    filtered_rows = service.build_osv(f)
    assert len(filtered_rows) > 0
    assert all("Холодильная" in r.storage.name for r in filtered_rows)


def test_osv_service_period_opening_balance_and_unit_conversion():
    # Проверяем расчет начального остатка по периоду и перевод граммов в кг
    manager = storage_manager()
    manager.init_data()

    main_storage = next(s for s in manager.storages if s.name == "Главный склад")
    sugar = next(n for n in manager.nomenclatures if n.name == "Сахар")
    gram = next(r for r in manager.ranges if r.name == "грамм")

    # Списание 500 г сахара (0.5 кг) 13 ноября
    tx_gram = transaction_model.create(
        main_storage, sugar, gram, -500.0, datetime.datetime(2026, 11, 13, 10, 0)
    )
    manager.add_entity(manager.transaction_key(), tx_gram)

    service = osv_service(manager)
    f = filter_dto(
        start_period=datetime.datetime(2026, 11, 11, 0, 0),
        end_period=datetime.datetime(2026, 11, 15, 0, 0),
    )
    f.add("name", filter_type_enum.EQUALS, "Сахар")

    rows = service.build_osv(f)
    assert len(rows) == 1
    row = rows[0]
    assert row.opening_balance == 100.0
    assert row.income == 0.0
    assert row.outcome == 25.5
    assert row.closing_balance == 74.5

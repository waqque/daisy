import datetime
import pytest
from Src.Core.exceptions import argument_exception
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum


def test_filter_type_enum_values():
    assert filter_type_enum.EQUALS.value == "EQUALS"
    assert filter_type_enum.LIKE.value == "LIKE"


def test_filter_type_enum_from_value():
    assert filter_type_enum.from_value("EQUALS") == filter_type_enum.EQUALS
    assert filter_type_enum.from_value("equals") == filter_type_enum.EQUALS
    assert filter_type_enum.from_value("EQ") == filter_type_enum.EQUALS
    assert filter_type_enum.from_value("LIKE") == filter_type_enum.LIKE
    assert filter_type_enum.from_value("like") == filter_type_enum.LIKE
    assert filter_type_enum.from_value("contains") == filter_type_enum.LIKE
    assert filter_type_enum.from_value(filter_type_enum.LIKE) == filter_type_enum.LIKE

    with pytest.raises(argument_exception):
        filter_type_enum.from_value("unknown")


def test_filter_item_dto_creation_and_properties():
    item = filter_item_dto("name", filter_type_enum.LIKE, "Сахар")
    assert item.field_name == "name"
    assert item.filter_type == filter_type_enum.LIKE
    assert item.value == "Сахар"


def test_filter_item_dto_to_dict_and_from_dict():
    orig = filter_item_dto("name", "like", "мука")
    d = orig.to_dict()
    assert d == {"field_name": "name", "filter_type": "LIKE", "value": "мука"}

    restored = filter_item_dto.from_dict(d)
    assert restored.field_name == "name"
    assert restored.filter_type == filter_type_enum.LIKE
    assert restored.value == "мука"


def test_filter_dto_creation_and_add():
    dto = filter_dto()
    dto.domain_type = "nomenclatures"
    dto.add("name", filter_type_enum.LIKE, "Сахар")
    dto.add("unique_code", filter_type_enum.EQUALS, "abc")

    assert dto.domain_type == "nomenclatures"
    assert len(dto.filters) == 2
    assert len(dto) == 2
    assert [f.field_name for f in dto] == ["name", "unique_code"]


def test_filter_dto_from_dict_with_filters_list():
    data = {
        "domain_type": "ranges",
        "filters": [
            {"field_name": "name", "filter_type": "EQUALS", "value": "кг"},
            {"field_name": "unique_code", "filter_type": "LIKE", "value": "001"},
        ],
    }
    dto = filter_dto.from_dict(data)
    assert dto.domain_type == "ranges"
    assert len(dto.filters) == 2
    assert dto.filters[0].field_name == "name"
    assert dto.filters[0].value == "кг"
    assert dto.filters[1].field_name == "unique_code"
    assert dto.filters[1].filter_type == filter_type_enum.LIKE


def test_filter_dto_from_dict_with_shorthand_fields():
    data = {"name": "Блинчики", "filter_type": "LIKE"}
    dto = filter_dto.from_dict(data)
    assert len(dto.filters) == 1
    assert dto.filters[0].field_name == "name"
    assert dto.filters[0].filter_type == filter_type_enum.LIKE
    assert dto.filters[0].value == "Блинчики"


def test_filter_dto_period_parsing():
    data = {
        "start_period": "2026-11-11T00:00:00",
        "end_period": "2026-11-15T00:00:00",
    }
    dto = filter_dto.from_dict(data)
    assert dto.start_period == datetime.datetime(2026, 11, 11, 0, 0)
    assert dto.end_period == datetime.datetime(2026, 11, 15, 0, 0)
    assert len(dto.filters) == 0


def test_filter_dto_validation_errors():
    item = filter_item_dto()
    with pytest.raises(argument_exception):
        item.field_name = 123

    dto = filter_dto()
    with pytest.raises(argument_exception):
        dto.domain_type = 456

    with pytest.raises(argument_exception):
        dto.filters = "not a list"

    with pytest.raises(argument_exception):
        dto.start_period = "not-a-date"

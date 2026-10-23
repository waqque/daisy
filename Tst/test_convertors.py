import datetime
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model


# 1. Тест basic_convertor: конвертация чисел
def test_basic_convertor_numeric_success():
    # Подготовка
    convertor = basic_convertor()
    number_int = 42
    number_float = 3.14

    # Действие
    result_int = convertor.convert(number_int)
    result_float = convertor.convert(number_float, "pi")

    # Проверка
    assert isinstance(result_int, dict)
    assert result_int.get("value") == 42
    assert result_float.get("pi") == 3.14


# 2. Тест basic_convertor: конвертация строки
def test_basic_convertor_string_success():
    # Подготовка
    convertor = basic_convertor()
    text = "Hello World"

    # Действие
    result = convertor.convert(text, "title")

    # Проверка
    assert isinstance(result, dict)
    assert result == {"title": "Hello World"}


# 3. Тест basic_convertor: конвертация объекта с простыми полями
def test_basic_convertor_object_with_basic_fields_success():
    # Подготовка
    convertor = basic_convertor()
    org = organization_model(
        "Ромашка", "1234567890", "123456789", "40702810000000000001", "ООО"
    )

    # Действие
    result = convertor.convert(org)

    # Проверка
    assert isinstance(result, dict)
    assert result["name"] == "Ромашка"
    assert result["inn"] == "1234567890"
    assert result["bic"] == "123456789"
    assert result["account"] == "40702810000000000001"
    assert result["ownership_form"] == "ООО"
    assert "id" in result


# 4. Тест datetime_convertor: конвертация datetime
def test_datetime_convertor_primitive_datetime_success():
    # Подготовка
    convertor = datetime_convertor()
    now = datetime.datetime(2026, 10, 23, 12, 30, 45)

    # Действие
    result = convertor.convert(now, "created_at")

    # Проверка
    assert isinstance(result, dict)
    assert result == {"created_at": "2026-10-23T12:30:45"}


# 5. Тест datetime_convertor: конвертация date
def test_datetime_convertor_primitive_date_success():
    # Подготовка
    convertor = datetime_convertor()
    today = datetime.date(2026, 10, 23)

    # Действие
    result = convertor.convert(today)

    # Проверка
    assert isinstance(result, dict)
    assert result.get("value") == "2026-10-23"


# 6. Тест datetime_convertor: извлечение полей DateTime из объекта
def test_datetime_convertor_object_with_datetime_success():
    # Подготовка
    class sample_event:
        def __init__(self):
            self.title = "Конференция"
            self.event_date = datetime.datetime(2026, 12, 1, 9, 0, 0)

    event = sample_event()
    convertor = datetime_convertor()

    # Действие
    result = convertor.convert(event)

    # Проверка
    assert isinstance(result, dict)
    assert "event_date" in result
    assert result["event_date"] == "2026-12-01T09:00:00"
    assert "title" not in result


# 7. Тест reference_convertor: конвертация одиночной ссылки с именем поля
def test_reference_convertor_single_reference_success():
    # Подготовка
    convertor = reference_convertor()
    group = nomenclature_group_model("Бакалея")

    # Действие
    result = convertor.convert(group, "group")

    # Проверка
    assert isinstance(result, dict)
    assert "group" in result
    assert result["group"]["name"] == "Бакалея"
    assert "id" in result["group"]


# 8. Тест reference_convertor: конвертация составного объекта с вложенными ссылками
def test_reference_convertor_composite_object_success():
    # Подготовка
    convertor = reference_convertor()
    group = nomenclature_group_model("Специи")
    unit = range_model("грамм", 1.0)
    item = nomenclature_model("Перец черный", "Перец черный молотый", group, unit)

    # Действие
    result = convertor.convert(item)

    # Проверка
    assert isinstance(result, dict)
    assert "group" in result
    assert "range" in result
    assert result["group"]["name"] == "Специи"
    assert result["range"]["name"] == "грамм"
    assert result["range"]["conversion_factor"] == 1.0
    assert "full_name" not in result

import datetime
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


# 1. Тест convert_factory: получение конвертора по типу через метод create
def test_convert_factory_create_returns_appropriate_convertor():
    # Подготовка
    factory = convert_factory()

    # Действие
    conv_basic = factory.create(123)
    conv_str = factory.create("текст")
    conv_dt = factory.create(datetime.datetime.now())
    conv_ref = factory.create(nomenclature_group_model("Тест"))

    # Проверка
    assert isinstance(conv_basic, basic_convertor)
    assert isinstance(conv_str, basic_convertor)
    assert isinstance(conv_dt, datetime_convertor)
    assert isinstance(conv_ref, reference_convertor)


# 2. Тест convert_factory: конвертация простых типов
def test_convert_factory_convert_primitive_types():
    # Подготовка
    factory = convert_factory()

    # Действие
    res_int = factory.convert(42)
    res_str = factory.convert("Привет")

    # Проверка
    assert res_int == {"value": 42}
    assert res_str == {"value": "Привет"}


# 3. Тест convert_factory: конвертация даты и времени
def test_convert_factory_convert_datetime():
    # Подготовка
    factory = convert_factory()
    now = datetime.datetime(2026, 10, 23, 10, 0, 0)

    # Действие
    result = factory.convert(now)

    # Проверка
    assert result == {"value": "2026-10-23T10:00:00"}


# 4. Тест convert_factory: конвертация простой модели
def test_convert_factory_convert_simple_model():
    # Подготовка
    factory = convert_factory()
    unit = range_model("кг", 1000.0)

    # Действие
    result = factory.convert(unit)

    # Проверка
    assert isinstance(result, dict)
    assert result["name"] == "кг"
    assert result["conversion_factor"] == 1000.0
    assert result["base_range"] is None
    assert "id" in result


# 5. Тест convert_factory: конвертация составной модели со ссылками
def test_convert_factory_convert_composite_model():
    # Подготовка
    factory = convert_factory()
    group = nomenclature_group_model("Бакалея")
    unit = range_model("кг", 1000.0)
    item = nomenclature_model("Сахар", "Сахар-песок ГОСТ", group, unit)

    # Действие
    result = factory.convert(item)

    # Проверка
    assert isinstance(result, dict)
    assert result["name"] == "Сахар"
    assert result["full_name"] == "Сахар-песок ГОСТ"
    # Ссылочное поле group преобразовано в словарь
    assert isinstance(result["group"], dict)
    assert result["group"]["name"] == "Бакалея"
    # Ссылочное поле range преобразовано в словарь
    assert isinstance(result["range"], dict)
    assert result["range"]["name"] == "кг"
    assert result["range"]["conversion_factor"] == 1000.0


# 6. Тест convert_factory: комплексная конвертация рецепта из хранилища
def test_convert_factory_convert_recipe_from_storage():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]
    factory = convert_factory()

    # Действие
    result = factory.convert(recipe)

    # Проверка
    assert isinstance(result, dict)
    assert result["name"] == recipe.name
    # Вложенное блюдо как словарь
    assert isinstance(result["dish"], dict)
    assert result["dish"]["name"] == recipe.dish.name
    # Вложенные строки рецепта как список словарей
    assert isinstance(result["rows"], list)
    assert len(result["rows"]) == len(recipe.rows)
    assert isinstance(result["rows"][0], dict)
    assert "nomenclature" in result["rows"][0]

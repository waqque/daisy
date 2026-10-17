import pytest
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_type_dto import report_type_enum
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.settings_model import settings_model


# 1. Положительный тест на создание отчетов всех типов
def test_report_factory_create_all_types_success():
    # Подготовка
    factory = report_factory()

    # Действие и проверка
    assert isinstance(factory.create(report_type_enum.TXT), text_report)
    assert isinstance(factory.create(report_type_enum.CSV), csv_report)
    assert isinstance(factory.create(report_type_enum.MARKDOWN), markdown_report)
    assert isinstance(factory.create(report_type_enum.XML), xml_report)
    assert isinstance(factory.create(report_type_enum.HTML), html_report)


# 2. Отрицательный тест на передачу некорректного типа
def test_report_factory_create_invalid_type_raises_exception():
    # Подготовка
    factory = report_factory()

    # Действие и проверка
    with pytest.raises(argument_exception):
        factory.create("INVALID_TYPE")

    with pytest.raises(argument_exception):
        factory.create(None)


# 3. Тест на создание и построение отчета через create
def test_report_factory_create_and_build_report_success():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]
    factory = report_factory()

    # Действие
    report = factory.create(report_type_enum.TXT)
    result = report.build(recipe)

    # Проверка
    assert result is not None
    assert result.text.startswith("Код|Наименование|Брутто|Нетто")
    assert len(result.text.split("\n")) == len(recipe.items) + 1
    assert "Молоко" in result.text


# 4. Проверка инкапсуляции настроек в фабрику
def test_report_factory_settings_encapsulation():
    # Подготовка
    custom_settings = settings_model()
    custom_settings.response_format = report_type_enum.MARKDOWN

    # Действие
    factory = report_factory(custom_settings)

    # Проверка
    assert factory.settings is custom_settings
    assert factory.settings.response_format == report_type_enum.MARKDOWN


# 5. Проверка создания ответа по умолчанию через create_default
def test_report_factory_create_default():
    # Подготовка
    storage = storage_manager()
    storage.init_data()
    recipe = storage.recipes[0]

    custom_settings = settings_model()
    custom_settings.response_format = report_type_enum.XML
    factory = report_factory(custom_settings)

    # Действие: без источника данных возвращает экземпляр отчета
    report = factory.create_default()
    assert isinstance(report, xml_report)

    # Действие: с источником данных возвращает результат
    result = factory.create_default(recipe)
    assert result is not None
    assert "<recipe" in result.text


# 6. Проверка динамической регистрации нового типа отчета в фабрике (Open/Closed Principle)
def test_report_factory_register_new_format_success():
    from Src.Core.abstract_report import abstract_report
    from Src.Dtos.report_result_dto import report_result_dto
    from Src.Models.recipe_model import recipe_model

    # Подготовка
    factory = report_factory()

    class custom_report(abstract_report):
        def __init__(self):
            super().__init__()
            self.register(recipe_model, lambda r: report_result_dto(text="custom"))

    # Действие: регистрируем кастомный класс для типа TXT
    factory.register(report_type_enum.TXT, custom_report)
    created = factory.create(report_type_enum.TXT)

    # Проверка
    assert isinstance(created, custom_report)
    assert created.build(storage_manager().recipes[0]).text == "custom"


# 7. Проверка валидации аргументов метода register в фабрике
def test_report_factory_register_invalid_arguments_raises_exception():
    # Подготовка
    factory = report_factory()

    # Проверка некорректного типа отчета
    with pytest.raises(argument_exception):
        factory.register("NOT_AN_ENUM", text_report)

    # Проверка некорректного класса отчета (не наследник abstract_report)
    with pytest.raises(argument_exception):
        factory.register(report_type_enum.TXT, dict)


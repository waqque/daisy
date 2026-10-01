import os
import time
import pytest
from Src.Core.exceptions import argument_exception
from Src.Logics.settings_manager import settings_manager


# Проверка успешной загрузки настроек по умолчанию без исключений
def test_settings_manager_load_success():
    manager = settings_manager()
    result = manager.load()
    assert result is True


# Проверка, что после загрузки объект настроек не пустой
def test_settings_manager_load_not_empty():
    manager = settings_manager()
    manager.load()
    assert manager.settings is not None
    assert manager.settings.name == "ООО Ромашка"


# Проверка работы шаблона Singleton: разные вызовы возвращают один и тот же объект
def test_settings_manager_singleton_equals():
    instance1 = settings_manager()
    time.sleep(0.01)
    instance2 = settings_manager()
    assert instance1 == instance2
    assert instance1 is instance2


# Проверка равенства свойств настроек между экземплярами Singleton
def test_settings_manager_singleton_properties_equals():
    instance1 = settings_manager()
    instance2 = settings_manager()
    instance1.load()
    assert instance1.settings == instance2.settings


# Проверка флага успешной загрузки настроек
def test_settings_manager_is_loaded_true():
    manager = settings_manager()
    manager.load()
    assert manager.is_loaded is True


# Проверка ошибки при загрузке несуществующего файла
def test_settings_manager_load_file_not_found_raises_exception():
    manager = settings_manager()
    with pytest.raises(argument_exception):
        manager.load("non_existent_file_path_12345.json")


# Проверка ошибки валидации при передаче нестрокового имени файла
def test_settings_manager_load_invalid_filename_type_raises_exception():
    manager = settings_manager()
    with pytest.raises(argument_exception):
        manager.load(123)


# Проверка ошибки валидации при передаче пустого имени файла
def test_settings_manager_load_empty_filename_raises_exception():
    manager = settings_manager()
    with pytest.raises(argument_exception):
        manager._load_validator("   ")


# Прямая проверка метода convert с валидным словарем данных
def test_settings_manager_convert_success():
    manager = settings_manager()
    data = {
        "name": "АО ВкусВилл",
        "inn": "7701234567",
        "bic": "044525225",
        "account": "40702810938000012345",
        "ownership_form": "АО",
        "is_first_start": False,
    }
    manager.convert(data)

    assert manager.settings is not None
    assert manager.settings.name == "АО ВкусВилл"
    assert manager.settings.inn == "7701234567"
    assert manager.settings.bic == "044525225"
    assert manager.settings.account == "40702810938000012345"
    assert manager.settings.ownership_form == "АО"
    assert manager.settings.is_first_start is False


# Проверка ошибки метода convert при передаче некорректного типа данных
def test_settings_manager_convert_invalid_type_raises_exception():
    manager = settings_manager()
    with pytest.raises(argument_exception):
        manager.convert("строка_вместо_словаря")

    with pytest.raises(argument_exception):
        manager.convert([1, 2, 3])

    with pytest.raises(argument_exception):
        manager.convert(None)


# Проверка метода convert при частичном наборе полей
def test_settings_manager_convert_partial_fields_success():
    manager = settings_manager()
    data = {
        "name": "ООО Новое Имя",
        "is_first_start": True,
    }
    manager.convert(data)

    assert manager.settings.name == "ООО Новое Имя"
    assert manager.settings.is_first_start is True
    # Остальные поля сохраняют значения по умолчанию модели
    assert manager.settings.inn == "7701234567"
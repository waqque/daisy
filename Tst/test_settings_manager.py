import pytest
from Src.Core.exceptions import argument_exception
from Src.Logics.settings_manager import settings_manager


# 1. Проверка успешной загрузки настроек по умолчанию из конфигурационного файла
def test_settings_manager_load_success():
    # Подготовка
    manager = settings_manager()

    # Действие
    result = manager.load()

    # Проверка
    assert result is True


# 2. Проверка создания и корректности свойств объекта организации после загрузки
def test_settings_manager_load_not_empty():
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверка
    assert manager.settings is not None
    assert manager.settings.organization is not None
    assert manager.settings.name == "ООО Ромашка"
    assert manager.settings.organization.name == "ООО Ромашка"


# 3. Проверка работы паттерна Singleton: повторные вызовы возвращают один и тот же объект
def test_settings_manager_singleton_same_instance():
    # Подготовка и Действие
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Проверка
    assert instance1 is instance2


# 4. Проверка идентичности объекта настроек в двух ссылках на Singleton
def test_settings_manager_singleton_properties_equals():
    # Подготовка
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Действие
    instance1.load()

    # Проверка
    assert instance1.settings is instance2.settings


# 5. Проверка выставления флага успешной загрузки настроек
def test_settings_manager_is_loaded_true():
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверка
    assert manager.is_loaded is True


# 6. Проверка ошибки при попытке загрузить несуществующий файл настроек
def test_settings_manager_load_file_not_found_raises_exception():
    # Подготовка
    manager = settings_manager()
    non_existent_file = "non_existent_file_path_12345.json"

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.load(non_existent_file)


# 7. Проверка ошибки валидации при передаче нестрокового имени файла
def test_settings_manager_load_invalid_filename_type_raises_exception():
    # Подготовка
    manager = settings_manager()
    invalid_filename = 123

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.load(invalid_filename)


# 8. Проверка ошибки валидации при передаче пустого имени файла
def test_settings_manager_load_empty_filename_raises_exception():
    # Подготовка
    manager = settings_manager()
    empty_filename = "   "

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.load(empty_filename)


# 9. Прямая проверка метода convert с валидным словарем данных
def test_settings_manager_convert_success():
    # Подготовка
    manager = settings_manager()
    data = {
        "name": "АО ВкусВилл",
        "inn": "7701234567",
        "bic": "044525225",
        "account": "40702810938000012345",
        "ownership_form": "АО",
        "is_first_start": False,
    }

    # Действие
    manager.convert(data)

    # Проверка
    assert manager.settings is not None
    assert manager.settings.organization is not None
    assert manager.settings.name == "АО ВкусВилл"
    assert manager.settings.inn == "7701234567"
    assert manager.settings.bic == "044525225"
    assert manager.settings.account == "40702810938000012345"
    assert manager.settings.ownership_form == "АО"
    assert manager.settings.is_first_start is False


# 10. Проверка ошибки метода convert при передаче некорректного типа данных
def test_settings_manager_convert_invalid_type_raises_exception():
    # Подготовка
    manager = settings_manager()
    invalid_cases = ["строка_вместо_словаря", [1, 2, 3], None, 123, 45.6]

    # Действие и проверка
    for case in invalid_cases:
        with pytest.raises(argument_exception):
            manager.convert(case)


# 11. Проверка использования значений по умолчанию при отсутствии полей в словаре настроек
def test_settings_manager_convert_missing_fields_uses_defaults():
    # Подготовка
    manager = settings_manager()

    # Действие: передача пустого словаря
    manager.convert({})

    # Проверка: должны примениться дефолтные параметры
    assert manager.settings is not None
    assert manager.settings.organization is not None
    assert manager.settings.name == "ООО Ромашка"
    assert manager.settings.inn == "7701234567"
    assert manager.settings.bic == "044525225"
    assert manager.settings.account == "40702810938000012345"
    assert manager.settings.ownership_form == "ООО"
    assert manager.settings.is_first_start is True


# 11.1. Проверка частичной передачи настроек (переданные поля перезаписываются, остальные берутся по умолчанию)
def test_settings_manager_convert_partial_data_uses_defaults():
    # Подготовка
    manager = settings_manager()
    partial_data = {
        "name": "ИП Иванов",
        "is_first_start": False,
    }

    # Действие
    manager.convert(partial_data)

    # Проверка
    assert manager.settings is not None
    assert manager.settings.name == "ИП Иванов"
    assert manager.settings.inn == "7701234567"
    assert manager.settings.is_first_start is False


# 12. Проверка, что небулевые значения для флага первого старта вызывают ошибку
def test_settings_manager_convert_string_bool_raises_exception():
    # Подготовка
    manager = settings_manager()
    invalid_bools = ["false", "0", 1, 0, "True", None]

    # Действие и проверка
    for invalid_val in invalid_bools:
        data = {
            "name": "ООО Новое Имя",
            "inn": "7701234567",
            "bic": "044525225",
            "account": "40702810938000012345",
            "ownership_form": "ООО",
            "is_first_start": invalid_val,
        }
        with pytest.raises(argument_exception):
            manager.convert(data)
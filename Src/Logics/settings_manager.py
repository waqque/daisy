import json
import os
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exceptions import argument_exception
from Src.Models.settings_model import settings_model


class settings_manager(abstract_manager):
    # Менеджер настроек приложения 
    __default_file_name: str = "settings.json"
    __settings: settings_model = None
    __is_loaded: bool = False

    def __new__(cls):
        # Обеспечение единственного экземпляра менеджера настроек в памяти
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> bool:
        # Чтение и загрузка данных конфигурации из файла
        if not isinstance(file_name, str):
            raise argument_exception(
                "file_name", "Имя файла должно быть строковым значением."
            )

        if not file_name or file_name.strip() == "":
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            inner_file_name = os.path.join(base_dir, self.__default_file_name)
        else:
            inner_file_name = file_name.strip()

        self._load_validator(inner_file_name)

        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.convert(data)
                settings_manager.__is_loaded = True
                return True
        except FileNotFoundError:
            raise argument_exception(
                "file_name", f"Файл настроек '{inner_file_name}' не найден."
            )
        except argument_exception:
            raise
        except Exception as ex:
            raise argument_exception("file", f"Ошибка обработки файла: {str(ex)}")

    def _load_validator(self, file_name: str) -> None:
        # Валидация входного параметра пути к файлу
        if not isinstance(file_name, str):
            raise argument_exception(
                "file_name", "Имя файла должно быть строковым значением."
            )
        if not file_name.strip():
            raise argument_exception("file_name", "Имя файла не может быть пустым.")

    def convert(self, data: dict) -> None:
        # Преобразование загруженного словаря в экземпляр settings_model
        if not isinstance(data, dict):
            raise argument_exception(
                "data", "Данные настроек должны передаваться в виде словаря (dict)."
            )

        model = settings_model()

        if "name" in data:
            model.name = data["name"]
        if "inn" in data:
            model.inn = data["inn"]
        if "bic" in data:
            model.bic = data["bic"]
        if "account" in data:
            model.account = data["account"]
        if "ownership_form" in data:
            model.ownership_form = data["ownership_form"]
        if "is_first_start" in data:
            model.is_first_start = bool(data["is_first_start"])

        settings_manager.__settings = model

    @property
    def settings(self) -> settings_model:
        # Доступ к текущему объекту настроек
        return settings_manager.__settings

    @property
    def is_loaded(self) -> bool:
        # Проверка факта успешной загрузки настроек
        return settings_manager.__is_loaded
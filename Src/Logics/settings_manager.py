import json
import os
from typing import Optional
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exceptions import argument_exception, operation_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Models.settings_model import settings_model


class settings_manager(abstract_manager):
    # Менеджер настроек приложения с реализацией шаблона Singleton
    __default_file_name: str = "settings.json"

    def __new__(cls):
        # Обеспечение единственного экземпляра менеджера настроек в памяти
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
            cls.instance.__init_state()
        return cls.instance

    def __init_state(self) -> None:
        # Инициализация состояния экземпляра
        super().__init__()
        self.__settings: Optional[settings_model] = None
        self._is_loaded: bool = False

    def __init__(self) -> None:
        # Защита от повторной инициализации при получении экземпляра Singleton
        pass

    def load(self, file_name: str = "") -> bool:
        # Чтение и загрузка данных конфигурации из файла
        if not isinstance(file_name, str):
            raise argument_exception(
                "file_name", "Имя файла должно быть строковым значением."
            )

        if file_name == "":
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            inner_file_name = os.path.join(base_dir, self.__default_file_name)
        elif not file_name.strip():
            raise argument_exception("file_name", "Имя файла не может быть пустым.")
        else:
            inner_file_name = file_name.strip()

        self._load_validator(inner_file_name)

        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.convert(data)
                self._is_loaded = True
                return True
        except FileNotFoundError as ex:
            raise argument_exception(
                "file_name", f"Файл настроек '{inner_file_name}' не найден."
            ) from ex
        except argument_exception:
            raise
        except Exception as ex:
            raise operation_exception(f"Ошибка обработки файла: {str(ex)}") from ex

    def _load_validator(self, file_name: str) -> None:
        # Валидация входного параметра пути к файлу
        if not isinstance(file_name, str):
            raise argument_exception(
                "file_name", "Имя файла должно быть строковым значением."
            )
        if not file_name.strip():
            raise argument_exception("file_name", "Имя файла не может быть пустым.")

    def convert(self, data: dict) -> None:
        # Десериализация словаря настроек в модель settings_model через фабрику
        if not isinstance(data, dict):
            raise argument_exception(
                "data", "Данные настроек должны передаваться в виде словаря (dict)."
            )

        factory = deserialize_factory()
        self.__settings = factory.deserialize(data, target_type=settings_model)
        self._is_loaded = True

    @property
    def settings(self) -> Optional[settings_model]:
        # Доступ к текущему объекту настроек
        return self.__settings

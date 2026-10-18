from abc import ABC
from typing import Callable, Dict, Optional, Type
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    # Базовый абстрактный класс для формирования отчетов с диспетчеризацией обработчиков (Open/Closed Principle)
    __handlers: Dict[Type, Callable]

    def __init__(self) -> None:
        # Инициализация словаря обработчиков типов сущностей
        self.__handlers = {}

    @property
    def handlers(self) -> Dict[Type, Callable]:
        # Словарь зарегистрированных обработчиков сущностей
        if not hasattr(self, "_abstract_report__handlers"):
            self.__handlers = {}
        return self.__handlers

    def register(self, entity_type: Type, handler: Callable) -> None:
        # Регистрация обработчика построения отчета для указанного типа сущности
        if not isinstance(entity_type, type):
            raise argument_exception(
                "entity_type", "Тип сущности должен быть классом (type)."
            )
        if not callable(handler):
            raise argument_exception(
                "handler", "Обработчик должен быть вызываемым объектом (callable)."
            )
        self.handlers[entity_type] = handler

    def _find_handler(self, source_type: Type) -> Optional[Callable]:
        # Поиск обработчика по точному типу или с учетом иерархии наследования
        if source_type in self.handlers:
            return self.handlers[source_type]
        for registered_type, handler in self.handlers.items():
            if issubclass(source_type, registered_type):
                return handler
        return None

    def build(self, source) -> report_result_dto:
        # Построение отчета на основе зарегистрированного обработчика без каскадов проверок
        if source is None:
            raise argument_exception("source", "Источник данных не может быть None.")

        handler = self._find_handler(type(source))
        if handler is None:
            raise argument_exception(
                "source", "Неподдерживаемый тип источника данных."
            )

        return handler(source)

    @property
    def mimetype(self) -> str:
        # MIME-тип формируемого отчета
        return "text/plain; charset=utf-8"

    @property
    def file_extension(self) -> str:
        # Расширение файла отчета
        return "txt"

    @property
    def as_attachment(self) -> bool:
        # Признак передачи в виде вложения (attachment)
        return False

    def create_response(self, result: report_result_dto, filename: str = "report"):
        # Полиморфное формирование HTTP-ответа (по умолчанию текстовый ответ)
        import flask

        return flask.Response(result.text, mimetype=self.mimetype)

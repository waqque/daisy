from typing import Optional
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_type_dto import report_type_enum
from Src.Models.organization_model import organization_model


class settings_model:
    # Модель настроек приложения с агрегацией организации, флагом первого старта и форматом ответа
    __organization: Optional[organization_model] = None
    __is_first_start: bool = True
    __response_format: report_type_enum = report_type_enum.TXT

    def __init__(self) -> None:
        # По умолчанию модель пустая 
        self.__organization = None
        self.__is_first_start = True
        self.__response_format = report_type_enum.TXT

    @property
    def organization(self) -> Optional[organization_model]:
        # Получение связанного объекта организации
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        # Установка организации с проверкой типа
        if not isinstance(value, organization_model):
            raise argument_exception(
                "organization", "Организация должна быть экземпляром organization_model."
            )
        self.__organization = value

    @property
    def is_first_start(self) -> bool:
        # Флаг первого запуска системы
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        # Валидация типа булевого флага
        if not isinstance(value, bool):
            raise argument_exception(
                "is_first_start", "Флаг первого запуска должен быть типа bool."
            )
        self.__is_first_start = value

    @property
    def response_format(self) -> report_type_enum:
        # Формат ответа по умолчанию
        return self.__response_format

    @response_format.setter
    def response_format(self, value) -> None:
        # Валидация и установка формата ответа
        if isinstance(value, report_type_enum):
            self.__response_format = value
            return

        if isinstance(value, str):
            val_upper = value.strip().upper()
            formats = {
                "CSV": report_type_enum.CSV,
                "MARKDOWN": report_type_enum.MARKDOWN,
                "XML": report_type_enum.XML,
                "TXT": report_type_enum.TXT,
                "HTML": report_type_enum.HTML,
            }
            if val_upper in formats:
                self.__response_format = formats[val_upper]
                return

        raise argument_exception(
            "response_format", "Формат ответа должен быть одним из: CSV, Markdown, XML, TXT, HTML."
        )

    @property
    def name(self) -> str:
        # Наименование организации из настроек
        return self.__organization.name if self.__organization is not None else ""

    @property
    def inn(self) -> str:
        # ИНН организации из настроек
        return self.__organization.inn if self.__organization is not None else ""

    @property
    def bic(self) -> str:
        # БИК банка организации из настроек
        return self.__organization.bic if self.__organization is not None else ""

    @property
    def account(self) -> str:
        # Расчетный счет организации из настроек
        return self.__organization.account if self.__organization is not None else ""

    @property
    def ownership_form(self) -> str:
        # Форма собственности организации из настроек
        return self.__organization.ownership_form if self.__organization is not None else ""
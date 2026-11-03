from abc import ABC, abstractmethod
from typing import Any, Optional, Type


class abstract_deserialize_factory(ABC):
    # Базовый интерфейс для фабрики десериализации данных в модели

    @abstractmethod
    def deserialize(self, data: Any, target_type: Optional[Type] = None) -> Any:
        # Главный метод: принимает словарь или JSON и превращает его в объект модели
        pass

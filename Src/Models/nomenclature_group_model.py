from typing import Optional
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception


class nomenclature_group_model(base_model):
    # Группа товаров и сырья (может ссылаться на родительскую группу)
    __parent_group: Optional["nomenclature_group_model"] = None

    def __init__(
        self,
        name: str,
        parent_group: Optional["nomenclature_group_model"] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.parent_group = parent_group

    @property
    def parent_group(self) -> Optional["nomenclature_group_model"]:
        # Группа-владелец (None, если группа верхнего уровня)
        return self.__parent_group

    @parent_group.setter
    def parent_group(self, value: Optional["nomenclature_group_model"]) -> None:
        if value is not None and not isinstance(value, nomenclature_group_model):
            raise argument_exception(
                "parent_group", "Группа-владелец должна быть объектом nomenclature_group_model."
            )
        # Не даем замкнуть дерево групп в цикл
        current = value
        while current is not None:
            if current is self or current.id == self.id:
                raise argument_exception(
                    "parent_group", "Обнаружена циклическая ссылка в иерархии групп."
                )
            current = current.parent_group
        self.__parent_group = value

    @staticmethod
    def create(
        name: str,
        parent_group: Optional["nomenclature_group_model"] = None,
    ) -> "nomenclature_group_model":
        # Фабричный метод создания группы
        return nomenclature_group_model(name, parent_group=parent_group)

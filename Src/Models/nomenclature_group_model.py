from Src.Core.abstract_model import base_model


class nomenclature_group_model(base_model):
  # Группа для товаров и сырья
  def __init__(self, name: str) -> None:
    super().__init__()
    self.name = name
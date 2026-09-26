from Src.Core.abstract_model import base_model


class storage_model(base_model):
  # Склад компании
  def __init__(self, name: str) -> None:
    super().__init__()
    self.name = name
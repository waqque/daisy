from typing import Dict, List, Optional, Tuple
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.osv_row_model import osv_row_model
from Src.Models.range_model import range_model


class osv_service:
    # Сервис формирования оборотно-сальдовой ведомости по складским транзакциям
    __storage: storage_manager

    def __init__(self, storage: Optional[storage_manager] = None) -> None:
        self.__storage = storage if storage is not None else storage_manager()

    @property
    def storage(self) -> storage_manager:
        return self.__storage

    def _ensure_loaded(self) -> None:
        # Подгружаем стартовые данные, если хранилище еще пустое
        if not self.__storage.is_loaded:
            self.__storage.start()

    @staticmethod
    def _get_root_range(unit: Optional[range_model]) -> Optional[range_model]:
        # Доходим до самой базовой единицы измерения (например, кг -> грамм)
        current = unit
        visited = set()
        while current is not None and current.base_range is not None:
            if id(current) in visited:
                break
            visited.add(id(current))
            current = current.base_range
        return current

    @classmethod
    def _convert_amount(
        cls,
        amount: float,
        src_unit: Optional[range_model],
        target_unit: Optional[range_model],
    ) -> float:
        # Переводим количество из единицы транзакции в единицу номенклатуры, если база общая
        if src_unit is None or target_unit is None or src_unit == target_unit:
            return float(amount)
        if cls._get_root_range(src_unit) == cls._get_root_range(target_unit):
            target_factor = target_unit.to_base(1.0)
            if target_factor > 0:
                return src_unit.to_base(amount) / target_factor
        return float(amount)

    def build_osv(self, filter: Optional[filter_dto] = None) -> List[osv_row_model]:
        # Собираем ОСВ: сначала фильтруем транзакции через прототип, затем считаем остатки и обороты
        self._ensure_loaded()

        raw_transactions = self.__storage.data[storage_manager.transaction_key()]
        tx_proto = prototype(raw_transactions)
        transactions = tx_proto.clone(filter).data if filter is not None else tx_proto.data

        start_period = filter.start_period if filter is not None else None
        end_period = filter.end_period if filter is not None else None

        # Группируем движения по паре (склад, номенклатура)
        groups: Dict[Tuple[str, str], dict] = {}
        for tx in transactions:
            if tx.storage is None or tx.nomenclature is None:
                continue
            if end_period is not None and tx.period > end_period:
                continue

            key = (tx.storage.unique_code, tx.nomenclature.unique_code)
            target_range = tx.nomenclature.range if tx.nomenclature.range is not None else tx.range
            if key not in groups:
                groups[key] = {
                    "storage": tx.storage,
                    "nomenclature": tx.nomenclature,
                    "range": target_range,
                    "opening_balance": 0.0,
                    "income": 0.0,
                    "outcome": 0.0,
                }

            val = self._convert_amount(tx.value, tx.range, groups[key]["range"])
            # Все операции до начала периода идут в начальный остаток, остальные в приход/расход
            if start_period is not None and tx.period < start_period:
                groups[key]["opening_balance"] += val
            elif val > 0:
                groups[key]["income"] += val
            else:
                groups[key]["outcome"] += abs(val)

        # Собираем итоговые строки ведомости
        rows: List[osv_row_model] = []
        for g in groups.values():
            closing = g["opening_balance"] + g["income"] - g["outcome"]
            rows.append(
                osv_row_model(
                    storage=g["storage"],
                    nomenclature=g["nomenclature"],
                    range_unit=g["range"],
                    opening_balance=g["opening_balance"],
                    income=g["income"],
                    outcome=g["outcome"],
                    closing_balance=closing,
                )
            )

        return rows

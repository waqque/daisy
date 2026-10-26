from typing import Optional
from Src.Logics.settings_manager import settings_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.settings_model import settings_model
from Src.Models.storage_model import storage_model


class storage_seeder:
    # Сервис первичного наполнения хранилища демонстрационными данными (Single Responsibility Principle)

    def seed(self, storage, settings: Optional[settings_model] = None) -> None:
        # Наполнение хранилища базовыми сущностями системы
        storage.clear()

        # 1. Единицы измерения (фабричные методы)
        g_unit = range_model.create_gram("грамм")
        kg_unit = range_model.create_kilogram("кг", base_range=g_unit)
        pcs_unit = range_model("шт", 1.0)
        for unit in (g_unit, kg_unit, pcs_unit):
            storage.add_entity("ranges", unit)

        # 2. Группы номенклатуры (фабричные методы)
        group_raw = nomenclature_group_model.create("Сырье")
        group_dairy = nomenclature_group_model.create("Молочная продукция")
        group_pack = nomenclature_group_model.create("Упаковка")
        for group in (group_raw, group_dairy, group_pack):
            storage.add_entity("groups", group)

        # 3. Номенклатура (сырье, упаковка и готовое блюдо, согласованы с рецептом ТТК)
        sugar = nomenclature_model.create("Сахар", "Сахар белый ГОСТ", group_raw, kg_unit)
        milk = nomenclature_model.create(
            "Молоко 3.2%", "Молоко пастеризованное 3.2%", group_dairy, g_unit
        )
        flour = nomenclature_model.create("Мука", "Мука пшеничная в/с", group_raw, g_unit)
        egg = nomenclature_model.create("Яйцо", "Яйцо куриное", group_raw, pcs_unit)
        salt = nomenclature_model.create("Соль", "Соль поваренная", group_raw, g_unit)
        oil = nomenclature_model.create(
            "Масло растительное", "Масло растительное рафинированное", group_raw, g_unit
        )
        box = nomenclature_model.create(
            "Контейнер", "Контейнер пищевой картонный для блинчиков", group_pack, pcs_unit
        )
        pancakes_dish = nomenclature_model.create(
            "Блинчики", "Блинчики классические (порция 2 шт.)", group_dairy, pcs_unit
        )
        for nom in (sugar, milk, flour, egg, salt, oil, box, pancakes_dish):
            storage.add_entity("nomenclatures", nom)

        # 4. Склады (фабричные методы)
        main_storage = storage_model.create("Главный склад")
        cold_storage = storage_model.create("Холодильная камера")
        for st in (main_storage, cold_storage):
            storage.add_entity("storages", st)

        # 5. Организация (композиция из настроек или дефолтная модель через фабричный метод)
        if settings is None:
            manager = settings_manager()
            settings = manager.settings

        if settings is not None and settings.organization is not None:
            storage.add_entity("organizations", settings.organization)
        else:
            org = organization_model.create(
                name="ООО Ромашка",
                inn="7701234567",
                bic="044525225",
                account="40702810938000012345",
                ownership_form="ООО",
            )
            storage.add_entity("organizations", org)

        # 6. Технологические карты (1 блюдо - 1 техкарта, рецепт с упаковкой по Docs/Recipe.md)
        row_milk = recipe_row_model.create(milk, 100.0, 100.0)
        row_flour = recipe_row_model.create(flour, 50.0, 50.0)
        row_egg = recipe_row_model.create(egg, 1.0, 1.0)
        row_sugar = recipe_row_model.create(sugar, 10.0, 10.0)
        row_salt = recipe_row_model.create(salt, 2.0, 2.0)
        row_oil = recipe_row_model.create(oil, 10.0, 10.0)
        row_box = recipe_row_model.create(box, 15.0, 0.0)

        pancakes_recipe = recipe_model.create(
            name="Блинчики классические",
            dish=pancakes_dish,
            rows=[row_milk, row_flour, row_egg, row_sugar, row_salt, row_oil, row_box],
        )
        storage.add_entity("recipes", pancakes_recipe)

        storage._is_loaded = True

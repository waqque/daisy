import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


@pytest.fixture
def sample_data():
    # Фикстура базовых сущностей для тестирования рецептов
    g_unit = range_model.create_gram("грамм")
    pcs_unit = range_model("шт", 1.0)

    group_raw = nomenclature_group_model.create("Сырье")
    group_dish = nomenclature_group_model.create("Готовая продукция")
    group_pack = nomenclature_group_model.create("Упаковка")

    milk = nomenclature_model.create(
        "Молоко 3.2%", "Молоко пастеризованное", group_raw, g_unit
    )
    flour = nomenclature_model.create("Мука", "Мука пшеничная в/с", group_raw, g_unit)
    egg = nomenclature_model.create("Яйцо", "Яйцо куриное", group_raw, pcs_unit)
    pancakes_dish = nomenclature_model.create(
        "Блинчики", "Блинчики классические (порция 2 шт.)", group_dish, pcs_unit
    )
    box = nomenclature_model.create(
        "Ланч-бокс", "Контейнер пищевой картонный", group_pack, pcs_unit
    )

    return {
        "g_unit": g_unit,
        "pcs_unit": pcs_unit,
        "milk": milk,
        "flour": flour,
        "egg": egg,
        "pancakes_dish": pancakes_dish,
        "box": box,
    }


# 1. Успешное создание строки рецепта через конструктор и фабричный метод
def test_recipe_row_model_init_success(sample_data):
    # Подготовка
    flour = sample_data["flour"]

    # Действие
    row1 = recipe_row_model(flour, 50.0, 50.0)
    row2 = recipe_row_model.create(flour, 60.0, 50.0)

    # Проверка
    assert row1.nomenclature is flour
    assert row1.gross_weight == 50.0
    assert row1.net_weight == 50.0
    assert row1.name == flour.name
    assert row1.range is flour.range
    assert row1.id != ""

    assert row2.gross_weight == 60.0
    assert row2.net_weight == 50.0


# 2. Ошибка: неверный тип номенклатуры в строке рецепта
def test_recipe_row_model_invalid_nomenclature_raises_exception():
    # Подготовка
    invalid_nom = "не объект номенклатуры"

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(invalid_nom, 100.0, 100.0)


# 3. Ошибка: отрицательный вес брутто или нетто в строке рецепта
def test_recipe_row_model_negative_weights_raise_exception(sample_data):
    # Подготовка
    milk = sample_data["milk"]

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(milk, -10.0, 10.0)

    with pytest.raises(argument_exception):
        recipe_row_model(milk, 10.0, -5.0)

    with pytest.raises(argument_exception):
        recipe_row_model(milk, "не_число", 10.0)

    with pytest.raises(argument_exception):
        recipe_row_model(milk, 10.0, "не_число")


# 4. Ошибка: вес нетто превышает вес брутто в строке рецепта
def test_recipe_row_model_net_greater_than_gross_raises_exception(sample_data):
    # Подготовка
    milk = sample_data["milk"]

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(milk, 50.0, 60.0)


# 5. Успешное создание технологической карты (рецепта) с расчетом брутто и нетто
def test_recipe_model_init_and_weight_calculation_success(sample_data):
    # Подготовка
    milk = sample_data["milk"]
    flour = sample_data["flour"]
    egg = sample_data["egg"]
    dish = sample_data["pancakes_dish"]

    row_milk = recipe_row_model.create(milk, 100.0, 100.0)
    row_flour = recipe_row_model.create(flour, 50.0, 50.0)
    row_egg = recipe_row_model.create(egg, 1.0, 1.0)

    # Действие
    recipe = recipe_model.create(
        name="Блинчики классические",
        dish=dish,
        rows=[row_milk, row_flour, row_egg],
    )

    # Проверка
    assert recipe.name == "Блинчики классические"
    assert recipe.dish is dish
    assert len(recipe.rows) == 3
    assert recipe.gross_weight == 151.0
    assert recipe.net_weight == 151.0


# 6. Проверка динамического пересчета веса Брутто и Нетто при добавлении ингредиента
def test_recipe_model_add_row_recalculates_weight(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    recipe = recipe_model(
        name="Тесто",
        dish=dish,
        rows=[recipe_row_model.create(flour, 50.0, 50.0)],
    )
    assert recipe.gross_weight == 50.0
    assert recipe.net_weight == 50.0

    # Действие: добавление молока
    recipe.add_row(recipe_row_model.create(milk, 100.0, 95.0))

    # Проверка
    assert len(recipe.rows) == 2
    assert recipe.gross_weight == 150.0
    assert recipe.net_weight == 145.0


# 7. Проверка динамического пересчета веса Брутто и Нетто при исключении ингредиента
def test_recipe_model_delete_row_recalculates_weight(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    row_flour = recipe_row_model.create(flour, 50.0, 50.0)
    row_milk = recipe_row_model.create(milk, 100.0, 95.0)
    recipe = recipe_model(name="Тесто", dish=dish, rows=[row_flour, row_milk])

    # Действие: удаление муки
    recipe.delete_row(row_flour)

    # Проверка
    assert len(recipe.rows) == 1
    assert recipe.gross_weight == 100.0
    assert recipe.net_weight == 95.0


# 8. Ошибка: исключение строки, которой нет в рецепте
def test_recipe_model_delete_nonexistent_row_raises_exception(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    recipe = recipe_model(name="Тесто", dish=dish)
    row_milk = recipe_row_model.create(milk, 100.0, 100.0)

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe.delete_row(row_milk)


# 9. Инкапсуляция: внешняя модификация возвращаемого списка rows не меняет рецепт
def test_recipe_model_rows_encapsulation(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    recipe = recipe_model(
        name="Тесто",
        dish=dish,
        rows=[recipe_row_model.create(flour, 50.0, 50.0)],
    )

    # Действие: попытка добавить строку в скопированный список
    recipe.rows.append(recipe_row_model.create(milk, 100.0, 100.0))

    # Проверка
    assert len(recipe.rows) == 1


# 10. Рецепт с упаковкой: расчет брутто и нетто с тарой
def test_recipe_model_with_packaging(sample_data):
    # Подготовка
    milk = sample_data["milk"]
    box = sample_data["box"]
    dish = sample_data["pancakes_dish"]

    # Ингредиент: молоко 100г, чистый выход 95г
    row_ingredient = recipe_row_model.create(milk, gross_weight=100.0, net_weight=95.0)
    # Упаковка: вес тары 15г брутто, 0г нетто (упаковка не употребляется в пищу)
    row_pack = recipe_row_model.create(box, gross_weight=15.0, net_weight=0.0)

    # Действие
    packaged_dish_recipe = recipe_model.create(
        name="Блинчики на вынос с упаковкой",
        dish=dish,
        rows=[row_ingredient, row_pack],
    )

    # Проверка: брутто включает упаковку, нетто только съедобную часть
    assert packaged_dish_recipe.gross_weight == 115.0
    assert packaged_dish_recipe.net_weight == 95.0


# 11. Ошибка: некорректный тип блюда при создании рецепта
def test_recipe_model_invalid_dish_raises_exception():
    # Подготовка
    invalid_dish = "строка_вместо_номенклатуры"

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_model(name="Рецепт", dish=invalid_dish)


# 12. Рекурсия "блюдо в блюде": блинчики с заготовкой (полуфабрикатом теста)
def test_recipe_model_composite_recursion_pancakes_dough():
    # Подготовка: единицы и группы
    g_unit = range_model.create_gram("грамм")
    pcs_unit = range_model("шт", 1.0)
    group_raw = nomenclature_group_model.create("Сырье")
    group_semi = nomenclature_group_model.create("Полуфабрикаты")
    group_dish = nomenclature_group_model.create("Готовые блюда")
    group_pack = nomenclature_group_model.create("Упаковка")

    milk = nomenclature_model.create("Молоко", "Молоко 3.2%", group_raw, g_unit)
    flour = nomenclature_model.create("Мука", "Мука пшеничная", group_raw, g_unit)
    egg = nomenclature_model.create("Яйцо", "Яйцо куриное", group_raw, pcs_unit)
    oil = nomenclature_model.create("Масло", "Масло растительное", group_raw, g_unit)
    box = nomenclature_model.create("Контейнер", "Контейнер пищевой", group_pack, pcs_unit)

    # Заготовка (полуфабрикат): тесто блинное (молоко 100г + мука 50г + яйцо 10г = 160г)
    dough_nom = nomenclature_model.create(
        "Тесто блинное", "Тесто блинное (заготовка)", group_semi, g_unit
    )
    dough_recipe = recipe_model.create(
        name="Тесто блинное",
        dish=dough_nom,
        rows=[
            recipe_row_model.create(milk, 100.0, 100.0),
            recipe_row_model.create(flour, 50.0, 50.0),
            recipe_row_model.create(egg, 10.0, 10.0),
        ],
    )
    assert dough_recipe.gross_weight == 160.0
    assert dough_recipe.net_weight == 160.0

    # Готовое блюдо: блинчики (заготовка теста через nested_recipe + масло 10г + упаковка 15г/0г)
    pancakes_nom = nomenclature_model.create(
        "Блинчики", "Блинчики классические", group_dish, pcs_unit
    )
    row_dough = recipe_row_model.create(dough_nom, nested_recipe=dough_recipe)
    assert row_dough.gross_weight == 160.0
    assert row_dough.net_weight == 160.0
    row_oil = recipe_row_model.create(oil, 10.0, 10.0)
    row_pack = recipe_row_model.create(box, 15.0, 0.0)

    pancakes_recipe = recipe_model.create(
        name="Блинчики классические",
        dish=pancakes_nom,
        rows=[row_dough, row_oil, row_pack],
    )

    # Проверка: рекурсивный вес брутто (160 + 10 + 15 = 185) и нетто (160 + 10 + 0 = 170)
    assert pancakes_recipe.is_composite is True
    assert pancakes_recipe.gross_weight == 185.0
    assert pancakes_recipe.net_weight == 170.0


# 13. Динамический пересчет веса составного блюда при изменении вложенного полуфабриката
def test_recipe_model_composite_dynamic_recalculation_when_semi_finished_changes():
    # Подготовка
    g_unit = range_model.create_gram("грамм")
    group = nomenclature_group_model.create("Ингредиенты")

    comp1 = nomenclature_model.create("Компонент 1", "Компонент 1", group, g_unit)
    comp2 = nomenclature_model.create("Компонент 2", "Компонент 2", group, g_unit)
    comp3 = nomenclature_model.create("Компонент 3", "Компонент 3", group, g_unit)
    semi_nom = nomenclature_model.create("Заготовка", "Заготовка ПФ", group, g_unit)
    dish_nom = nomenclature_model.create("Блюдо", "Финальное блюдо", group, g_unit)

    # Создаем заготовку: 50г + 50г = 100г
    semi_recipe = recipe_model.create(
        "Заготовка",
        dish=semi_nom,
        rows=[recipe_row_model.create(comp1, 50.0, 50.0)],
    )

    # Создаем блюдо с заготовкой: 50г (заготовка) + 30г (компонент 2) = 80г
    main_recipe = recipe_model.create(
        "Блюдо",
        dish=dish_nom,
        rows=[
            recipe_row_model.create(semi_nom, nested_recipe=semi_recipe),
            recipe_row_model.create(comp2, 30.0, 30.0),
        ],
    )
    assert main_recipe.gross_weight == 80.0
    assert main_recipe.net_weight == 80.0

    # Действие: добавляем компонент 3 (40г) в заготовку
    semi_recipe.add_row(recipe_row_model.create(comp3, 40.0, 40.0))

    # Проверка: вес итогового блюда автоматически увеличился за счет рекурсивного пересчета
    assert semi_recipe.gross_weight == 90.0
    assert main_recipe.gross_weight == 120.0
    assert main_recipe.net_weight == 120.0


# 14. Многоуровневая рекурсия (3 уровня вложенности: начинка -> заготовка -> блюдо)
def test_recipe_model_multilevel_recursion_three_levels():
    # Подготовка
    g_unit = range_model.create_gram("грамм")
    group = nomenclature_group_model.create("Кухня")

    berries = nomenclature_model.create("Ягоды", "Ягоды свежие", group, g_unit)
    sugar = nomenclature_model.create("Сахар", "Сахар", group, g_unit)
    dough = nomenclature_model.create("Тесто", "Тесто", group, g_unit)
    topping = nomenclature_model.create("Топинг", "Топинг", group, g_unit)

    filling_nom = nomenclature_model.create("Начинка", "Начинка ягодная", group, g_unit)
    base_nom = nomenclature_model.create("Блинчик с начинкой п/ф", "Блинчик с начинкой заготовка", group, g_unit)
    dish_nom = nomenclature_model.create("Блинчики десертные", "Блинчики десертные порция", group, g_unit)

    # Уровень 1: Начинка (20г + 10г = 30г)
    filling_recipe = recipe_model.create(
        "Начинка",
        dish=filling_nom,
        rows=[recipe_row_model.create(berries, 20.0, 20.0), recipe_row_model.create(sugar, 10.0, 10.0)],
    )

    # Уровень 2: Заготовка (Начинка [вложенная 30г] + Тесто 70г = 100г)
    base_recipe = recipe_model.create(
        "Блинчик с начинкой п/ф",
        dish=base_nom,
        rows=[
            recipe_row_model.create(filling_nom, nested_recipe=filling_recipe),
            recipe_row_model.create(dough, 70.0, 70.0),
        ],
    )

    # Уровень 3: Финальное блюдо (Заготовка [вложенная 100г] + Топинг 50г = 150г)
    final_recipe = recipe_model.create(
        "Блинчики десертные",
        dish=dish_nom,
        rows=[
            recipe_row_model.create(base_nom, nested_recipe=base_recipe),
            recipe_row_model.create(topping, 50.0, 50.0),
        ],
    )

    # Проверка сквозной трехуровневой рекурсии
    assert filling_recipe.gross_weight == 30.0
    assert base_recipe.gross_weight == 100.0
    assert final_recipe.gross_weight == 150.0
    assert final_recipe.net_weight == 150.0


# 15. Защита от циклической рекурсии: рецепт не может включать сам себя
def test_recipe_model_self_nesting_raises_exception():
    # Подготовка
    pcs = range_model("шт", 1.0)
    group = nomenclature_group_model.create("Блюда")
    dish = nomenclature_model.create("Суп", "Суп овощной", group, pcs)

    recipe = recipe_model.create("Суп", dish=dish)
    row_self = recipe_row_model.create(dish, nested_recipe=recipe)

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe.add_row(row_self)


# 16. Ошибка: неверный тип вложенного рецепта в строке
def test_recipe_row_model_nested_recipe_invalid_type_raises_exception():
    # Подготовка
    pcs = range_model("шт", 1.0)
    group = nomenclature_group_model.create("Блюда")
    dish = nomenclature_model.create("Блюдо", "Блюдо", group, pcs)

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(nomenclature=dish, nested_recipe="не_рецепт")

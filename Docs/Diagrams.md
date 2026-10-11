# UML-диаграммы подсистем управления данными

Данный документ содержит UML-диаграммы классов и диаграмму последовательности для компонентов `settings_manager` и `storage_manager` информационной системы сети ресторанов «Ромашка».

---

## 1. Диаграмма классов `settings_manager`

Менеджер настроек реализует паттерн **Singleton** и отвечает за загрузку конфигурационного файла `settings.json`, валидацию пути и структуры, а также трансформацию словаря настроек в композитную модель `settings_model`.

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        #_is_loaded: bool
        +load(file_name: str) bool
        +convert(data: dict)* None
        +is_loaded: bool
    }

    class settings_manager {
        -instance: settings_manager$
        +load(file_name: str) bool
        +convert(data: dict) None
        +settings: settings_model
        +is_loaded: bool
    }

    class base_model {
        <<abstract>>
        +id: str
        +name: str
    }

    class organization_model {
        +inn: str
        +bic: str
        +account: str
        +ownership_form: str
    }

    class settings_model {
        +organization: organization_model
        +is_first_start: bool
    }

    abstract_manager <|-- settings_manager
    base_model <|-- organization_model
    settings_manager "1" *-- "1" settings_model : Управляет
    settings_model "1" *-- "1" organization_model : Агрегирует
```

---

## 2. Диаграмма классов `storage_manager`

`storage_manager` реализует паттерн **Singleton** и хранит коллекции доменных сущностей с контролем уникальности записей по наименованию (`name`) и идентификатору (`unique_code`). При первом запуске системы (`is_first_start == True`) менеджер производит автоматическое первичное наполнение (seed data).

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        #_is_loaded: bool
        +load(file_name: str) bool
        +convert(data: dict)* None
        +is_loaded: bool
    }

    class storage_manager {
        -instance: storage_manager$
        +clear() None
        +start(settings: settings_model) None
        +add_entity(key: str, entity: base_model) None
        +convert(data: dict) None
        +init_data(settings: settings_model) None
        +ranges: list
        +groups: list
        +nomenclatures: list
        +storages: list
        +organizations: list
        +recipes: list
    }

    class base_model {
        <<abstract>>
        +id: str
        +name: str
    }

    class range_model {
        +conversion_factor: float
        +base_range: range_model
        +create_gram(name: str)$ range_model
        +create_kilogram(name: str)$ range_model
    }

    class nomenclature_group_model {
        +create(name: str)$ nomenclature_group_model
    }

    class nomenclature_model {
        +full_name: str
        +group: nomenclature_group_model
        +range: range_model
        +create(name, full_name, group, range)$ nomenclature_model
    }

    class recipe_row_model {
        +nomenclature: nomenclature_model
        +gross_weight: float
        +net_weight: float
        +range: range_model
        +create(nomenclature, gross, net)$ recipe_row_model
    }

    class recipe_model {
        +dish: nomenclature_model
        +rows: list
        +gross_weight: float
        +net_weight: float
        +add_row(row: recipe_row_model) None
        +delete_row(row: recipe_row_model) None
        +create(name, dish, rows)$ recipe_model
    }

    class storage_model {
        +create(name: str)$ storage_model
    }

    class organization_model {
        +inn: str
        +bic: str
        +account: str
        +ownership_form: str
        +create(name, inn, bic, account, ownership_form)$ organization_model
    }

    abstract_manager <|-- storage_manager
    base_model <|-- range_model
    base_model <|-- nomenclature_group_model
    base_model <|-- nomenclature_model
    base_model <|-- recipe_row_model
    base_model <|-- recipe_model
    base_model <|-- storage_model
    base_model <|-- organization_model

    storage_manager "1" *-- "*" base_model : Хранит коллекции
    recipe_model "1" --> "1" nomenclature_model : 1 блюдо - 1 техкарта
    recipe_model "1" *-- "*" recipe_row_model : Строки рецепта
    recipe_row_model --> nomenclature_model : Сырье / тара
```

---

## 3. Диаграмма классов моделей технологических карт (рецептов)

Диаграмма детально отражает доменные модели производственного учета: технологическую карту (`recipe_model`) и строку расхода (`recipe_row_model`), а также их связи с номенклатурой (`nomenclature_model`) и единицами измерения (`range_model`).

```mermaid
classDiagram
    direction TB

    class base_model {
        <<abstract>>
        +id: str
        +name: str
    }

    class range_model {
        +conversion_factor: float
        +base_range: range_model
        +create_gram(name: str)$ range_model
        +create_kilogram(name: str)$ range_model
    }

    class nomenclature_model {
        +full_name: str
        +group: nomenclature_group_model
        +range: range_model
        +create(name, full_name, group, range)$ nomenclature_model
    }

    class recipe_row_model {
        +nomenclature: nomenclature_model
        +gross_weight: float
        +net_weight: float
        +range: range_model
        +create(nomenclature, gross_weight, net_weight)$ recipe_row_model
    }

    class recipe_model {
        +dish: nomenclature_model
        +rows: list
        +gross_weight: float
        +net_weight: float
        +add_row(row: recipe_row_model) None
        +delete_row(row: recipe_row_model) None
        +create(name, dish, rows)$ recipe_model
    }

    base_model <|-- range_model
    base_model <|-- nomenclature_model
    base_model <|-- recipe_row_model
    base_model <|-- recipe_model

    recipe_model "1" --> "1" nomenclature_model : 1 блюдо - 1 карта
    recipe_model "1" *-- "*" recipe_row_model : Содержит строки
    recipe_row_model "1" --> "1" nomenclature_model : Расходуемое сырье / тара
    recipe_row_model ..> range_model : Делегирует единицу
```

---

## 4. Диаграмма последовательности: Инициализация и запуск хранилища

Диаграмма иллюстрирует базовый сценарий взаимодействия компонентов при запуске хранилища (`storage_manager.start()`): получение настроек через `settings_manager`, загрузку файла `settings.json` (если настройки еще не были загружены) и первичное наполнение данными (`init_data()`) при первом старте системы (`is_first_start == True`).

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant SM as storage_manager
    participant SetM as settings_manager
    participant File as settings.json
    participant Model as settings_model

    Client->>SM: start()
    activate SM

    SM->>SetM: settings_manager()
    activate SetM
    SetM-->>SM: instance
    deactivate SetM

    opt Настройки не загружены (is_loaded == False)
        SM->>SetM: load()
        activate SetM
        SetM->>File: Чтение файла конфигурации
        File-->>SetM: JSON данные
        SetM->>SetM: convert(data)
        SetM->>Model: Создание settings_model
        SetM-->>SM: True
        deactivate SetM
    end

    SM->>SetM: settings
    activate SetM
    SetM-->>SM: settings_model
    deactivate SetM

    alt Первый запуск (is_first_start == True)
        SM->>SM: init_data(settings)
        Note over SM: Первичное наполнение (seed data):<br/>единицы, группы, номенклатура (с упаковкой),<br/>склады, организация, рецепты
    else Обычный запуск (is_first_start == False)
        Note over SM: Установка флага is_loaded = True
    end

    SM-->>Client: Завершение инициализации
    deactivate SM
```

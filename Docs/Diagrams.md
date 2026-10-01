# UML Диаграммы классов подсистем управления данными

Данный документ содержит UML-диаграммы классов и взаимодействия для компонентов `settings_manager` и `storage_manager` информационной системы сети ресторанов «Ромашка».

---

## 1. Диаграмма классов `settings_manager`

Менеджер настроек реализует паттерн **Singleton** и отвечает за загрузку конфигурационного файла `settings.json`, валидацию пути и структуры, а также трансформацию словаря настроек в модель `settings_model`.

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        -__file_name: str
        -__is_loaded: bool
        -__data: list
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
    }

    class settings_manager {
        -instance: settings_manager$
        -__default_file_name: str
        -__settings: settings_model
        -__is_loaded: bool
        +__new__() settings_manager
        +load(file_name: str) bool
        -_load_validator(file_name: str) void
        +convert(data: dict) void
        +settings() settings_model
        +is_loaded() bool
    }

    class base_model {
        <<abstract>>
        -__unique_code: str
        -__name: str
        +unique_code: str
        +id: str
        +name: str
        +__eq__(other: object) bool
    }

    class organization_model {
        -__inn: str
        -__bic: str
        -__account: str
        -__ownership_form: str
        +inn: str
        +bic: str
        +account: str
        +ownership_form: str
    }

    class settings_model {
        -__is_first_start: bool
        +is_first_start: bool
    }

    abstract_manager <|-- settings_manager : Наследование
    base_model <|-- organization_model : Наследование
    organization_model <|-- settings_model : Наследование
    settings_manager o-- settings_model : Агрегирует (хранит)
```

---

## 2. Диаграмма классов `storage_manager`

`storage_manager` реализует паттерн **Singleton** и хранит списки доменных сущностей с контролем уникальности записей по идентификатору (`unique_code`). При первом запуске системы (`is_first_start == True`) менеджер производит автоматическое первичное наполнение (seed data).

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
    }

    class storage_manager {
        -instance: storage_manager$
        -__data: dict
        +__new__() storage_manager
        +clear() void
        -__load_from_settings() void
        +add_entity(key: str, entity: base_model) void
        +convert(source_data: dict) void
        +init_data() void
        +data() dict
        +ranges() list
        +groups() list
        +nomenclatures() list
        +storages() list
        +organizations() list
    }

    class settings_manager {
        +settings: settings_model
        +is_loaded: bool
        +load() bool
    }

    class base_model {
        <<abstract>>
        +unique_code: str
        +id: str
        +name: str
        +__eq__(other: object) bool
    }

    class range_model {
        -__conversion_factor: float
        -__base_range: range_model
        +conversion_factor: float
        +base_range: range_model
        +to_base(amount: float) float
    }

    class nomenclature_group_model {
        +name: str
    }

    class nomenclature_model {
        -__full_name: str
        -__group: nomenclature_group_model
        -__range: range_model
        +full_name: str
        +group: nomenclature_group_model
        +range: range_model
    }

    class storage_model {
        +name: str
    }

    class organization_model {
        +inn: str
        +bic: str
        +account: str
        +ownership_form: str
    }

    abstract_manager <|-- storage_manager : Наследование
    storage_manager ..> settings_manager : Зависимость (проверка первого старта)

    base_model <|-- range_model : Наследование
    base_model <|-- nomenclature_group_model : Наследование
    base_model <|-- nomenclature_model : Наследование
    base_model <|-- storage_model : Наследование
    base_model <|-- organization_model : Наследование

    storage_manager *-- base_model : Хранит коллекции сущностей
    nomenclature_model --> nomenclature_group_model : Ссылается на группу
    nomenclature_model --> range_model : Ссылается на единицу
```

---

## 3. Диаграмма последовательности: Инициализация при первом старте

Диаграмма демонстрирует сценарий взаимодействия компонентов при первичном запуске системы:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant SM as storage_manager (Singleton)
    participant SetM as settings_manager (Singleton)
    participant File as settings.json
    participant Model as settings_model

    Client->>SM: storage_manager()
    activate SM
    Note over SM: Проверка отсутствия instance
    SM->>SM: clear()
    SM->>SM: __load_from_settings()
    SM->>SetM: settings_manager()
    activate SetM
    SetM-->>SM: instance
    deactivate SetM

    alt Настройки еще не загружены
        SM->>SetM: load()
        activate SetM
        SetM->>File: Чтение конфигурации
        File-->>SetM: JSON данные
        SetM->>SetM: convert(data)
        SetM->>Model: Создание settings_model
        SetM-->>SM: True
        deactivate SetM
    end

    SM->>SetM: settings.is_first_start
    activate SetM
    SetM-->>SM: True
    deactivate SetM

    opt Первый запуск (is_first_start == True)
        SM->>SM: init_data()
        Note over SM: Наполнение базовыми единицами (грамм, кг, шт),<br/>группами, складами и номенклатурой
    end

    SM-->>Client: instance storage_manager
    deactivate SM
```

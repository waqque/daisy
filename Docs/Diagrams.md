# UML Диаграммы классов подсистем управления данными

Данный документ содержит UML-диаграммы классов для компонентов `settings_manager` и `storage_manager` информационной системы сети ресторанов «Ромашка».

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
        -__default_file_name: str
        -__settings: settings_model
        +__new__() settings_manager
        +load(file_name: str) bool
        -_load_validator(file_name: str) None
        +convert(data: dict) None
        +settings: settings_model
        +is_loaded: bool
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
        -__organization: organization_model
        -__is_first_start: bool
        +organization: organization_model
        +is_first_start: bool
        +name: str
        +inn: str
        +bic: str
        +account: str
        +ownership_form: str
    }

    abstract_manager <|-- settings_manager
    base_model <|-- organization_model
    settings_manager "1" *-- "1" settings_model : Управляет жизненным циклом
    settings_model "1" *-- "1" organization_model : Агрегирует реквизиты
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
        -__data: dict
        +__new__() storage_manager
        +clear() None
        +start(settings: settings_model) None
        +add_entity(key: str, entity: base_model) None
        +convert(data: dict) None
        +init_data(settings: settings_model) None
        +data: dict
        +ranges: list
        +groups: list
        +nomenclatures: list
        +storages: list
        +organizations: list
        +is_loaded: bool
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

    abstract_manager <|-- storage_manager
    storage_manager ..> settings_manager : Зависимость конфигурации

    base_model <|-- range_model
    base_model <|-- nomenclature_group_model
    base_model <|-- nomenclature_model
    base_model <|-- storage_model
    base_model <|-- organization_model

    storage_manager "1" *-- "*" base_model : Хранит коллекции сущностей
    nomenclature_model --> nomenclature_group_model : Ссылается на группу
    nomenclature_model --> range_model : Ссылается на единицу
```

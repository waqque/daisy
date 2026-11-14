import connexion
import flask
from Src.Dtos.report_type_dto import report_type_enum
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

api = connexion.FlaskApp(__name__, specification_dir="./")

# Инициализация хранилища данных и настроек
storage = storage_manager()


def create_response(report, result, filename: str = "report"):
    # Формирование ответа RestApi делегированием полиморфному методу отчета
    if hasattr(report, "create_response"):
        return report.create_response(result, filename)
    if hasattr(result, "create_response"):
        return result.create_response(report, filename)
    instance = report_factory().create(result if isinstance(result, report_type_enum) else report)
    dto = report if not isinstance(result, report_type_enum) else result
    return instance.create_response(dto, filename)


@api.route("/", methods=["GET"])
def index():
    # Перенаправление на получение отчета по умолчанию
    return flask.redirect("/api/get_report")


@api.route("/swagger", methods=["GET"])
def swagger():
    return flask.redirect("/ui/")


@api.route("/api/get_report", methods=["GET"])
def get_report():
    # Формирование и получение текстового отчета по технологической карте
    if not storage.is_loaded:
        storage.start()

    if len(storage.recipes) == 0:
        return "Рецепты не найдены в хранилище.", 404

    # Определение технологической карты (по умолчанию первая из хранилища)
    recipe = storage.recipes[0]
    if flask.has_request_context():
        recipe_name = flask.request.args.get("recipe")
        if recipe_name:
            found_recipe = next(
                (r for r in storage.recipes if r.name.lower() == recipe_name.lower()),
                None,
            )
            if found_recipe:
                recipe = found_recipe

    # Определение формата отчета (по умолчанию TXT)
    report_type = report_type_enum.TXT
    if flask.has_request_context():
        format_name = flask.request.args.get("format")
        if format_name:
            try:
                report_type = report_type_enum[format_name.upper()]
            except KeyError:
                return f"Неподдерживаемый формат отчета: {format_name}", 400

    report = report_factory().create(report_type)
    result = report.build(recipe)
    return report.create_response(result, filename=recipe.name)


# 5. Метод GET: формирование отчета в указанном формате для указанного типа и кода сущности
@api.route("/api/report/<entity_type>/<entity_code>", methods=["GET"])
def get_report_by_format(entity_type: str, entity_code: str):
    format_name = flask.request.args.get("format", "TXT")
    try:
        report_type = report_type_enum[format_name.upper()]
    except KeyError:
        return f"Неподдерживаемый формат отчета: {format_name}", 400

    entity, err_msg, status_code = storage.get_entity(entity_type, entity_code)
    if err_msg:
        return err_msg, status_code

    report = report_factory().create(report_type)
    result = report.build(entity)
    return report.create_response(result, filename=f"{entity_type}_{entity.name}")


# 8. Метод GET: формирование отчета для указанного типа и кода сущности с использованием create_default
@api.route("/api/report/default/<entity_type>/<entity_code>", methods=["GET"])
def get_report_default(entity_type: str, entity_code: str):
    entity, err_msg, status_code = storage.get_entity(entity_type, entity_code)
    if err_msg:
        return err_msg, status_code

    factory = report_factory()
    report = factory.create_default()
    result = report.build(entity)
    return report.create_response(result, filename=f"{entity_type}_{entity.name}")


# 1. Получить список всех форматов для построения отчетов (GET \ Json)
@api.route("/api/reports/formats", methods=["GET"])
def get_report_formats():
    formats = [item.name for item in report_type_enum]
    return flask.jsonify(formats), 200


# 2. Получить список всех зарегистрированных типов доменных сущностей (GET \ Json)
@api.route("/api/entities", methods=["GET"])
def get_entities():
    if not storage.is_loaded:
        storage.start()
    return flask.jsonify(list(storage.data.keys())), 200


# 3. CRUD: Получить список сущностей указанного типа (GET \ Json)
@api.route("/api/entities/<entity_type>", methods=["GET"])
def get_entities_by_type(entity_type: str):
    if not storage.is_loaded:
        storage.start()
    if not storage.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    aliases = {
        "ranges": "ranges", "range": "ranges", "единица измерения": "ranges", "единица_измерения": "ranges",
        "groups": "groups", "group": "groups", "группа": "groups",
        "nomenclatures": "nomenclatures", "nomenclature": "nomenclatures", "номенклатура": "nomenclatures",
        "storages": "storages", "storage": "storages", "склад": "storages",
        "organizations": "organizations", "organization": "organizations", "организация": "organizations",
        "recipes": "recipes", "recipe": "recipes", "рецепт": "recipes"
    }
    key = aliases[entity_type.lower().strip()]
    items = storage.data.get(key, [])
    converted = [convert_factory().convert(item) for item in items]
    return flask.jsonify(converted), 200


# 4. CRUD: Получить конкретную сущность по коду / id (GET \ Json)
@api.route("/api/entities/<entity_type>/<entity_id>", methods=["GET"])
def get_entity_by_id(entity_type: str, entity_id: str):
    entity, err_msg, status_code = storage.get_entity(entity_type, entity_id)
    if err_msg or entity is None:
        return flask.jsonify({"error": err_msg or "Сущность не найдена"}), status_code
    return flask.jsonify(convert_factory().convert(entity)), 200


# 5. CRUD: Добавить доменную сущность (POST \ Json)
@api.route("/api/entities/<entity_type>", methods=["POST"])
def create_entity(entity_type: str):
    if not storage.is_loaded:
        storage.start()
    if not storage.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    data = flask.request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return flask.jsonify({"error": "Тело запроса должно быть JSON объектом"}), 400

    aliases = {
        "ranges": "ranges", "range": "ranges", "единица измерения": "ranges", "единица_измерения": "ranges",
        "groups": "groups", "group": "groups", "группа": "groups",
        "nomenclatures": "nomenclatures", "nomenclature": "nomenclatures", "номенклатура": "nomenclatures",
        "storages": "storages", "storage": "storages", "склад": "storages",
        "organizations": "organizations", "organization": "organizations", "организация": "organizations",
        "recipes": "recipes", "recipe": "recipes", "рецепт": "recipes"
    }
    key = aliases[entity_type.lower().strip()]

    # Разрешение типа модели для десериализации
    model_type_mapping = {
        "ranges": "range_model",
        "groups": "nomenclature_group_model",
        "nomenclatures": "nomenclature_model",
        "storages": "storage_model",
        "organizations": "organization_model",
        "recipes": "recipe_model",
    }
    target_type_name = model_type_mapping[key]

    try:
        factory = deserialize_factory()
        entity = factory.deserialize(data, target_type=target_type_name)
        storage.add_entity(key, entity)
        return flask.jsonify(convert_factory().convert(entity)), 201
    except Exception as exc:
        return flask.jsonify({"error": str(exc)}), 400


# 6. CRUD: Обновить доменную сущность (PUT \ Json)
@api.route("/api/entities/<entity_type>/<entity_id>", methods=["PUT"])
def update_entity(entity_type: str, entity_id: str):
    if not storage.is_loaded:
        storage.start()
    if not storage.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    data = flask.request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return flask.jsonify({"error": "Тело запроса должно быть JSON объектом"}), 400

    aliases = {
        "ranges": "ranges", "range": "ranges", "единица измерения": "ranges", "единица_измерения": "ranges",
        "groups": "groups", "group": "groups", "группа": "groups",
        "nomenclatures": "nomenclatures", "nomenclature": "nomenclatures", "номенклатура": "nomenclatures",
        "storages": "storages", "storage": "storages", "склад": "storages",
        "organizations": "organizations", "organization": "organizations", "организация": "organizations",
        "recipes": "recipes", "recipe": "recipes", "рецепт": "recipes"
    }
    key = aliases[entity_type.lower().strip()]

    existing_entity, err_msg, status_code = storage.get_entity(key, entity_id)
    if err_msg or existing_entity is None:
        return flask.jsonify({"error": err_msg or "Сущность не найдена"}), status_code

    req_data = dict(data)
    if "id" not in req_data and "unique_code" not in req_data:
        req_data["id"] = existing_entity.id

    model_type_mapping = {
        "ranges": "range_model",
        "groups": "nomenclature_group_model",
        "nomenclatures": "nomenclature_model",
        "storages": "storage_model",
        "organizations": "organization_model",
        "recipes": "recipe_model",
    }
    target_type_name = model_type_mapping[key]

    try:
        factory = deserialize_factory()
        new_entity = factory.deserialize(req_data, target_type=target_type_name)
        storage.update_entity(key, entity_id, new_entity)
        return flask.jsonify(convert_factory().convert(new_entity)), 200
    except Exception as exc:
        err_text = str(exc)
        if "не найдена" in err_text.lower():
            return flask.jsonify({"error": err_text}), 404
        return flask.jsonify({"error": err_text}), 400


# 7. CRUD: Удалить доменную сущность (DELETE \ Json)
@api.route("/api/entities/<entity_type>/<entity_id>", methods=["DELETE"])
def delete_entity(entity_type: str, entity_id: str):
    if not storage.is_loaded:
        storage.start()
    if not storage.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    try:
        storage.delete_entity(entity_type, entity_id)
        return flask.jsonify({"result": True}), 200
    except Exception as exc:
        err_text = str(exc)
        if "не найдена" in err_text.lower():
            return flask.jsonify({"error": err_text}), 404
        return flask.jsonify({"error": err_text}), 400


# Подключение спецификации OpenAPI / Swagger UI
api.add_api("openapi.yaml")

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)

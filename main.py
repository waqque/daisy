import io
import connexion
import flask
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_dto import report_type_enum
from Src.Logics.convert_factory import convert_factory
from Src.Logics.report_factory import report_factory
from Src.Logics.storage_manager import storage_manager
from Src.Logics.storage_service import storage_service

api = connexion.FlaskApp(__name__, specification_dir="./")

# Инициализация хранилища данных и настроек
storage = storage_manager()
service = storage_service(storage)


def create_response(report, result: report_result_dto, filename: str = "report"):
    # Формирование HTTP-ответа по отчету
    if isinstance(report, report_type_enum):
        report = report_factory().create(report)

    if getattr(report, "as_attachment", False):
        data_bytes = result.data if result.data else result.text.encode("utf-8")
        ext = getattr(report, "file_extension", "txt")
        return flask.send_file(
            io.BytesIO(data_bytes),
            mimetype=report.mimetype,
            as_attachment=True,
            download_name=f"{filename}.{ext}",
        )
    return flask.Response(result.text, mimetype=report.mimetype)


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
    recipe_name = flask.request.args.get("recipe") if flask.has_request_context() else None
    recipe = service.get_default_recipe(recipe_name)
    if recipe is None:
        return "Рецепты не найдены в хранилище.", 404

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
    return create_response(report, result, filename=recipe.name)


# 5. Метод GET: формирование отчета в указанном формате для указанного типа и кода сущности
@api.route("/api/report/<entity_type>/<entity_code>", methods=["GET"])
def get_report_by_format(entity_type: str, entity_code: str):
    format_name = flask.request.args.get("format", "TXT")
    try:
        report_type = report_type_enum[format_name.upper()]
    except KeyError:
        return f"Неподдерживаемый формат отчета: {format_name}", 400

    entity, err_msg, status_code = service.get_entity(entity_type, entity_code)
    if err_msg:
        return err_msg, status_code

    report = report_factory().create(report_type)
    result = report.build(entity)
    return create_response(report, result, filename=f"{entity_type}_{entity.name}")


# 8. Метод GET: формирование отчета для указанного типа и кода сущности с использованием create_default
@api.route("/api/report/default/<entity_type>/<entity_code>", methods=["GET"])
def get_report_default(entity_type: str, entity_code: str):
    entity, err_msg, status_code = service.get_entity(entity_type, entity_code)
    if err_msg:
        return err_msg, status_code

    factory = report_factory()
    report = factory.create_default()
    result = report.build(entity)
    return create_response(report, result, filename=f"{entity_type}_{entity.name}")


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
    if not service.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    items = service.get_list(entity_type)
    converter = convert_factory()
    converted = [converter.convert(item) for item in items]
    return flask.jsonify(converted), 200


# 4. CRUD: Получить конкретную сущность по коду / id (GET \ Json)
@api.route("/api/entities/<entity_type>/<entity_id>", methods=["GET"])
def get_entity_by_id(entity_type: str, entity_id: str):
    entity, err_msg, status_code = service.get_entity(entity_type, entity_id)
    if err_msg or entity is None:
        return flask.jsonify({"error": err_msg or "Сущность не найдена"}), status_code
    return flask.jsonify(convert_factory().convert(entity)), 200


# 5. CRUD: Добавить доменную сущность (POST \ Json)
@api.route("/api/entities/<entity_type>", methods=["POST"])
def create_entity(entity_type: str):
    if not service.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    data = flask.request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return flask.jsonify({"error": "Тело запроса должно быть JSON объектом"}), 400

    try:
        entity = service.create_entity(entity_type, data)
        return flask.jsonify(convert_factory().convert(entity)), 201
    except Exception as exc:
        return flask.jsonify({"error": str(exc)}), 400


# 6. CRUD: Обновить доменную сущность (PUT \ Json)
@api.route("/api/entities/<entity_type>/<entity_id>", methods=["PUT"])
def update_entity(entity_type: str, entity_id: str):
    if not service.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    data = flask.request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return flask.jsonify({"error": "Тело запроса должно быть JSON объектом"}), 400

    try:
        new_entity = service.update_entity(entity_type, entity_id, data)
        return flask.jsonify(convert_factory().convert(new_entity)), 200
    except Exception as exc:
        err_text = str(exc)
        if "не найдена" in err_text.lower():
            return flask.jsonify({"error": err_text}), 404
        return flask.jsonify({"error": err_text}), 400


# 7. CRUD: Удалить доменную сущность (DELETE \ Json)
@api.route("/api/entities/<entity_type>/<entity_id>", methods=["DELETE"])
def delete_entity(entity_type: str, entity_id: str):
    if not service.is_valid_type(entity_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {entity_type}"}), 400

    try:
        service.delete_entity(entity_type, entity_id)
        return flask.jsonify({"result": True}), 200
    except Exception as exc:
        err_text = str(exc)
        if "не найдена" in err_text.lower():
            return flask.jsonify({"error": err_text}), 404
        return flask.jsonify({"error": err_text}), 400


# Фильтрация доменных сущностей через прототип
@api.route("/api/filter/<domain_type>", methods=["POST"])
def filter_entities(domain_type: str, body: dict = None, **kwargs):
    if not service.is_valid_type(domain_type):
        return flask.jsonify({"error": f"Неподдерживаемый тип сущности: {domain_type}"}), 400

    data = body if body is not None else flask.request.get_json(silent=True)

    try:
        dto = filter_dto.from_dict(data)
        items = service.filter_entities(domain_type, dto)
        converter = convert_factory()
        converted = [converter.convert(item) for item in items]
        return flask.jsonify(converted), 200
    except Exception as exc:
        return flask.jsonify({"error": str(exc)}), 400


# Оборотно-сальдовая ведомость с фильтрацией через прототип
@api.route("/api/reports/osv", methods=["POST"])
def get_osv_report(body: dict = None, **kwargs):
    data = body if body is not None else flask.request.get_json(silent=True)

    try:
        dto = filter_dto.from_dict(data)
        rows = service.get_osv(dto)
        converter = convert_factory()
        converted = [converter.convert(row) for row in rows]
        return flask.jsonify(converted), 200
    except Exception as exc:
        return flask.jsonify({"error": str(exc)}), 400


# Подключение спецификации OpenAPI / Swagger UI
api.add_api("openapi.yaml")

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)

import io
import connexion
import flask
from Src.Dtos.report_type_dto import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

api = connexion.FlaskApp(__name__, specification_dir="./")

# Инициализация хранилища данных и настроек
storage = storage_manager()
storage.start()


def get_entity(entity_type: str, entity_code: str):
    # Поиск сущности по типу и коду
    if not storage.is_loaded:
        storage.start()

    t = entity_type.lower().strip()
    c = str(entity_code).strip()

    if t in ("номенклатура", "nomenclature", "nomenclatures"):
        items = storage.nomenclatures
    elif t in ("единица измерения", "единица_измерения", "range", "ranges"):
        items = storage.ranges
    elif t in ("рецепт", "recipe", "recipes"):
        items = storage.recipes
    else:
        return None, f"Неподдерживаемый тип сущности: {entity_type}", 400

    for item in items:
        if item.unique_code == c or item.name.lower() == c.lower():
            return item, None, 200

    return None, f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена.", 404


def create_response(result, report_type: report_type_enum, filename: str = "report"):
    # Формирование ответа RestApi в зависимости от формата
    if report_type == report_type_enum.CSV:
        return flask.send_file(
            io.BytesIO(result.data),
            mimetype="text/csv; charset=utf-8",
            as_attachment=True,
            download_name=f"{filename}.csv",
        )
    if report_type == report_type_enum.MARKDOWN:
        return flask.send_file(
            io.BytesIO(result.data),
            mimetype="text/markdown; charset=utf-8",
            as_attachment=True,
            download_name=f"{filename}.md",
        )
    if report_type == report_type_enum.XML:
        return flask.Response(result.text, mimetype="application/xml; charset=utf-8")
    if report_type == report_type_enum.HTML:
        return flask.Response(result.text, mimetype="text/html; charset=utf-8")

    return flask.Response(result.text, mimetype="text/plain; charset=utf-8")


@api.route("/", methods=["GET"])
def index():
    # Перенаправление на получение отчета по умолчанию
    return flask.redirect("/api/get_report")


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

    result = report_factory.create_report(report_type, recipe)
    return create_response(result, report_type, filename=recipe.name)


# 5. Метод GET: формирование отчета в указанном формате для указанного типа и кода сущности
@api.route("/api/report/<entity_type>/<entity_code>", methods=["GET"])
def get_report_by_format(entity_type: str, entity_code: str):
    format_name = flask.request.args.get("format", "TXT")
    try:
        report_type = report_type_enum[format_name.upper()]
    except KeyError:
        return f"Неподдерживаемый формат отчета: {format_name}", 400

    entity, err_msg, status_code = get_entity(entity_type, entity_code)
    if err_msg:
        return err_msg, status_code

    result = report_factory.create_report(report_type, entity)
    return create_response(result, report_type, filename=f"{entity_type}_{entity.name}")


# 8. Метод GET: формирование отчета для указанного типа и кода сущности с использованием create_default
@api.route("/api/report/default/<entity_type>/<entity_code>", methods=["GET"])
def get_report_default(entity_type: str, entity_code: str):
    entity, err_msg, status_code = get_entity(entity_type, entity_code)
    if err_msg:
        return err_msg, status_code

    factory = report_factory()
    result = factory.create_default(entity)

    report_type = factory.settings.response_format if factory.settings else report_type_enum.TXT
    return create_response(result, report_type, filename=f"{entity_type}_{entity.name}")


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)
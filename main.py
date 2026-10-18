import connexion
import flask
from Src.Dtos.report_type_dto import report_type_enum
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


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)
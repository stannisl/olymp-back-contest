from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy import text

import config
from config import (POSTGRES_DATABASE, POSTGRES_HOST, POSTGRES_PASSWORD,
                    POSTGRES_PORT, POSTGRES_USERNAME)
from db import db

# from models.countries import CountriesModel
# from database import start_session, start_engine

# from resources.countries import blp as ContriesBlueprint


def create_app() -> Flask:
    db.metadata.clear()
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    )
    db.init_app(app)
    migrate = Migrate(app, db)

    from flask_jwt_extended import JWTManager
    from flask_smorest import Api

    from resources.user import blp as UserBlueprint

    api = Api(app=app)
    jwt = JWTManager(app=app)

    api.register_blueprint(UserBlueprint)

    # 6 часов попыток засунуть в схему не увенчались успехом :(, зато старался миш.
    @app.route("/api/countries", methods=["GET"])
    def list_countries():
        if not request.args.get("region") == None:
            with db.engine.connect() as connection:
                result = connection.execute(
                    text(
                        f"SELECT name, alpha2, alpha3, region FROM countries WHERE region = '{request.args.get('region').capitalize()}'"
                    )
                ).all()
                print(result)
                return (
                    jsonify(
                        [
                            {
                                "name": result[i][0],
                                "alpha2": result[i][1],
                                "alpha3": result[i][2],
                                "region": result[i][3],
                            }
                            for i in range(len(result))
                        ]
                    ),
                    200,
                )
        else:
            with db.engine.connect() as connection:
                result = connection.execute(text(f"SELECT name, alpha2, alpha3, region FROM countries")).all()
                print(result)
                return (
                    jsonify(
                        [
                            {
                                "name": result[i][0],
                                "alpha2": result[i][1],
                                "alpha3": result[i][2],
                                "region": result[i][3],
                            }
                            for i in range(len(result))
                        ]
                    ),
                    200,
                )

    @app.route("/api/countries/<alpha2>", methods=["GET"])
    def get_country_by_alpha2(alpha2):
        with db.engine.connect() as connection:
            print(alpha2)
            result = connection.execute(
                text(f"SELECT name, alpha2, alpha3, region FROM countries WHERE alpha2 = '{alpha2.upper()}'")
            ).all()
            print(result)
            return (
                jsonify(
                    {
                        "name": result[0][0],
                        "alpha2": result[0][1],
                        "alpha3": result[0][2],
                        "region": result[0][3],
                    }
                ),
                200,
            )

    @app.route("/api/ping", methods=["GET"])
    def send():
        print()
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=config.SERVER_ADDRESS, port=config.SERVER_PORT, debug=True)

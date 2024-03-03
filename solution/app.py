from datetime import timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from sqlalchemy import text

from blocklist import BLOCKLIST
from config import (
    JWT_SECRET_KEY,
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USERNAME,
    SERVER_ADDRESS,
    SERVER_PORT,
)
from db import db
from resources.profile import blp as ProfileBlueprint
from resources.user import blp as UserBlueprint


def create_app() -> Flask:
    db.metadata.clear()
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCES_TOKEN_EXPIRES"] = timedelta(hours=12)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    )
    db.init_app(app)
    migrate = Migrate(app, db)

    # with app.app_context():
    #     with db.engine.connect() as connection:
    #                 res = connection.execute(
    #                     text(f"SELECT DISTINCT alpha2 FROM countries")).all()
    #                 print("RU" in [i[0] for i in res])

    api = Api(app=app)
    jwt = JWTManager(app=app)

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ProfileBlueprint)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"reason": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"reason": "Signature verification failed.", "error": "invalid_token"}),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "reason": "Request does not contain an access token.",
                }
            ),
            401,
        )

    # 6 часов попыток засунуть в схему не увенчались успехом :(.
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
    app.run(host=SERVER_ADDRESS, port=SERVER_PORT, debug=True)

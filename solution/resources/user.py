import psycopg2
import sqlalchemy
from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint
from passlib.hash import pbkdf2_sha256
from sqlalchemy import text

from db import db
from models import UserModel
from schemas import LoginSchema, RegisterSchema

blp = Blueprint("Users", "users", url_prefix="/api/auth", description="Действия с пользователями")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(RegisterSchema)
    def post(self, request):
        """Register a user"""
        try:
            if (
                (UserModel.query.filter(UserModel.phone == request["phone"])).all()
                or (UserModel.query.filter(UserModel.email == request["email"])).all()
                or (UserModel.query.filter(UserModel.login == request["login"])).all()
            ):
                return jsonify({"reason": "Registration data is not unique."}), 409
        except sqlalchemy.exc.ProgrammingError:
            return jsonify({"reason": "Migrations are not applied."}), 500
        except sqlalchemy.exc.IntegrityError:
            return jsonify({"reason": "Registration data is not unique."}), 409

        with db.engine.connect() as connection:
            res = connection.execute(text(f"SELECT DISTINCT alpha2 FROM countries")).all()
            if request["countryCode"].upper() not in [i[0] for i in res]:
                return jsonify({"reason": "Invalid country code"}), 400

        if (len(request["login"]) < 1) or (len(request["phone"]) < 1) or (len(request["email"]) < 1):
            return jsonify({"reason": "Invalid form data"}), 400

        user = UserModel(
            login=request["login"],
            email=request["email"],
            password=pbkdf2_sha256.hash(request["password"]),
            country_code=request["countryCode"],
            is_public=request["isPublic"],
            phone=request["phone"] if "phone" in request.keys() else "",
            image=request["image"] if "image" in request.keys() else "",
        )

        response = {
            "profile": {
                "login": user.login,
                "email": user.email,
                "countryCode": user.country_code,
                "isPublic": user.is_public,
            }
        }

        if user.phone != "":
            response["profile"]["phone"] = user.phone
        if user.image != "":
            response["profile"]["image"] = user.image

        db.session.add(user)
        db.session.commit()

        return jsonify(response), 201


@blp.route("/sign-in")
class UserLogin(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, request):
        try:

            user = UserModel.query.filter(UserModel.login == request["login"]).first()
        except Exception as e:
            return jsonify({"message": "Invalid creds"}), 401
        if user and pbkdf2_sha256.verify(request["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return jsonify({"token": access_token}), 200

        return jsonify({"message": "Invalid creds"}), 401

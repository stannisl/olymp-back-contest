from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from passlib.hash import pbkdf2_sha256
from sqlalchemy import text

from blocklist import BLOCKLIST
from db import db
from models import UserModel
from schemas import ChangePasswordSchema, ProfileUpdateSchema

blp = Blueprint("Profiles", "profile", url_prefix="/api/", description="Действия с пользователями")


@blp.route("/profile/<string:login>")
class UserProfile(MethodView):
    @jwt_required(optional=True)
    def get(self, login):

        try:
            user = UserModel.query.filter(UserModel.login == login).first()

        except Exception as e:
            return jsonify({"reason": "Пользователь не найден"}), 403

        response = {
            "login": user.login,
            "email": user.email,
            "countryCode": user.country_code,
            "isPublic": user.is_public,
        }

        if user.phone != "":
            response["phone"] = str(user.phone.e164)
        if user.image != "":
            response["image"] = user.image

        jwt_id = get_jwt_identity()

        if not user.is_public == True:
            if not user.id == jwt_id:
                return jsonify({"reason": "Запрашиваемый пользователь не существует или у вас нет доступа к нему."}), 403
            else:
                return response
        else:
            return response


@blp.route("/me/profile")
class UpdateProfile(MethodView):
    @jwt_required(optional=False)
    def get(self):
        jwt_id = get_jwt_identity()

        try:
            user = UserModel.query.filter(UserModel.id == jwt_id).first()
        except Exception as e:
            return jsonify({"reason": "Переданный токен не существует либо некорректен."}), 401

        response = {
            "login": user.login,
            "email": user.email,
            "countryCode": user.country_code,
            "isPublic": user.is_public,
        }

        if user.phone != "":
            response["phone"] = str(user.phone.e164)
        if user.image != "":
            response["image"] = user.image

        return response

    @blp.arguments(ProfileUpdateSchema)
    @jwt_required(optional=False)
    def patch(self, request):
        jwt_id = get_jwt_identity()

        with db.engine.connect() as connection:
            res = connection.execute(text(f"SELECT DISTINCT alpha2 FROM countries")).all()
            if request["countryCode"].upper() not in [i[0] for i in res]:
                return jsonify({"reason": "Invalid country code."}), 400

        user = UserModel.query.filter(UserModel.id == jwt_id).first()

        new_user = UserModel(
            login=request["login"] if "login" in request.keys() else user.login,
            email=request["email"] if "email" in request.keys() else user.email,
            country_code=request["country_code"] if "countryCode" in request.keys() else user.country_code,
            is_public=request["isPublic"] if "isPublic" in request.keys() else user.is_public,
            phone=request["phone"] if "phone" in request.keys() else user.phone,
            image=request["image"] if "image" in request.keys() else user.image,
        )

        if UserModel.query.filter(
            UserModel.phone == request["phone"] or UserModel.email == request["email"] or UserModel.login == request["login"]
        ).all():
            return jsonify({"reason": "New data is not unique."}), 409

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"reason": "db did not accepted it"}), 400

        response = {
            "login": new_user.login,
            "email": new_user.email,
            "countryCode": new_user.country_code,
            "isPublic": new_user.is_public,
        }

        if user.phone != "":
            response["phone"] = str(new_user.phone.e164)
        if user.image != "":
            response["image"] = new_user.image

        return response, 200


@blp.route("/me/updatePassword")
class ChangePassword(MethodView):
    @blp.arguments(ChangePasswordSchema)
    @jwt_required()
    def post(self, request):
        jwt_id = get_jwt_identity()
        jti = get_jwt()["jti"]

        user = UserModel.query.filter(UserModel.id == jwt_id).first()

        if user and pbkdf2_sha256.verify(request["oldPassword"], user.password):
            BLOCKLIST.add(jti)
            user.password = pbkdf2_sha256.hash(request["newPassword"])
            try:
                db.session.add(user)
                db.session.commit()
                return jsonify({"status": "ok"}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"reason": "db did not accepted it"}), 400
        else:
            return jsonify({"message": "Пароли не сходятся"}), 403

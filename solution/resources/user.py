from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask import jsonify
from db import db
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users", "users", description="Действия с пользователями")

@blp.route("/api/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, request):
        print("[*] Got a request")
        if UserModel.query.filter(UserModel.login == request["login"], UserModel.phone == request["phone"], UserModel.email == request["email"]).first():
            abort(409, message="Registration data is not unique.")
        print("[*] request info: ", request)
        user = UserModel(
            login=request["login"],
            email=request["email"],
            password=pbkdf2_sha256.hash(request["password"]),
            country_code=request["countryCode"],
            is_public=request["isPublic"],
            phone=request["phone"] if "phone" in request.keys() else "",
            image=request["image"] if "image" in request.keys() else ""
        )

        response = { "profile": {
            "login": user.login,
            "email": user.email,
            "countryCode": user.country_code,
            "isPublic": user.is_public,
        }}

        if user.phone != "":
            response["profile"]["phone"] = user.phone
        if user.image != "":
            response["profile"]["image"] = user.image
        db.session.add(user)
        db.session.commit()
        
        return jsonify(response), 201
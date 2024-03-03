from marshmallow import Schema, fields


class RegisterSchema(Schema):
    login = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    countryCode = fields.Str(required=True)
    isPublic = fields.Bool(required=True)
    phone = fields.Str(required=False)
    image = fields.Str(required=False)


class LoginSchema(Schema):
    login = fields.Str(required=True)
    password = fields.Str(required=True)


class ProfileUpdateSchema(Schema):
    login = fields.Str(required=False)
    email = fields.Str(required=False)
    countryCode = fields.Str(required=False)
    isPublic = fields.Bool(required=False)
    phone = fields.Str(required=False)
    image = fields.Str(required=False)

from marshmallow import Schema, fields


class UserSchema(Schema):
    login = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    countryCode = fields.Str(required=True)
    isPublic = fields.Bool(required=True)
    phone = fields.Str(required=False)

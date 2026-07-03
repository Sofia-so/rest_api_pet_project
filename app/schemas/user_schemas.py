from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError
)

class MessageSchema(Schema):
    message = fields.Str(required=True)


class UserBaseSchema(Schema):
    first_name = fields.Str(
        required = True,
        validate=validate.Length(max=50)
    )
    last_name = fields.Str(
        required = True,
        validate=validate.Length(max=50)
    )
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
    confirm_password = fields.Str(
        required=True,
        load_only=True
    )

    @validates_schema
    def validate_password_match(self, data, **kwargs):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Паролі не співпадають")


class UserUpdateSchema(Schema):
    first_name = fields.Str(
        required=False,
        validate=validate.Length(max=50)
    )
    last_name = fields.Str(
        required=False,
        validate=validate.Length(max=50)
    )
    username = fields.Str(
        required=False,
        validate=validate.Length(min=3, max=50)
    )
    email = fields.Email(required=False)


class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)


class UserLoginSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50)
    )
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
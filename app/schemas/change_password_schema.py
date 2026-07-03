from marshmallow import (
    Schema,
    fields,
    validates_schema,
    validate,
    ValidationError
)


class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
    confirm_password = fields.Str(required=True, load_only=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data["new_password"] != data["confirm_password"]:
            raise ValidationError(
                {"confirm_password": "Паролі не співпадають."}
            )
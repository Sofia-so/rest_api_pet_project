from marshmallow import Schema, fields


class TokenSchema(Schema):
    access_token = fields.Str(
        required=True,
        metadata={"description": "JWT access token"}
    )
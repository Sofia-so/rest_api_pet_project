from marshmallow import (
    fields,
    Schema,
    validate
)


class CategoryBaseSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(max=60)
    )
    description = fields.Str()


class CategoryResponseSchema(Schema):
    id = fields.Int(dump_only=True)

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
    description = fields.Str(required=False)


class CategoryResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()


class CategoryUpdateSchema(Schema):
    name = fields.Str(
        validate=validate.Length(max=60)
    )
    description = fields.Str()

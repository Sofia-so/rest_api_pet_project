from marshmallow import (
    Schema,
    fields,
    validate
)

from app.schemas.category_schema import CategoryResponseSchema
from app.db.model_enum import ProductStatus


class ProductBaseSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(max=60)
    )
    description = fields.Str(required=False)
    status = fields.Enum(
        ProductStatus,
        by_value=True,
        required=True
    )
    price = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0)
    )
    quantity = fields.Int(required=True)
    category_id = fields.Int(required=True)


class ProductResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    status = fields.Str()
    price = fields.Decimal()
    category = fields.Nested(CategoryResponseSchema, only=("name",))


class ProductUpdateSchema(Schema):
    name = fields.Str(
        validate=validate.Length(max=60)
    )
    description = fields.Str()
    status = fields.Str()
    price = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    quantity = fields.Int()
    category_id = fields.Int()

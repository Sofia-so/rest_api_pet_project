from marshmallow import (
    Schema,
    fields,
    validate
)

from app.db.model_enum import DeliveryMethod, OrderStatus


class OrderItemSchema(Schema):
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )
    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )


class OrderCreateSchema(Schema):
    customer_first_name = fields.Str(required=True)
    customer_last_name = fields.Str(required=True)
    customer_phone = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^\+380\d{9}$",
            error="Номер має бути у форматі +380XXXXXXXXX"
        )
    )
    delivery_method = fields.Enum(
        DeliveryMethod,
        by_value=True,
        required=True
)
    items = fields.List(
        fields.Nested(OrderItemSchema),
        required=True,
        validate=validate.Length(min=1)
    )


class OrderItemResponsesSchema(Schema):
    product_id = fields.Int()
    product_name = fields.Str(attribute="product.name")
    quantity = fields.Int()
    price = fields.Decimal(
        places=2,
        dump_only=True
    )


class OrderResponsesSchema(Schema):
    id = fields.Int(dump_only=True)
    number = fields.Str(dump_only=True)
    status = fields.Enum(
        OrderStatus,
        by_value=True,
        dump_only=True
    )
    total_price = fields.Decimal(
        places=2,
        dump_only=True
    )
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)

    customer_first_name = fields.Str()
    customer_last_name = fields.Str()
    customer_phone = fields.Str()

    delivery_method = fields.Enum(
        DeliveryMethod,
        by_value=True
    )

    items = fields.List(
        fields.Nested(OrderItemResponsesSchema)
    )


class OrderStatusUpdateSchema(Schema):
    status = fields.Enum(
        OrderStatus,
        by_value=True,
        required=True
    )
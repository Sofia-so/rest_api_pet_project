from marshmallow import Schema, fields

class SearchSchema(Schema):
    query = fields.String(required=True)

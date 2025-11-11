from marshmallow import Schema, fields, validate, pre_load, validates_schema, ValidationError

class User_Schema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=256))

class Category_Schema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=256))
    user_id = fields.Int(load_only=True, allow_none=True)

class Record_Schema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    datetime = fields.AwareDateTime(required=True)
    amount = fields.Float(required=True)

    @pre_load
    def fix_z_suffix(self, data, **kwargs):
        dt = data.get("datetime")
        if isinstance(dt, str) and dt.strip().endswith(("Z", "z")):
            data["datetime"] = dt.strip()[:-1] + "+00:00"
        return data

class CategoryDeleteSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(allow_none=True, load_default=None)

class CategoryQuerySchema(Schema):
    user_id = fields.Int(allow_none=True, load_default=None)

class RecordQuerySchema(Schema):
    user_id = fields.Int(allow_none=True, load_default=None)
    category_id = fields.Int(allow_none=True, load_default=None)

    @validates_schema
    def at_least_one(self, data, **kwargs):
        if data.get("user_id") is None and data.get("category_id") is None:
            raise ValidationError("provide user_id and/or category_id")

class UserIdPathSchema(Schema):
    user_id = fields.Int(required=True)

class RecordIdPathSchema(Schema):
    record_id = fields.Int(required=True)
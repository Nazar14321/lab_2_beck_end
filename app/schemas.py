from marshmallow import Schema, fields, validate, pre_load

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

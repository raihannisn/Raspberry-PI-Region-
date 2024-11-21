from marshmallow import Schema, fields, pre_load
from marshmallow.validate import Range
from datetime import datetime

class SettingUpdateSchema(Schema):
    current_region = fields.Integer(validate=Range(min=1,max=5))
    delay = fields.Integer(validate=Range(min=0))
    step = fields.Integer(validate=Range(min=0))
    status = fields.Integer(validate=Range(min=0))
    axis = fields.Integer(validate=Range(min=0))
    auto_start_status = fields.Boolean()
    auto_start_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    cpe1_time = fields.Integer(validate=Range(min=1))
    cpe2_time = fields.Integer(validate=Range(min=1))
    cpe3_time = fields.Integer(validate=Range(min=1))
    cpe4_time = fields.Integer(validate=Range(min=1))
    multi_region = fields.Boolean()

    @pre_load
    def set_auto_start_time(self, data, many, **kwargs):
        auto_start_status = data.get('auto_start_status')
        if auto_start_status is True:
            data['auto_start_time'] = datetime.utcnow()
        elif auto_start_status is False:
            data['auto_start_time'] = None

        return data
import os
from app import db
from datetime import datetime
from dotenv import load_dotenv
from flask import jsonify
load_dotenv()

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    microscope_id = db.Column(db.Integer, default=os.getenv('MICROSCOPE_ID'))
    batch_id = db.Column(db.Integer, default=os.getenv('BATCH_ID'))
    current_region = db.Column(db.Integer)
    delay = db.Column(db.Integer)
    step = db.Column(db.Integer)
    status = db.Column(db.Integer)
    axis = db.Column(db.Integer)
    auto_start_status = db.Column(db.Boolean)
    auto_start_time = db.Column(db.DateTime)
    cpe1_time = db.Column(db.Integer)
    cpe2_time = db.Column(db.Integer)
    cpe3_time = db.Column(db.Integer)
    cpe4_time = db.Column(db.Integer)
    multi_region = db.Column(db.Boolean)
    is_uptodate = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def as_dict(self):
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        data['created_at'] = self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        return data
    
    def item_setting(self):
        return {
            "current_region": self.current_region,
            "step": self.step,
            "delay": self.delay,
            "axis": self.axis,
            "auto_start_status": self.auto_start_status,
            "auto_start_time": self.auto_start_time.strftime("%Y-%m-%d %H:%M:%S") if self.auto_start_time else None,
            "cpe1_time": self.cpe1_time,
            "cpe2_time": self.cpe2_time,
            "cpe3_time": self.cpe3_time,
            "cpe4_time": self.cpe4_time,
            "multi_region": self.multi_region
        }
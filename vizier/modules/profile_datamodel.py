import peewee as pw
import yaml
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

with open("./vizier/config/config.yaml") as config_file:
    config = yaml.safe_load(config_file)

db_path = config["application"]["profile_db_path"]
db = pw.SqliteDatabase(db_path)

# dataclass for anaglyph glasses color calibration data
@dataclass
class Calibration():
    color_left: tuple = (0)
    color_right: tuple = (0)

# Database model and classes representing tables
class ActiveProfile():
    def __call__(self, *args, **kwargs):
        """This is a singleton."""
        if 'instance' not in self.__dict__:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

    def __init__(self):
        self.user = False
        self.calibration_data = CalibrationData()
        self.db_safe_init()

    def activate(self, username):
        """Fetch data from the database and store it in the session."""
        def _to_tuple(x):
            """Unfortunately sqlite saves our tuples as a string.
            We have to convert this string back to a tuple."""
            return tuple(map(float, x[1:-1].split(',')))

        with db:
            self.user = User.get(User.username == username)
            self.calibration_data = CalibrationData.get(CalibrationData.user == self.user.id)
            # if calibdata:
                # self.calibration.color_left = _to_tuple(calibdata.color_left)
                # self.calibration.color_right = _to_tuple(calibdata.color_right)

    def db_safe_init(self):
        """Explicitly open the database, create tables and close. Initalizes missing tables."""
        tables = [User(), CalibrationData(), Result()]
        db.connect()
        db.create_tables(tables)
        db.close()

    def __repr__(self):
        if self.user:
            return f'[{self.user.id}] {self.user.first_name} {self.user.last_name} ({self.user.username})'
        else:
            return f'No user activated.'

class BaseModel(pw.Model):
    class Meta:
        database = db
        legacy_table_names = False

class User(BaseModel):
    username = pw.CharField(unique=True)
    first_name = pw.CharField()
    last_name = pw.CharField()

class CalibrationData(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    user = pw.ForeignKeyField(User, backref="calibration", unique=True)
    color_left = pw.CharField()
    color_right = pw.CharField()

class Result(BaseModel):
    user = pw.ForeignKeyField(User, backref="results")
    session = pw.UUIDField()
    exercise = pw.CharField()
    difficulty = pw.CharField()
    created = pw.DateTimeField(default=datetime.now)
    count = pw.IntegerField()
    primary_param = pw.IntegerField(null=True)
    correctness = pw.BooleanField()
    time = pw.FloatField()
    time_diff = pw.FloatField()

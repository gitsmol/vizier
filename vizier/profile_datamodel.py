import peewee as pw
import yaml
from datetime import datetime
from pathlib import Path

with open("./vizier/config/config.yaml") as config_file:
    config = yaml.safe_load(config_file)

db_path = config["application"]["profile_db_path"]
db = pw.SqliteDatabase(db_path)

class ActiveProfile():
    def __call__(self, *args, **kwargs):
        """This is a singleton."""
        if 'instance' not in self.__dict__:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

    def __init__(self):
        self.username = None
        self.db_safe_init()

    def activate(self, username, display_name=""):
        self.display_name = display_name
        self.username = username

    def db_safe_init(self):
        """Explicitly open the database, create tables and close. Initalizes missing tables."""
        tables = [User(), CalibrationData(), Result()]
        db.connect()
        db.create_tables(tables)
        db.close()

    def __repr__(self):
        return f'{self.display_name} ({self.usernam })'

# Database model and classes representing tables
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
    user = pw.ForeignKeyField(User, backref="calibration")
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

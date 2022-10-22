import peewee as pw
import dearpygui.dearpygui as dpg
import yaml
from pathlib import Path
from . import helpers
from .profile_datamodel import ActiveProfile
from .profile_datamodel import User
from .profile_datamodel import CalibrationData
from .profile_datamodel import BaseModel
from .profile_datamodel import Result

with open("./vizier/config/config.yaml") as config_file:
    config = yaml.safe_load(config_file)

db_path = config["application"]["profile_db_path"]
db = pw.SqliteDatabase(db_path)

SESSION = ActiveProfile()

def add_user():
    def db_user_add(sender, a, u):
        try:
            User.create(
                username = dpg.get_value('username'),
                first_name = dpg.get_value('first_name'),
                last_name = dpg.get_value('last_name')
            )
        except Exception as e:
            helpers.error(exc=e)
        finally:
            dpg.delete_item(u)
            dpg.delete_item('win_switch_user', children_only=True)
            list_users('win_switch_user')

    winid = dpg.generate_uuid()
    with dpg.window(tag=winid, modal=True, pos=[200, 200], width=400, height=300, on_close=helpers.delete):
        helpers.center(winid)
        dpg.add_input_text(tag='username', label='Username')
        dpg.add_input_text(tag='first_name', label='First name')
        dpg.add_input_text(tag='last_name', label='Last name')
        dpg.add_button(label='Add', callback=db_user_add, user_data=winid)

def login_user():
    raise NotImplementedError()

def add_result_from_tuples(username, session, exercise, difficulty, results):
    with db:
        for result in results:
            Result.create(
                user=username,
                session=session,
                exercise=exercise,
                difficulty=difficulty,
                count=result.count,
                primary_param=result.primary_param,
                correctness=result.correctness,
                time = result.time,
                time_diff=result.time_diff,
            )

def get_results():
    raise NotImplementedError()

def list_users(parentid):
    with dpg.table(header_row=False, resizable=False, policy=4, scrollY=False, parent=parentid):
        dpg.add_table_column(init_width_or_weight=50, width_stretch=True)
        dpg.add_table_column(width=300, width_fixed=True)
        dpg.add_table_column(init_width_or_weight=50, width_stretch=True)
        for user in User.select():
            userdata = {
                "display_name": f'{user.first_name} {user.last_name} ({user.username})',
                "username": user.username
            }
            with dpg.table_row(filter_key=userdata['display_name']):
                dpg.add_table_cell()
                dpg.add_button(label=userdata['display_name'], callback=activate_user, user_data=userdata, width=250)
        with dpg.table_row():
                    dpg.add_table_cell()
                    dpg.add_button(label='Add user', callback=add_user, width=250)

def activate_user(sender, app_data, userdata):
    """Activate user for session singleton. Update dpg variables to display logged in user. Destroy switch_user window(s)."""
    SESSION.activate(username=userdata['username'], display_name=userdata['display_name'])
    dpg.set_value('txt_activeprofile', userdata['display_name'])
    dpg.set_item_label('btn_profile', 'Switch user')
    dpg.delete_item('win_switch_user')

def switch_user():
    with db:
        with dpg.window(tag='win_switch_user', pos=[200, 100], width=400, height=400, no_close=True, no_move=True, no_resize=True, no_collapse=True, label='Select user', on_close=helpers.delete):
            helpers.center('win_switch_user')
            list_users('win_switch_user')

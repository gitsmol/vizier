"""Module containing evaluation programs for various exercises."""
import dearpygui.dearpygui as dpg
import yaml
from vizier import helpers
from vizier import profile
from vizier.exercises import * # NOTE yes frowned upon but programmatic ways dont work?

def generic(sender, app_data, user_data=''):
    if sender == 'btn_close':
        try:
            dpg.delete_item(f'{user_data}_handler_registry')
        finally:
            dpg.delete_item(user_data, children_only=True)
            dpg.hide_item(user_data)

def evaluations():
    def launch(sender, app_data, user_data):
        # extract data from tuple 'user_data'
        evaluation_func = f'{user_data[0]}.run'  # the module to call. Expects 'run()'.
        config = user_data[1]                    # the configuration dict
        eval(evaluation_func)(config)

    with dpg.window(pos=[100, 100], width=500, height=500):
        with open('vizier/config/exercise_configs.yaml') as config_file:
            configs = yaml.safe_load(config_file)

        with dpg.table(header_row=False):
            dpg.add_table_column(width_stretch=True)
            dpg.add_table_column(width_stretch=True)
            dpg.add_table_column(width_stretch=True)
            dpg.add_table_column(width_stretch=True)
            for key_, value_ in configs['Exercises'].items(): # get different exercices
                with dpg.table_row():
                    dpg.add_text(key_)  # exercise name
                    dpg.add_text(value_.get('Plugin')) # exercise type
                with dpg.table_row():
                    for config, params in configs['Exercises'][key_]['Configurations'].items():    # get configs per exercise
                        dpg.add_button(label=config, callback=launch, user_data=(value_.get('Plugin'), params))

if __name__ == '__main__':
    print('Only to be used as part of the Vizier application.')

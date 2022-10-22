import dearpygui.dearpygui as dpg
from vizier import helpers
from vizier import launcher
import yaml

def save_and_close(s, a, u):
    """Load configfile, get config data from UI, write to configfile."""
    with open('./vizier/config/config.yaml') as configfile:
        config = yaml.safe_load(configfile)

    for key in config['application'].keys():
        config['application'][key] = dpg.get_value(key)

    with open('./vizier/config/config.yaml', 'w') as configfile:
        helpers.debugger('Writing config to file.')
        yaml.safe_dump(config, configfile)

    #destroy config window
    dpg.delete_item(u)


def list_config_items():
    """Lists configuration options as dpg items."""
    with open('./vizier/config/config.yaml') as configfile:
        config = yaml.safe_load(configfile)

    for key, value in config['application'].items():
        if value == True or value == False:
            with dpg.table_row():
                dpg.add_checkbox(label=key, default_value=value, tag=key)
        if type(value) == str:
            with dpg.table_row():
                dpg.add_input_text(label=key, default_value=value, tag=key)
    
def edit_config():
    win_uuid = dpg.generate_uuid()
    with dpg.window(width=500, height=300, pos=[200, 200], tag=win_uuid, modal=True, no_resize=True, no_close=True):
        helpers.center(win_uuid)
        dpg.add_button(label='Save', tag='btn_close', callback=save_and_close, user_data=win_uuid)
        with dpg.table(header_row=False):
            dpg.add_table_column()
            list_config_items()

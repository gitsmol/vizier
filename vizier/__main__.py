import dearpygui.dearpygui as dpg
import yaml
from .modules import helpers
from .modules import launcher
from .modules import theme
from .modules import profile
from .modules import settings
from .modules.profile_datamodel import ActiveProfile
from .modules.theme import COLORS

dpg.create_context()

# Some variables used throughout
fixed_window = {'no_title_bar': True, 'menubar': False, 'no_resize': True, 'no_move': True}
__version__ = 'Vizier 0.2.0'

with open('vizier/config/config.yaml') as config_file:
        config = yaml.safe_load(config_file)

def keypress(sender, app_data):
    # TODO move this to helpers
    key_translated = helpers.translate_key(app_data)

    if key_translated == 'tilde':
        debug_show = dpg.get_item_configuration('win_debug')['show']
        if debug_show == False:
            dpg.show_item('win_debug')
        if debug_show == True:
            dpg.hide_item('win_debug')

# anaglyph configuration values
with dpg.value_registry(tag='value_anaglyph'):
    dpg.add_color_value(default_value=COLORS['blue'], tag='color_left')
    dpg.add_color_value(default_value=COLORS['red'], tag='color_right')

# some general values
with dpg.value_registry(tag='value_main'):
    dpg.add_string_value(default_value='', tag='txt_debug')
    dpg.add_string_value(default_value=0, tag='str_time_remaining')
    dpg.add_bool_value(default_value=True, tag='bool_debug')
    dpg.add_string_value(default_value="No active profile.", tag='txt_activeprofile')

# keypress handler for general use
with dpg.handler_registry():
    dpg.add_key_press_handler(callback=keypress)

# primary window contains the main menu.
with dpg.window(tag='primary_window'):
    dpg.add_text(f"Active user:")
    dpg.add_text(source='txt_activeprofile')
    with dpg.window(tag='main_menu', pos=[350, 100], height=300, width=300, **fixed_window):
        with dpg.table(resizable=False, policy=4, scrollY=False, header_row=False):
            dpg.add_table_column(width=25, width_stretch=True)
            dpg.add_table_column(width=200, width_fixed=True)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_profile', label='Login', callback=profile.switch_user, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_evaluate', label='Exercises', callback=launcher.evaluations, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_edit_config', label='Configuration', callback=settings.edit_config, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_calibrate', label='Calibrate', callback=settings.calibrate, width=200)

            if config['application']['debug'] == True:
                with dpg.table_row():
                    dpg.add_table_cell()
                    dpg.add_button(tag='btn_style_editor', label='Style editor', callback=dpg.show_style_editor, width=200)
                with dpg.table_row():
                    dpg.add_table_cell()
                    dpg.add_button(tag='btn_font_manager', label='Font manager', callback=dpg.show_font_manager, width=200)
                with dpg.table_row():
                    dpg.add_table_cell()
                    dpg.add_button(tag='btn_item_registry', label='Item registry', callback=dpg.show_item_registry, width=200)
                with dpg.table_row(height=100):
                    dpg.add_table_cell()
                    dpg.add_button(tag='btn_value_registry', label='Value registry', callback=helpers.value_registry, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_quit', label='Quit', callback=dpg.stop_dearpygui, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_text(__version__)
            dpg.add_table_column(width=25, width_stretch=True)

# add debug window (show/hide quake-style with ~)
if config['application']['debug'] == True:
    with dpg.window(tag='win_debug', pos=[200, 500], width=600, height=300, **fixed_window):
        dpg.add_checkbox(tag='check_debug', source='bool_debug', label='Show debugging info')
        dpg.add_text(source='txt_debug', wrap=280)

theme.initialize()


# DPG context etc
dpg.create_viewport(title='Vizier', width=1000, height=700)
dpg.set_viewport_resize_callback(helpers.resizer)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_viewport_vsync(True)
dpg.set_primary_window("primary_window", True)
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

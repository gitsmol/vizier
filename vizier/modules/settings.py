import dearpygui.dearpygui as dpg
from . import helpers
from . import launcher
from .profile import db
from .profile import SESSION
from .profile_datamodel import CalibrationData
from .theme import COLORS
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

def calibrate():
    """Creates a window to calibrate the colors for the anaglyph exercise.
    Takes no arguments. Sets 'color_left' and 'color_right' in the DPG
    value registry. Can save calibration data to profile in db."""

    def default():
            dpg.set_value('color_left', COLORS['blue'])
            dpg.set_value('color_right', COLORS['red'])
            redraw()

    def redraw():
            dpg.delete_item('draw_calibrate', children_only=True)
            dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
            dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')

    def swap_eyes():
            left = dpg.get_value('color_left')
            right = dpg.get_value('color_right')
            dpg.set_value('color_left', right)
            dpg.set_value('color_right', left)
            redraw()

    def profile_save(s, a, u):
        """Save calibration data by storing it in the session object and
        updating the associated database record."""
        if SESSION.user:
            SESSION.calibration_data.color_left = dpg.get_value('color_left')
            SESSION.calibration_data.color_right = dpg.get_value('color_right')
            SESSION.calibration_data.save()

        else:
            helpers.error('No profile selected: not saved. Current settings will be lost after quitting.')
        dpg.delete_item('win_calibrate')

    with dpg.window(tag='win_calibrate', pos=[200,50], width=500, height=500, modal=True, on_close=helpers.delete):

        # calibration window gets its own theme
        with dpg.theme() as theme_calibrate:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 1, category=dpg.mvThemeCat_Core)
        dpg.bind_item_theme('win_calibrate', theme_calibrate)

        with dpg.table(resizable=True, policy=4, scrollY=False, header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(tag='btn_swap_eyes', label='Swap left/right', callback=swap_eyes)
                dpg.add_button(label='Set default', callback=default)
            with dpg.table_row():
                dpg.add_color_picker(label='Left eye', source='color_left', alpha_bar=True, no_inputs=True, callback=redraw)
                dpg.add_color_picker(label='Right eye', source='color_right', alpha_bar=True, no_inputs=True, callback=redraw)
        with dpg.drawlist(tag='draw_calibrate', width=300, height=200):
            dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
            dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')

        dpg.add_button(label='Save and close', callback=profile_save)

import dearpygui.dearpygui as dpg
import numpy as np
from time import time
from . import helpers
from . import exercises
from . import evaluations

dpg.create_context()

# Some variables used throughout
fixed_window = {'no_title_bar': True, 'menubar': False, 'no_resize': True, 'no_move': True}
COLORS = {
    'red'   : (255,25, 25, 50),
    'green' : (85, 255, 0),
    'blue'  : (0, 38, 230, 100),
    'white' : (255, 255, 255),
    'black' : (0, 0, 0)
}

# color blind safe colors defined by Bang Wong:
# https://www.nature.com/articles/nmeth.1618
SAFE_COLORS_WONG = {
    'red'    : (213, 94, 0),
    'green'  : (0, 157, 115),
    'blue'   : (86,180,233),
    'yellow' : (240, 228, 66),
    'orange' : (230, 159, 0),
    'purple' : (204, 121, 167),
    'black'  : (0, 0, 0)
}

# color blind safe colors defined by Paul Tol:
# https://personal.sron.nl/~pault/
# TODO move to separate colors.py
SAFE_COLORS_TOL = {
    'paleblue'  : (187, 204, 238),
    'blue'      : (68, 119, 170),
    'darkblue'  : (34, 34, 85),
    'night'     : (0, 6, 136),
    'palecyan'  : (204, 238, 255),
    'cyan'      : (102, 204, 238),
    'darkcyan'  : (34, 85, 85),
    'palegreen' : (204, 221, 170),
    'green'     : (34, 136, 51),
    'darkgreen' : (34, 85,34),
    'lightyellow': (238,204,102),
    'paleyellow': (238, 238, 187),
    'yellow'    : (204, 187, 68),
    'darkyellow': (102, 102, 51),
    'lightred'  : (255, 204, 204),
    'red'       : (238, 102, 119),
    'darkred'   : (102, 51, 51),
    'purple'    : (170, 51, 119),
    'palegrey'  : (221, 221, 221),
    'grey'      : (187, 187, 187),
    'darkgrey'  : (85, 85, 85),
    'lightblack': (26, 26, 26),
    'black'     : (0, 0, 0),
}

def keypress(sender, app_data):
    # TODO move this to helpers
    key_translated = helpers.translate_key(app_data)

    if key_translated == 'tilde':
        debug_show = dpg.get_item_configuration('win_debug')['show']
        if debug_show == False:
            dpg.show_item('win_debug')
        if debug_show == True:
            dpg.hide_item('win_debug')

def menu_launcher(sender, app_data):
    """Launches stuff from the main menu."""
    # TODO move this to helpers.
    if sender == 'btn_configure':
        with dpg.window(tag='configure', width=300, pos=(100,100)):
            dpg.add_slider_int(label='Size', source='anaglyph_size', min_value=100, max_value=400)
            dpg.add_slider_int(label='Pixel size', source='anaglyph_pixel_size', min_value=1, max_value=10)
            dpg.add_slider_float(label='Focal point size', source='anaglyph_focal_size', min_value=0.1, max_value=0.5)
            dpg.add_separator()
            dpg.add_slider_int(label='Initial value', source='anaglyph_initial_value', min_value=0, max_value=10)
            dpg.add_slider_int(label='Step', source='anaglyph_step', min_value=0, max_value=10)
            dpg.add_slider_int(label='Success threshold', source='anaglyph_success_threshold', min_value=1, max_value=10)
            dpg.add_slider_int(label='Failure threshold', source='anaglyph_fail_threshold', min_value=1, max_value=10)
            dpg.add_slider_int(label='Time', source='anaglyph_time', min_value=30, max_value=600)
            dpg.add_slider_int(label='Count', source='anaglyph_time', min_value=10, max_value=150)

    if sender == 'btn_calibrate':
        helpers.calibrate()

# anaglyph configuration values
with dpg.value_registry(tag='value_anaglyph'):
    dpg.add_color_value(default_value=COLORS['blue'], tag='color_left')
    dpg.add_color_value(default_value=COLORS['red'], tag='color_right')
    dpg.add_int_value(default_value=300, tag='anaglyph_size')
    dpg.add_int_value(default_value=3, tag='anaglyph_pixel_size')
    dpg.add_float_value(default_value=0.35, tag='anaglyph_focal_size')
    dpg.add_int_value(default_value = 0, tag='anaglyph_initial_value')
    dpg.add_int_value(default_value = 1, tag='anaglyph_step')
    dpg.add_int_value(default_value = 2, tag='anaglyph_success_threshold')
    dpg.add_int_value(default_value = 2, tag='anaglyph_fail_threshold')
    dpg.add_int_value(default_value = 100, tag='anaglyph_count')
    dpg.add_int_value(default_value = 120, tag='anaglyph_time')

# some general values
with dpg.value_registry(tag='value_main'):
    dpg.add_string_value(default_value='', tag='txt_debug')
    dpg.add_string_value(default_value=0, tag='str_time_remaining')
    dpg.add_bool_value(default_value=True, tag='bool_debug')

# keypress handler for general use
with dpg.handler_registry():
    dpg.add_key_press_handler(callback=keypress)

# primary window contains the main menu.
with dpg.window(tag='primary_window'):
    with dpg.window(tag='main_menu', pos=[250, 100], height=300, width=300, **fixed_window):
        with dpg.table(resizable=False, policy=4, scrollY=False, header_row=False):
            dpg.add_table_column(width=25, width_stretch=True)
            dpg.add_table_column(width=200, width_fixed=True)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_anaglyph', label='Anaglyph exercise', callback=evaluations.launcher, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_configure', label='Anaglyph config', callback=menu_launcher, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_alignment', label='Alignment exercise', callback=evaluations.launcher, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_calibrate', label='Calibrate', callback=menu_launcher, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_style_editor', label='Style editor', callback=dpg.show_style_editor, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_font_manager', label='Font manager', callback=dpg.show_font_manager, width=200)
            with dpg.table_row(height=100):
                dpg.add_table_cell()
                dpg.add_button(tag='btn_item_registry', label='Item registry', callback=dpg.show_item_registry, width=200)
            with dpg.table_row():
                dpg.add_table_cell()
                dpg.add_button(tag='btn_quit', label='Quit', callback=dpg.stop_dearpygui, width=200)
            dpg.add_table_column(width=25, width_stretch=True)

# add debug window (show/hide quake-style with ~)
with dpg.window(tag='win_debug', pos=[100, 500], width=600, height=300, **fixed_window):
    dpg.add_checkbox(tag='check_debug', source='bool_debug', label='Show debugging info')
    dpg.add_text(source='txt_debug', wrap=280)

# themes, fonts
with dpg.theme() as exercise_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 1, category=dpg.mvThemeCat_Core)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        # background colors
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, SAFE_COLORS_TOL['lightblack'], category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SAFE_COLORS_TOL['darkgrey'], category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SAFE_COLORS_TOL['darkgrey'], category=dpg.mvThemeCat_Core)

        # item colors
        dpg.add_theme_color(dpg.mvThemeCol_Button, SAFE_COLORS_TOL['darkgrey'], category=dpg.mvThemeCat_Core)

        # dpg.add_theme_color()
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2, category=dpg.mvThemeCat_Core)
dpg.bind_theme(global_theme)

with dpg.font_registry():
    font_default = dpg.add_font("vizier/assets/fonts/Roboto/Roboto-Regular.ttf", 16)

dpg.bind_font(font_default)
# dpg.bind_font(font_dyslexic)

# DPG context etc
dpg.create_viewport(title='Vizier', width=800, height=700)
dpg.set_viewport_resize_callback(helpers.resizer)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_viewport_vsync(True)
dpg.set_primary_window("primary_window", True)
dpg.start_dearpygui()
dpg.destroy_context()

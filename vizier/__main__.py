import dearpygui.dearpygui as dpg
import numpy as np
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

def keypress(sender, app_data):
    key_translated = helpers.translate_key(app_data)

    if key_translated == 'tilde':
        debug_show = dpg.get_item_configuration('win_debug')['show']
        if debug_show == False:
            dpg.show_item('win_debug')
        if debug_show == True:
            dpg.hide_item('win_debug')

def menu_launcher(sender, app_data):
    if sender == 'btn_configure':
        with dpg.window(tag='configure', width=300, pos=(100,100)):
            dpg.add_slider_int(label='Size', source='anaglyph_size', min_value=200, max_value=800)
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

with dpg.value_registry(tag='value_anaglyph'):
    dpg.add_color_value(default_value=COLORS['blue'], tag='color_left')
    dpg.add_color_value(default_value=COLORS['red'], tag='color_right')
    dpg.add_int_value(default_value=500, tag='anaglyph_size')
    dpg.add_int_value(default_value=4, tag='anaglyph_pixel_size')
    dpg.add_float_value(default_value=0.25, tag='anaglyph_focal_size')
    dpg.add_int_value(default_value = 0, tag='anaglyph_initial_value')
    dpg.add_int_value(default_value = 1, tag='anaglyph_step')
    dpg.add_int_value(default_value = 2, tag='anaglyph_success_threshold')
    dpg.add_int_value(default_value = 2, tag='anaglyph_fail_threshold')
    dpg.add_int_value(default_value = 100, tag='anaglyph_count')
    dpg.add_int_value(default_value = 120, tag='anaglyph_time')

with dpg.value_registry(tag='value_translate'):
    dpg.add_int_value(default_value=0, tag='parallax_translation')
    dpg.add_int_value(default_value=0, tag='x_translation')
    dpg.add_int_value(default_value=0, tag='y_translation')
    dpg.add_string_value(default_value='', tag='txt_debug')

with dpg.value_registry(tag='value_main'):
    dpg.add_bool_value(default_value=True, tag='bool_debug')

with dpg.handler_registry():
    dpg.add_key_press_handler(callback=keypress)

with dpg.window(tag='primary_window'):
    with dpg.window(tag="main_menu", pos=[250, 100], width=300, height=300, **fixed_window):
        dpg.add_button(tag='btn_anaglyph', label='Anaglyph exercise', callback=evaluations.launcher, user_data='new')
        dpg.add_button(tag='btn_configure', label='Anaglyph config', callback=menu_launcher)
        dpg.add_button(tag='btn_alignment', label='Alignment exercise', callback=evaluations.launcher)
        dpg.add_button(tag='btn_calibrate', label='Calibrate', callback=menu_launcher)
        dpg.add_button(tag='btn_style_editor', label='Style editor', callback=dpg.show_style_editor)
        dpg.add_button(tag='btn_quit', label='Quit', callback=dpg.stop_dearpygui)

with dpg.window(tag='win_debug', pos=[100, 500], width=600, height=300, **fixed_window):
    dpg.add_checkbox(tag='check_debug', source='bool_debug', label='Show debugging info')
    dpg.add_text(source='txt_debug', wrap=280)


dpg.add_window(tag='win_exercise', width=800, height=800, show=False, **fixed_window)

with dpg.theme() as exercise_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 1, category=dpg.mvThemeCat_Core)
dpg.bind_item_theme('win_exercise', exercise_theme)
# dpg.bind_theme(global_theme)

dpg.create_viewport(title='Vizier', width=800, height=800)
dpg.set_viewport_resize_callback(helpers.resizer)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_viewport_vsync(True)
dpg.set_primary_window("primary_window", True)
dpg.start_dearpygui()
dpg.destroy_context()

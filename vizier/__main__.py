import dearpygui.dearpygui as dpg
import numpy as np
from . import exercises
from . import helpers

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
    def translate_key(key_pressed):
        keys_translated = {
            265: 'up',
            264: 'down',
            263: 'left',
            262: 'right',
            256: 'escape',
            257: 'return',
            96: 'tilde',
            32: 'space'
        }

        if key_pressed in keys_translated:
            return keys_translated.get(key_pressed)
        else:
            helpers.debugger(f'unknown key pressed: {key_pressed}')
            return key_pressed

    key_translated = translate_key(app_data)

    if key_translated == "up":
        pass
        set_config['p4'][1] -= 1

    if key_translated == "down":
        pass
        set_config['p1'][1] += 1

    if key_translated == "left":
        pass
        set_config['p1'][0] -= 1

    if key_translated == "right":
        pass
        set_config['p1'][0] += 1

    if key_translated == 'tilde':
        debug_show = dpg.get_item_configuration('win_debug')['show']
        if debug_show == False:
            dpg.show_item('win_debug')
        if debug_show == True:
            dpg.hide_item('win_debug')

    dpg.set_value("response_indicator", f"key pressed: {key_translated} \n set_config = {set_config}")
    return set_config

def anaglyph(sender, app_data):
    with helpers.parent('win_exercise'):
        def anaglyph_next(sender, app_data):
            focal_diamond = exercises.Anaglyph(**{'bg_offset' : 10, 'focal_offset' : 4, 'parent' : 'draw_exercise'})
            anaglyph_queue.add(focal_diamond.draw())
            anaglyph_queue.next()

        anaglyph_queue = helpers.DrawQueue()
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(tag='btn_close', label='Close', callback=launch_exercise, user_data='win_exercise')
                dpg.add_button(tag='btn_anaglyph_next', label='Next', callback=anaglyph_next, user_data='next')

        with dpg.drawlist(tag='draw_exercise', parent='win_exercise', width=600, height=550):
            focal_diamond = exercises.Anaglyph(
                **{ 'bg_offset' : 8,
                    'focal_offset' : 4,
                    'parent' :'draw_exercise'
                    }
            )
            anaglyph_queue.add(focal_diamond.draw())
            focal_diamond = exercises.Anaglyph(
                **{ 'bg_offset' : 8,
                    'focal_offset' : 4,
                    'parent' :'draw_exercise'
                    }
            )
            anaglyph_queue.add(focal_diamond.draw())
            helpers.debugger(f'{len(anaglyph_queue.list())} items in queue')
            anaglyph_queue.next()

def launch_exercise(sender, app_data, user_data=''):
    if dpg.does_item_exist('win_exercise'):
        dpg.show_item('win_exercise')

    if sender == 'btn_anaglyph':
        anaglyph(sender, app_data)

    if sender == 'btn_alignment':
        exercises.Alignment()

    if sender == 'btn_close':
        dpg.hide_item(user_data)
        dpg.delete_item(user_data, children_only=True)

def launch_menu(sender, app_data):
    if sender == 'btn_configure':
        with dpg.window(tag='configure', width=300, pos=(100,100)):
            dpg.add_slider_int(label='Size', source='anaglyph_size', min_value=200, max_value=800)
            dpg.add_slider_int(label='Pixel size', source='anaglyph_pixel_size', min_value=1, max_value=10)
            dpg.add_slider_float(label='Focal point size', source='anaglyph_focal_size', min_value=0.1, max_value=0.5)

    if sender == 'btn_calibrate':
        if  dpg.does_item_exist('win_calibrate') == True:
            dpg.show_item('win_calibrate')
        if  dpg.does_item_exist('win_calibrate') == False:
            with dpg.window(tag='win_calibrate', pos=[200,50], width=500, height=500, modal=True):
                dpg.add_button(tag='btn_swap_eyes', label='Swap left/right', callback=calibrate)
                with dpg.table(resizable=True, policy=4, scrollY=False, header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    with dpg.table_row():
                        dpg.add_color_picker(label='Left eye', source='color_left', alpha_bar=True, no_inputs=True, callback=calibrate)
                        dpg.add_color_picker(label='Right eye', source='color_right', alpha_bar=True, no_inputs=True, callback=calibrate)
                with dpg.drawlist(tag='draw_calibrate', width=300, height=200):
                    dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
                    dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')

def calibrate(sender, app_data):
    if sender == 'btn_swap_eyes':
        left = dpg.get_value('color_left')
        right = dpg.get_value('color_right')
        dpg.set_value('color_left', right)
        dpg.set_value('color_right', left)
    dpg.delete_item('draw_calibrate', children_only=True)
    dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
    dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')

with dpg.value_registry(tag='value_anaglyph'):
    dpg.add_color_value(default_value=COLORS['blue'], tag='color_left')
    dpg.add_color_value(default_value=COLORS['red'], tag='color_right')
    dpg.add_int_value(default_value=500, tag='anaglyph_size')
    dpg.add_int_value(default_value=4, tag='anaglyph_pixel_size')
    dpg.add_float_value(default_value=0.25, tag='anaglyph_focal_size')

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
        dpg.add_button(tag='btn_anaglyph', label='Anaglyph exercise', callback=launch_exercise, user_data='new')
        dpg.add_button(tag='btn_configure', label='Anaglyph config', callback=launch_menu)
        dpg.add_button(tag='btn_alignment', label='Alignment exercise', callback=launch_exercise)
        dpg.add_button(tag='btn_calibrate', label='Calibrate', callback=launch_menu)
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

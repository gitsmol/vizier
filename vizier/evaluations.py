"""Module containing evaluation programs for various exercises."""

import dearpygui.dearpygui as dpg
import time
from threading import Thread

from . import helpers
from . import exercises

def launcher(sender, app_data, user_data=''):
    if dpg.does_item_exist('win_exercise'):
        dpg.show_item('win_exercise')

    if sender == 'btn_anaglyph':
        anaglyph(sender, app_data, 'win_exercise')

    if sender == 'btn_alignment':
        exercises.Alignment()

    if sender == 'btn_close':
        try:
            dpg.delete_item(f'{user_data}_handler_registry')
        finally:
            dpg.delete_item(user_data, children_only=True)
            dpg.hide_item(user_data)

def anaglyph(sender, app_data, parent, **kwargs):
    # TODO standard configurations
    # TODO format for saving configurations
    #   TODO create a TOMl/JSON/YAML-file containing basic configs
    #   TODO create dialog to add, change, remove configs
    # TODO configuration selection and editing screen
    # TODO performance evaluation screen
    """Evaluate performance using anaglyph images.

    :param primary_param: the primary exercise parameter.
    :param step: increase or decrease of the primary parameter when success_threshold is reached.
    :param success_threshold: number of succesfull answers needed to change primary parameter by 'step'.
    :param fail_threshold: number of wrong answers needed to reset primary parameter to its initial_value.
    :param count: number of iterations of the sequence.
    :param duration_secs: duration of the sequence in seconds.

    """
    def evaluate_keypress(sender, app_data):
        """Keypress callback function for this specific exercise."""
        key = helpers.translate_key(app_data)
        possible_answers = {'left': 'left', 'right': 'right', 'up': 'top', 'down': 'bottom'}
        if key in possible_answers:
            helpers.debugger(f'current item: {queue.current_item}')
            result = possible_answers.get(key) == queue.current_item.focal_position
            session.add_result(result)

            anaglyph_image.bg_offset = session.primary_param
            queue.add(anaglyph_image.draw())
            queue.next()

    # Set up evaluation session and queue.
    config = {
        'step' : -2,
        'primary_param_init' : 0,
        'duration_secs' : 100,
    }
    window_tag = dpg.generate_uuid()
    session = helpers.Evaluation(window_tag, **config)
    queue = helpers.DrawQueue()
    viewp_h, viewp_w = dpg.get_viewport_height(), dpg.get_viewport_width()

    # draw all items with the given parent.
    with dpg.window(tag=window_tag, width=viewp_w, height=viewp_h):
        # dpg.bind_item_theme(window_tag, exercise_theme)
        # create keypress handler for this evaluation
        with dpg.handler_registry(tag=f'{parent}_handler_registry'):
            dpg.add_key_press_handler(callback=evaluate_keypress)

    # basic buttons, timer etc
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(tag='btn_close', label='Close', callback=launcher, user_data=window_tag)
                dpg.add_text(tag='txt_timer', label='Time remaining', source='str_time_remaining', default_value='No time remaining.')

        # All drawing is done within this drawlist.
        with dpg.drawlist(tag='draw_exercise', width=viewp_w, height=viewp_h*0.90):
            anaglyph_image = exercises.Anaglyph(
                **{ 'bg_offset' : session.primary_param_init,
                    'focal_offset' : 2,
                    }
            )
            queue.add(anaglyph_image.draw())
            queue.next()

if __name__ == '__main__':
    print('Only to be used as part of the Vizier application.')

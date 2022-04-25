"""Module containing evaluation programs for various exercises."""

import dearpygui.dearpygui as dpg
import time
from threading import Thread
import json

from . import helpers
from . import exercises

def launcher(sender, app_data, user_data=''):
    if sender == 'btn_anaglyph':
        anaglyph(sender, app_data)

    if sender == 'btn_recognition':
        recognition(sender, app_data)

    if sender == 'btn_alignment':
        exercises.Alignment()

    if sender == 'btn_close':
        try:
            dpg.delete_item(f'{user_data}_handler_registry')
        finally:
            dpg.delete_item(user_data, children_only=True)
            dpg.hide_item(user_data)

def evaluation_launcher():
    with dpg.window(pos=[100, 100], width=400, height=500):
        with open('vizier/config/exercise_configs.json') as config_file:
            configs = json.load(config_file)

        with dpg.table():
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            for key_, value_ in configs.items(): # get different exercices
                with dpg.table_row():
                    dpg.add_text(key_)  # exercise name
                    dpg.add_text(value_.get('type')) # exercise type
                with dpg.table_row():
                    for config in value_.get('configs'):    # get configs per exercise
                        dpg.add_button(label=config, callback=anaglyph, user_data=value_['configs'][config])

def anaglyph(sender, app_data, config):
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
    def evaluate(sender, app_data):
        """Keypress callback function containing the evaluation logic.
        Add results to the session object. Add drawnodes to the queue."""
        key = helpers.translate_key(app_data)
        possible_answers = {'left': 'left', 'right': 'right', 'up': 'top', 'down': 'bottom'}
        if key in possible_answers:
            helpers.debugger(f'current item: {queue.current_item}')
            result = possible_answers.get(key) == queue.current_item.focal_position
            session.add_result(result)

            if session.active:
                anaglyph.bg_offset = session.primary_param
                queue.add(anaglyph.draw())
                queue.next()

    # Set up evaluation session and queue.
    # config = {
        # 'step' : -2,
        # 'primary_param_init' : 0,
        # 'duration_secs' : 50,
        # 'count' : 5,
    # }
    # config = kwargs
    session = helpers.EvaluationSession(**config)
    queue = helpers.DrawQueue()
    viewp_h, viewp_w = dpg.get_viewport_height(), dpg.get_viewport_width()
    # create keypress handler for this evaluation
    with dpg.handler_registry(tag=session.handler_uuid):
        dpg.add_key_press_handler(callback=evaluate)

    with dpg.window(tag=session.win_uuid, width=viewp_w, height=viewp_h):
        # dpg.bind_item_theme(window_tag, exercise_theme)

    # basic buttons, timer etc
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(tag='btn_close', label='Close', callback=session.end, user_data=session.win_uuid)
                dpg.add_text(tag='txt_timer', label='Time remaining', source='str_time_remaining', default_value='No time remaining.')

        # All drawing is done within this drawlist.
        dpg.add_drawlist(tag=session.drawlist_uuid, width=viewp_w, height=viewp_h*0.90)

        # Finally, create the anaglyph object and draw the first frame.
        anaglyph = exercises.Anaglyph(
            **{ 'bg_offset' : session.primary_param_init,
                'focal_offset' : 2,
                'drawlist_uuid' : session.drawlist_uuid
                }
        )

        queue.add(anaglyph.draw())
        queue.next()

def recognition(sender, app_data, **kwargs):
    """Evaluate performance recognizing and remembering briefly displayed objects.

    :param primary_param: the primary exercise parameter.
    :param step: increase or decrease of the primary parameter when success_threshold is reached.
    :param success_threshold: number of succesfull answers needed to change primary parameter by 'step'.
    :param fail_threshold: number of wrong answers needed to reset primary parameter to its initial_value.
    :param count: number of iterations of the sequence.
    :param duration_secs: duration of the sequence in seconds.

    """
    def evaluate(sender, app_data):
        """Keypress callback function containing the evaluation logic.
        Add results to the session object. Add drawnodes to the queue."""
        key = helpers.translate_key(app_data)
        possible_answers = ['left', 'right', 'up', 'down']
        if key in possible_answers:
            helpers.debugger(f'current item: {queue.current_item}')
            result = key == queue.current_item.directions
            session.add_result(result)

            if session.active:
                # recognition.bg_offset = session.primary_param
                queue.add(recognition.draw())
                queue.next()

    config = {
        'step' : 1,
        'primary_param_init' : 4,
        'duration_secs' : 50,
        'count' : 5,
    }
    session = helpers.EvaluationSession(**config)
    queue = helpers.DrawQueue()
    viewp_h, viewp_w = dpg.get_viewport_height(), dpg.get_viewport_width()

    # create keypress handler for this evaluation
    with dpg.handler_registry(tag=session.handler_uuid):
        dpg.add_key_press_handler(callback=evaluate)

    with dpg.window(tag=session.win_uuid, width=viewp_w, height=viewp_h):
        # dpg.bind_item_theme(window_tag, exercise_theme)

        # basic buttons, timer etc
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(tag='btn_close', label='Close', callback=session.end, user_data=session.win_uuid)
                dpg.add_text(tag='txt_timer', label='Time remaining', source='str_time_remaining', default_value='No time remaining.')

        # All drawing is done within this drawlist.
        dpg.add_drawlist(tag=session.drawlist_uuid, width=viewp_w, height=viewp_h*0.90)

        # Finally, create the anaglyph object and draw the first frame.
        recognition = exercises.Recognition(
            **{ 'object_count' : session.primary_param_init,
                # 'focal_offset' : 2,
                'drawlist_uuid' : session.drawlist_uuid
                }
        )

        queue.add(recognition.draw())
        # timer = Thread(target=hide_after, args=queue.current_item.display_time_secs)

        queue.next()

if __name__ == '__main__':
    print('Only to be used as part of the Vizier application.')

"""Module containing evaluation programs for various exercises."""

import dearpygui.dearpygui as dpg

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
        dpg.hide_item(user_data)
        dpg.delete_item(user_data, children_only=True)


def anaglyph(sender, app_data, parent, **kwargs):
    # TODO standard configurations
    # TODO format for saving configurations
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
        key = helpers.translate_key(app_data)
        possible_answers = {'left': 'left', 'right': 'right', 'up': 'top', 'down': 'bottom'}
        if key in possible_answers:
            helpers.debugger(f'current item: {queue.current_item}')
            result = possible_answers.get(key) == queue.current_item.focal_position
            session.add_result(result)

            anaglyph_image.bg_offset = session.primary_param
            queue.add(anaglyph_image.draw())
            queue.next()

    with helpers.parent(parent):
        dpg.add_handler_registry(tag='handler_anaglyph')
        dpg.add_key_press_handler(callback=evaluate_keypress, parent='handler_anaglyph')

        session = helpers.Evaluation()

        def anaglyph_next(sender, app_data):
            queue.add(anaglyph_image.draw())
            queue.next()

        queue = helpers.DrawQueue()
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(tag='btn_close', label='Close', callback=launcher, user_data='win_exercise')
                dpg.add_button(tag='btn_anaglyph_next', label='Next', callback=anaglyph_next, user_data='next')

        with dpg.drawlist(tag='draw_exercise', parent='win_exercise', width=600, height=550):
            anaglyph_image = exercises.Anaglyph(
                **{ 'bg_offset' : session.primary_param,
                    'focal_offset' : 4,
                    }
            )
            queue.add(anaglyph_image.draw())
            queue.next()

if __name__ == '__main__':
    print('Only to be used as part of the Vizier application.')

import numpy as np
import dearpygui.dearpygui as dpg
from collections import namedtuple
from time import sleep
from vizier import helpers
from vizier import imagemap

class Recognition():
    """Game where subject sees a number of objects and has to reproduce them
    through keyboard input as quickly as possible.

    :param object_type
    :param object_count
    :param object_size
    :param display_delay_secs: delay between drawing each object in secs
    :param display_time_secs
    :param drawlist_uuid: uuid of the drawlist to draw on
    """
    def __init__(self, drawlist, **kwargs):
        self.object_type = kwargs.get('object_type', 'arrow')
        self.object_count = kwargs.get('object_count', 3)
        self.object_rel_size = kwargs.get('object_size', 5)
        self.display_delay_secs = kwargs.get('display_delay_secs', 0.3)
        self.display_time_secs = kwargs.get('display_time_secs', 0.7)
        self.drawlist_uuid = drawlist
        self.drawlist_width = dpg.get_item_width(self.drawlist_uuid)
        self.drawlist_height = dpg.get_item_height(self.drawlist_uuid)
        self.answers_node_uuid = dpg.generate_uuid()
        self.object_size = self.object_rel_size / 100 * self.drawlist_width
        self.object_margin = self.object_size * 0.15
        self.rng = np.random.default_rng()

    def draw(self):
        """Draw sequence of objects in hidden state. Return drawnode uuid."""
        x_min = (self.drawlist_width / 2) - (self.object_count * (self.object_size + self.object_margin) / 2)
        y = (self.drawlist_height / 2) - (self.object_size / 2)
        node_uuid = str(dpg.generate_uuid())
        arrow_direction = self.rng.choice(['top', 'bottom', 'left', 'right'])
        directions = []

        with dpg.draw_node(tag=node_uuid, parent=self.drawlist_uuid, show=True):
            for i in range(self.object_count):
                random_direction = self.rng.choice(['up', 'down', 'left', 'right'])
                x = x_min + (i * (self.object_size + self.object_margin))
                dpg.draw_image(imagemap.arrows.get(random_direction), pmin=(x, y), pmax=(x + self.object_size, y + self.object_size))
                directions.append(random_direction)
                sleep(self.display_delay_secs)

         # return a namedtuple for legibility in other places
        drawing = namedtuple('Drawing', ['node_uuid', 'directions', 'display_time_secs'])
        return drawing(node_uuid, directions, self.display_time_secs)

    def draw_single(self, key, pos):
        image = imagemap.arrows.get(key)
        x_min = (self.drawlist_width / 2) - (self.object_count * (self.object_size + self.object_margin) / 2)
        x = x_min + (pos * (self.object_size + self.object_margin))
        y = (self.drawlist_height / 2) - (self.object_size / 2) + (self.object_size)
        with dpg.draw_node(tag=self.answers_node_uuid, parent=self.drawlist_uuid):
            dpg.draw_image(image, pmin=(x, y), pmax=(x + self.object_size, y + self.object_size))

def run(config):
    """Evaluate performance recognizing and remembering briefly displayed objects.

    :param primary_param: the primary exercise parameter.
    :param step: increase or decrease of the primary parameter when success_threshold is reached.
    :param success_threshold: number of succesfull answers needed to change primary parameter by 'step'.
    :param fail_threshold: number of wrong answers needed to reset primary parameter to its initial_value.
    :param count: number of iterations of the sequence.
    :param duration_secs: duration of the sequence in seconds.
    """

    def evaluate(sender, app_data, accept_input=True):
        """Keypress callback function containing the evaluation logic.
        Add results to the session object. Add drawnodes to the queue."""
        key = helpers.translate_key(app_data)
        possible_answers = ['left', 'right', 'up', 'down']
        if (key in possible_answers) & (answers.accept_input == True):
            answers.add(key)
            pos = len(answers.answers) - 1
            recognition.draw_single(key, pos)

            if len(answers.answers) == recognition.object_count:
                answers.accept_input = False    # dont accept input while evaluating and drawing
                result = answers.answers == queue.current_item.directions
                session.add_result(result)
                answers.reset()

                if session.active:
                    sleep(2)    # a little pause before the next exercise
                    dpg.delete_item(recognition.answers_node_uuid)
                    queue.add(recognition.draw())
                    queue.next()
                    answers.accept_input = True # accept input again

    session_config = config.get('Session')  # this config part is required
    exercise_config = config.get('Exercise', None) # this config part is optional
    answers = helpers.Answers()
    session = helpers.EvaluationSession(**session_config)
    queue = helpers.DrawQueue()
    viewp_h, viewp_w = dpg.get_viewport_height(), dpg.get_viewport_width()

    # create keypress handler for this evaluation
    with dpg.handler_registry(tag=session.handler_uuid):
        dpg.add_key_press_handler(callback=evaluate)

    with dpg.window(tag=session.win_uuid, width=viewp_w, height=viewp_h):
        dpg.bind_item_theme(session.win_uuid, 'exercise_theme')

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
        recognition = Recognition(drawlist=session.drawlist_uuid, **exercise_config)
        queue.add(recognition.draw())
        queue.next()
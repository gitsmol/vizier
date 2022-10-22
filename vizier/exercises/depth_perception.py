import dearpygui.dearpygui as dpg
import numpy as np
from collections import namedtuple
from vizier import helpers
from vizier import imagemap
from time import sleep

"""
Depth perception exercise.
"""

class DepthPerception():
    def __init__(self, drawlist, **kwargs):
        self.object_type = kwargs.get('object_type', 'circle')
        self.object_count = kwargs.get('object_count', 3)
        self.object_rel_size = kwargs.get('object_size', 5)
        self.drawlist_uuid = drawlist
        self.drawlist_width = dpg.get_item_width(self.drawlist_uuid)
        self.drawlist_height = dpg.get_item_height(self.drawlist_uuid)
        self.object_size = self.object_rel_size / 100 * self.drawlist_width
        self.object_margin = self.object_size * 0.20
        self.arrow_size = (50, 50)
        self.min_depth = kwargs.get('min_depth', 0) / 100 * self.object_size
        self.max_depth = kwargs.get('max_depth', 10) / 100 * self.object_size
        self.min_depth_diff = kwargs.get('min_depth_diff', 5)
        self.max_depth_diff = kwargs.get('max_depth_diff', 15)

    def draw(self) -> tuple:
        """Draw sequence of anaglyph objects in hidden state. One of the objects has a different anaglyph_offset. Return drawnode uuid."""
        x_min = (self.drawlist_width / 2) - (self.object_count * (self.object_size + self.object_margin) / 2)
        y = (self.drawlist_height / 2) - (self.object_size / 2)
        node_uuid = str(dpg.generate_uuid())
        offset = np.random.randint(self.min_depth, self.max_depth)
        special_object = np.random.randint(self.object_count)
        special_offset = np.random.randint(self.min_depth_diff, self.max_depth_diff)
        plus = np.random.choice([True, False])
        if plus == True:
            special_offset = offset + special_offset
        if plus == False:
            special_offset = offset - special_offset

        with dpg.draw_node(tag=node_uuid, parent=self.drawlist_uuid, show=True):
            for i in range(self.object_count):
                sleep(0.2)
                if i == special_object:
                    x_offset = special_offset
                else:
                    x_offset = offset
                x = x_min + i * (self.object_size + self.object_margin)
                dpg.draw_circle(
                [x - x_offset / 2, y],
                self.object_size / 2,
                color = dpg.get_value('color_left'),
                thickness = 5
                )
                dpg.draw_circle(
                    [x + x_offset / 2, y],
                    self.object_size / 2,
                    color = dpg.get_value('color_right'),
                    thickness = 5
                )
            self.draw_arrow(0)
        
         # return a namedtuple for legibility in other places
        drawing = namedtuple('Drawing', ['node_uuid', 'special_object'])
        return drawing(node_uuid, special_object)

    def draw_arrow(self, position):
        if dpg.does_item_exist('answer_arrow'):
            dpg.delete_item('answer_arrow')
        x_min = (self.drawlist_width / 2) - (self.object_count * (self.object_size + self.object_margin) / 2)
        x = x_min + position * (self.object_size + self.object_margin) - self.arrow_size[0] / 2
        y = (self.drawlist_height / 2) + (self.object_size / 2)

        with dpg.draw_node(tag='answer_arrow', parent=self.drawlist_uuid, show=True):
            dpg.draw_image(imagemap.arrows.get('up'), pmin=(x, y), pmax=(x + self.arrow_size[0], y + self.arrow_size[1]))

def run(config) -> None:
    """Depth perception evaluation."""

    def evaluate(sender, app_data):
        key = helpers.translate_key(app_data)
        if key == 'left':
            if answers.answers[0] > 0:
                answers.replace(answers.answers[0] - 1)
        if key == 'right':
            if answers.answers[0] < exercise.object_count - 1:
                answers.replace(answers.answers[0] + 1)
        exercise.draw_arrow(answers.answers[0])
        
        if key == 'return':
            if answers.answers[0] == queue.current_item.special_object:
                session.add_result(True)
            else:
                session.add_result(False)
            if session.active:
                queue.remove()
                answers.replace(0)
                exercise.draw_arrow(answers.answers[0])
                queue.add(exercise.draw())
                helpers.debugger(f'Next.')
                queue.next()

  # set up basic configs and objects
    session_config = config.get('Session')  # this config part is required
    exercise_config = config.get('Exercise', None) # this config part is optional
    session = helpers.EvaluationSession(**session_config)
    queue = helpers.DrawQueue()
    answers = helpers.Answers()
    answers.add(0)
    viewp_h, viewp_w = dpg.get_viewport_height(), dpg.get_viewport_width()

    # create keypress handler for this evaluation
    with dpg.handler_registry(tag=session.handler_uuid):
        dpg.add_key_press_handler(callback=evaluate)

    with dpg.window(tag=session.win_uuid, width=viewp_w, height=viewp_h):
        # assign theme with black background
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

        # Finally, create the exercise object and draw the first frame.
        exercise = DepthPerception(drawlist=session.drawlist_uuid, **exercise_config)
        queue.add(exercise.draw())
        queue.next()
        helpers.debugger('Next.')
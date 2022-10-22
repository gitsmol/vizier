import numpy as np
import dearpygui.dearpygui as dpg
from collections import namedtuple
import vizier.helpers as helpers

class Alignment():
    def __init__(self, drawlist, **kwargs):
        self.drawlist_uuid = drawlist
        self.object_rel_size = kwargs.get('object_size', 4)
        self.drawlist_width = dpg.get_item_width(self.drawlist_uuid)
        self.drawlist_height = dpg.get_item_height(self.drawlist_uuid)
        self.object_size = self.object_rel_size / 100 * self.drawlist_width
        self.position_randomness = kwargs.get('randomness', 0)

    def draw(self):
        # draw a target in a random place near the center of the screen
        # draw a crosshair in a random place
        # return the uuid of the node and the coords of the target
        draw_node_uuid = dpg.generate_uuid()
        x_center = self.drawlist_width / 2
        y_center = self.drawlist_height / 2
        x_min = x_center - self.object_size
        y_min = y_center - self.object_size

        def random_coords():
            # range is the tolerated deviation from center in both directions of each axis
            if self.position_randomness > 0:
                x_range = self.position_randomness / 100 * self.drawlist_width / 2
                y_range = self.position_randomness / 100 * self.drawlist_height / 2
            if self.position_randomness <= 0:
                x_range = 1
                y_range = 1
            x = x_min + np.random.randint(-x_range, x_range)
            y = y_min + np.random.randint(-y_range, y_range)
            s = self.object_size
            return x, y, s

        with dpg.draw_node(tag=draw_node_uuid, parent=self.drawlist_uuid):
            with dpg.draw_node(tag='target'):
                x, y, s = random_coords()
                dpg.draw_rectangle((x, y), (x + self.object_size, y + self.object_size), color=COLORS['blue'], thickness=2)

            node_aim_uuid = dpg.generate_uuid()
            with dpg.draw_node(tag=node_aim_uuid):
                x, y, s = random_coords()
                # how to draw a quad?
                # p1 (left): x, y+s/2       # p2 (down): x+s/2, y+s
                # p3 (right): x+s, y+s/2    # p4 (up): x+s/2, y
                dpg.draw_quad((x, y+s/2), ((x+s/2), (y+s)), (x+s, y+s/2), (x+s/2, y), color=COLORS['red'], thickness=2)

        # return a namedtuple for legibility in other places
        # TODO switch to dataclass
        drawing = namedtuple('Drawing', ['node_uuid', 'node_aim_uuid'])
        return drawing(draw_node_uuid, node_aim_uuid)

def run(config):
    def evaluate(sender, app_data):
        key = helpers.translate_key(app_data)
        movement_keys = ['left', 'right', 'up', 'down']
        if key in movement_keys:
            # translate the target node
            node_aim = queue.current_item.node_aim_uuid
            node_aim_pos = dpg.get_item_pos(node_aim)
            if key == 'left':
                node_aim_pos[0] -= 1
            dpg.set_item_pos(queue.current_item.node_aim_uuid, node_aim_pos)
            # dpg.set_item_pos(queue.current_item.node_aim_uuid, pos=newpos)
            # dpg.set_item_configuration(queue.curent_item.node_aim_uuid, pos=newpos)

    # set up basic configs and objects
    session_config = config.get('Session')  # this config part is required
    exercise_config = config.get('Exercise', None) # this config part is optional
    session = helpers.EvaluationSession(**session_config)
    queue = helpers.DrawQueue()
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
        exercise = Alignment(drawlist=session.drawlist_uuid, **exercise_config)
        queue.add(exercise.draw())
        queue.next()


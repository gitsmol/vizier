"""Module containing helper functions for Vizier."""
# this is only necessary to avoid circular imports.

import dearpygui.dearpygui as dpg
from contextlib import contextmanager
from dataclasses import dataclass
from time import time, time_ns, sleep
from threading import Thread
from collections import namedtuple
from pathlib import Path
import json

class DrawQueue():
    """Queue, show and delete draw_nodes."""
    def __init__(self):
        self.queue = []
        self.current_item = ''

    def add(self, item_tuple):
        """Add a tag for a dpg item to the queue."""
        self.queue.append(item_tuple)

    def next(self):
        """Unhides current node, deletes previous node."""
        queued_item = self.queue.pop(0)
        dpg.show_item(queued_item.node_uuid)
        if hasattr(queued_item, 'display_time_secs'):
            debugger(f'Displaying for {queued_item.display_time_secs}')
            timer = Thread(target=self.display_timer, \
                           args=(queued_item.node_uuid, queued_item.display_time_secs))
            timer.start()
        if self.current_item:
            dpg.delete_item(self.current_item.node_uuid)
        self.current_item = queued_item

    def display_timer(self, node_uuid, secs):
        sleep(secs)
        dpg.hide_item(node_uuid)


class EvaluationSession():
    """Stores evaluation context variables, parameters and results.

    :param primary_param: the primary exercise parameter.
    :param step: increase or decrease of the primary parameter when success_threshold is reached.
    :param success_threshold: number of succesfull answers needed to change primary parameter by 'step'.
    :param fail_threshold: number of wrong answers needed to reset primary parameter to its initial_value.
    :param count: number of iterations of the sequence.
    :param duration_secs: duration of the sequence in seconds.

    :func add_result(tuple): adds a tuple containing an evaluation result to the session results.
    :func end(): stops the evaluation and displays the results.
    """
    def __init__(self, window_tag=None, **kwargs):
        self.window = window_tag
        self.win_uuid = dpg.generate_uuid()
        self.handler_uuid = dpg.generate_uuid()
        self.drawlist_uuid = dpg.generate_uuid()
        self.primary_param_init = kwargs.get('primary_param_init', 0)
        self.primary_param = self.primary_param_init
        self.step = kwargs.get('step', 1)
        self.success_threshold = kwargs.get('success_threshold', 2)
        self.fail_threshold = kwargs.get('fail_threshold', 2)
        self.count = kwargs.get('count', 50)
        self.duration_secs = kwargs.get('duration_secs', 120)
        self.epoch_start = time()
        self.results = []
        self.fail = 0
        self.success = 0
        self.active = True
        self.timer = Thread(target=self._countdown)
        self.timer.start()
        self.Result = namedtuple('Result', ['count', 'primary_param', 'correctness', 'time', 'time_diff'])

    def dataframe(self) -> int:
        df = pd.DataFrame(self.results, columns=['Count', 'Answer', 'Epoch', 'Diff_sec'])
        return df

    def add_result(self, result):
        now = time()
        count = len(self.results) + 1
        if count > 1:
            prev = self.results[-1][3]
            diff = round(now - prev, 4)
        if count == 1:
            diff = 0
        record = self.Result(count, self.primary_param, result, now, diff)
        self.results.append(record)

        if result == True:
            self.success += 1
            self.fail = 0

        if result == False:
            self.succes = 0
            self.fail += 1

        if self.success == self.success_threshold:
            self.primary_param += self.step
            self.success = 0

        if self.fail == self.fail_threshold:
            self.primary_param = self.primary_param_init
            self.fail = 0

        if (len(self.results) >= self.count) & (self.active):
            self.end()

    def _countdown(self):
        """"Counts down time remaining in the evaluation session."""
        time_end = time() + self.duration_secs
        while (time() < time_end) & (self.active):
            time_remaining = round(time_end - time())
            dpg.set_value('str_time_remaining', time_remaining)
            debugger(f'Countdown: {time_remaining}')
            sleep(1)
        dpg.set_value('str_time_remaining', 'All done.')
        debugger(f'Countdown stopped.')
        if self.active:
            self.end()

    def end(self):
        """Ends the evaluation session. Destroys IO handler and window. Stops _countdown thread. Creates results window."""
        debugger('Stopping evaluation.')
        self.active = False
        dpg.delete_item(self.handler_uuid)
        dpg.delete_item(self.win_uuid)
        self.show_results()

    def show_results(self):
        with dpg.window(pos=[100, 200], width=400, height=500):
            dpg.add_text('Finished!')
            with dpg.table(resizable=False, policy=4, scrollY=False, header_row=True):
                for item in self.results[0]:
                    dpg.add_table_column(width=25, width_stretch=True, label='Label')
                    # dpg.add_table_column(width=25, width_stretch=True)
                # dpg.add_table_column(width=25, width_stretch=True)
                # dpg.add_table_column(width=25, width_stretch=True)
                # dpg.add_table_column(width=25, width_stretch=True)
                for i in range(len(self.results)):
                    with dpg.table_row():
                        dpg.add_text(self.results[i].primary_param)    # primary param
                        dpg.add_text(self.results[i].correctness)    # correctness
                        dpg.add_text(self.results[i].time_diff)    # time


@contextmanager
def parent(parent_id):
    """Draw all items in this context under the given parent."""

    try:
        yield dpg.push_container_stack(parent_id)

    finally:
        dpg.pop_container_stack()

def calibrate():
    """Creates a window to calibrate the colors for the anaglyph exercise. Takes no arguments.
    Sets 'color_left' and 'color_right' in the DPG value registry."""
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

    # TODO replace 'if exist show-pattern' with helper function
    if  dpg.does_item_exist('win_calibrate') == True:
        dpg.show_item('win_calibrate')
    if  dpg.does_item_exist('win_calibrate') == False:
        with dpg.window(tag='win_calibrate', pos=[200,50], width=500, height=500, modal=True):

            # calibration window gets its own theme
            with dpg.theme() as theme_calibrate:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 1, category=dpg.mvThemeCat_Core)
            dpg.bind_item_theme('win_calibrate', theme_calibrate)

            dpg.add_button(tag='btn_swap_eyes', label='Swap left/right', callback=swap_eyes)
            with dpg.table(resizable=True, policy=4, scrollY=False, header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_color_picker(label='Left eye', source='color_left', alpha_bar=True, no_inputs=True, callback=redraw)
                    dpg.add_color_picker(label='Right eye', source='color_right', alpha_bar=True, no_inputs=True, callback=redraw)
            with dpg.drawlist(tag='draw_calibrate', width=300, height=200):
                dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
                dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')

def debugger(debug_data, level='info'):
    """Sends data to the debugging window."""
    if dpg.get_value('bool_debug') == True:
        old_data = dpg.get_value('txt_debug')
        dpg.set_value('txt_debug', f'{debug_data}\n{old_data}')

def resizer():
    """Resizes and repositions items whenever the viewport is resized."""
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()

    def center(item, rel_y='none'):
        item_width = dpg.get_item_width(item)
        item_height = dpg.get_item_height(item)

        rel_y_positions = {
            'top' : 0,
            'bottom' : dpg.get_viewport_height() - item_height,
            'none' : dpg.get_item_pos(item)[1]
        }

        newpos_x = viewport_width / 2 - item_width / 2
        newpos_y = rel_y_positions[rel_y]
        debugger(f'setting pos [{newpos_x, newpos_y}] for {item}')
        dpg.set_item_pos(item, [newpos_x, newpos_y])

    def fullscreen(item):
        dpg.set_item_width(item, viewport_width)
        dpg.set_item_height(item, viewport_height)

    center('main_menu')
    center('win_debug', 'bottom')
    # fullscreen('win_exercise')

def translate_key(key_pressed):
    keys = {
        265: 'up',
        264: 'down',
        263: 'left',
        262: 'right',
        256: 'escape',
        257: 'return',
        96: 'tilde',
        32: 'space'
    }

    if key_pressed in keys:
        return keys.get(key_pressed)
    else:
        debugger(f'unknown key pressed: {key_pressed}')
        return None


def temp(sender, app_data, user_data):
    debugger(f'Temp sent {user_data}')
    # config = user_data['configs'][config]

def dirwalk(path):
    for p in Path(path).iterdir():
        if p.is_dir():
            yield from dirwalk(p)
            continue
        yield p.resolve()


if __name__ == '__main__':
    print('Only to be used as part of the Vizier application.')

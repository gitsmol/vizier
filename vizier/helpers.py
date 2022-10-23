"""Module containing helper functions for Vizier."""

import dearpygui.dearpygui as dpg
from contextlib import contextmanager
from time import time, sleep
from threading import Thread
from collections import namedtuple
from pathlib import Path
import importlib
import pkgutil
import yaml
import logging
from .theme import COLORS, SAFE_COLORS_TOL, SAFE_COLORS_WONG
from . import profile

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
fixed_window = {'no_title_bar': True, 'menubar': False, 'no_resize': True, 'no_move': True}

class Answers():
    """Keeps a temporary record of given answers. This is useful in cases when a series of answers needs to be evaluated by the evaluation logic. For instance, when showing multiple arrows that need to be recalled in the correct order."""

    def __init__(self):
        self.answers = []
        self.accept_input = True

    def add(self, new_answer):
        if self.accept_input:
            self.answers.append(new_answer)

    def replace(self, new_answer):
        if self.accept_input:
            self.answers = [new_answer]

    def reset(self):
        self.answers = []

class DrawQueue():
    """Queue, show and delete draw_nodes.

    The queue must be fed a tuple containing at least a string referring to a dpg draw_node tag.
    Optionally the tuple can contain a 'display_time_secs' attribute. This will be used to
    hide the indicated dpg draw_node after a give amount of seconds.
    """
    def __init__(self):
        self.queue = []
        self.current_item = None

    def __repr__(self):
        summary = f'Queued: {self.queue}\nCurrent item: {self.current_item}'
        return summary

    def add(self, item_tuple):
        """Add a tag for a dpg item to the queue."""
        self.queue.append(item_tuple)

    def remove(self):
        """Remove current dpg item from the queue."""
        dpg.delete_item(self.current_item.node_uuid)
        self.current_item = None

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
    def __init__(self, window_tag=None, **session_config):
        self.window = window_tag
        self.win_uuid = dpg.generate_uuid()
        self.handler_uuid = dpg.generate_uuid()
        self.drawlist_uuid = dpg.generate_uuid()
        self.primary_param_init = session_config.get('primary_param_init', 0)
        self.primary_param = self.primary_param_init
        self.step = session_config.get('step', 1)
        self.success_threshold = session_config.get('success_threshold', 2)
        self.fail_threshold = session_config.get('fail_threshold', 2)
        self.count = session_config.get('count', 50)
        self.duration_secs = session_config.get('duration_secs', 120)
        self.epoch_start = time()
        self.results = []
        self.fail = 0
        self.success = 0
        self.active = True
        self.timer = Thread(target=self._countdown)
        self.timer.start()
        self.Result = namedtuple('Result', ['count', 'primary_param', 'correctness', 'time', 'time_diff'])

    def dataframe(self) -> int:
        raise NotImplemented()
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
        """Ends the evaluation session. Destroys IO handler and window. Stops _countdown() thread. Creates results window."""
        debugger('Stopping evaluation.')
        self.active = False
        dpg.delete_item(self.handler_uuid)
        dpg.delete_item(self.win_uuid)
        eval_results(self.results)

def eval_results(results):
    count = []
    param = []
    correct = []
    time_diff = []

    for i, val in enumerate(results):
        count.append(i)
        param.append(val.primary_param)
        correct.append(val.correctness)
        time_diff.append(val.time_diff)

    count_true = correct.count(True)
    count_false = correct.count(False)

    with dpg.window(width=800, height=600, modal=True):
        with dpg.table():
            dpg.add_table_column(width_fixed=True)
            dpg.add_table_column(width_stretch=True)
            with dpg.table_row():
                with dpg.plot(label="Score", height=250, width=250):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes
                    dpg.add_plot_axis(dpg.mvXAxis, label="", no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                    dpg.set_axis_limits(dpg.last_item(), 0, 1)

                    # create y axis
                    with dpg.plot_axis(dpg.mvYAxis, label="", no_gridlines=True, no_tick_marks=True, no_tick_labels=True):
                        dpg.set_axis_limits(dpg.last_item(), 0, 1)
                        # dpg.add_pie_series(0.5, 0.5, 0.5, [0.25, 0.30, 0.30], ["fish", "cow", "chicken"])
                        dpg.add_pie_series(0.5, 0.5, 0.5, values=[count_true, count_false], labels=['True', 'False'])

                with dpg.plot(label="Development", height=250, width=550):
                    y_score = dpg.generate_uuid()
                    y_difficulty = dpg.generate_uuid()
                    y_time_diff = dpg.generate_uuid()
                    dpg.add_plot_legend()

                    dpg.add_plot_axis(dpg.mvXAxis, label="Tries")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Score", tag=y_score)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Difficulty", tag=y_difficulty)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Timing", tag=y_time_diff)

                    dpg.add_bar_series(count, correct, label="Correct", parent=y_score)
                    dpg.add_line_series(count, param, label="Param", parent=y_difficulty)
                    dpg.add_line_series(count, time_diff, label="Time", parent=y_time_diff)

        with dpg.collapsing_header(label='Results'):
            with dpg.table(resizable=False, policy=4, scrollY=False, header_row=True):
                for field in results[0]._fields:
                    dpg.add_table_column(width=25, width_stretch=True, label=field)
                for i in range(len(results)):
                    with dpg.table_row():
                        for field in results[0]._fields:
                            dpg.add_text(getattr(results[i], field))   # primary param


@contextmanager
def parent(parent_id):
    """Draw all items in this context under the given parent."""

    try:
        yield dpg.push_container_stack(parent_id)

    finally:
        dpg.pop_container_stack()

def debugger(debug_data, level='info'):
    """Sends data to the debugging window and the debug logger."""
    logging.debug(debug_data)
    if dpg.get_value('bool_debug') == True:
        old_data = dpg.get_value('txt_debug')
        dpg.set_value('txt_debug', f'{debug_data}\n{old_data}')

def delete(sender, app_data):
    dpg.delete_item(sender)

def center(item, rel_y=None):
        """Center given dpg item."""
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        item_width = dpg.get_item_width(item)
        item_height = dpg.get_item_height(item)

        rel_y_positions = {
            'top' : 0,
            'bottom' : dpg.get_viewport_height() - item_height,
            None : dpg.get_item_pos(item)[1]
        }

        newpos_x = viewport_width / 2 - item_width / 2
        newpos_y = rel_y_positions[rel_y]
        debugger(f'setting pos [{newpos_x, newpos_y}] for {item}')
        dpg.set_item_pos(item, [newpos_x, newpos_y])

def resizer():
    """Resizes and repositions items whenever the viewport is resized."""
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()

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
        # debugger(f'unknown key pressed: {key_pressed}')
        return None

def value_registry():
    def refresh():
        dpg.delete_item('win_value_registry')
        value_registry()

    with dpg.window(tag='win_value_registry', width=300, height=300, on_close=delete):
        color_left = dpg.get_value('color_left')
        color_right = dpg.get_value('color_right')

        dpg.add_button(label='Refresh', callback=refresh)
        dpg.add_text(color_left, label='color_left')
        dpg.add_text(color_right, label='color_right')


def dirwalk(path):
    for p in Path(path).iterdir():
        if p.is_dir():
            yield from dirwalk(p)
            continue
        yield p.resolve()

def error(exc, debug_info=''):
    win_id = dpg.generate_uuid()
    with dpg.window(tag=win_id, modal=True, no_resize=True, width=300):
        center(win_id, rel_y='top')
        dpg.add_text(debug_info)
        dpg.add_text(exc)

def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results

if __name__ == '__main__':
    print('Only to be used as part of the Vizier application.')

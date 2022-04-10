"""Module containing helper functions for Vizier."""
# this is only necessary to avoid circular imports.

import dearpygui.dearpygui as dpg
from contextlib import contextmanager

class DrawQueue():
    """Queue, show and delete draw_nodes."""

    def __init__(self):
        self.queue = []
        self.current_item = ''

    def add(self, item_tag):
        """Add a tag for a dpg item to the queue."""
        self.queue.append(item_tag)

    def next(self):
        """Deletes previous node, unhides current node."""
        if self.current_item:
            dpg.delete_item(self.current_item)
        queued_item = self.queue.pop(0)
        dpg.show_item(queued_item)
        self.current_item = queued_item

    def list(self):
        return self.queue


@contextmanager
def parent(parent_id):

    try:
        yield dpg.push_container_stack(parent_id)

    finally:
        dpg.pop_container_stack()

def debugger(debug_data):
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
    fullscreen('win_exercise')

import dearpygui.dearpygui as dpg
import numpy as np
import uuid
from collections import namedtuple
from . import helpers

"""Module providing visual therapy exercises as classes."""
COLORS = {
    'red'   : (255,25, 25, 50),
    'green' : (85, 255, 0),
    'blue'  : (0, 38, 230, 100),
    'white' : (255, 255, 255),
    'black' : (0, 0, 0)
}


class Alignment():
    def __init__(self):
        with dpg.drawlist(tag='draw_alignment', parent='exercise_graphics', width=200, height=200):
            dpg.draw_rectangle((0, 0), (51, 51), color=COLORS['blue'], thickness=5, tag="square")
            dpg.draw_quad((0, 25), (25, 50), (50, 25), (25, 0), color=COLORS['red'], thickness=2, tag='diamond')

class Anaglyph():
    """
    Class to create anaglyph images. Each image consists of a background and a focal point.
    draw() draws both focal point and background in order, according to the kwargs defined in __init__.

    :param bg_offset: Define drawing offset on x-axis for the background image.
    :param focal_offset: Define drawing offset on x-axis for the focal image.
    :param size: Size of one side of the image in pixels. Used for x and y size.
    :param pixel_size: Size of the individual squares ('pixels') drawn.
    :param focal_size_rel: Relative size of the focal point as fraction of 1.
    """

    def __init__(self, **kwargs):
        self.node_uuid = uuid.uuid4()
        self.parent = kwargs.get('parent', 'draw_exercise')
        self.bg_offset = kwargs.get('bg_offset', 0)
        self.focal_offset = kwargs.get('focal_offset', 2)
        self.size = kwargs.get('size', dpg.get_value('anaglyph_size'))
        self.pixel_size = kwargs.get('pixel_size', dpg.get_value('anaglyph_pixel_size'))
        self.focal_size_rel = kwargs.get('focal_size_rel', dpg.get_value('anaglyph_focal_size'))
        self.focal_size = self.size * self.focal_size_rel
        self.pixel_count = int(self.size / self.pixel_size)
        self.focal_pixel_count = int(self.focal_size / self.pixel_size)
        self.rng = np.random.default_rng()
        self.focal_position = None
        self.init_pixel_array = None
        self.bg_pixel_array = None
        self.mask_array = None
        self.focal_pixel_rng = None

    def draw_focal(self, eye):
        """Draws a diamond shaped focal point. Removes the datapoints for the focal point from
        the pixel_array used for the background. This creates the illusion of the focal point
        obscuring its background.

        Focal offset creates the illusion of the focal point being in front of the background.
        To achieve this effect, the focal point is shifted slightly to the center of vision
        relative to the background. The brain interprets this as the object being closer.
        """

        if eye == 'left':
            color = dpg.get_value('color_left')
            bg_offset = int(self.bg_offset * -0.5) # bg moves further apart
            focal_offset = int(self.focal_offset * 0.5) # focal is moved closer

        if eye == 'right':
            color = dpg.get_value('color_right')
            bg_offset = int(self.bg_offset * 0.5)
            focal_offset = int(self.focal_offset * -0.5)

        if eye not in ['left', 'right']:
            raise ValueError("Wrong value given for 'eye'. Accepted values are 'left' and 'right'.")

        focal_array = np.zeros((self.focal_pixel_count, self.focal_pixel_count), dtype=int)
        focal_loc = {
            'top': {'x': 0.5, 'y': 0.25 },
            'bottom': {'x': 0.5, 'y': 0.75 },
            'left': {'x': 0.25, 'y': 0.5 },
            'right': {'x': 0.75, 'y': 0.5 }
        }
        x_min = int(self.pixel_count * focal_loc[self.focal_position]['x'])
        y_min = int(self.pixel_count * focal_loc[self.focal_position]['y']) - int(self.focal_pixel_count / 2)

        diamond_builder = []
        step = round(self.focal_pixel_count / (self.focal_pixel_count/2))
        [diamond_builder.append(i) for i in range(0, self.focal_pixel_count, step)]
        diamond_builder.extend(list(diamond_builder[::-1]))

        for y, pixels in enumerate(diamond_builder):
            center = round(self.focal_size / 2)     # find middle of array
            y = y_min + y                           # == y_min + current row
            x = int(x_min - pixels / 2)             # half of the pixels to be drawn
                                                    # must be drawn left of center
            for x in range(x, x+pixels):
                self.mask_array[x+focal_offset, y] = 1           # draw the diamond in the mask array
                if self.focal_pixel_rng[x, y] == 1:
                    draw_x = (x + bg_offset + focal_offset) * self.pixel_size
                    draw_y = y * self.pixel_size
                    dpg.draw_rectangle((draw_x, draw_y), (draw_x+self.pixel_size, draw_y+self.pixel_size), fill=color, color=color)

        self.bg_pixel_array = self.bg_pixel_array - self.mask_array   # cut the mask array out of the bg array

    def draw_bg(self, eye):
        """Draws the background from a randomly generated self.bg_pixel_array. Draw_focal needs to be called beforehand
        so the pixels in the focal point are removed from the background array."""

        if eye == 'left':
            color = dpg.get_value('color_left')
            bg_offset = int(self.bg_offset * -0.5)

        if eye == 'right':
            color = dpg.get_value('color_right')
            bg_offset = int(self.bg_offset * 0.5)

        if eye not in ['left', 'right']:
            raise ValueError("Wrong value given for 'eye'. Accepted values are 'left' and 'right'.")

        pixels = (self.bg_pixel_array > 0).nonzero()
        coords = zip(pixels[0], pixels[1])
        for x, y in coords:
            x = (x + bg_offset) * self.pixel_size
            y = y * self.pixel_size
            dpg.draw_rectangle((x, y), (x+self.pixel_size, y+self.pixel_size), fill=color, color=color)

        # cleanup arrays for second pass of drawing
        self.bg_pixel_array = self.init_pixel_array
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)

    def draw(self):
        """Takes care of drawing two anaglyph images with focal points and backgrounds correctly spaced.
        Can be used by DrawQueue to create a queued draw_node."""

        helpers.debugger(f'drawing {self.node_uuid}')

        # initialize random arrays for every draw_node
        self.node_uuid = str(uuid.uuid4())
        self.focal_position = np.random.choice(['top', 'bottom', 'left', 'right'])
        self.rng = np.random.default_rng()
        self.init_pixel_array = self.rng.choice([0, 1], size=(self.pixel_count, self.pixel_count))
        self.bg_pixel_array = self.init_pixel_array
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)
        self.focal_pixel_rng = self.rng.choice([0, 1], size=(self.pixel_count, self.pixel_count))

        def draw_eye(eye):
            self.draw_focal(eye)
            self.draw_bg(eye)

        with dpg.draw_node(tag=self.node_uuid, parent=self.parent):
            dpg.hide_item(self.node_uuid)
            draw_eye('left')
            draw_eye('right')

        # return a namedtuple for legibility in other places
        drawing = namedtuple('Drawing', ['node_uuid', 'focal_position'])
        return drawing(self.node_uuid, self.focal_position)

    def check_answer(self, answer):
        """Checks the given answer for correctness. In this case: did user indicate the right
        position of the focal point?"""
        if answer == self.focal_position:
            return True
        else:
            return False


class DepthPerception():
    def __init__(self):
        self.object_shape = ''
        self.object_count = ''

class Recognition():
    """Game where subject sees a number of objects and has to reproduce them
    through keyboard input as quickly as possible."""
    def __init__(self):
        self.object_shape = ''
        self.object_count = ''

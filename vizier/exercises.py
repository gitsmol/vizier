import dearpygui.dearpygui as dpg
import numpy as np
from collections import namedtuple
from . import helpers
from . import imagemap
from time import sleep

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

    def __init__(self, drawlist, **kwargs):
        self.node_uuid = dpg.generate_uuid()
        self.drawlist_uuid = drawlist
        self.bg_offset = kwargs.get('bg_offset', 0)
        self.focal_offset = kwargs.get('focal_offset', 2)
        self.size = kwargs.get('size', dpg.get_value('anaglyph_size'))
        self.drawlist_x_center = dpg.get_item_width(self.drawlist_uuid) / 2 - self.size / 2
        self.drawlist_y_center = dpg.get_item_height(self.drawlist_uuid) / 2 - self.size / 2
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
                    draw_x = (x + bg_offset + focal_offset) * self.pixel_size + self.drawlist_x_center
                    draw_y = y * self.pixel_size + self.drawlist_y_center
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
            x = (x + bg_offset) * self.pixel_size + self.drawlist_x_center
            y = y * self.pixel_size + self.drawlist_y_center
            dpg.draw_rectangle((x, y), (x+self.pixel_size, y+self.pixel_size), fill=color, color=color)

        # cleanup arrays for second pass of drawing
        self.bg_pixel_array = self.init_pixel_array
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)

    def draw(self):
        """Takes care of drawing two anaglyph images with focal points and backgrounds correctly spaced.
        Can be used by DrawQueue to create a queued draw_node."""

        helpers.debugger(f'drawing {self.node_uuid}')

        # initialize random arrays for every draw_node
        self.node_uuid = str(dpg.generate_uuid())
        self.focal_position = np.random.choice(['top', 'bottom', 'left', 'right'])
        self.rng = np.random.default_rng()
        self.init_pixel_array = self.rng.choice([0, 1], size=(self.pixel_count, self.pixel_count))
        self.bg_pixel_array = self.init_pixel_array
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)
        self.focal_pixel_rng = self.rng.choice([0, 1], size=(self.pixel_count, self.pixel_count))

        def draw_eye(eye):
            self.draw_focal(eye)
            self.draw_bg(eye)

        with dpg.draw_node(tag=self.node_uuid, parent=self.drawlist_uuid):
            dpg.hide_item(self.node_uuid)
            draw_eye('left')
            draw_eye('right')

        # return a namedtuple for legibility in other places
        drawing = namedtuple('Drawing', ['node_uuid', 'focal_position'])
        return drawing(self.node_uuid, self.focal_position)

class DepthPerception():
    def __init__(self):
        self.object_shape = ''
        self.object_count = ''

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
        self.display_time_secs = kwargs.get('delay', 0.7)
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
        rng = np.random.default_rng()
        node_uuid = str(dpg.generate_uuid())
        arrow_direction = rng.choice(['top', 'bottom', 'left', 'right'])
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

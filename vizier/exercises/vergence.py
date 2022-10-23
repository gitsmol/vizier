import dearpygui.dearpygui as dpg
import numpy as np
from collections import namedtuple
from ..modules import helpers

ar_down = np.array([
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0]
])

class Anaglyph:
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
        self.bg_offset = kwargs.get("bg_offset", 0)
        self.focal_offset = kwargs.get("focal_offset", 2)
        self.size = kwargs.get("size", 300)
        self.drawlist_x_center = (
            dpg.get_item_width(self.drawlist_uuid) / 2 - self.size / 2
        )
        self.drawlist_y_center = (
            dpg.get_item_height(self.drawlist_uuid) / 2 - self.size / 2
        )
        self.pixel_size = kwargs.get("pixel_size", 3)
        self.focal_size_rel = kwargs.get("focal_size_rel", .35)
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

        if eye == "left":
            color = dpg.get_value("color_left")
            bg_offset = int(self.bg_offset * -0.5)  # bg moves further apart
            focal_offset = int(self.focal_offset * 0.5)  # focal is moved closer

        if eye == "right":
            color = dpg.get_value("color_right")
            bg_offset = int(self.bg_offset * 0.5)
            focal_offset = int(self.focal_offset * -0.5)

        if eye not in ["left", "right"]:
            raise ValueError(
                "Wrong value given for 'eye'. Accepted values are 'left' and 'right'."
            )

        focal_loc = {
            "top": {"x": 0.5, "y": 0.25},
            "bottom": {"x": 0.5, "y": 0.75},
            "left": {"x": 0.25, "y": 0.5},
            "right": {"x": 0.75, "y": 0.5},
        }
        x_min = int(self.pixel_count * focal_loc[self.focal_position]["x"])
        y_min = int(self.pixel_count * focal_loc[self.focal_position]["y"]) - int(
            self.focal_pixel_count / 2
        )

        # create a matrix containing the diamond shape focal point
        diamond_builder = []
        # step means: how many extra pixels to draw on each subsequent row of the matrix
        # by incrementing the amount of pixels to draw, a triangle shape is created
        step = round(self.focal_pixel_count / (self.focal_pixel_count / 2))
        # create a list of the number of pixels to draw on each row
        [diamond_builder.append(i) for i in range(0, self.focal_pixel_count, step)]
        # finally, extend the list with itself reversed, 
        # effectively appending an upside down triangle
        diamond_builder.extend(list(diamond_builder[::-1]))

        for y, pixels in enumerate(diamond_builder):
            center = round(self.focal_size / 2)  # find middle of array
            y = y_min + y  # == y_min + current row
            x = int(x_min - pixels / 2)  # half of the pixels to be drawn
            # must be drawn left of center
            for x in range(x, x + pixels):
                self.mask_array[x + focal_offset, y] = 1  # draw the diamond in the mask array
                if self.focal_pixel_rng[x, y] == 1:
                    draw_x = (
                        x + bg_offset + focal_offset
                    ) * self.pixel_size + self.drawlist_x_center
                    draw_y = y * self.pixel_size + self.drawlist_y_center
                    dpg.draw_rectangle(
                        (draw_x, draw_y),
                        (draw_x + self.pixel_size, draw_y + self.pixel_size),
                        fill=color,
                        color=color,
                    )

        self.bg_pixel_array = (
            self.bg_pixel_array - self.mask_array
        )  # cut the mask array out of the bg array

    def draw_bg(self, eye):
        """Draws the background from a randomly generated self.bg_pixel_array. Draw_focal needs to be called beforehand
        so the pixels in the focal point are removed from the background array."""

        if eye == "left":
            color = dpg.get_value("color_left")
            bg_offset = int(self.bg_offset * -0.5)

        if eye == "right":
            color = dpg.get_value("color_right")
            bg_offset = int(self.bg_offset * 0.5)

        if eye not in ["left", "right"]:
            raise ValueError(
                "Wrong value given for 'eye'. Accepted values are 'left' and 'right'."
            )

        pixels = (self.bg_pixel_array > 0).nonzero()
        coords = zip(pixels[0], pixels[1])
        for x, y in coords:
            x = (x + bg_offset) * self.pixel_size + self.drawlist_x_center
            y = y * self.pixel_size + self.drawlist_y_center
            dpg.draw_rectangle(
                (x, y),
                (x + self.pixel_size, y + self.pixel_size),
                fill=color,
                color=color,
            )

        # cleanup arrays for second pass of drawing
        self.bg_pixel_array = self.init_pixel_array
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)

    def draw(self):
        """Takes care of drawing two anaglyph images with focal points and backgrounds correctly spaced.
        Can be used by DrawQueue to create a queued draw_node."""

        helpers.debugger(f"drawing {self.node_uuid}")

        # initialize random arrays for every draw_node
        self.node_uuid = str(dpg.generate_uuid())
        self.focal_position = np.random.choice(["top", "bottom", "left", "right"])
        self.rng = np.random.default_rng()
        self.init_pixel_array = self.rng.choice(
            [0, 1], size=(self.pixel_count, self.pixel_count)
        )
        self.bg_pixel_array = self.init_pixel_array
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)
        self.focal_pixel_rng = self.rng.choice(
            [0, 1], size=(self.pixel_count, self.pixel_count)
        )

        def draw_eye(eye):
            self.draw_focal(eye)
            self.draw_bg(eye)

        with dpg.draw_node(tag=self.node_uuid, parent=self.drawlist_uuid):
            dpg.hide_item(self.node_uuid)
            draw_eye("left")
            draw_eye("right")

        # return a namedtuple for legibility in other places
        drawing = namedtuple("Drawing", ["node_uuid", "focal_position"])
        return drawing(self.node_uuid, self.focal_position)


def run(config):
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
        possible_answers = {
            "left": "left",
            "right": "right",
            "up": "top",
            "down": "bottom",
        }
        if key in possible_answers:
            helpers.debugger(f"current item: {queue.current_item}")
            result = possible_answers.get(key) == queue.current_item.focal_position
            session.add_result(result)

            if session.active:
                anaglyph.bg_offset = session.primary_param
                queue.add(anaglyph.draw())
                queue.next()

    session_config = config.get("Session")  # this config part is required
    exercise_config = config.get("Exercise", {})  # this config part is optional
    session = helpers.EvaluationSession(**session_config)
    queue = helpers.DrawQueue()
    viewp_h, viewp_w = dpg.get_viewport_height(), dpg.get_viewport_width()
    # create keypress handler for this evaluation
    with dpg.handler_registry(tag=session.handler_uuid):
        dpg.add_key_press_handler(callback=evaluate)

    with dpg.window(tag=session.win_uuid, width=viewp_w, height=viewp_h, **helpers.fixed_window):
        dpg.bind_item_theme(session.win_uuid, "exercise_theme")

        # basic buttons, timer etc
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_button(
                    tag="btn_close",
                    label="Close",
                    callback=session.end,
                    user_data=session.win_uuid,
                )
                dpg.add_text(
                    tag="txt_timer",
                    label="Time remaining",
                    source="str_time_remaining",
                    default_value="No time remaining.",
                )

        # All drawing is done within this drawlist.
        dpg.add_drawlist(
            tag=session.drawlist_uuid, width=viewp_w, height=viewp_h * 0.90
        )

        # Finally, create the anaglyph object and draw the first frame.
        anaglyph = Anaglyph(drawlist=session.drawlist_uuid, **exercise_config)

        queue.add(anaglyph.draw())
        queue.next()

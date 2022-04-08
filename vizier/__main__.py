import dearpygui.dearpygui as dpg
import random
import numpy as np

dpg.create_context()

# Some variables used throughout
fixed_window = {'no_title_bar': True, 'menubar': False, 'no_resize': True, 'no_move': True}
COLORS = {
    'red'   : (255,25, 25, 50),
    'green' : (85, 255, 0),
    'blue'  : (0, 38, 230, 100),
    'white' : (255, 255, 255),
    'black' : (0, 0, 0)
}

class Anaglyph():
    """
    Class to create anaglyph images. Each anaglyph consists of two instances of this class, i.e. Left() and Right().
    draw() creates the anaglyph background according to the kwargs defined in __init__.


    :param label: Give a unique label to this part of the anaglyph. Used to tag draw_nodes.
    :param bg_offset: Define drawing offset on x-axis for the background image.
    :param focal_offset: Define drawing offset on x-axis for the focal image.
    :param size: Size of one side of the image in pixels. Used for x and y size.
    :param pixel_size: Size of the individual squares ('pixels') drawn.
    :param focal_size: Size of the focal point.
    :param rng: Random state used by the RNG for the background image.
    :param rng_focal: Random state used by the RNG for the focal image.
    """

    def __init__(self, **kwargs):
        self.label = kwargs.get('label', 'no_label')
        self.bg_offset = kwargs.get('bg_offset', 0)
        self.focal_offset = kwargs.get('focal_offset', 0)
        self.size = dpg.get_value('anaglyph_size')
        self.pixel_size = dpg.get_value('anaglyph_pixel_size')
        self.focal_size_rel = dpg.get_value('anaglyph_focal_size')
        self.focal_size = self.size * self.focal_size_rel
        self.pixel_count = int(self.size / self.pixel_size)
        self.focal_pixel_count = int(self.focal_size / self.pixel_size)
        self.color = kwargs.get('color', COLORS['white'])
        self.rng = np.random.RandomState(kwargs.get('random_state', 0))
        self.rng_focal = np.random.RandomState(kwargs.get('random_state', 1))
        self.focal_position = kwargs.get('focal_position', 'left')
        self.pixel_array = self.rng.choice([0, 1], size=(self.pixel_count, self.pixel_count))
        self.mask_array = np.zeros((self.pixel_count, self.pixel_count), dtype=int)
        self.focal_pixel_rng = self.rng_focal.choice([0, 1], size=(self.pixel_count, self.pixel_count))


    def draw_focal(self):
        """Draws a diamond shaped focal point. Removes the datapoints for the focal point from
        the pixel_array used for the background. This creates the illusion of the focal point
        obscuring its background."""
        focal_array = np.zeros((self.focal_pixel_count, self.focal_pixel_count), dtype=int)
        focal_loc = {
            'top': {'x': 0.5, 'y': 0.25 },
            'bottom': {'x': 0.5, 'y': 0.75 },
            'left': {'x': 0.25, 'y': 0.5 },
            'right': {'x': 0.75, 'y': 0.5 }
        }
        x_min = int(self.pixel_count * focal_loc[self.focal_position]['x'])
        y_min = int(self.pixel_count * focal_loc[self.focal_position]['y']) - int(self.focal_pixel_count / 2)
        debugger(f'x_min: {x_min}, y_min: {y_min}')
        debugger(f'pixel count: {self.pixel_count}')
        debugger(f'pixel_array shape: {self.pixel_array.shape}')
        debugger(f'mask_array shape: {self.mask_array.shape}')
        debugger(f'focal pixel count: {self.focal_pixel_count}')
        debugger(f'focal_array shape: {focal_array.shape}')

        diamond_builder = []
        step = round(self.focal_pixel_count / (self.focal_pixel_count/2))
        [diamond_builder.append(i) for i in range(0, self.focal_pixel_count, step)]
        diamond_builder.extend(list(diamond_builder[::-1]))
        debugger(f'diamond_builder: \n{diamond_builder}')

        with dpg.draw_node(tag=f'{self.label}_focal'):
            dpg.hide_item(f'{self.label}_focal')
            for y, pixels in enumerate(diamond_builder):
                center = round(self.focal_size / 2)     # find middle of array
                y = y_min + y                              # == y_min + current row
                x = int(x_min - pixels / 2)    # half of the pixels to be drawn
                                                        # must be drawn left of center
                for x in range(x, x+pixels):
                    self.mask_array[x+self.focal_offset, y] = 1           # draw the diamond in a mask array
                    if self.focal_pixel_rng[x, y] == 1:
                        draw_x = (x + self.bg_offset + self.focal_offset) * self.pixel_size
                        draw_y = y * self.pixel_size
                        dpg.draw_rectangle((draw_x, draw_y), (draw_x+self.pixel_size, draw_y+self.pixel_size), fill=self.color, color=self.color)

        self.pixel_array = self.pixel_array - self.mask_array   # mask is 'cut out' of bg array

    def draw_bg(self):
        """Draws the background from a randomly generated self.pixel_array. Draw_focal needs to be called beforehand
        so the pixels in the focal point are removed from the background array."""
        debugger(f'pixel_array shape:\n{self.pixel_array.shape}')
        with dpg.draw_node(tag=self.label):
            dpg.hide_item(self.label)
            pixels = (self.pixel_array >0).nonzero()
            coords = zip(pixels[0], pixels[1])
            for x, y in coords:
                x = (x + self.bg_offset) * self.pixel_size
                y = y * self.pixel_size
                dpg.draw_rectangle((x, y), (x+self.pixel_size, y+self.pixel_size), fill=self.color, color=self.color)

    def draw(self):
        self.draw_focal()
        self.draw_bg()
        dpg.show_item(self.label)
        dpg.show_item(f'{self.label}_focal')

# TODO: create drawqueue class
# NOTE: - item, status (visible), parent
# NOTE: functions:
#       - add_to_queue
#       - pop_queue
#           - destroy previous
#           - show current
#           - create next


# class Square():
   # SHOULD REALLY MAKE OBJECTS IN CLASSES TO BE MOVED OR SOMETHING ABSTRACT THIS P1 stuff away...
   # TODO: use translation

def move_object(tag, app_data):
    get_config = dpg.get_item_configuration(tag)
    set_config = {}
    set_config['p1'] = get_config['p1']
    set_config['p2'] = get_config['p2']
    set_config['p3'] = get_config['p3']
    set_config['p4'] = get_config['p4']

    def translate_key(key_pressed):
        keys_translated = {
            265: 'up',
            264: 'down',
            263: 'left',
            262: 'right',
            256: 'escape',
            257: 'return',
            32: 'space'
        }

        if key_pressed in keys_translated:
            return keys_translated.get(key_pressed)
        else:
            return key_pressed

    key_translated = translate_key(app_data)

    if key_translated == "up":
        set_config['p1'][1] -= 1
        set_config['p2'][1] -= 1
        set_config['p3'][1] -= 1
        set_config['p4'][1] -= 1

    if key_translated == "down":
        set_config['p1'][1] += 1
        set_config['p2'][1] += 1
        set_config['p3'][1] += 1
        set_config['p4'][1] += 1

    if key_translated == "left":
        set_config['p1'][0] -= 1
        set_config['p2'][0] -= 1
        set_config['p3'][0] -= 1
        set_config['p4'][0] -= 1


    if key_translated == "right":
        set_config['p1'][0] += 1
        set_config['p2'][0] += 1
        set_config['p3'][0] += 1
        set_config['p4'][0] += 1

    dpg.set_value("response_indicator", f"key pressed: {key_translated} \n set_config = {set_config}")
    return set_config

def key_press(sender, app_data):
    set_config = move_object("diamond", app_data)
    dpg.configure_item("diamond", **set_config)

def draw_anaglyph():
    dpg.delete_item('excercise_graphics', children_only=True)
    with dpg.drawlist(tag='draw_anaglyph', label='draw_anaglyph', parent='excercise_graphics', width=600, height=650): # create drawing
        focal_position = np.random.choice(['top', 'bottom', 'left', 'right'])
        left_square = Anaglyph(
            **{'label' : 'left',
                'bg_offset' : 0,
                'focal_offset' : 1,
                'focal_position' : focal_position,
                'color': dpg.get_value('color_left')}
        )
        right_square = Anaglyph(
            **{'label' : 'right',
                'bg_offset' : 10,
                'focal_offset': -1,
                'focal_position' : focal_position,
                'color': dpg.get_value('color_right')}
        )
        left_square.draw()
        right_square.draw()


def launcher(sender, app_data):
    if sender == 'btn_configure':
        with dpg.window(tag='configure'):
            dpg.add_slider_int(label='Size', source='anaglyph_size', min_value=200, max_value=800)
            dpg.add_slider_int(label='Pixel size', source='anaglyph_pixel_size', min_value=1, max_value=10)
            dpg.add_slider_float(label='Focal point size', source='anaglyph_focal_size', min_value=0.1, max_value=0.5)

    if sender == 'btn_anaglyph':
        draw_anaglyph()

    if sender == 'btn_alignment':
        dpg.delete_item('excercise_graphics', children_only=True)
        with dpg.drawlist(tag='alignment_test', parent='excercise_graphics', width=200, height=200):
            dpg.draw_rectangle((0, 0), (51, 51), color=COLORS['blue'], thickness=5, tag="square")
            dpg.draw_quad((0, 25), (25, 50), (50, 25), (25, 0), color=COLORS['red'], thickness=2, tag='diamond')

    if sender == 'btn_calibrate' and dpg.does_item_exist('win_calibrate') == False:
        with dpg.window(tag='win_calibrate', pos=[200,50], width=500, height=500):
            # dpg.add_button(tag='btn_apply_calibration', label='Apply', callback=calibrate)
            dpg.add_button(tag='btn_swap_eyes', label='Swap left/right', callback=calibrate)
            with dpg.table(resizable=True, policy=4, scrollY=False, header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_color_picker(label='Left eye', source='color_left', alpha_bar=True, no_inputs=True, callback=calibrate)
                    dpg.add_color_picker(label='Right eye', source='color_right', alpha_bar=True, no_inputs=True, callback=calibrate)
            with dpg.drawlist(tag='draw_calibrate', width=300, height=200):
                dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
                dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')

def calibrate(sender, app_data):
    if sender == 'btn_swap_eyes':
        left = dpg.get_value('color_left')
        right = dpg.get_value('color_right')
        dpg.set_value('color_left', right)
        dpg.set_value('color_right', left)
    dpg.delete_item('draw_calibrate', children_only=True)
    dpg.draw_quad((0, 50), (50, 100), (100, 50), (50, 0), fill=dpg.get_value('color_left'), color=dpg.get_value('color_left'), thickness=0, parent='draw_calibrate')
    dpg.draw_quad((50, 50), (100, 100), (150, 50), (100, 0), fill=dpg.get_value('color_right'), color=dpg.get_value('color_right'), thickness=0, parent='draw_calibrate')


def translator(sender, app_data):
    if sender == 'parallax_translator':
        # dpg.apply_transform("left_focal", dpg.create_translation_matrix([app_data * -1, 0]))
        dpg.apply_transform("right_focal", dpg.create_translation_matrix([app_data * 1, 0]))
    if sender == 'x_translator':
        dpg.apply_transform("left", dpg.create_translation_matrix([app_data, 0]))

def debugger(debug_data):
    old_data = dpg.get_value('txt_debug')
    dpg.set_value('txt_debug', f'{debug_data}\n{old_data}')

# with dpg.handler_registry(tag='translators'):
    # dpg.add_key_press_handler(callback=key_press)

with dpg.value_registry(tag='value_anaglyph'):
    dpg.add_color_value(default_value=COLORS['blue'], tag='color_left')
    dpg.add_color_value(default_value=COLORS['red'], tag='color_right')
    dpg.add_int_value(default_value=500, tag='anaglyph_size')
    dpg.add_int_value(default_value=4, tag='anaglyph_pixel_size')
    dpg.add_float_value(default_value=0.25, tag='anaglyph_focal_size')

with dpg.value_registry(tag='value_translate'):
    dpg.add_int_value(default_value=0, tag='parallax_translation')
    dpg.add_int_value(default_value=0, tag='x_translation')
    dpg.add_int_value(default_value=0, tag='y_translation')
    dpg.add_string_value(default_value='', tag='txt_debug')

with dpg.window(tag="A_excerciser", pos=[600, 400]):
    dpg.add_text("Heb je op een knop gedrukt?", tag="response_indicator")
    dpg.add_text("arrow metadata", tag="arrow_metadata")


with dpg.window(tag="controls", pos=[600,0], width=300, height=300, **fixed_window):
    dpg.add_button(tag='btn_anaglyph', label='Anaglyph exercise', callback=launcher)
    dpg.add_button(tag='btn_configure', label='Anaglyph config', callback=launcher)
    dpg.add_button(tag='btn_alignment', label='Alignment excercise', callback=launcher)
    dpg.add_button(tag='btn_calibrate', label='Calibrate', callback=launcher)

    parallax_translator = dpg.add_slider_int(tag="parallax_translator", label="Parallax translation", width=100, min_value=-50, max_value=50, source='parallax_translation')
    dpg.set_item_callback('parallax_translator', translator)
    x_translator = dpg.add_slider_int(tag="x_translator", label="X translation", width=100, min_value=-50, max_value=50, source='x_translation', callback='translator')
    dpg.set_item_callback('x_translator', translator)
    y_translator = dpg.add_slider_int(tag="y_translator", label="Y translation", width=100, min_value=-50, max_value=50, source='y_translation')

with dpg.window(tag='debugger', pos=[600, 300], width=300, height=400, **fixed_window):
    dpg.add_text(source='txt_debug', wrap=280)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 1, category=dpg.mvThemeCat_Core)
dpg.bind_theme(global_theme)

dpg.add_window(tag="excercise_graphics",width=600, height=700, pos=[0, 0], **fixed_window)
dpg.create_viewport(title='Veni Vidi Vici', width=900, height=900)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_viewport_vsync(True)
# dpg.set_primary_window("Graphics", True)
dpg.start_dearpygui()
dpg.destroy_context()

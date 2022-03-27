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
    """
    def __init__(self, **kwargs):
        self.label = kwargs.get('label', 'no_label')
        self.offset_x = kwargs.get('offset_x', 0)
        self.focal_offset = kwargs.get('focal_offset', 0)
        self.size = kwargs.get('size', 500)
        self.pixel_size = kwargs.get('pixel_size', 10)
        self.focal_size = kwargs.get('focal_size',int(self.size/8))
        self.pixel_count = int(self.size / self.pixel_size)
        self.focal_pixel_count = int(self.focal_size / self.pixel_size)
        self.color = kwargs.get('color', COLORS['white'])
        self.rng = np.random.RandomState(kwargs.get('random_state', 0))
        self.rng_focal = np.random.RandomState(kwargs.get('random_state', 1))
        self.pixel_array = self.rng.choice([0, 1, 2], size=(self.pixel_count, self.pixel_count))
        self.focal_pixel_rng = self.rng_focal.choice([0, 1], size=(self.pixel_count, self.pixel_count))

    def add_focal(self):
        debugger(f'calling add_focal()')

        focal_array = np.zeros((self.focal_size, self.focal_size), dtype=int)
        focal_loc = {
            'top': {'x': 0.5, 'y': 0.15 }
        }
        position = 'top'
        x_min = int(self.size * focal_loc[position]['x']) - int(self.size / 2) + self.focal_offset
        y_min = int(self.size * focal_loc[position]['y']) - int(self.size / 2)

        debugger(f'focal_array shape:\n{focal_array.shape}')

        diamond_builder = []
        step = round(self.focal_size / (self.focal_size/2))
        [diamond_builder.append(i) for i in range(0, self.focal_size, step)]
        diamond_builder.extend(list(diamond_builder[::-1]))

        for y, pixels in enumerate(diamond_builder):
            center = round(self.focal_size / 2)
            y +- y_min
            x = int(center - pixels /2) + x_min
            for x in range(x, x+pixels):
                # focal_array[y, x] = self.focal_pixel_rng[y, x]
                self.pixel_array[y, x] = self.focal_pixel_rng[y, x]

    def draw(self):
        debugger(f'pixel_array shape:\n{self.pixel_array.shape}')
        self.add_focal()
        with dpg.draw_node(tag=self.label):
            for i, row_ in enumerate(self.pixel_array):
                x = (i * self.pixel_size) + self.offset_x
                for j, rand_value in enumerate(row_):
                    y = (j * self.pixel_size)
                    if rand_value == 1:
                        dpg.draw_rectangle((x, y), (x+self.pixel_size, y+self.pixel_size), fill=self.color, color=self.color)

    def draw_focal(self, parallax_factor=1, mask=False):
        if mask ==True:
            node_name = f'{self.label}_focalmask'
        else:
            node_name = f'{self.label}_focal'
        with dpg.draw_node(tag=node_name):
            parallax_factor = 1
            focal_pixels_x = self.pixel_count / 8    # relative size of the focal diamond
            pixels_in_diamond = list(range(0, int(focal_pixels * 2)))   # create a list for
            pixels_in_diamond.extend(list(squares_in_diamond[::-1]))       # nr of sq per row
            center_x = round((self.offset_x +             # start at the offset
                        focal_pixels_x *           # and take max width of diamond
                        self.pixel_size * 2 *      # multiply by size of pixels * 2
                        parallax_factor), 0)            # finally factor in parallax
            for row, pixels in enumerate(squares_in_diamond):  # start new row
                x = center_x - self.pixel_size * pixels
                y = self.pixel_size * row
                for i in range(0, pixels * 2):     # draw all squares in row
                    x += self.pixel_size
                    rand_value = self.pixel_array[row, i]
                    if rand_value == 1:
                        dpg.draw_rectangle((x, y), (x+self.pixel_size, y+self.pixel_size), fill=self.color, color=self.color)

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

def launcher(sender, app_data):
    if sender == 'btn_anaglyph':
        dpg.delete_item('excercise_graphics', children_only=True)
        with dpg.drawlist(tag='draw_anaglyph', label='draw_anaglyph', parent='excercise_graphics', width=600, height=650): # create drawing
            left_square = Anaglyph(
                **{'label' : 'left',
                    'size': 300,
                    'pixel_size': 2,
                    'color': dpg.get_value('color_left')}
            )
            right_square = Anaglyph(
                **{'label' : 'right',
                    'size': 300,
                    'offset_x' : 10,
                    'focal_offset': 2,
                    'pixel_size': 2,
                    'color': dpg.get_value('color_right')}
            )
            left_square.draw()
            right_square.draw()
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
                    dpg.add_color_picker(label='Left eye', source='color_left', alpha_bar=True, no_inputs=True)
                    dpg.add_color_picker(label='Right eye', source='color_right', alpha_bar=True, no_inputs=True)

def calibrate(sender, app_data):
    if sender == 'btn_swap_eyes':
        left = dpg.get_value('color_left')
        right = dpg.get_value('color_right')
        dpg.set_value('color_left', right)
        dpg.set_value('color_right', left)

def translator(sender, app_data):
    if sender == 'parallax_translator':
        dpg.apply_transform("left_focal", dpg.create_translation_matrix([app_data, 0]))
    if sender == 'x_translator':
        dpg.apply_transform("left", dpg.create_translation_matrix([app_data, 0]))

def debugger(debug_data):
    old_data = dpg.get_value('txt_debug')
    dpg.set_value('txt_debug', f'{debug_data}\n{old_data}')

# with dpg.handler_registry(tag='translators'):
    # dpg.add_key_press_handler(callback=key_press)

with dpg.value_registry():
    dpg.add_int_value(default_value=0, tag='parallax_translation')
    dpg.add_int_value(default_value=0, tag='x_translation')
    dpg.add_int_value(default_value=0, tag='y_translation')
    dpg.add_color_value(default_value=COLORS['blue'], tag='color_left')
    dpg.add_color_value(default_value=COLORS['red'], tag='color_right')
    dpg.add_string_value(default_value='', tag='txt_debug')

with dpg.window(tag="A_excerciser", pos=[600, 400]):
    dpg.add_text("Heb je op een knop gedrukt?", tag="response_indicator")
    dpg.add_text("arrow metadata", tag="arrow_metadata")


with dpg.window(tag="controls", pos=[600,0], width=300, height=300, **fixed_window):
    dpg.add_button(tag='btn_anaglyph', label='Anaglyph config', callback=launcher)
    dpg.add_button(tag='btn_alignment', label='Alignment excercise', callback=launcher)
    dpg.add_button(tag='btn_calibrate', label='Calibrate', callback=launcher)

    parallax_translator = dpg.add_slider_int(tag="parallax_translator", label="Parallax translation", width=100, min_value=-50, max_value=50, source='parallax_translation')
    dpg.set_item_callback('parallax_translator', translator)
    x_translator = dpg.add_slider_int(tag="x_translator", label="X translation", width=100, min_value=-50, max_value=50, source='x_translation', callback='translator')
    dpg.set_item_callback('x_translator', translator)
    y_translator = dpg.add_slider_int(tag="y_translator", label="Y translation", width=100, min_value=-50, max_value=50, source='y_translation')

with dpg.window(tag='debugger', pos=[600, 300], width=300, height=400, **fixed_window):
    dpg.add_text(source='txt_debug', wrap=280)

dpg.add_window(tag="excercise_graphics",width=600, height=700, pos=[0, 0], **fixed_window)
dpg.create_viewport(title='Veni Vidi Vici', width=900, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_viewport_vsync(True)
# dpg.set_primary_window("Graphics", True)
dpg.start_dearpygui()
dpg.destroy_context()

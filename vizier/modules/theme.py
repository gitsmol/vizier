import dearpygui.dearpygui as dpg
from . import helpers
import yaml

COLORS = {
    'red'   : (255,25, 25, 50),
    'green' : (85, 255, 0),
    'blue'  : (0, 38, 230, 100),
    'white' : (255, 255, 255),
    'black' : (0, 0, 0)
}

# color blind safe colors defined by Bang Wong:
# https://www.nature.com/articles/nmeth.1618
SAFE_COLORS_WONG = {
    'red'    : (213, 94, 0),
    'green'  : (0, 157, 115),
    'blue'   : (86,180,233),
    'yellow' : (240, 228, 66),
    'orange' : (230, 159, 0),
    'purple' : (204, 121, 167),
    'black'  : (0, 0, 0)
}

# color blind safe colors defined by Paul Tol:
# https://personal.sron.nl/~pault/
# TODO move to separate colors.py
SAFE_COLORS_TOL = {
    'paleblue'  : (187, 204, 238),
    'blue'      : (68, 119, 170),
    'darkblue'  : (34, 34, 85),
    'night'     : (0, 6, 136),
    'palecyan'  : (204, 238, 255),
    'cyan'      : (102, 204, 238),
    'darkcyan'  : (34, 85, 85),
    'palegreen' : (204, 221, 170),
    'green'     : (34, 136, 51),
    'darkgreen' : (34, 85,34),
    'lightyellow': (238,204,102),
    'paleyellow': (238, 238, 187),
    'yellow'    : (204, 187, 68),
    'darkyellow': (102, 102, 51),
    'lightred'  : (255, 204, 204),
    'red'       : (238, 102, 119),
    'darkred'   : (102, 51, 51),
    'purple'    : (170, 51, 119),
    'palegrey'  : (221, 221, 221),
    'grey'      : (187, 187, 187),
    'darkgrey'  : (85, 85, 85),
    'lightblack': (26, 26, 26),
    'black'     : (0, 0, 0),
}

def initialize():
    with open('./vizier/config/config.yaml') as config_file:
        config = yaml.safe_load(config_file)

    # themes, fonts
    with dpg.theme(tag='exercise_theme') as exercise_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 1, category=dpg.mvThemeCat_Core)

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            # background colors
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, SAFE_COLORS_TOL['lightblack'], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SAFE_COLORS_TOL['darkgrey'], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SAFE_COLORS_TOL['darkgrey'], category=dpg.mvThemeCat_Core)

            # item colors
            dpg.add_theme_color(dpg.mvThemeCol_Button, SAFE_COLORS_TOL['darkgrey'], category=dpg.mvThemeCat_Core)

            # dpg.add_theme_color()
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2, category=dpg.mvThemeCat_Core)
    dpg.bind_theme(global_theme)

    with dpg.font_registry():
        font_default = dpg.add_font("vizier/assets/fonts/Roboto/Roboto-Regular.ttf", 16)
        font_default_hidpi = dpg.add_font("vizier/assets/fonts/Roboto/Roboto-Regular.ttf", 32)
        font_dyslexic = dpg.add_font("/Users/nme/Tresors/Code/Python/dear_atrac/assets/fonts/OpenDyslexic 3 Beta/OpenDyslexic3-Regular.ttf", 16)
        font_dyslexic_hidpi = dpg.add_font("/Users/nme/Tresors/Code/Python/dear_atrac/assets/fonts/OpenDyslexic 3 Beta/OpenDyslexic3-Regular.ttf", 16)

    # dpg.bind_font(font_dyslexic)

    if config['application']['hidpi'] == True:
        dpg.set_global_font_scale(0.5)
        dpg.bind_font(font_default_hidpi)
    else:
        dpg.bind_font(font_default)

    # set image path to walk through
    image_path = config['application']['image_path']

    # add all png images in image_path to texture registry
    with dpg.texture_registry(show=False, tag='textures'):
        for imagefile in helpers.dirwalk(image_path):
            if imagefile.suffix == '.png':
                width, height, channels, data = dpg.load_image(str(imagefile))
                dpg.add_static_texture(width, height, data, label=str(imagefile.name), tag=str(imagefile.name))

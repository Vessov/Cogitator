import pyray as pr
import json
import argparse
from outStruct import CanticleOutput, BroadcastOutput

parser = argparse.ArgumentParser(description="Cogitator background/graphical effect")
parser.add_argument("-b", action="store_false",
                     help="turn background semi-transparent. Prioritized over fullscreen",
                     dest="background")
parser.add_argument("-c", choices=["teal", "navy", "green", "red", "white", "yellow"], default="teal", 
                    help="select display color", dest="color",
                    nargs='?', const='teal')
parser.add_argument("-f", action="store_true", help="select if the Cogitator should be displayed full screen (without the 1 pixel line around). Mutually exclusive with background transparency", 
                    dest="fullscreen")
 
# parser.print_help()
settings = vars(parser.parse_args())

# silence the logger output to only warnings
pr.set_trace_log_level(pr.TraceLogLevel.LOG_WARNING)

# set the standard config flags
pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_TOPMOST)
pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_UNDECORATED)

# this flag has to be set before the window initialization
if settings["background"] is False:
    pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_TRANSPARENT)

# window initialization
pr.init_window(10, 10, "Sanctified Cogitator")
pr.set_window_position(0, 0)
pr.set_target_fps(60)

# getting the screen dimensions
screen_height = pr.get_monitor_height(0)
screen_width = pr.get_monitor_width(0)

# this flag has to be set after window initialization, since it relies on screen size
if settings["fullscreen"] is True and not settings["background"] is False:
    pr.set_config_flags(pr.ConfigFlags.FLAG_FULLSCREEN_MODE)
    pr.set_window_size(screen_width, screen_height)

else:
    # position set with 1 pixel difference, due to raylib defaulting to fullscreen
    # if the dimensions are the same as screen size; fullscreen prevents window transparency
    pr.set_window_position(1, 1)
    pr.set_window_size(screen_width - 1, screen_height - 1)

# disabling and hiding cursor
pr.disable_cursor()
pr.hide_cursor()

# used colors
background_transparent = [0, 0, 0, 140]
background_opaque = [0, 0, 0, 255]

colors = {"darkteal": [20, 239, 255, 20],
          "teal": [20, 239, 255, 120],
          "darknavy": [0, 0, 214, 40],
          "navy": [0, 0, 214, 160],
          "darkgreen": [29, 173, 0, 40],
          "green": [29, 173, 0, 160],
          "darkred": [199, 0, 0, 40],
          "red": [199, 0, 0, 175],
          "darkwhite": [255, 255, 255, 25],
          "white": [255, 255, 255, 150],
          "darkyellow": [210, 200, 0, 25],
          "yellow": [210, 200, 0, 160]}


# used variables
FPS_counter = 0
init_flag = True

# positional variables
skull_pos = pr.Vector3(0, -5, 0)
noosphere_font_size = screen_height/30
output_font_size = screen_height/45

# getting the selected color
# color = eval(settings["color"])
# darkcolor = eval("dark" + settings["color"])
color = colors[settings["color"]]
darkcolor = colors["dark" + settings["color"]]


# loading used objects
skull = pr.load_model(".\models\skull_simple_thin.obj")
noosphere_font = pr.load_font(rf".\fonts\films.EXH.ttf")
canticles_font = pr.load_font(rf".\fonts\films.EXL.ttf")
broadcast_font = pr.load_font(rf".\fonts\setbackt.ttf")

# loading incantations file
with open("incantations.json", "r") as file:
    incantations = json.load(file)

# parsing incantation variables
init_messages = incantations["initialization"]
imperatives = incantations["imperatives"]
canticles = incantations["canticles"]

# setting 3D camera for skull logo rotation
camera = pr.Camera3D([18.0, 16.0, 210.0], [0, 0, 0], [0.0, 2.0, 0.0], 45.0, 0)

# used functions
def calculate_init_mess_vectors(messList):

    vectors = []
    i = 100

    for message in messList:

        # measure initialization messages length, to correctly position them on the screen
        measure = pr.measure_text_ex(noosphere_font, message, noosphere_font_size, 2.0)
        length = pr.vector2_length(measure)

        # create vector position for all messages
        vector = pr.Vector2(screen_width/2 - length/2, screen_height/2 - ((noosphere_font_size*2) + i))
        vectors.append(vector)
        i -= 40

    return vectors

def draw_initialization_screen(messages, vectors, fps_counter):
    # get initialization messages
    m1_mess = messages[0]
    m2_mess = messages[1]
    m3_mess = messages[2]
    m4_mess = messages[3]
    m5_mess = messages[4]
    m6_mess = messages[5]

    # get initialiation message position vectors
    m1_vec = vectors[0]
    m2_vec = vectors[1]
    m3_vec = vectors[2]
    m4_vec = vectors[3]
    m5_vec = vectors[4]
    m6_vec = vectors[5]

    # set initialization flag
    flag = True

    # every 1.5 seconds add the next initialization message
    if fps_counter > 90:
        pr.draw_text_ex(noosphere_font, m1_mess, m1_vec, noosphere_font_size, 2.0, color)
    if fps_counter > 180:
        pr.draw_text_ex(noosphere_font, m2_mess, m2_vec, noosphere_font_size, 2.0, color)
    if fps_counter > 270:
        pr.draw_text_ex(noosphere_font, m3_mess, m3_vec, noosphere_font_size, 2.0, color)
    if fps_counter > 360:
        pr.draw_text_ex(noosphere_font, m4_mess, m4_vec, noosphere_font_size, 2.0, color)
    if fps_counter > 450:
        pr.draw_text_ex(noosphere_font, m5_mess, m5_vec, noosphere_font_size, 2.0, color)
    if fps_counter > 540:
        pr.draw_text_ex(noosphere_font, m6_mess, m6_vec, noosphere_font_size, 2.0, color)
    
    # after all messages has been added, wait another 1.5 second and set initialization flag to False
    if fps_counter > 630:
        flag = False
    
    return flag

def draw_bg_logo():
    pr.begin_mode_3d(camera)
    pr.draw_model_wires(skull, skull_pos, 0.15, darkcolor)
    pr.end_mode_3d()

# initialize Canticles
cantOut = CanticleOutput(color, screen_height, screen_width, output_font_size,
                         canticles_font, noosphere_font, canticles)

# initialize Imperatives
broadOut = BroadcastOutput(color, screen_height, screen_width, output_font_size,
                           broadcast_font, noosphere_font, imperatives)

# variables calculated at the start by custom functions
# (mainly dealing with positioning, timers, scrolling intervals, etc)
init_vec = calculate_init_mess_vectors(init_messages)

while not pr.window_should_close():
    FPS_counter += 1
    pr.update_camera(camera, pr.CAMERA_ORBITAL)
    pr.begin_drawing()

    if init_flag == False:
        pr.clear_background(background_transparent)
        draw_bg_logo()

        cantOut.draw_canticle_output(FPS_counter)
        broadOut.draw_broadcast_output(FPS_counter)

        if FPS_counter == 600:
            FPS_counter = 0

        # draw_broadcast_canticle_output_rec()
        
        
    else:
        pr.clear_background(background_opaque)
        init_flag = draw_initialization_screen(init_messages, init_vec, FPS_counter)
        
    
    pr.end_drawing()

pr.unload_model(skull)
pr.unload_font(noosphere_font)
pr.unload_font(canticles_font)
pr.unload_font(broadcast_font)
pr.close_window()

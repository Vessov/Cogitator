# Copyright (C) 2023  Tomasz Winecki (@Vessov)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/.


import pyray as pr
import textwrap
import random, string
import colorsys

# output canticle rectangle with scrolling text
class CanticleOutput:

    def __init__(self,
                 color: list,
                 screen_height: int,
                 screen_width: int,
                 out_font_size: float,
                 cant_font: pr.Font,
                 noos_font: pr.Font,
                 canticles: list ) -> None:
        
        self.color = color
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.out_font_size = out_font_size
        self.cant_font = cant_font
        self.noos_font = noos_font
        self.canticles = canticles
        self.midpoint = int(screen_width/2)

        # size and position variables
        self.rec_width = self.midpoint - 300
        self.rec_height = self.screen_height - 80
        self.cant_pos_x = self.midpoint + (self.midpoint - self.rec_width - 30)
        self.cant_pos_y = int(self.screen_height - (40 + self.out_font_size*2))
        self.cant_curr_threshold = 0
        self.cant_line_threshold = int(self.out_font_size + 5)
        self.cant_new_threshold = self.cant_line_threshold * 3
        self.cant_line_length = self.max_canticle_length()

        # drawing variables
        self.curr_cant_line_index = 0
        self.curr_cant = []
        self.cant_draw_text = []

    def max_canticle_length(self) -> int:
        # calculate max length (in chars) of string that will fit into canticles output rec
        checkstring = ""
        perm_chars = string.ascii_letters + string.punctuation + string.digits + " "

        for _ in range(200):

            char = random.choice(perm_chars)
            checkstring += char
            measure = pr.measure_text_ex(self.cant_font, checkstring,
                                         self.out_font_size, 2.0)
            length = pr.vector2_length(measure)

            if self.rec_width <= length:
                # return max line length with a little bit of space left
                max_length = len(checkstring) - 8
                return max_length

    def draw_cant_rec(self):
        # draw the output rectangle
        out_label_size = self.screen_height/41
        cant_rec_pos_x = self.midpoint + (self.midpoint - self.rec_width - 40)
        cant_label_pos = pr.Vector2(cant_rec_pos_x + 10, 50)

        cant_out_rec = pr.Rectangle(cant_rec_pos_x, 40, self.rec_width, self.rec_height)
        pr.draw_rectangle_rounded_lines(cant_out_rec, 0.1, 10, 2, self.color)
        pr.draw_text_ex(self.noos_font, "+++ Holy Guidance of the Omnissiah +++",
                        cant_label_pos, out_label_size, 2.0, self.color)
        
    def get_new_canticle(self, max_length: int) -> list:
        # gets new canticle from the canticles list, parses it so that it fits
        # the output max length; additional checks for quote author separation
        # to newline implemented this way to avoid improper formatting by textwrap

        new_input = self.canticles[random.randint(0, len(self.canticles) - 1)]
        cant_list = []
        separator = "|"

        def wrp_ln(line, length):
            # wrap single line to max length
            txt_wrap = textwrap.wrap(line, length)
            for wrap in txt_wrap:
                cant_list.append(wrap)
        
        def parse_sep(line):
            # parse line with separator present and pass results to wrp_ln
            new = line.split(sep=separator)
            for l in new:
                wrp_ln(l, max_length)

        if isinstance(new_input, list):
            for line in new_input:
                result = [char in line for char in separator]
                if True in result:
                    parse_sep(line)              
                else:
                    wrp_ln(line, max_length)
        
        else:
            result = [char in new_input for char in separator]
            if True in result:
                parse_sep(new_input)
            else:
                wrp_ln(new_input, max_length)
        
        return cant_list

    def add_new_cant_line(self, cant: list, index: int) -> int:
        # add new line from currently selected canticle to the output drawing list
        start_pos = pr.Vector2(self.cant_pos_x, self.cant_pos_y)
        line_add = [self.cant_font, cant[index],
                    start_pos, self.out_font_size, 2.0, self.color]
        line_draw = [line_add, self.cant_pos_y]
        self.cant_draw_text.append(line_draw)
        index += 1
        return index
    
    def upd_cant_posit(self, fps_counter: int):
        # update the position of all drawn lines, to get the scrolling effect
        if fps_counter%3 == 0:
            for line in self.cant_draw_text:
                upd_pos = line[1] - 1
                upd_pos_vec = pr.Vector2(self.cant_pos_x, upd_pos)
                line[0][2] = upd_pos_vec
                line[1] = upd_pos

                if line[1] < (55 + 1.5*self.out_font_size):
                    self.cant_draw_text.remove(line)

    def draw_canticle_output(self, fps_counter: int):
        
        self.draw_cant_rec()

        if self.curr_cant_line_index > (len(self.curr_cant) - 1):
            self.curr_cant = self.get_new_canticle(self.cant_line_length)
            self.curr_cant_line_index = 0
            self.cant_curr_threshold = self.cant_new_threshold
        
        else:
            self.upd_cant_posit(fps_counter)

            if (len(self.cant_draw_text) == 0) or (self.cant_draw_text[-1][1] <= (self.cant_pos_y - self.cant_curr_threshold)):
                upd_index = self.add_new_cant_line(self.curr_cant, self.curr_cant_line_index)
                self.curr_cant_line_index = upd_index
                self.cant_curr_threshold = self.cant_line_threshold
            
        for line in self.cant_draw_text:
            pr.draw_text_ex(*line[0])


# output imperatives rectangle with "typed" recieved text
class BroadcastOutput:

    def __init__(self,
                 color: list,
                 screen_height: int,
                 screen_width: int,
                 out_font_size: float,
                 broad_font: pr.Font,
                 noos_font: pr.Font,
                 imperatives: list) -> None:
        
        self.color = color
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.out_font_size = out_font_size
        self.broad_font = broad_font
        self.noos_font = noos_font
        self.imperatives = imperatives
        self.out_label_size = self.screen_height/41
        self.midpoint = int(screen_width/2)

        # size and position variables
        self.rec_width = self.midpoint - 300
        self.rec_height = self.screen_height - 80
        self.broad_pos_x = 50
        self.broad_pos_y = int(self.screen_height - (40 + self.out_font_size*2))
        self.broad_upper_threshold = int(60 + self.out_label_size*2)

        # drawing variables
        self.curr_imper = self.get_new_imperative()
        self.curr_imper_line_index = 0
        self.curr_imper_line = ""
        self.curr_imper_char_index = 0
        self.imper_draw_text = []
        self.timer = 0

        # flags
        self.move_up_flag = False
        self.wait_up_flag = False
        self.flash_up_flag = False
        self.clear_flag = False

        # color modification variablaes
        self.modifier = 20
        self.changed_bright = 0

    def draw_broad_rec(self):
        # draw the output rectangle
        broadcast_label_pos = pr.Vector2(65, 50)
        broadcast_out_rec = pr.Rectangle(40, 40, self.rec_width, self.rec_height)
        pr.draw_rectangle_rounded_lines(broadcast_out_rec, 0.1, 10, 2, self.color)
        pr.draw_text_ex(self.broad_font, "+++ Noosphere Broadcast Recieved +++",
                        broadcast_label_pos, self.out_label_size, 2.0, self.color)
        
    def get_new_imperative(self):
        # gets new imperative from imperatives list

        new_input = self.imperatives[random.randint(0, len(self.imperatives) - 1)]
        
        return new_input

    def add_new_imper_char(self):
        
        current_line = self.curr_imper_line
        char_index = self.curr_imper_char_index
        start_pos = pr.Vector2(self.broad_pos_x, self.broad_pos_y)

        if not self.curr_imper_char_index > (len(self.curr_imper[self.curr_imper_line_index]) - 1):
            self.curr_imper_line = current_line + self.curr_imper[self.curr_imper_line_index][self.curr_imper_char_index]
            line_add = [self.broad_font, self.curr_imper_line, start_pos,
                        self.out_font_size, 2.0, self.color]
            line_draw = [line_add, self.broad_pos_y]

            if len(self.imper_draw_text) > (self.curr_imper_line_index - 1) and not len(self.imper_draw_text) == 0:
                self.imper_draw_text[-1] = line_draw
            else:
                self.imper_draw_text.append(line_draw)

            self.curr_imper_char_index += 1
        
        else:
            self.curr_imper_line = ""
            self.curr_imper_char_index = 0
            self.curr_imper_line_index += 1
            self.move_line_up()           

    def move_line_up(self):
        step = int(self.out_font_size + 4)

        for line in self.imper_draw_text:
            upd_pos = line[1] - step
            upd_pos_vec = pr.Vector2(self.broad_pos_x, upd_pos)
            line[0][2] = upd_pos_vec
            line[1] = upd_pos

    def move_to_tresh(self):
        # print(f"In move to treshold, timer: {self.timer}")
        self.timer += 1
        up_line_pos = self.imper_draw_text[0][1]

        if (self.timer > 120) and (up_line_pos >= self.broad_upper_threshold) and (self.timer%4==0):
            self.move_line_up()
        
        if up_line_pos <= self.broad_upper_threshold:
            self.timer = 0
            self.move_up_flag = False
            self.wait_up_flag = True

    def wait_x_sec(self, sec, set_flash=False):
        # print(f"Timer entered: {self.timer}")
        self.timer += 1

        if self.timer >= (sec * 60):
            self.timer = 0
            self.wait_up_flag = False
            if set_flash:
                self.flash_up_flag = True

    def flash_up(self):
        self.timer += 1

        # if (self.imper_draw_text[0][0][5][3] < 255) and (self.imper_draw_text[0][0][5][3] > 40):
        #     self.changed_bright = self.imper_draw_text[0][0][5][3] + self.modifier
        
        if((self.imper_draw_text[0][0][5][3] + self.modifier) < 220) and (self.modifier > 0):
            self.changed_bright = self.imper_draw_text[0][0][5][3] + self.modifier
        elif((self.imper_draw_text[0][0][5][3] + self.modifier) > 60) and (self.modifier < 0):
            self.changed_bright = self.imper_draw_text[0][0][5][3] + self.modifier
        
        flash_color = [self.color[0], self.color[1], self.color[2], self.changed_bright]
        for line in self.imper_draw_text:
            line[0][5] = flash_color
        
        if self.timer%40==0:
            self.modifier *= -1
        
        if self.timer > (4*60):
            self.timer = 0
            self.modifier = abs(self.modifier)
            self.flash_up_flag = False
            self.clear_flag = True

    def draw_broadcast_output(self, fps_counter):

        self.draw_broad_rec()
        flags = [self.move_up_flag, self.wait_up_flag, self.flash_up_flag, self.clear_flag]

        if self.curr_imper_line_index > (len(self.curr_imper) - 1) and not (True in flags):
            self.move_up_flag = True
        elif not (True in flags):
            if fps_counter%4 == 0:
                self.add_new_imper_char()
        
        if self.move_up_flag:
            self.move_to_tresh()
        if self.wait_up_flag:
            self.wait_x_sec(4, True)
        if self.flash_up_flag:
            self.flash_up()

        if self.clear_flag:
            self.curr_imper = self.get_new_imperative()
            self.curr_imper_line_index = 0
            self.curr_imper_char_index = 0
            self.curr_imper_line = ""
            self.imper_draw_text = []
            self.move_up_flag = False
            self.wait_up_flag = False
            self.flash_up_flag = False
            self.clear_flag = False
        else:
            for line in self.imper_draw_text:
                pr.draw_text_ex(*line[0])


# output rectangle with stats (FPS, volume, color, etc) and additional effects
class StatsOutput:

    def __init__(self,
                 color: list,
                 screen_height: int,
                 screen_width: int,
                 out_font_size: float,
                 broad_font: pr.Font,
                 noos_font: pr.Font,
                 settings: dict) -> None:
        
        self.color = color
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.out_font_size = (out_font_size/1.5)
        self.broad_font = broad_font
        self.noos_font = noos_font
        self.sound = settings["sound"]
        self.volume = settings["volume"]
        self.praise = settings["praise"]
        self.midpoint = int(screen_width/2)
        self.monitor = pr.get_current_monitor()
        self.physical_width = pr.get_monitor_physical_width(self.monitor)
        self.physical_height = pr.get_monitor_physical_height(self.monitor)
        self.wavelength = self.get_wavelength()

        # size and position variables
        self.rec_width = (self.midpoint - (self.midpoint - 200))*2
        self.rec_height = int(self.screen_height/4)
        self.stat_pos_x = self.midpoint - (self.rec_width/2)
        self.stat_pos_y = self.screen_height - (self.rec_height + 40)

        # text variables
        self.main_stat_label = "+ Sanctified Cogitator Stats +" 
        # stored in class scope (instead of method) so it can be accessed to calculate correct position

        # calculate output position vectors
        self.positions = self.calc_pos_vec()

    def calc_pos_vec(self) -> dict:
        # calculate positions and vectors of all labels and variables displayed
        # in Stats Output Rectangle. Calculated separatly to avoid recalculation
        # every frame 

        positions ={}

        # position variables
        text_left_pos = self.stat_pos_x + 10
        text_right_pos = (self.rec_width + self.stat_pos_x) - (self.rec_width/2.5)
        text_up_pos = self.stat_pos_y + self.out_font_size
        text_shift = self.out_font_size + 10

        # calculate correct label position
        mes = pr.measure_text_ex(self.noos_font, self.main_stat_label, self.out_font_size*1.2, 2.0)
        length = pr.vector2_length(mes)
        m_s_l_beg = self.midpoint -  int(length/2)

        # prepare position vectors
        positions["main_stat_label_vec"] = pr.Vector2(m_s_l_beg, text_up_pos - 10)
        positions["stat_fps_label_vec"] = pr.Vector2(text_left_pos, text_up_pos + text_shift)
        positions["stat_fps_vec"] = pr.Vector2(text_right_pos, text_up_pos + text_shift)
        positions["size_label_vec"] = pr.Vector2(text_left_pos, text_up_pos + text_shift*2)
        positions["size_var_vec"] = pr.Vector2(text_right_pos, text_up_pos + text_shift*2)
        positions["screens_label_vec"] = pr.Vector2(text_left_pos, text_up_pos + text_shift*3)
        positions["screens_var_vec"] = pr.Vector2(text_right_pos, text_up_pos + text_shift*3)
        positions["wavelength_label_vec"] = pr.Vector2(text_left_pos, text_up_pos + text_shift*4)
        positions["wavelength_var_vec"] = pr.Vector2(text_right_pos, text_up_pos + text_shift*4)
        positions["volume_label_vec"] = pr.Vector2(text_left_pos, text_up_pos + text_shift*5)
        positions["volume_var_vec"] = pr.Vector2(text_right_pos, text_up_pos + text_shift*5)

        return positions

    def get_wavelength(self):
        # based on RGB values passed as color, calculate closest light wavelength
        red = self.color[0] / 255
        green = self.color[1] / 255
        blue = self.color[2] / 255
        if red == green == blue:
            # since white light contains full spectrum of wavelengths,
            # display ~ symbol to avoid defaulting to max value (650nm)
            return "~"
        else:
            hsv = colorsys.rgb_to_hsv(red, green, blue)
            hue = hsv[0] * 360
            wvlength = int(650 - 250 / 270 * hue)
            return wvlength

    def draw_stat_output(self, frametime):

        # object/data/label variables
        stat_rec = pr.Rectangle(self.stat_pos_x, self.stat_pos_y,
                                self.rec_width, self.rec_height)
        
        stat_fps_label = "Data Refresh Rate:"
        curr_fps = round((1/frametime), 1)
        stat_fps = f"{curr_fps} / 60 FPS"

        size_label = "Cogitator Display:"
        size_var = f"{self.physical_width} x {self.physical_height} mm"
        # size_var = f"{self.screen_width} x {self.screen_height} mm"

        screens_label = "Connected monitors:"
        screens_var = f"{pr.get_monitor_count()} pcs."

        wavelength_label = "Display wavelength:"
        wavelength_var = f"{self.wavelength} nm."

        main_stat_label_vec = self.positions["main_stat_label_vec"]
        stat_fps_label_vec = self.positions["stat_fps_label_vec"]
        stat_fps_vec = self.positions["stat_fps_vec"]
        size_label_vec = self.positions["size_label_vec"]
        size_var_vec = self.positions["size_var_vec"]
        screens_label_vec = self.positions["screens_label_vec"]
        screens_var_vec = self.positions["screens_var_vec"]
        wavelength_label_vec = self.positions["wavelength_label_vec"]
        wavelength_var_vec = self.positions["wavelength_var_vec"]


        pr.draw_rectangle_rounded_lines(stat_rec, 0.1, 10, 2, self.color)
        pr.draw_text_ex(self.noos_font, self.main_stat_label, main_stat_label_vec,
                        self.out_font_size*1.2, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, stat_fps_label, stat_fps_label_vec,
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, stat_fps, stat_fps_vec, 
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, size_label, size_label_vec,
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, size_var, size_var_vec,
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, screens_label, screens_label_vec,
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, screens_var, screens_var_vec,
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, wavelength_label, wavelength_label_vec,
                        self.out_font_size, 2.0, self.color)
        pr.draw_text_ex(self.broad_font, wavelength_var, wavelength_var_vec,
                        self.out_font_size, 2.0, self.color)



import math
import time
from dataclasses import dataclass
import serial
import yaml
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinter import filedialog as fd

ctk.set_appearance_mode('System')
ctk.set_default_color_theme('blue')

class App(ctk.CTk):
    WIDTH = 1000
    HEIGHT = 550

    def __init__(self):
        super().__init__()

        self.title('LinkedIn Park GUI')
        self.geometry(f'{App.WIDTH}x{App.HEIGHT}')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_editor = ctk.CTkFrame(master=self)
        self.frame_editor.grid(row=0, column=0, columnspan=15, sticky='nsew', padx=20, pady=20)

        self.editor_container = ctk.CTkCanvas(master=self.frame_editor, bg=self.frame_editor['background'], highlightthickness=0)
        self.scrollbar_editor = ctk.CTkScrollbar(master=self.frame_editor, orientation='horizontal', command=self.editor_container.xview)
        self.editor_canvas = ctk.CTkCanvas(master=self.editor_container, bg=self.frame_editor['background'], highlightthickness=0)
        self.editor_canvas.bind('<Configure>', lambda e: self.editor_container.configure(scrollregion=self.editor_container.bbox('all')))
        self.editor_container.create_window((0,0), window=self.editor_canvas, anchor='nw')
        self.editor_container.configure(xscrollcommand=self.scrollbar_editor.set)
        self.editor_container.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        self.scrollbar_editor.pack(side='bottom', fill='x', padx=5, pady=5)

        self.editor = Editor(self.editor_canvas)

        ctk.CTkLabel(master=self, text='zoom:', width=20).grid(row=1, column=0, sticky='w', padx=20, pady=(0, 20))
        self.zoom_out_button = ctk.CTkButton(master=self, text='-', width=30, command=self.zoom_out)
        self.zoom_out_button.grid(row=1, column=1, pady=(0, 20), sticky='w')
        self.zoom_in_button = ctk.CTkButton(master=self, text='+', width=30, command=self.zoom_in)
        self.zoom_in_button.grid(row=1, column=2, padx=20, pady=(0, 20), sticky='w')
        self.load_button = ctk.CTkButton(master=self, text='load', width=50, command=self.load)
        self.load_button.grid(row=1, column=3, pady=(0, 20), sticky='w')
        self.save_button = ctk.CTkButton(master=self, text='save', width=50, command=self.save)
        self.save_button.grid(row=1, column=4, padx=20, pady=(0, 20), sticky='w')
        ctk.CTkLabel(master=self, text='', width=10).grid(row=1, column=5, sticky='ew')
        ctk.CTkLabel(master=self, text='time signature:', width=120).grid(row=1, column=6, pady=(0, 20), sticky='e')
        self.time_signature_entry_1 = ctk.CTkEntry(master=self, width=30)
        self.time_signature_entry_1.insert(0, '4')
        self.time_signature_entry_1.grid(row=1, column=7, pady=(0, 20), sticky='e')
        ctk.CTkLabel(master=self, text='/', width=30).grid(row=1, column=8, pady=(0, 20), sticky='e')
        self.time_signature_entry_2 = ctk.CTkEntry(master=self, width=30)
        self.time_signature_entry_2.insert(0, '4')
        self.time_signature_entry_2.grid(row=1, column=9, pady=(0, 20), sticky='e')
        ctk.CTkLabel(master=self, text='tempo:', width=80).grid(row=1, column=10, pady=(0, 20), sticky='e')
        self.tempo_entry = ctk.CTkEntry(master=self, width=40)
        self.tempo_entry.insert(0, '120')
        self.tempo_entry.grid(row=1, column=11, pady=(0, 20), sticky='e')
        self.set_button = ctk.CTkButton(master=self, text='set', width=40, command=self.set_timing)
        self.set_button.grid(row=1, column=12, padx=20, pady=(0, 20), sticky='e')
        self.add_measure_button = ctk.CTkButton(master=self, text='add measure', width=60, command=self.editor.add_measure)
        self.add_measure_button.grid(row=1, column=13, pady=(0, 20), sticky='e')
        self.play_button = ctk.CTkButton(master=self, text='play', width=40, command=self.editor.play)
        self.play_button.grid(row=1, column=14, padx=20, pady=(0, 20), sticky='e')

        self.set_timing()

    def on_closing(self, event=0):
        self.destroy()

    def zoom(self, dir):
        self.editor.zoom(dir)
        button = self.zoom_in_button if dir=='in' else self.zoom_out_button

    def zoom_out(self):
        self.zoom('out')

    def zoom_in(self):
        self.zoom('in')
    
    def set_timing(self):
        try:
            self.editor.set_timing(int(self.time_signature_entry_1.get()), int(self.time_signature_entry_2.get()), int(self.tempo_entry.get()))
        except Exception as e:
            print(str(e))
    
    def load(self):
        filename = fd.askopenfilename()
        self.editor.load(filename)

    def save(self):
        filename = fd.askopenfilename()
        self.editor.save(filename)

NOTES = {
    1: 80,
    2: 330,
    3: 590,
    4: 830,
    5: 1140,
    6: 1480,
    7: 1820,
    8: 2160,
    9: 2450,
    10: 2800,
    11: 3220,
    12: 3640,
    13: 4000,
}

@dataclass
class Note:
    time: float
    position: int

@dataclass
class Trajectory:
    time: float
    position: int
    velocity: int
    acceleration: int

    def duration(self, last_position):
        return (abs(self.position-last_position)+self.velocity**2/self.acceleration)/self.velocity

class Editor:
    HEIGHT = 400
    ZOOM_MIN = 100.0
    ZOOM_MAX = 1000.0
    ZOOM_STEP = 100.0

    P_HEIGHT = 150.0
    P_SCALE = 150.0/4000.0
    V_HEIGHT = 100.0
    V_SCALE = 0.005
    A_HEIGHT = 100.0
    A_SCALE = 0.0005

    current_zoom = 100.0
    canvas: ctk.CTkCanvas
    events: list[Note | Trajectory]

    ts1 = 4
    ts2 = 4
    tempo = 120

    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas.config(height=self.HEIGHT)
        self.canvas.bind('<Button-1>', self.left_click_callback)
        self.canvas.bind('<Button-2>', self.right_click_callback) # mac trackpad right click
        self.canvas.bind('<Button-3>', self.right_click_callback)
        self.events = []
        
        self.song_duration = self.ts1*60/self.tempo
        self.instrument = Instrument('/dev/cu.usbserial-145130')

        self.draw()
    
    def __draw_axes(self, x, y, h, w, zero=1.0):
        t = 4
        self.canvas.create_line(x, y-t/2, x, y+h+t/2, fill='#C0C0C0', width=4)
        self.canvas.create_line(x-t/2, y+zero*h, x+w+t/2, y+zero*h, fill='#C0C0C0', width=4)

    def __generate_trajectory(self, t_f, x_f):
        # first try minimum acceleration
        v_m = 2.0*x_f/t_f
        a_m = 2.0*v_m/t_f
        if v_m > 100000.0:
            v_m = 100000.0
            a_m = v_m**2/(x_f-t_f*v_m)
        return (v_m, a_m)

    def __evaluate_trajectory(self, num_points, t_f, x_f, v_m, a_m):
        x_vals = []
        v_vals = []
        a_vals = []

        t_a = v_m/a_m
        time_step = t_f/num_points
        t = 0.0

        while t < t_a:
            x_vals.append(0.5*a_m*t**2)
            v_vals.append(a_m*t)
            a_vals.append(a_m)
            t += time_step
        while t < t_f - t_a:
            x_vals.append(0.5*a_m*t_a**2+v_m*(t-t_a))
            v_vals.append(v_m)
            a_vals.append(0)
            t += time_step
        while t < t_f:
            x_vals.append(0.5*a_m*t_a**2+v_m*(t_f-2*t_a)+v_m*(t-t_f+t_a)-0.5*a_m*(t-t_f+t_a)**2)
            v_vals.append(v_m-a_m*(t-t_f+t_a))
            a_vals.append(-a_m)
            t += time_step

        return (x_vals, v_vals, a_vals)

    def draw(self):
        self.canvas.delete('all')
        song_duration = self.song_duration
        if len(self.events) > 0:
            if self.events[-1].time > self.song_duration: song_duration = self.events[-1].time
        self.canvas.config(width=song_duration*self.current_zoom+50)

        # "constants"
        WIDTH=song_duration*self.current_zoom

        # draw note reference lines
        for n in NOTES:
            self.canvas.create_line(20, 20+NOTES[n]*Editor.P_SCALE, WIDTH+20, 20+NOTES[n]*Editor.P_SCALE, fill='#808080')
        
        # draw timing reference lines
        beat_duration = self.ts1*60/self.tempo/self.ts2/2
        t = 0
        i = 0
        while t < song_duration:
            if i%self.ts1*2 == 0:
                self.canvas.create_line(20+t*self.current_zoom, 20, 20+t*self.current_zoom, 20+self.P_HEIGHT, fill='#C0C0C0')
            elif i%2 == 0:
                self.canvas.create_line(20+t*self.current_zoom, 20, 20+t*self.current_zoom, 20+self.P_HEIGHT, fill='#606060')
            else:
                self.canvas.create_line(20+t*self.current_zoom, 20, 20+t*self.current_zoom, 20+self.P_HEIGHT, fill='#404040')
            t += beat_duration
            i += 1

        # draw graph axes
        self.__draw_axes(20, 20, Editor.P_HEIGHT, WIDTH, zero =0.0)
        self.__draw_axes(20, 40+Editor.P_HEIGHT, Editor.V_HEIGHT, WIDTH, zero=0.5)
        self.__draw_axes(20, 60+Editor.P_HEIGHT+Editor.V_HEIGHT, Editor.A_HEIGHT, WIDTH, zero=0.5)

        if len(self.events) == 0: return

        previous_x = 0

        # draw trajectories
        for event in self.events:
            if type(event) is Trajectory:
                x_vals, v_vals, a_vals = self.__evaluate_trajectory(event.duration(previous_x)*self.current_zoom, event.duration(previous_x), abs(event.position-previous_x), event.velocity, event.acceleration)
                sign = 1 if event.position >= previous_x else -1
                x_vals = [previous_x+sign*x for x in x_vals]
                v_vals = [sign*v for v in v_vals]
                a_vals = [sign*a for a in a_vals]

                last_t = event.time*self.current_zoom
                t = last_t
                for last_x, x in zip([previous_x] + x_vals, x_vals + [event.position]):
                    self.canvas.create_line(20+last_t, 20+last_x*Editor.P_SCALE, 20+t, 20+x*Editor.P_SCALE, fill='blue', width=2)
                    last_t = t
                    t += 1
                previous_x = event.position

                last_t = event.time*self.current_zoom
                t = last_t
                for last_v, v in zip([0] + v_vals, v_vals + [0]):
                    self.canvas.create_line(20+last_t, 40+Editor.P_HEIGHT+Editor.V_HEIGHT/2+last_v*Editor.V_SCALE, 20+t, 40+Editor.P_HEIGHT+Editor.V_HEIGHT/2+v*Editor.V_SCALE, fill='green', width=2)
                    last_t = t
                    t += 1

                last_t = event.time*self.current_zoom
                t = last_t
                for last_a, a in zip([0] + a_vals, a_vals + [0]):
                    self.canvas.create_line(20+last_t, 60+Editor.P_HEIGHT+Editor.V_HEIGHT+Editor.A_HEIGHT/2+last_a*Editor.A_SCALE, 20+t, 60+Editor.P_HEIGHT+Editor.V_HEIGHT+Editor.A_HEIGHT/2+a*Editor.A_SCALE, fill='yellow', width=2)
                    last_t = t
                    t += 1

        for event in self.events:
            if type(event) is Note:
                self.canvas.create_oval(20+event.time*self.current_zoom-4, 20+event.position*Editor.P_SCALE-4, 20+event.time*self.current_zoom+4, 20+event.position*Editor.P_SCALE+4, fill='#E0E0E0')

    def update_events(self):
        notes = [n for n in filter(lambda f: type(f) == Note, self.events)]
        notes.sort(key=lambda n: n.time)
        events = []
        if len(notes) > 0 and notes[0].position != 0:
            v, a = self.__generate_trajectory(notes[0].time - 0.05, notes[0].position)
            events.append(Trajectory(0.025, notes[0].position, int(v), int(a)))
        if len(notes) >= 1:
            for note, next_note in zip(notes[:-1], notes[1:]):
                events.append(note)
                if note.position - next_note.position == 0: continue
                v, a = self.__generate_trajectory(next_note.time - note.time - 0.05, abs(next_note.position - note.position))
                events.append(Trajectory(note.time+0.025, next_note.position, int(v), int(a)))
            events.append(next_note)
        if len(notes) > 0:
            v, a = self.__generate_trajectory(2, notes[-1].position)
            events.append(Trajectory(notes[-1].time+0.025, 0, int(v), int(a)))
        self.events = events

    def left_click_callback(self, event):
        if event.y > 20+Editor.P_HEIGHT or event.y < 20: return
        if event.x < 20: return
        y = min([NOTES[i]*self.P_SCALE+20 for i in NOTES], key=lambda x:abs(x-event.y))
        self.events.append(Note((event.x-20)/self.current_zoom, (y-20)/self.P_SCALE))
        self.update_events()
        self.draw()

    def right_click_callback(self, event):
        if event.y > 20+Editor.P_HEIGHT or event.y < 20: return
        if event.x < 20: return
        closest_note = min(filter(lambda f: type(f) == Note, self.events), key=lambda x:math.sqrt(abs(x.position*self.P_SCALE+20-event.y)**2+abs(x.time*self.current_zoom+20-event.x)**2))
        self.events.remove(closest_note)
        self.update_events()
        self.draw()

    def can_zoom(self, dir):
        if dir == 'in':
            return self.current_zoom + Editor.ZOOM_STEP <= Editor.ZOOM_MIN
        return self.current_zoom - Editor.ZOOM_STEP >= Editor.ZOOM_MAX

    def zoom(self, dir):
        if dir == 'in': self.current_zoom += Editor.ZOOM_STEP
        else: self.current_zoom -= Editor.ZOOM_STEP
        if self.current_zoom < Editor.ZOOM_MIN: self.current_zoom = Editor.ZOOM_MIN
        if self.current_zoom > Editor.ZOOM_MAX: self.current_zoom = Editor.ZOOM_MAX
        self.draw()
    
    def set_timing(self, ts1, ts2, tempo):
        for event in self.events:
            event.time *= self.tempo/tempo
        self.tempo = tempo
        self.ts1 = ts1
        self.ts2 = ts2
        self.update_events()
        self.draw()

    def add_measure(self):
        self.song_duration += self.ts1*60/self.tempo
        self.draw()

    def play(self):
        if len(self.events) > 0 and type(self.events[0] is Trajectory):
            self.instrument.move(self.events[0].position, self.events[0].velocity, self.events[0].acceleration)
        last_time = 0.0
        for event in self.events:
            time.sleep(event.time - last_time)
            last_time = event.time
            if type(event) is Trajectory:
                self.instrument.move(event.position, event.velocity, event.acceleration)
            else:
                self.instrument.pluck()

    def save(self, filename):
        try:
            data = {
                'ts1': self.ts1,
                'ts2': self.ts2,
                'tempo': self.tempo,
            }
            notes = []
            for note in filter(lambda e: type(e) is Note, self.events):
                n = 0
                for N in NOTES:
                    if NOTES[N] == note.position:
                        n = N
                        break
                notes.append([note.time, n])
            data.update({'notes': notes})
            
            with open(filename, 'w+') as f:
                yaml.dump(data, f)

        except Exception as e:
            print(str(e))

    def load(self, filename):
        try:
            data = {}
            with open(filename, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            self.ts1 = data['ts1']
            self.ts2 = data['ts2']
            self.temp = data['tempo']
            notes = data['notes']
            events = []
            for note in notes:
                events.append(Note(note[0], NOTES[note[1]]))
            self.events = events
        except Exception as e:
            print(str(e))
        self.update_events()
        self.draw()


class Instrument:
    BAUD = 115200

    def __init__(self, port):
        self.ser = serial.Serial(port, Instrument.BAUD)
        pass

    def move(self, p, v, a):
        self.ser.write(f'M {round(p)} {round(v)} {round(a)}\n'.encode('ASCII'))

    def pluck(self):
        self.ser.write(f'P\n'.encode('ASCII'))


if __name__ == '__main__':
    app = App()
    app.mainloop()

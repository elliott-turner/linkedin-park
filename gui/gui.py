import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

ctk.set_appearance_mode('System')
ctk.set_default_color_theme('blue')

class App(ctk.CTk):
    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()

        self.title('LinkedIn Park GUI')
        self.geometry(f'{App.WIDTH}x{App.HEIGHT}')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = ctk.CTkFrame(master=self, width=180, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky='nsew')

        self.frame_right = ctk.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)

        self.frame_right.grid_columnconfigure(4, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=1)

        self.frame_editor = ctk.CTkFrame(master=self.frame_right)
        self.frame_editor.grid(row=0, column=0, columnspan=5, sticky='nsew', padx=20, pady=20)

        self.editor_container = ctk.CTkCanvas(master=self.frame_editor, bg=self.frame_editor['background'], highlightthickness=0)
        self.scrollbar_editor = ctk.CTkScrollbar(master=self.frame_editor, orientation='horizontal', command=self.editor_container.xview)
        self.editor_canvas = ctk.CTkCanvas(master=self.editor_container, bg=self.frame_editor['background'], highlightthickness=0)
        self.editor_canvas.bind('<Configure>', lambda e: self.editor_container.configure(scrollregion=self.editor_container.bbox('all')))
        self.editor_container.create_window((0,0), window=self.editor_canvas, anchor='nw')
        self.editor_container.configure(xscrollcommand=self.scrollbar_editor.set)
        self.editor_container.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        self.scrollbar_editor.pack(side='bottom', fill='x', padx=5, pady=5)
        
        ctk.CTkLabel(master=self.frame_right, text='Zoom:', width=30).grid(row=1, column=0, sticky='w', padx=20, pady=(0, 20))
        self.zoom_minus_button = ctk.CTkButton(master=self.frame_right, text='-', width=30)
        self.zoom_minus_button.grid(row=1, column=1, padx=10, pady=(0, 20), sticky='w')
        self.zoom_plus_button = ctk.CTkButton(master=self.frame_right, text='+', width=30)
        self.zoom_plus_button.grid(row=1, column=2, pady=(0, 20), sticky='w')
        ctk.CTkLabel(master=self.frame_right, text='').grid(row=1, column=3, sticky='ew')
        self.add_measure_button = ctk.CTkButton(master=self.frame_right, text='add 1 measure')
        self.add_measure_button.grid(row=1, column=4, padx=20, pady=(0, 20), sticky='e')

    def on_closing(self, event=0):
        self.destroy()

if __name__ == '__main__':
    app = App()
    app.mainloop()

import tkinter as tk

top = tk.Tk()
P = tk.Canvas(top, bg="#EEEEEE", height=250, width=1000)
V = tk.Canvas(top, bg="#EEEEEE", height=250, width=1000)
A = tk.Canvas(top, bg="#EEEEEE", height=250, width=1000)

ps = []

def clear():
    for x in [P,V,A]: x.delete("all")

clear_button = tk.Button(top, command=clear)

max_accel = 100
max_vel = 100

last_time = 0.0
last_position = 0.0
last_velocity = 0.0
last_acceleration = 0.0
time = 0.0
position = 0.0
velocity = 0.0
acceleration = 0.0

def add_point(p1, p2):
    global last_time, time, last_position, last_velocity, last_acceleration, position, velocity, acceleration
    time = last_time + 1
    P.create_line(last_time, last_position+125, time, position+125, fill="blue", width=2)
    V.create_line(last_time, last_velocity*50+125, time, velocity*50+125, fill="purple", width=2)
    A.create_line(last_time, last_acceleration*500+125, time, acceleration*500+125, fill="red", width=2)
    last_time = time
    last_position = position
    last_velocity = velocity
    last_acceleration = acceleration

def callback(event):
    global last_time, time, last_position, last_velocity, last_acceleration, position, velocity, acceleration
    clear()
    ps.append([event.x, event.y-125])
    ps.sort(key=lambda p: p[0])
    if len(ps) >= 1:
        p2 = ps[0]
        P.create_oval(p2[0]-4, p2[1]+125-4, p2[0]+4, p2[1]+125+4, fill="black")
    if len(ps) >= 2:
        for p1, p2 in zip(ps[:-1], ps[1:]):
            move_distance = p2[1] - p1[1]
            move_time = p2[0] - p1[0]
            coast_time = 0.4 * move_time
            accel_time = 0.3 * move_time
            accel = 100.0*move_distance/21.0/(move_time*move_time)
            coast_velocity = 10.0*move_distance/7.0/move_time
            last_time = p1[0]
            last_position = float(p1[1])
            last_velocity = 0.0
            last_acceleration = 0.0
            position = 0.0
            velocity = 0.0
            acceleration = 0.0
            for t in range(int(accel_time)):
                acceleration = accel
                velocity = last_velocity + acceleration
                position = last_position + velocity
                add_point(p1, p2)
            for t in range(int(accel_time), int(accel_time + coast_time)):
                acceleration = 0
                velocity = coast_velocity
                position = last_position + velocity
                add_point(p1, p2)
            for t in range(int(accel_time + coast_time), int(move_time)+1):
                acceleration = -accel
                velocity = last_velocity + acceleration
                position = last_position + velocity
                add_point(p1, p2)
            P.create_oval(p2[0]-4, p2[1]+125-4, p2[0]+4, p2[1]+125+4, fill="black")

P.bind("<Button-1>", callback)

P.pack()
V.pack()
A.pack()

top.mainloop()

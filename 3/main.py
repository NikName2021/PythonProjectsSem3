import math
import random
import tkinter as tk


class Point:
    def __init__(self, x, y, r=2):
        self.x = x
        self.y = y
        self.color = 'red'
        self.radius = r

    def get_coords(self):
        return self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius

    def __call__(self, *args, **kwargs):
        return int(self.x), int(self.y)


class SetPoints:
    def __init__(self):
        self.points = []


COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'brown', 'pink']


def random_color():
    return random.choice(COLORS)


def points():
    canvas.delete("all")
    points = []
    for _ in range(5):
        point = Point(random.randint(0, 400), random.randint(0, 400), 2)
        canvas.create_oval(*point.get_coords(), fill='red')
        points.append(point)
    SetPoints.points = points


def draw_random_line(line=5):
    for i in range(line):
        gb = random.sample(SetPoints.points, 2)
        canvas.create_line(*gb[0](), *gb[1](), fill='blue', width=3)


def rectangles(count=1):
    for _ in range(count):
        x1 = random.randint(0, 350)
        y1 = random.randint(0, 350)
        x2 = x1 + random.randint(20, 80)
        y2 = y1 + random.randint(20, 80)
        canvas.create_rectangle(x1, y1, x2, y2,
                                fill=random_color(),
                                outline='black',
                                width=1)


def ellipses(count=1):
    for _ in range(count):
        x1 = random.randint(0, 350)
        y1 = random.randint(0, 350)
        x2 = x1 + random.randint(30, 100)
        y2 = y1 + random.randint(20, 60)
        canvas.create_oval(x1, y1, x2, y2,
                           fill=random_color(),
                           outline='black',
                           width=2)


def triangles(count=1):
    for _ in range(count):
        cx = random.randint(50, 350)
        cy = random.randint(50, 350)
        size = random.randint(20, 50)

        points = []
        for i in range(3):
            angle = math.radians(i * 120 - 90 + random.randint(-20, 20))
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.extend([x, y])

        canvas.create_polygon(points,
                              fill=random_color(),
                              outline='black',
                              width=2)


def stars(count=1):
    for _ in range(count):
        cx = random.randint(50, 350)
        cy = random.randint(50, 350)
        outer_r = random.randint(20, 40)
        inner_r = outer_r // 2
        num_points = random.choice([5, 6, 8])

        points = []
        for i in range(num_points * 2):
            angle = math.radians(i * 180 / num_points - 90)
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.extend([x, y])

        canvas.create_polygon(points,
                              fill=random_color(),
                              outline='black',
                              width=1)


def circles(count=1):
    for _ in range(count):
        cx = random.randint(50, 350)
        cy = random.randint(50, 350)
        r = random.randint(15, 40)

        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=random_color(),
                           outline='black',
                           width=2)


def draw_all_shapes():
    canvas.delete("all")
    points()
    draw_random_line(3)
    ellipses(3)
    triangles(3)
    stars(2)


def clear_canvas():
    canvas.delete("all")
    SetPoints.points = []


root = tk.Tk()
root.title("Генератор фигур")

canvas = tk.Canvas(root, width=400, height=400, bg='white')
canvas.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack()

left_frame = tk.Frame(button_frame)
left_frame.pack(side=tk.LEFT, padx=10)

right_frame = tk.Frame(button_frame)
right_frame.pack(side=tk.LEFT, padx=10)

tk.Button(left_frame, text="Точки", command=points, width=20).pack(pady=2)
tk.Button(left_frame, text="Линии", command=draw_random_line, width=20).pack(pady=2)
tk.Button(left_frame, text="Прямоугольники", command=rectangles, width=20).pack(pady=2)

tk.Button(right_frame, text="Круги", command=circles, width=20).pack(pady=2)
tk.Button(right_frame, text="Треугольники", command=triangles, width=20).pack(pady=2)
tk.Button(right_frame, text="Звёзды", command=stars, width=20).pack(pady=2)

control_frame = tk.Frame(root)
control_frame.pack(pady=10)

tk.Button(control_frame, text="Нарисовать всё", command=draw_all_shapes,
          width=20, bg='lightgreen').pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Очистить", command=clear_canvas,
          width=20, bg='lightcoral').pack(side=tk.LEFT, padx=5)


root.mainloop()

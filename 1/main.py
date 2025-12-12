from math import pi


class Share:
    def perimeter(self):
        raise AssertionError

    def area(self):
        raise AssertionError

    @property
    def get_perimetr(self):
        return self.perimeter()

    @property
    def get_square(self):
        return self.area()


class Rect(Share):
    def __init__(self, a: int, b: int):
        if a <= 0 or b <= 0:
            raise ValueError
        self.a, self.b = a, b

    def __str__(self):
        return f"Прямоугольник {self.a}x{self.b}"

    def perimeter(self):
        return f"{(self.a + self.b) * 2:.1f}"

    def area(self):
        return f"{self.a * self.b:.1f}"


class Circle(Share):
    def __init__(self, r: float):
        if r <= 0:
            raise AssertionError
        self.r = r

    def __str__(self):
        return f"Круг радиусом {self.r:.1f}"

    def perimeter(self):
        return f"{2 * self.r * pi:.1f}"

    def area(self):
        return f"{self.r ** 2 * pi:.1f}"


class Triangle(Share):
    def __init__(self, a: float, b: float, c: float):
        if a <= 0 or b <= 0 or c <= 0:
            raise AssertionError
        self.a, self.b, self.c = a, b, c

    def __str__(self):
        return f"Треугольник с {self.a}x{self.b}x{self.c}"

    def perimeter(self):
        return f"{self.a + self.b + self.c:.1f}"

    def area(self):
        p = self.a * self.b * self.c / 2
        return f"{(p * (p - self.a) * (p - self.b) * (p - self.c)) ** 0.5:.1f}"


if __name__ == "__main__":
    r = Rect(1, 2)
    print(r.get_perimetr)
    print(r.get_square)
    s = Circle(5)
    print(s)
    print(s.get_perimetr)
    print(s.get_square)
    t = Triangle(2, 2, 4)
    print(t)
    print(t.get_perimetr)
    print(t.get_square)
    s = Share()

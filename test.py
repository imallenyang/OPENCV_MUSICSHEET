from rectangle import Rectangle

a = Rectangle(0, 30, 10, 20)
b = Rectangle(30, 0, 20, 10)
print(Rectangle.merge(a, b).x)
print(Rectangle.merge(a, b).y)
print(Rectangle.merge(a, b).w)
print(Rectangle.merge(a, b).h)
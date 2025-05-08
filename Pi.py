import random
import matplotlib.pyplot as plt
INTERVAL = 1000

circle_points = 0
square_points = 0

inside_x = []
inside_y = []
outside_x = []
outside_y = []

for i in range(INTERVAL):
    rand_x = random.uniform(-1.0,1.0)
    rand_y = random.uniform(-1.0,1.0)

    origin_dist = rand_x ** 2 + rand_y ** 2
    if origin_dist <= 1:
        circle_points += 1
        inside_x.append(rand_x)
        inside_y.append(rand_y)
    else:
        outside_x.append(rand_x)
        outside_y.append(rand_y)
    square_points += 1
    pi = 4 * circle_points / square_points
    print(pi)

plt.figure(figsize = (8,8))
plt.scatter(inside_x, inside_y, color = "blue", s=1, label = "inside Circle")
plt.scatter(outside_x, outside_y, color = "red", s=1, label= "outside Circle")

plt.title("Monte Carlo simulation")
plt.legend()
plt.show()
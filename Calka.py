import numpy as np
import scipy.integrate
import matplotlib.pyplot as plt

def acceleration(t):
    return 2*t

v0 = 0.0
x0 = 0.0

t_start = 0
t_end = 5.0

t_values = np.linspace(t_start,t_end,100)

velocity = scipy.integrate.cumulative_trapezoid(acceleration(t_values),t_values,initial=v0)

position = scipy.integrate.cumulative_trapezoid(velocity,t_values,initial=x0)

#print("Time (t)", t_values)
#print("Velocity (v)", velocity)
#print("Position (x)", position)

plt.figure(figsize=(10,6))
plt.subplot(3,1,1)
plt.plot(t_values,acceleration(t_values), label="Acceleration(a)", color="red")
plt.grid()

plt.subplot(3,1,2)
plt.plot(t_values,velocity, label="Velocity")
plt.grid()

plt.subplot(3,1,3)
plt.plot(t_values,position, label="Position(x)", color="green")
plt.grid()

plt.tight_layout()
plt.show()
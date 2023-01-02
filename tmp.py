import matplotlib.pyplot as plt
import numpy as np
import math

def prod(w,p):
        if w<3:
            return 0
        elif w>20:
            return 0
        elif w>12:
            return p
        else:
            return p*(w-3)/(12-3)

x = [i/1000 for i in range(0,22000)]
y = [prod(i,100) for i in x]

plt.plot(x,y)
plt.show()

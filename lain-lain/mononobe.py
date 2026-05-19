import numpy as np

R24 = 120
t = np.array([0.5, 1, 2, 3, 6, 12])

I = (R24 / 24) * (24 / t) ** (2/3)

print(I)
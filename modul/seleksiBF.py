import numpy as np

def seleksiBF(barisKoma, kolomKoma):
    """
    Seleksi Brute Force untuk mencari titik terdekat.
    """
    dmin = np.inf
    barisMatriks, kolomMatriks = -1, -1
    for i in range(1, 3602):
        for j in range(1, 3602):
            d = np.sqrt((i - barisKoma) ** 2 + (j - kolomKoma) ** 2)
            if d < dmin:
                dmin = d
                barisMatriks = i
                kolomMatriks = j
    return barisMatriks, kolomMatriks
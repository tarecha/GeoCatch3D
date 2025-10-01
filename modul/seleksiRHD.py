import numpy as np

def seleksiRHD(barisKoma, kolomKoma):
    """
    Seleksi Round Half Down untuk mencari titik terdekat.
    """
    # Proses baris
    barisMatriksMin = np.floor(barisKoma)
    barisMatriksMax = barisMatriksMin + 1
    dBarisMatriksMin = abs(barisKoma - barisMatriksMin)
    dBarisMatriksMax = abs(barisKoma - barisMatriksMax)

    if dBarisMatriksMin > dBarisMatriksMax:
        barisMatriks = barisMatriksMax
    else:
        barisMatriks = barisMatriksMin

    # Proses kolom
    kolomMatriksMin = np.floor(kolomKoma)
    kolomMatriksMax = kolomMatriksMin + 1
    dKolomMatriksMin = abs(kolomKoma - kolomMatriksMin)
    dKolomMatriksMax = abs(kolomKoma - kolomMatriksMax)

    if dKolomMatriksMin > dKolomMatriksMax:
        kolomMatriks = kolomMatriksMax
    else:
        kolomMatriks = kolomMatriksMin

    return int(barisMatriks), int(kolomMatriks)
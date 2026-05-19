import numpy as np


def interpolasiLinier(matrikInput):
    """
    Fungsi untuk melakukan interpolasi linier pada matriks.
    """
    baris, kolom = matrikInput.shape
    matrikOutput = np.zeros((baris * 2 - 1 , kolom * 2 - 1 ), dtype=matrikInput.dtype)

    for i in range(baris):
        for j in range(kolom):
            # Salin nilai asli
            matrikOutput[i * 2, j * 2] = matrikInput[i, j]

            # Interpolasi vertikal
            if i < baris - 1:
                matrikOutput[i * 2 + 1, j * 2] = (matrikInput[i, j] + matrikInput[i + 1, j]) / 2

            # Interpolasi horizontal
            if j < kolom - 1 :
                matrikOutput[i * 2, j * 2 + 1] = (matrikInput[i, j] + matrikInput[i, j + 1]) / 2

            # Interpolasi diagonal
            if i < baris - 1  and j < kolom - 1:
                matrikOutput[i * 2 + 1, j * 2 + 1] = (matrikInput[i, j] + matrikInput[i + 1, j + 1] + matrikInput[i + 1, j] + matrikInput[i, j + 1]) / 4

    return matrikOutput
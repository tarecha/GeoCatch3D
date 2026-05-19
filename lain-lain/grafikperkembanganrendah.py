import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
# Data dimasukkan secara manual sesuai gambar dan teks
# Data sesuai tabel (61 baris)
data = {
    "ID": [
        1,1,1,1,1,
        2,2,2,2,2,
        3,3,3,3,
        4,4,4,4,4,
        5,5,5,5,5,
        6,
        7,
        8,
        9,9,9,
        10,10,
        11,11,11,
        12,12,12,
        13,13,13,
        14,14,
        15,15,
        16,
        17,
        18,
        19
    ],
    "Radius": [
        50,100,150,200,250,
        50,100,150,200,250,
        100,150,200,250,
        100,150,200,250,300,
        100,150,200,250,300,
        300,
        300,
        300,
        300,400,450,
        300,350,
        350,400,450,
        350,400,450,
        350,400,450,
        400,450,
        400,450,
        400,
        400,
        450,
        450
    ],
    "Area": [
        0.21,0.21,0.21,0.21,0.21,
        0.20,0.20,0.20,0.20,0.20,
        0.22,0.22,0.22,0.22,
        0.35,0.35,0.35,0.35,0.35,
        0.17,0.17,0.17,0.17,0.17,
        0.27,
        0.36,
        0.25,
        0.60,5.94,8.58,
        0.46,1.69,
        3.04,6.89,12.27,
        1.21,3.31,6.78,
        1.47,3.88,4.29,
        2.07,3.30,
        2.38,4.26,
        2.21,
        2.58,
        3.37,
        3.50
    ]
}
print(data)
# Buat DataFrame
df = pd.DataFrame(data)
# Plotting
plt.figure(figsize=(12, 6))
for key, grp in df.groupby("ID"):
    print(f"key {key}, grp {grp}")
    plt.plot(grp["Radius"], grp["Area"], marker='o', label=f"ID {key}")


plt.title("Perkembangan Daerah Aliran Sungai (DAS) berdasarkan radius analisis",fontsize=18)
plt.xlabel("Radius (interval 30 m)",fontsize=14)
plt.ylabel("Luas area DAS (km²)",fontsize=14)
plt.legend(title="ID DAS", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
# Data dimasukkan secara manual sesuai gambar dan teks
# Data sesuai tabel (61 baris)
data = {
    "ID": [
        1,1,1,1,1,1,1,
        2,2,2,2,2,2,2,2,2,
        3,
        4,4,4,
        5,5,5,5,5,5,5,
        6,6,6,6,6,6,6,
        7,
        8,8,8,
        9,9,9,9,9,
        10,10,
        11,
        12,12,
        13,13,
        14
    ],
    "Radius": [
        50,100,150,200,250,300,350,
        50,100,150,200,250,300,350,400,450,
        100,
        100,150,200,
        150,200,250,300,350,400,450,
        150,200,250,300,350,400,450,
        250,
        250,300,350,
        250,300,350,400,450,
        300,350,
        350,
        400,450,
        400,450,
        450
    ],
    "Area": [
        0.6214,1.8999,2.6833,4.1271,5.8186,6.1620,6.1620,
        0.6979,2.2471,5.6546,8.6110,10.2331,10.6344,10.6344,10.6344,10.6344,
        1.1663,
        1.7229,1.3209,3.3857,
        5.5185,8.9486,10.8149,10.8149,10.8149,10.8149,10.8149,
        2.6631,5.5322,7.5786,7.5786,7.5786,7.5786,7.5786,
        5.1572,
        6.1401,13.2638,16.0109,
        5.9758,8.0749,8.0687,8.0671,8.0743,
        5.8479,11.7205,
        6.4845,
        48.4864,62.9785,
        6.9045,12.9953,
        7.6672
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

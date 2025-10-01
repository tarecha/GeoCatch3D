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
        8,8,8,8,8,
        9,9,9,9,9,
        10,10,10,10,
        11,
        12,12,
        13,13,
        14,14,
        15,15,
        16,
        17,
        18
    ],
    "Radius": [
         50,100,150,200,250,300,350,
         50,100,150,200,250,300,350,400,450,
        100,
        100,150,200,
        150,200,250,300,350,400,450,
        150,200,250,300,350,400,450,
        250,
        250,300,350,400,450,
        250,300,350,400,450,
        300,350,400,450,
        350,
        400,450,
        400,450,
        400,450,
        400,450,
        450,
        450,
        450
    ],
    "Area": [
        0.6214, 1.8999, 2.6833, 4.1271, 5.8186, 6.1620, 6.1620,
        0.6979, 2.2471, 5.6546, 8.6110,10.2331,10.6344,10.6344,10.6344,10.6344,
        1.1663,
        1.7229, 3.3812, 3.3857,
        5.5185, 8.9486,10.8149,10.8149,10.8149,10.8149,10.8149,
        2.6631, 5.5322, 7.5786, 7.5786, 7.5786, 7.5786, 7.5786,
        5.1572,
        6.1401,13.2638,16.0159,18.0980,18.0984,
        5.9758, 8.0749, 8.0743, 8.0743, 8.0743,
        5.8479,11.7205,11.8920,11.8920,
        6.4845,
       48.3821,62.8743,
       35.7966,49.9845,
        8.7876,22.3777,
        7.1017,12.9954,
        7.6672,
       13.9431,
        7.5467
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


plt.title("Area of Watershed vs. Radius for Each Watershed ID")
plt.xlabel("Radius (interval 30 m)")
plt.ylabel("Area of Watershed (km²)")
plt.legend(title="ID", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()

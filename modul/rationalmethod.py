from modul import config as cfg

def hitungdebit(A):
    print(f"koefisien di fungsi {cfg.koefisien}")
    print(f"curah hujan di fungsi {cfg.curahhujan}")
    Qp = round(0.278 * float(cfg.koefisien) * cfg.curahhujan * A,4)
    return Qp
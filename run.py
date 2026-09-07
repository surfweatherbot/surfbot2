import subprocess
import time

# Navnene på de 4 skriptene dine i riktig rekkefølge
SCRIPTS = [
    "timer_sf.py",
    "dager_sf.py",
    "yr_timer.py",
    "yr_dager.py",
    "bølge.py",
]

def kjör_alle():
    print("--- Starter kjøring av alle skript ---")
    for script in SCRIPTS:
        print(f"Kjører {script}...")
        
        # run() venter til skriptet er helt ferdig før koden går videre
        resultat = subprocess.run(["python", script], check=True)
        
        print(f"Ferdig med {script}.\n")
    print("--- Alle skript er fullført! ---")

if __name__ == "__main__":
    # 1. Kjører alle skriptene umiddelbart ved oppstart
    kjör_alle()
    
    # 2. Loop som venter 1 time (3600 sekunder) og kjører på nytt
    while True:
        print("Venter 1 time til neste kjøring...")
        time.sleep(3600)
        kjör_alle()

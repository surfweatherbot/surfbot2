import subprocess
import sys

# Navnene på alle de 6 skriptene dine
SCRIPTS = [
    "timer_sf.py",
    "dager_sf.py",
    "yr_timer.py",
    "yr_dager.py",
    "bølge.py",
    "vanntemp.py",
]

def kjor_alle():
    print("--- Starter kjøring av alle skript ---")
    for script in SCRIPTS:
        print(f"Kjører {script}...")
        try:
            # Kjører hvert skript med samme Python-interpreter
            resultat = subprocess.run([sys.executable, script], check=True)
            print(f"Ferdig med {script}.\n")
        except subprocess.CalledProcessError as e:
            print(f"Feil ved kjøring av {script}: {e}\n")
            raise e
    print("--- Alle skript er fullført! ---")

if __name__ == "__main__":
    kjor_alle()

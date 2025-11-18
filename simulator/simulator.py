import pyodbc
import time
import random
from datetime import datetime

# Configurare SQL Server
SERVER_NAME = r"..."  
DATABASE_NAME = "FabricaImbuteliere"

conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Parametri simulare
CYCLE_TIME = 5              # secunde per sticla
P_REJECT = 0.03              # 3% rebut
P_FAILURE = 0.01             # 1% sanse defect
REPAIR_TIME = 20             # secunde avarie
SHIFT_ID = 1
PRODUCT_ID = 1


def insert_event(event_type, details=None):
    cursor.execute("""
        INSERT INTO MachineEvents (EventTime, EventType, ShiftID, Details)
        VALUES (?, ?, ?, ?)
    """, datetime.now(), event_type, SHIFT_ID, details)
    conn.commit()


def insert_production():
    is_good = 1 if random.random() > P_REJECT else 0
    cursor.execute("""
        INSERT INTO ProductionCycles (Timestamp, ShiftID, ProductID, GoodPiece, ActualCycleTimeSec)
        VALUES (?, ?, ?, ?, ?)
    """, datetime.now(), SHIFT_ID, PRODUCT_ID, is_good, CYCLE_TIME)
    conn.commit()


def run():
    print("SIMULATOR PORNIT")
    insert_event("RUN_START", "Simulator started")

    while True:
        # verificam defect
        if random.random() < P_FAILURE:
            print(">>> DEFECT simulat")
            insert_event("FAILURE_START", "Avarie")

            time.sleep(REPAIR_TIME)

            insert_event("FAILURE_END", "Avarie rezolvata")
            print(">>> linia si-a revenit")

        # productie normala
        insert_production()
        print("Produsa o sticla")

        time.sleep(CYCLE_TIME)


if __name__ == "__main__":
    run()

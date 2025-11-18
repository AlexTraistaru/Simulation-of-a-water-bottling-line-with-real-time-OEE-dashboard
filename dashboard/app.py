import pyodbc
import pandas as pd
import streamlit as st
from datetime import datetime

SERVER_NAME = r"DESKTOP-G3O3B85\SQLEXPRESS"   
DATABASE_NAME = "FabricaImbuteliere"

conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"
)

@st.cache_data(ttl=5)
def load_data():
    """Citeste datele din SQL Server in trei DataFrame-uri."""
    df_shifts = pd.read_sql("SELECT * FROM Shifts", conn)
    df_events = pd.read_sql("SELECT * FROM MachineEvents", conn)
    df_prod = pd.read_sql("SELECT * FROM ProductionCycles", conn)
    df_products = pd.read_sql("SELECT * FROM Products", conn)
    return df_shifts, df_events, df_prod, df_products


def calc_oee_for_shift(shift_row, df_events, df_prod, df_products):
    """
    Calculeaza Disponibilitate, Performanta, Calitate, OEE
    pentru un anumit shift (o singura linie din df_shifts).
    """
    shift_id = int(shift_row["ShiftID"])
    start = shift_row["StartTime"]
    end = shift_row["EndTime"]

    # Asiguram conversie la datetime
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # Timp planificat (secunde)
    planned_time_sec = (end - start).total_seconds()

    # Filtram evenimentele pentru acest shift
    ev = df_events[df_events["ShiftID"] == shift_id].copy()
    ev["EventTime"] = pd.to_datetime(ev["EventTime"])
    ev = ev.sort_values("EventTime")

    # Calcul downtime din FAILURE_START / FAILURE_END
    downtime_sec = 0.0
    in_failure = False
    failure_start_time = None

    for _, row in ev.iterrows():
        etype = row["EventType"]
        t = row["EventTime"]

        if etype == "FAILURE_START" and not in_failure:
            in_failure = True
            failure_start_time = t

        elif etype == "FAILURE_END" and in_failure:
            in_failure = False
            dt = (t - failure_start_time).total_seconds()
            downtime_sec += dt

    # Daca cumva shiftul s-a terminat inca in failure, taiem la final de shift
    if in_failure and failure_start_time is not None:
        dt = (end - failure_start_time).total_seconds()
        downtime_sec += max(dt, 0)

    # Timp efectiv de functionare
    run_time_sec = max(planned_time_sec - downtime_sec, 0)

    # Filtram productia pentru acest shift
    prod = df_prod[df_prod["ShiftID"] == shift_id].copy()
    prod["Timestamp"] = pd.to_datetime(prod["Timestamp"])

    total_pieces = len(prod)
    good_pieces = int(prod["GoodPiece"].sum())
    reject_pieces = total_pieces - good_pieces

    # Daca nu s-a produs nimic, toate valorile sunt 0
    if total_pieces == 0 or run_time_sec == 0:
        return {
            "availability": 0.0,
            "performance": 0.0,
            "quality": 0.0,
            "oee": 0.0,
            "total_pieces": total_pieces,
            "good_pieces": good_pieces,
            "reject_pieces": reject_pieces,
            "run_time_sec": run_time_sec,
            "planned_time_sec": planned_time_sec,
            "downtime_sec": downtime_sec,
        }

    # IdealCycleTime din Products (luam produsul folosit in shift - aici presupunem ProdID 1)
    # Daca ai mai multe produse, poti rafina logica.
    products_map = df_products.set_index("ProductID")["IdealCycleTimeSec"].to_dict()
    # luam produsul majoritar ca referinta
    most_common_product = prod["ProductID"].mode().iloc[0]
    ideal_cycle = products_map.get(most_common_product, 30)

    # Volum maxim teoretic
    theo_max_pieces = run_time_sec / ideal_cycle

    # Componente OEE
    availability = run_time_sec / planned_time_sec if planned_time_sec > 0 else 0.0
    performance = total_pieces / theo_max_pieces if theo_max_pieces > 0 else 0.0
    quality = good_pieces / total_pieces if total_pieces > 0 else 0.0

    oee = availability * performance * quality

    return {
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": oee,
        "total_pieces": total_pieces,
        "good_pieces": good_pieces,
        "reject_pieces": reject_pieces,
        "run_time_sec": run_time_sec,
        "planned_time_sec": planned_time_sec,
        "downtime_sec": downtime_sec,
    }

#aplicatia streamlit

def main():
    st.set_page_config(page_title="Dashboard Linie Îmbuteliere", layout="wide")

    st.title("📊 Dashboard Linie de Îmbuteliere Apă")
    st.write("Monitorizare producție și indicatori OEE pe bază de date SQL Server.")

    df_shifts, df_events, df_prod, df_products = load_data()

    if df_shifts.empty:
        st.error("Nu exista schimburi in tabelul Shifts.")
        return

    # Convertim in datetime pentru siguranta
    df_shifts["StartTime"] = pd.to_datetime(df_shifts["StartTime"])
    df_shifts["EndTime"] = pd.to_datetime(df_shifts["EndTime"])

    # Selectie shift din sidebar
    st.sidebar.header("Filtru")
    shift_options = {
        f'{row.ShiftID} - {row.ShiftName} ({row.StartTime} – {row.EndTime})': row.ShiftID
        for _, row in df_shifts.iterrows()
    }
    selected_label = st.sidebar.selectbox("Alege schimbul", list(shift_options.keys()))
    selected_shift_id = shift_options[selected_label]

    current_shift = df_shifts[df_shifts["ShiftID"] == selected_shift_id].iloc[0]

    # Calcul OEE pentru shift
    metrics = calc_oee_for_shift(current_shift, df_events, df_prod, df_products)

    # OEE
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Disponibilitate",
        f"{metrics['availability']*100:0.1f} %",
        help="Timp de functionare / timp planificat"
    )
    col2.metric(
        "Performanta",
        f"{metrics['performance']*100:0.1f} %",
        help="Volum actual / volum maxim teoretic"
    )
    col3.metric(
        "Calitate",
        f"{metrics['quality']*100:0.1f} %",
        help="Piese bune / piese totale"
    )
    col4.metric(
        "OEE",
        f"{metrics['oee']*100:0.1f} %",
        help="Disponibilitate × Performanta × Calitate"
    )

    st.markdown("---")

    # productie
    st.subheader("📦 Producție în schimbul selectat")

    prod_shift = df_prod[df_prod["ShiftID"] == selected_shift_id].copy()
    if not prod_shift.empty:
        prod_shift["Timestamp"] = pd.to_datetime(prod_shift["Timestamp"])
        prod_shift = prod_shift.sort_values("Timestamp")

        c1, c2, c3 = st.columns(3)
        c1.write(f"**Total sticle:** {metrics['total_pieces']}")
        c2.write(f"**Conforme:** {metrics['good_pieces']}")
        c3.write(f"**Rebuturi:** {metrics['reject_pieces']}")

        # Grupare pe ora pentru grafic
        prod_shift["Hour"] = prod_shift["Timestamp"].dt.floor("H")
        prod_by_hour = prod_shift.groupby("Hour")["CycleID"].count()

        st.line_chart(prod_by_hour, height=250)
    else:
        st.info("Nu exista productie in acest schimb.")

    st.markdown("---")

    # evenimente linie
    st.subheader("🛠️ Evenimente linie (ultimele 50)")

    events_shift = df_events[df_events["ShiftID"] == selected_shift_id].copy()
    events_shift["EventTime"] = pd.to_datetime(events_shift["EventTime"])
    events_shift = events_shift.sort_values("EventTime", ascending=False).head(50)

    st.dataframe(
        events_shift[["EventTime", "EventType", "Details"]],
        use_container_width=True,
        height=250
    )

    st.caption("Pagina se poate reîncărca (Ctrl+R sau butonul `Rerun` din Streamlit) pentru a vedea date noi generate de simulator.")


if __name__ == "__main__":
    main()

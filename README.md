# Simulation of a Water Bottling Production Line with Real-Time OEE Dashboard

This project simulates the operation of a water bottling production line and monitors its performance in real time.  
It consists of:

1. A Python-based simulator that generates production cycles and machine events.
2. A SQL Server database that stores all generated data.
3. A Streamlit dashboard that visualizes production metrics and computes the OEE (Overall Equipment Effectiveness).

The project demonstrates how industrial performance indicators can be collected and analyzed in real time, similar to what happens in SCADA systems.

## System Architecture

- The simulator writes production data and machine events at regular intervals.
- The dashboard reads the data continuously and generates performance analytics.

  The database `FabricaImbuteliere` includes four tables.  
Below is the structure of each table.

### 1. Products

| Column              | Description                                     |
|---------------------|-------------------------------------------------|
| ProductID           | Primary key                                     |
| ProductName         | Product name                                    |
| ProductCode         | Internal code                                   |
| IdealCycleTimeSec   | Ideal cycle time per unit (in seconds)          |

---

### 2. Shifts

| Column     | Description                     |
|------------|---------------------------------|
| ShiftID    | Primary key                     |
| ShiftName  | Name of the shift               |
| StartTime  | Start timestamp of the shift    |
| EndTime    | End timestamp of the shift      |

---

### 3. MachineEvents

| Column     | Description                                            |
|------------|--------------------------------------------------------|
| EventID    | Primary key                                            |
| EventTime  | Timestamp of the event                                 |
| EventType  | RUN_START, FAILURE_START, FAILURE_END                  |
| ShiftID    | Foreign key referencing Shifts                         |
| Details    | Additional notes                                       |

---

### 4. ProductionCycles

| Column              | Description                                |
|---------------------|--------------------------------------------|
| CycleID             | Primary key                                |
| Timestamp           | When the unit was produced                 |
| ShiftID             | Foreign key referencing Shifts             |
| ProductID           | Foreign key referencing Products           |
| GoodPiece           | 1 = good unit, 0 = reject                  |
| ActualCycleTimeSec  | Actual measured cycle time (seconds)       |

---

## Simulator 

The simulator performs the following operations:

- Generates a new bottle every `CYCLE_TIME` seconds.
- Randomly marks bottles as “good” or “reject”.
- Randomly generates machine failures.
- Records:
  - Production cycles  
  - Machine events indicating failures and recoveries
 


## The Streamlit dashboard provides:

- Total number of produced units  
- Number of good units and rejects  
- Production rate per hour  
- Machine event logs  
- Full OEE computation based on recorded data  

The dashboard refreshes automatically as new data appears in the database.

## OEE Calculation

OEE (Overall Equipment Effectiveness) is calculated based on three components: Availability, Performance, and Quality.

### 1. Availability

Measures how much of the planned production time the line was actually running.

$$
\text{Availability} = \frac{\text{Planned Time} - \text{Downtime}}{\text{Planned Time}}
$$


### 2. Performance

Measures how fast the line produced compared to its ideal speed.
$$
\text{Performance} = 
\frac{\text{Actual Output}}
     {\frac{\text{Run Time}}{\text{Ideal Cycle Time}}}
$$


### 3. Quality

Measures how many units were produced without defects.

$$
\text{Quality} = \frac{\text{Good Units}}{\text{Total Units}}
$$


### Final OEE

$$
\text{OEE} = 
\text{Availability} \times \text{Performance} \times \text{Quality}
$$


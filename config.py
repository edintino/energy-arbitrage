from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class BatteryParams:
    battery_capacity: float
    battery_capacity_buffer: float
    charge_rate: float
    initial_soc: float
    final_soc_target: float
    efficiency: float

# Simulation settings
START_DATE = datetime(2025, 4, 1)
END_DATE   = START_DATE + timedelta(days=2)
COUNTRIES  = [
    'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Czechia',
    'Denmark', 'Estonia', 'Finland', 'France', 'Germany'
]
DATA_PATH = 'data/all_countries.csv'
TARGET_RMSE = 25.0
BIAS_FRACTION = 0.15
NUM_SCENARIOS = 2500
RISK_AVERSION = 1.0

BATTERY_CAPACITY = 30.0

BATTERY = BatteryParams(
    battery_capacity=BATTERY_CAPACITY,
    battery_capacity_buffer=0.1,
    charge_rate=0.15 * BATTERY_CAPACITY,
    initial_soc=BATTERY_CAPACITY / 2,
    final_soc_target=BATTERY_CAPACITY / 2,
    efficiency=0.95,
)

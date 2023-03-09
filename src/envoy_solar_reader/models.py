from dataclasses import dataclass


@dataclass
class ProductionData:
    currentTotalPowerInWatts: float
    energyProducedTodayInKwh: float

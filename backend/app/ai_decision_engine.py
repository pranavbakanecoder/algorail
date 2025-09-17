from typing import List, Dict


class Train:
    def __init__(
        self,
        train_id: str,
        priority: int,
        train_type: str,
        length: int,
        delay: int,
        passenger_load: int,
        energy_efficiency: float,
    ):
        self.train_id = train_id
        self.priority = priority  # Lower number = higher priority
        self.train_type = train_type
        self.length = length  # in meters
        self.delay = delay  # in minutes
        self.passenger_load = passenger_load
        self.energy_efficiency = energy_efficiency


class SectionConflict:
    def __init__(
        self,
        section_id: str,
        competing_trains: List[str],
        signal_state: str,  # e.g. "Green", "Red", "Yellow"
        weather_condition: str,  # e.g. "Clear", "Rain", "Fog"
        platform_availability: Dict[str, bool],  # train_id -> bool availability
        track_capacity: int,  # number of trains allowed simultaneously
    ):
        self.section_id = section_id
        self.competing_trains = competing_trains
        self.signal_state = signal_state
        self.weather_condition = weather_condition
        self.platform_availability = platform_availability
        self.track_capacity = track_capacity


def ai_decision(
    trains: Dict[str, Train], conflicts: List[SectionConflict]
) -> Dict[str, str]:
    """
    Generate train priority recommendations for conflicting sections.
    Considers priority, delay, train length, passenger load, energy efficiency,
    signal state, weather, platform availability, and track capacity.
    """
    decisions = {}

    weather_delay_map = {"Clear": 0, "Rain": 2, "Fog": 5, "Storm": 10}  # minutes delay

    for conflict in conflicts:
        # Filter trains that have platform available
        available_trains = [
            tid
            for tid in conflict.competing_trains
            if conflict.platform_availability.get(tid, True)
        ]

        if not available_trains:
            continue  # skip if no available trains on this section

        # Calculate combined score for each train factoring multiple aspects
        def score_train(tid):
            train = trains[tid]
            # Base priority and delay
            base = train.priority * 10 + train.delay
            # Adjust for weather delay impact
            weather_delay = weather_delay_map.get(conflict.weather_condition, 0)
            # Adjust for train length (longer trains might cause more blockage)
            length_penalty = train.length / 100  # scaled
            # Passenger load and energy efficiency as factors (lower is better)
            passenger_factor = -train.passenger_load / 1000  # prioritize more passengers
            energy_factor = train.energy_efficiency  # higher energy efficiency preferred
            # Signal state penalty (if signal is red or yellow, lower priority)
            signal_penalty = 0
            if conflict.signal_state == "Red":
                signal_penalty = 20
            elif conflict.signal_state == "Yellow":
                signal_penalty = 10
            return base + weather_delay + length_penalty - passenger_factor - energy_factor + signal_penalty

        # Sort available trains by score ascending (lower score = higher priority)
        sorted_trains = sorted(available_trains, key=score_train)

        # Decide which trains get to proceed given section capacity
        allowed_train_count = min(conflict.track_capacity, len(sorted_trains))
        trains_to_proceed = sorted_trains[:allowed_train_count]
        trains_to_hold = sorted_trains[allowed_train_count:]

        # Compose decisions
        for tid in trains_to_proceed:
            decisions[tid] = f"Proceed first on section {conflict.section_id}"

        for tid in trains_to_hold:
            if trains_to_proceed:
                delay_min = int(score_train(tid) - score_train(trains_to_proceed[-1])) + weather_delay_map.get(conflict.weather_condition, 0)
                delay_min = max(delay_min, 5)  # minimum hold 5 minutes
            else:
                delay_min = 10  # fallback hold if no trains proceed
            decisions[tid] = f"Hold for {delay_min} minutes to let other trains pass on section {conflict.section_id}"

    return decisions

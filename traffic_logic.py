import time

class TrafficLightManager:
    def __init__(self):
        self.green_feed_index = 0  # Default: start from feed 0
        self.last_override_time = 0
        self.override_duration = 5  # seconds
        self.override_index = None

    def update_lights(self, vehicle_counts):
        """
        vehicle_counts: dict or list of vehicle counts per feed
                        e.g., {0: 2, 1: 5, 2: 1, 3: 3}
        Returns: list of traffic light statuses per feed ['green', 'red', ...]
        """
        current_time = time.time()

        # Check if any feed exceeds the threshold
        for idx, count in vehicle_counts.items():
            if count > 3:
                self.override_index = idx
                self.last_override_time = current_time
                break

        if self.override_index is not None:
            # Check if override time is still active
            if current_time - self.last_override_time < self.override_duration:
                statuses = ['red'] * len(vehicle_counts)
                statuses[self.override_index] = 'green'
                return statuses
            else:
                # Reset override
                self.override_index = None

        # Normal cycle: green one at a time, others red
        statuses = ['red'] * len(vehicle_counts)
        statuses[self.green_feed_index] = 'green'
        # Move to the next feed in the cycle
        self.green_feed_index = (self.green_feed_index + 1) % len(vehicle_counts)
        return statuses

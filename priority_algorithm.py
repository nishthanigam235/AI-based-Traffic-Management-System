import heapq

class PriorityScheduler:
    def __init__(self, threshold=3):
        self.threshold = threshold
        self.lights = {}  # feed_id -> light status

    def schedule(self, vehicle_counts: dict):
        """
        vehicle_counts: dict {feed_id: vehicle_count}
        Returns: dict {feed_id: light_status}
        """

        # Max-heap (Python heapq is min-heap, so we negate counts)
        heap = [(-count, feed_id) for feed_id, count in vehicle_counts.items()]
        heapq.heapify(heap)

        # Reset lights
        self.lights = {feed_id: "RED" for feed_id in vehicle_counts.keys()}

        if not heap:
            return self.lights

        # Extract the lane with max vehicles
        max_count, max_feed = heapq.heappop(heap)
        max_count = -max_count  # convert back

        # If max_count exceeds threshold → set it GREEN
        if max_count >= self.threshold:
            self.lights[max_feed] = "GREEN"
        else:
            # If no lane has >= threshold, just pick one in round robin style
            self.lights[max_feed] = "GREEN"

        return self.lights

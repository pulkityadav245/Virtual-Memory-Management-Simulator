class PageFrame:
    def __init__(self, frame_id):
        self.frame_id = frame_id
        self.page = None
        self.last_used = 0

class VirtualMemoryManager:
    def __init__(self, num_frames, algorithm, page_sequence=None):
        self.num_frames = num_frames
        self.frames = [PageFrame(i) for i in range(num_frames)]
        self.page_table = {}
        self.time = 0
        self.algorithm = algorithm
        self.history = []
        # Used by various algorithms
        self.queue = []
        self.page_sequence = page_sequence if page_sequence else []
        self.seq_ptr = 0

    def _find_frame(self, page_id):
        for frame in self.frames:
            if frame.page == page_id:
                return frame
        return None

    def _fifo(self):
        victim = None
        if None in [frame.page for frame in self.frames]:
            for frame in self.frames:
                if frame.page is None:
                    return frame
        else:
            victim = self.queue.pop(0)
        return victim

    def _lifo(self):
        victim = None
        if None in [frame.page for frame in self.frames]:
            for frame in self.frames:
                if frame.page is None:
                    return frame
        else:
            victim = self.queue.pop(-1)
        return victim

    def _lru(self):
        min_time = float('inf')
        victim = None
        for frame in self.frames:
            if frame.page is None:
                return frame
            if frame.last_used < min_time:
                min_time = frame.last_used
                victim = frame
        return victim

    def _mru(self):
        max_time = float('-inf')
        victim = None
        for frame in self.frames:
            if frame.page is None:
                return frame
            if frame.last_used > max_time:
                max_time = frame.last_used
                victim = frame
        return victim

    def _optimal(self):
        # Needs page sequence context
        if None in [frame.page for frame in self.frames]:
            for frame in self.frames:
                if frame.page is None:
                    return frame
        future_indices = {}
        seq = self.page_sequence[self.seq_ptr+1:] if self.page_sequence else []
        for frame in self.frames:
            try:
                index = seq.index(frame.page)
                future_indices[frame] = index
            except ValueError:
                # Not used again
                return frame
        # Find page used farthest in future
        farthest = -1
        victim = None
        for frame, idx in future_indices.items():
            if idx > farthest:
                farthest = idx
                victim = frame
        return victim if victim else self.frames[0]

    def access_page(self, page_id):
        self.time += 1
        self.seq_ptr += 1
        if page_id in self.page_table and self.page_table[page_id] in self.frames:
            frame = self.page_table[page_id]
            frame.last_used = self.time
            self.history.append({
                "page": page_id,
                "status": "HIT",
                "frames": [f.page for f in self.frames],
                "queue": [f.page for f in self.queue]
            })
            return {
                "status": "HIT",
                "state": {
                    "frames": [f.page for f in self.frames],
                    "queue": [f.page for f in self.queue]
                }
            }

        # MISS - fault
        if self.algorithm == "FIFO":
            victim = self._fifo()
        elif self.algorithm == "LRU":
            victim = self._lru()
        elif self.algorithm == "MRU":
            victim = self._mru()
        elif self.algorithm == "LIFO":
            victim = self._lifo()
        elif self.algorithm == "OPTIMAL":
            victim = self._optimal()
        else:
            return {"status": "ERROR", "error": "Unknown algorithm"}

        # Remove old page mapping
        if victim.page:
            self.page_table.pop(victim.page)
            self.queue = [f for f in self.queue if f != victim]

        victim.page = page_id
        victim.last_used = self.time
        self.page_table[page_id] = victim
        self.queue.append(victim)
        self.history.append({
            "page": page_id,
            "status": "FAULT",
            "frames": [f.page for f in self.frames],
            "queue": [f.page for f in self.queue]
        })
        return {
            "status": "FAULT",
            "state": {
                "frames": [f.page for f in self.frames],
                "queue": [f.page for f in self.queue]
            }
        }

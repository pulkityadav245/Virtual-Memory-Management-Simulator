# backend/vmm_simulator.py

class PageFrame:
    def __init__(self, frame_id):
        self.frame_id = frame_id
        self.page = None
        self.last_used = 0

class VirtualMemoryManager:
    def __init__(self, num_frames):
        self.num_frames = num_frames
        self.frames = [PageFrame(i) for i in range(num_frames)]
        self.page_table = {}
        self.time = 0
        self.fifo_queue = []

    def access_page(self, page_id):
        self.time += 1
        if page_id in self.page_table and self.page_table[page_id] in self.frames:
            frame = self.page_table[page_id]
            frame.last_used = self.time
            return "HIT"

        # MISS - page fault
        victim = None
        if None in [frame.page for frame in self.frames]:
            for frame in self.frames:
                if frame.page is None:
                    victim = frame
                    break
        else:
            # FIFO Replacement
            victim = self.fifo_queue.pop(0)
        if victim:
            # Remove existing mapping
            if victim.page:
                self.page_table.pop(victim.page)
            victim.page = page_id
            self.page_table[page_id] = victim
            self.fifo_queue.append(victim)
            return "FAULT"
        return "ERROR"

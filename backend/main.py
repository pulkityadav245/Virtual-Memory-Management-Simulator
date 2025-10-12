# In main.py:
from fastapi import FastAPI
from pydantic import BaseModel
from vmm_simulator import VirtualMemoryManager

app = FastAPI()
vmm = None  # Start with no VMM

class InitRequest(BaseModel):
    num_frames: int

class MemoryRequest(BaseModel):
    page_id: int

@app.post("/init")
def init_vmm(init_req: InitRequest):
    global vmm
    vmm = VirtualMemoryManager(num_frames=init_req.num_frames)
    return {"msg": f"VMM initialized with {init_req.num_frames} frames"}

@app.post("/access")
def access_page(req: MemoryRequest):
    global vmm
    if vmm is None:
        return {"error": "VMM not initialized. Set frame count first."}
    result = vmm.access_page(req.page_id)
    state = {"frames": [frame.page for frame in vmm.frames], "fifo_queue": [frame.page for frame in vmm.fifo_queue]}
    return {"status": result, "state": state}

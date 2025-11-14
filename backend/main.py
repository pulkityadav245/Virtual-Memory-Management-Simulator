from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .vmm_simulator import VirtualMemoryManager
from backend.ai.gpt_explainer import explain_event

# ---------------------------------------------------------
# 🚀 FastAPI App Setup
# ---------------------------------------------------------
app = FastAPI(title="Virtual Memory Simulator Backend", version="2.0")

# Allow frontend requests (Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this for security later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 🧠 Simulator Instance
# ---------------------------------------------------------
vmm: VirtualMemoryManager | None = None


# ---------------------------------------------------------
# 📦 Pydantic Models
# ---------------------------------------------------------
class InitRequest(BaseModel):
    num_frames: int
    algorithm: str
    page_sequence: list | None = None


class AccessRequest(BaseModel):
    page_id: int


# ---------------------------------------------------------
# 🧩 API Endpoints
# ---------------------------------------------------------

@app.post("/init")
async def init_sim(req: InitRequest):
    """
    Initialize the virtual memory simulator with a given algorithm and number of frames.
    """
    global vmm
    try:
        vmm = VirtualMemoryManager(req.num_frames, req.algorithm.upper(), req.page_sequence)
        return {
            "msg": f"Simulator initialized with {req.num_frames} frames "
                   f"and algorithm {req.algorithm.upper()}"
        }
    except Exception as e:
        return {"status": "error", "msg": f"Initialization failed: {str(e)}"}


@app.post("/access")
async def access_sim(req: AccessRequest):
    """
    Access a page in the current simulator instance and return the result
    along with a detailed AI-generated explanation.
    """
    global vmm
    if vmm is None:
        return {
            "status": "error",
            "ai_explanation": "Simulator not initialized. Please initialize first."
        }

    # Run simulation step
    try:
        result = vmm.access_page(req.page_id)
    except Exception as e:
        return {
            "status": "error",
            "ai_explanation": f"Simulation error: {str(e)}"
        }

    # Construct log description for AI explanation
    log = (
        f"Algorithm: {vmm.algorithm} | "
        f"Accessed Page: {req.page_id} | "
        f"Result: {result['status']} | "
        f"Frames: {result['state']['frames']} | "
        f"Queue: {result['state']['queue']}"
    )

    # Generate AI explanation using Gemini
    try:
        explanation = explain_event(log)
    except Exception as e:
        explanation = f"AI explanation not available due to error: {str(e)}"

    # Attach explanation to the result
    result["ai_explanation"] = explanation
    return result


@app.get("/")
async def root():
    """
    Root endpoint to verify the backend is running.
    """
    return {"msg": "✅ Virtual Memory Simulator Backend is running with AI integration."}

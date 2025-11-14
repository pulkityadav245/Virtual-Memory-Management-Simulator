### Virtual Memory Manager (VMM) Simulator ###

# An interactive educational simulator for the FIFO page replacement algorithm in Operating Systems, built using Python, FastAPI, and Streamlit.

 🚀 Features
# FIFO Page Replacement simulation and visualization.

# Interactive Streamlit UI: visualize frame and queue state at every page access.

# FastAPI backend: clean APIs for initializing and running simulation steps.

Summary statistics: page HITs, FAULTs, and more.

# 🛠️ Tech Stack
Frontend: Streamlit (Python)

Backend: FastAPI (Python)

Algorithm: FIFO page replacement via OOP-based VirtualMemoryManager.

# Project Structure
 
    ai-enhanced-vmm/
│
├── ai/          # optional, stores AI helper code
├── backend/     # FastAPI backend, core FIFO logic and APIs
│    ├── main.py
│    ├── vmm_simulator.py
├── frontend/    # Streamlit interactive simulation UI
│    ├── app.py
├── docs/        # Documentation, diagrams, etc.
├── README.md


# 🏃 How to Run
1. Clone the repository

bash
git clone https://github.com/pulkityadav245/Virtual-Memory-Management-Simulator.git
cd Virtual-Memory-Management-Simulator

2. Install requirements
You’ll need Python 3.8+.

bash
pip install -r requirements.txt
Or individually:

bash
pip install fastapi uvicorn streamlit pydantic

3. Run the FastAPI Backend
bash
cd backend
uvicorn main:app --reload
This should show the backend running at http://localhost:8000.

4. Run the Streamlit Frontend
bash
cd ../frontend
streamlit run app.py
5. Open the simulator UI
Go to http://localhost:8501 in your browser.

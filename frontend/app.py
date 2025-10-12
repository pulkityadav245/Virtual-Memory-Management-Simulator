import streamlit as st
import requests

st.set_page_config(page_title="VMM Simulator", layout="centered")
st.title("🧮 Virtual Memory Simulator")

backend_url = "http://localhost:8000"

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = False
if 'page_history' not in st.session_state:
    st.session_state['page_history'] = []

# Input for number of frames
num_frames = st.number_input("Enter Number of Frames", min_value=1, max_value=20, step=1, value=4)
if st.button("Initialize Simulator"):
    res = requests.post(f"{backend_url}/init", json={"num_frames": num_frames})
    if res.status_code == 200 and "msg" in res.json():
        st.success(res.json()["msg"])
        st.session_state["initialized"] = True
        st.session_state["page_history"] = []
    else:
        st.error("Failed to initialize VMM backend.")

# Input for page reference string (sequence)
st.subheader("Page Reference String")
page_seq = st.text_input("Enter sequence of page IDs (comma-separated)", "7, 0, 1, 2, 0, 3, 0, 4")
if st.button("Run Sequence") and st.session_state.get("initialized"):
    pages = [int(x.strip()) for x in page_seq.split(",") if x.strip().isdigit()]
    history = []
    for page_id in pages:
        res = requests.post(f"{backend_url}/access", json={"page_id": page_id})
        if res.status_code == 200:
            history.append((page_id, res.json()))
        else:
            history.append((page_id, {"status": "error", "ai_explanation": "Backend error."}))
    st.session_state["page_history"] = history

# Show simulation history (Visualized)
if st.session_state.get("page_history"):
    st.subheader("Simulation Results (Step Visualization)")
    total_hits = 0
    total_faults = 0
    for i, (page_id, result) in enumerate(st.session_state["page_history"]):
        status = result.get("status", "error")
        frames = result.get("state", {}).get("frames", [])
        queue = result.get("state", {}).get("fifo_queue", [])
        explanation = result.get("ai_explanation", "")

        # Count HIT/FAULT
        if status == "HIT":
            total_hits += 1
        elif status == "FAULT":
            total_faults += 1

        st.markdown(f"**Step {i+1}: Page `{page_id}` ({status})**")
        cols = st.columns(len(frames) if frames else 1)
        for idx, val in enumerate(frames):
            color = "#28a745" if val == page_id else "#141c26"
            frame_txt = f"<div style='padding:12px;border-radius:8px;background:{color};color:#fff;text-align:center'><b>{val if val is not None else 'EMPTY'}</b><br/><span style='font-size:0.8em;'>Frame {idx}</span></div>"
            cols[idx].markdown(frame_txt, unsafe_allow_html=True)
        st.markdown("**FIFO Queue:**")
        st.markdown(' ➡️ '.join([f"`{key}`" if key is not None else "EMPTY" for key in queue]))
        st.markdown(f"🧠 <b>AI Explanation:</b> {explanation}", unsafe_allow_html=True)
        st.markdown("---")

    # Show HIT and FAULT Summary at end
    st.success(f"Total HITs: {total_hits}")
    st.error(f"Total FAULTs (Page Faults): {total_faults}")

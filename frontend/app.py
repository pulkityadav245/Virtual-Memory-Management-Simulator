import streamlit as st
import requests
import plotly.graph_objs as go

st.set_page_config(page_title="VMM Simulator", layout="centered")
st.title("🧮 Virtual Memory Simulator")

backend_url = "http://localhost:8000"

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = False
if 'page_history' not in st.session_state:
    st.session_state['page_history'] = []
if 'history_raw' not in st.session_state:
    st.session_state['history_raw'] = []
if 'selected_algorithm' not in st.session_state:
    st.session_state['selected_algorithm'] = "FIFO"

algorithm_option = st.selectbox(
    "Select Page Replacement Algorithm",
    options=["FIFO", "LRU", "MRU", "LIFO", "OPTIMAL"],
    index=0
)
st.session_state['selected_algorithm'] = algorithm_option

num_frames = st.number_input("Enter Number of Frames", min_value=1, max_value=20, step=1, value=4)
st.subheader("Page Reference String")
page_seq = st.text_input("Enter sequence of page IDs (comma-separated)", "7, 0, 1, 2, 0, 3, 0, 4")

if st.button("Initialize Simulator"):
    pages = [int(x.strip()) for x in page_seq.split(",") if x.strip().isdigit()]
    payload = {
        "num_frames": num_frames,
        "algorithm": algorithm_option,
        "page_sequence": pages if algorithm_option == "OPTIMAL" else []
    }
    res = requests.post(f"{backend_url}/init", json=payload)
    if res.status_code == 200 and "msg" in res.json():
        st.success(res.json()["msg"])
        st.session_state["initialized"] = True
        st.session_state["page_history"] = []
        st.session_state["history_raw"] = []
    else:
        st.error("Failed to initialize VMM backend.")

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
    st.session_state["history_raw"] = history  # For animation

# --- Animation first ---
if st.session_state.get("history_raw"):
    st.subheader("Animated Page Frames (Step-by-Step)")
    frames_data = st.session_state["history_raw"]
    plot_frames = []
    for idx, (page_id, result) in enumerate(frames_data):
        frame_vals = result.get("state", {}).get("frames", [])
        bars = go.Bar(x=[f"Frame {i}" for i in range(len(frame_vals))],
                      y=[val if val is not None else 0 for val in frame_vals],
                      marker_color=['green' if val == page_id else 'blue' for val in frame_vals])
        queue = result.get("state", {}).get("queue", [])
        queue_str = ' ➡️ '.join([f"{key}" if key is not None else "EMPTY" for key in queue])
        plot_frames.append(go.Frame(
            data=[bars],
            layout=go.Layout(
                title=dict(text=f"Step {idx+1}: Access page {page_id} - {result.get('status','error')}<br><span style='font-size:0.8em;'>Queue: {queue_str}</span>")
            )
        ))

    frame0_vals = frames_data[0][1].get("state", {}).get("frames", [])
    queue0 = frames_data[0][1].get("state", {}).get("queue", [])
    queue0_str = ' ➡️ '.join([f"{key}" if key is not None else "EMPTY" for key in queue0])

    fig = go.Figure(
        data=[go.Bar(x=[f"Frame {i}" for i in range(len(frame0_vals))],
                     y=[val if val is not None else 0 for val in frame0_vals],
                     marker_color=['blue' for _ in frame0_vals])],
        frames=plot_frames
    )
    fig.update_layout(
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 3000, "redraw": True}, "transition": {"duration": 700}, "fromcurrent": True, "mode": "immediate"}]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
                },
            ],
            "showactive": True
        }],
        title=f"Step 1: Access page {frames_data[0][0]} - {frames_data[0][1].get('status','error')}<br><span style='font-size:0.8em;'>Queue: {queue0_str}</span>",
        xaxis_title="Frames",
        yaxis_title="Page ID",
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Static detailed step-by-step after animation ---
if st.session_state.get("page_history"):
    st.subheader("Simulation Static Results (Step Visualization Table)")
    total_hits = 0
    total_faults = 0
    for i, (page_id, result) in enumerate(st.session_state["page_history"]):
        status = result.get("status", "error")
        frames = result.get("state", {}).get("frames", [])
        queue = result.get("state", {}).get("queue", [])
        explanation = result.get("ai_explanation", "")
        if status == "HIT":
            total_hits += 1
        elif status == "FAULT":
            total_faults += 1

        st.markdown(f"**Step {i+1}: Page `{page_id}` ({status}) | Algorithm: `{algorithm_option}`**")
        cols = st.columns(len(frames) if frames else 1)
        for idx, val in enumerate(frames):
            color = "#28a745" if val == page_id else "#141c26"
            frame_txt = f"<div style='padding:12px;border-radius:8px;background:{color};color:#fff;text-align:center'><b>{val if val is not None else 'EMPTY'}</b><br/><span style='font-size:0.8em;'>Frame {idx}</span></div>"
            cols[idx].markdown(frame_txt, unsafe_allow_html=True)
        st.markdown(f"**Order/Queue (Algorithm View):**")
        st.markdown(' ➡️ '.join([f"`{key}`" if key is not None else "EMPTY" for key in queue]))
        st.markdown(f"🧠 <b>AI Explanation:</b> {explanation}", unsafe_allow_html=True)
        st.markdown("---")

    st.success(f"Total HITs: {total_hits}")
    st.error(f"Total FAULTs (Page Faults): {total_faults}")

import streamlit as st
import time
from self_moa_pipeline import generate_drafts, aggregate_drafts, MODEL

# Must be the first Streamlit command
st.set_page_config(
    page_title="Self-MoA 2026",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Rich Aesthetics ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Headers */
    h1, h2, h3 {
        color: #4DB6AC !important;
        font-family: 'Inter', sans-serif;
    }
    /* Accent color for buttons */
    .stButton>button {
        background-color: #4DB6AC;
        color: #000000;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #26A69A;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(77, 182, 172, 0.4);
    }
    /* Draft boxes */
    .draft-box {
        background-color: #1E2127;
        border-left: 4px solid #4DB6AC;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    /* Final output box */
    .final-box {
        background-color: #121A21;
        border: 2px solid #4DB6AC;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(77, 182, 172, 0.15);
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #161A22;
    }
</style>
""", unsafe_allow_html=True)

# --- App Header ---
st.title("🧠 Self-MoA Pipeline (2026 Edition)")
st.markdown(f"**Powered by:** `{MODEL}` | **Architecture:** `Temperature Scaling & Single Pass Reasoning`")
st.markdown("---")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Self-MoA Core Settings")
    st.markdown("Adjust the pipeline parameters for the reasoning engine.")
    
    num_drafts = st.slider("Number of Drafts (Proposers)", min_value=2, max_value=12, value=8, step=1, 
                           help="More drafts provide diverse perspectives but increase cost and latency.")
    
    # We restrict temperature to 0.7 to avoid hallucinations as per benchmark analysis
    temperature_val = st.slider("Proposer Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1,
                                help="Higher values increase creativity. Set to 0.7 for optimal reasoning without extreme hallucination.")
    
    st.markdown("---")
    st.header("⚖️ Aggregator Settings")
    
    default_criteria = """1. Act as a Critical Judge. 
2. Analyze the contradictions between the proposed solutions.
3. Extract the safest, most scalable, and highest-quality design.
4. Format the response with clear hierarchical Markdown headers.
5. Provide a single, definitive, flawless final answer."""
    
    criteria = st.text_area("Evaluation Criteria (In-Context Reasoning)", value=default_criteria, height=200)

# --- Main Interface ---
prompt = st.text_area("What complex problem would you like to solve?", height=150, 
                      placeholder="e.g., Design a highly secure and scalable microservices architecture for a real-time banking application...")

if st.button("🚀 Execute Self-MoA Pipeline"):
    if not prompt.strip():
        st.warning("Please enter a prompt to begin.")
    else:
        # Containers for dynamic UI updates
        progress_container = st.empty()
        status_text = st.empty()
        
        # --- Stage 1 & 2: Proposing ---
        start_time = time.time()
        
        with st.status("🧠 Phase 1: Generating Diverse Drafts...", expanded=True) as status:
            st.write(f"Generating {num_drafts} concurrent drafts at temperature {temperature_val}...")
            drafts = generate_drafts(prompt, num_drafts=num_drafts, temperatures=[temperature_val])
            
            if not drafts or all(d.startswith("Error") for d in drafts):
                status.update(label="❌ Failed to generate drafts.", state="error", expanded=True)
                st.stop()
                
            status.update(label=f"✅ Successfully generated {len(drafts)} drafts!", state="complete", expanded=False)
            
        drafts_time = time.time() - start_time
        
        # --- Display Drafts (Optional, in an expander) ---
        with st.expander(f"👀 View all {len(drafts)} generated drafts (Raw Proposer Outputs)"):
            cols = st.columns(2)
            for i, draft in enumerate(drafts):
                col_idx = i % 2
                with cols[col_idx]:
                    st.markdown(f"**Draft {i+1}**")
                    st.markdown(f"<div class='draft-box'>{draft[:800]}...<br><i>(Truncated for preview)</i></div>", unsafe_allow_html=True)

        # --- Stage 3: Aggregation ---
        st.markdown("---")
        with st.spinner("⚖️ Phase 2: Performing Single Pass In-Context Reasoning..."):
            agg_start_time = time.time()
            final_answer = aggregate_drafts(prompt, drafts, criteria=criteria)
            agg_time = time.time() - agg_start_time

        # --- Final Output ---
        st.subheader("🎯 Definitive Final Answer")
        st.markdown(f"<div class='final-box'>{final_answer}</div>", unsafe_allow_html=True)
        
        # --- Metrics ---
        total_time = drafts_time + agg_time
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Draft Generation Time", f"{drafts_time:.2f}s")
        m2.metric("Aggregation Time", f"{agg_time:.2f}s")
        m3.metric("Total Latency", f"{total_time:.2f}s")
        
        st.success("Pipeline execution complete!")

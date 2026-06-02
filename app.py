import streamlit as st
import time
import os
import csv
import subprocess
from self_moa_pipeline import generate_drafts, aggregate_drafts, MODEL, DEFAULT_API_KEY, DEFAULT_BASE_URL

def load_csv_data(filepath):
    """Safely loads a CSV file into a list of dictionaries in pure Python to avoid DLL blockages"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        st.error(f"Error reading {filepath}: {e}")
        return []

# Set premium page layout and configuration
st.set_page_config(
    page_title="Self-MoA Advanced Pipeline Console",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Premium CSS for Rich Aesthetics & Arabic Support ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main body styling */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111520 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Header Gradient styling */
    .main-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(20, 26, 38, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(0, 242, 254, 0.2);
        box-shadow: 0 12px 40px 0 rgba(0, 242, 254, 0.05);
    }
    
    /* Draft Box styling */
    .draft-box {
        background: rgba(15, 23, 42, 0.4);
        border-left: 4px solid #00f2fe;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #CBD5E1;
        border-top: 1px solid rgba(255,255,255,0.02);
        border-right: 1px solid rgba(255,255,255,0.02);
        border-bottom: 1px solid rgba(255,255,255,0.02);
    }
    
    /* Final Synthesis Box styling */
    .final-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.25);
        padding: 2.2rem;
        border-radius: 18px;
        box-shadow: 0 16px 48px rgba(0, 242, 254, 0.08);
        line-height: 1.75;
        font-size: 1.05rem;
        color: #F8FAFC;
    }
    
    /* Metric Card styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #00f2fe !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif;
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #94A3B8;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #00f2fe;
    }

    .stTabs [aria-selected="true"] {
        color: #00f2fe !important;
        border-bottom-color: #00f2fe !important;
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #0B0E14 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.5) !important;
        color: #ffffff !important;
    }
    
    /* Arabic alignment support classes */
    .rtl-text {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Self-MoA Core Engine")
    st.markdown("Configure runtime variables and API keys.")
    
    # 1. API Keys & Endpoint configuration
    with st.expander("🔑 API Credentials Override", expanded=False):
        api_key_input = st.text_input(
            "OpenRouter/OpenAI API Key",
            type="password",
            value="",
            placeholder="sk-or-v1-...",
            help="If left blank, the environment variable or built-in default key will be used."
        )
        base_url_input = st.text_input(
            "API Base URL",
            value=DEFAULT_BASE_URL,
            placeholder="https://openrouter.ai/api/v1"
        )
        model_input = st.text_input(
            "Active Pipeline Model",
            value=MODEL,
            placeholder="qwen/qwen3.5-flash-02-23"
        )

    # Resolve active credentials
    active_key = api_key_input.strip() if api_key_input.strip() else None
    active_url = base_url_input.strip() if base_url_input.strip() else None
    active_model = model_input.strip() if model_input.strip() else None

    st.markdown("---")
    st.markdown("### 🎛️ Pipeline Parameters")
    
    num_drafts = st.slider(
        "Number of Proposers (N)",
        min_value=2,
        max_value=12,
        value=6,
        step=1,
        help="Higher numbers provide more diverse starting ideas but increase API cost."
    )
    
    temperature_val = st.slider(
        "Proposer Temperature Scale",
        min_value=0.1,
        max_value=1.5,
        value=0.7,
        step=0.1,
        help="Standard is 0.7. 1.0+ increases creativity/diversity but can trigger hallucinations."
    )
    
    st.markdown("---")
    st.markdown("### ⚖️ In-Context Arbiter Rules")
    
    default_criteria = """1. Act as a Critical Judge.
2. Analyze the contradictions between the proposed solutions.
3. Extract the safest, most scalable, and highest-quality design.
4. Format the response with clear hierarchical Markdown headers.
5. Provide a single, definitive, flawless final answer."""
    
    criteria = st.text_area("Aggregator Evaluation Guidelines", value=default_criteria, height=180)

# --- App Layout Header ---
st.markdown("<div class='main-title'>🧠 Self-MoA Advanced Console</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Scale-free Local Mixture-of-Agents Pipeline with Single Pass In-Context Synthesis</div>", unsafe_allow_html=True)

# Setup tabs
tab1, tab2, tab3 = st.tabs([
    "🎯 Interactive Solver (الموجه التفاعلي)",
    "📊 Benchmark Analytics (مقارنة الأداء والتقييم)",
    "📖 System Architecture (هيكلية العمل ودليل التشغيل)"
])

# --- TAB 1: INTERACTIVE SOLVER ---
with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("💡 Input Complex Reasoning Task")
    st.markdown("Enter a logic puzzle, system architecture challenge, or highly mathematical query that benefits from collaborative reasoning.")
    
    prompt = st.text_area(
        "Problem Statement",
        height=140,
        placeholder="e.g., A pirate captain needs to divide 100 gold coins among 5 rational pirates. What proposal should he make to survive and maximize coins? Explain step by step."
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("🚀 Trigger Self-MoA Pipeline"):
        if not prompt.strip():
            st.warning("Please enter a valid problem statement to proceed.")
        else:
            # Containers for active progress tracking
            st.markdown("### ⛓️ Pipeline Execution Logs")
            
            step1_status = st.status("Phase 1: Generating Diverse Drafts (Concurrent Threads)...", expanded=True)
            with step1_status:
                st.write(f"Initiating {num_drafts} proposer threads using model: `{active_model or MODEL}`...")
                start_time = time.time()
                
                # Execute concurrently inside the pipeline (first is temp 0.0, rest are scaled)
                drafts = generate_drafts(
                    prompt=prompt,
                    num_drafts=num_drafts,
                    temperatures=[temperature_val],
                    api_key=active_key,
                    base_url=active_url,
                    model=active_model
                )
                
                drafts_time = time.time() - start_time
                if not drafts or all(d.startswith("Error") for d in drafts):
                    step1_status.update(label="❌ Draft Generation Failed.", state="error")
                    st.stop()
                    
                step1_status.update(label=f"✅ Successfully generated {len(drafts)} drafts ({drafts_time:.2f}s)", state="complete", expanded=False)

            # Display drafts in side-by-side expandable preview
            with st.expander(f"🔍 Expand to Preview Raw Drafts (N={len(drafts)})"):
                cols = st.columns(2)
                for idx, draft in enumerate(drafts):
                    with cols[idx % 2]:
                        st.markdown(f"**Draft {idx + 1} (Temp: {0.0 if idx == 0 else temperature_val})**")
                        st.markdown(f"<div class='draft-box'>{draft[:500]}...<br><br><i>(Truncated preview)</i></div>", unsafe_allow_html=True)

            # Stage 2: In-Context Reasoning & Aggregation
            step2_status = st.status("Phase 2: In-Context Aggregation (Single Pass Synthesis)...", expanded=True)
            with step2_status:
                st.write("Constructing compound prompt and calling expert evaluator...")
                agg_start_time = time.time()
                
                final_answer = aggregate_drafts(
                    prompt=prompt,
                    drafts=drafts,
                    criteria=criteria,
                    api_key=active_key,
                    base_url=active_url,
                    model=active_model
                )
                
                agg_time = time.time() - agg_start_time
                step2_status.update(label=f"✅ Synthesis Complete ({agg_time:.2f}s)", state="complete", expanded=False)

            # Show results and performance metrics
            st.markdown("### 🎯 Final Synthesized Output")
            st.markdown(f"<div class='final-box'>{final_answer}</div>", unsafe_allow_html=True)
            
            st.markdown("### ⏱️ Performance Metrics")
            m1, m2, m3 = st.columns(3)
            m1.metric("Proposer Phase Duration", f"{drafts_time:.2f} s")
            m2.metric("Aggregator Phase Duration", f"{agg_time:.2f} s")
            m3.metric("Total Latency", f"{drafts_time + agg_time:.2f} s")

# --- TAB 2: BENCHMARK ANALYTICS ---
with tab2:
    st.markdown("### 📊 Benchmark Control Center")
    st.markdown("Evaluate the Self-MoA pipeline compared to standard zero-shot models like Claude Opus on complex deductive tasks and MMLU questions.")
    
    col_bench_1, col_bench_2 = st.columns(2)
    
    with col_bench_1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🧪 Run Custom Benchmarks")
        st.markdown("Trigger automated benchmarks directly from the UI. Note: Running evaluations can take 1-3 minutes and consumes API tokens.")
        
        bench_mode = st.selectbox(
            "Select Benchmark Target",
            ["Logic Benchmarks (Self-MoA vs Claude)", "Automated MMLU (100 Questions Benchmark)"]
        )
        
        if st.button("▶️ Execute Selected Benchmark"):
            status_container = st.empty()
            with st.spinner(f"Running {bench_mode}... Please wait."):
                try:
                    if bench_mode == "Logic Benchmarks (Self-MoA vs Claude)":
                        import benchmark_logic
                        # Setup environment overrides
                        if active_key: os.environ["OPENAI_API_KEY"] = active_key
                        if active_url: os.environ["OPENAI_BASE_URL"] = active_url
                        
                        benchmark_logic.run_benchmark()
                        
                        # Generate chart
                        import llm_judge_and_chart
                        llm_judge_and_chart.evaluate_and_chart()
                        st.success("Logic benchmark successfully finished! Charts updated below.")
                    else:
                        import mmlu_evaluator
                        if active_key: os.environ["OPENAI_API_KEY"] = active_key
                        if active_url: os.environ["OPENAI_BASE_URL"] = active_url
                        if active_model: os.environ["OPENAI_MODEL"] = active_model
                        
                        mmlu_evaluator.main()
                        st.success("MMLU evaluation completed successfully! CSV updated.")
                except Exception as e:
                    st.error(f"Execution Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_bench_2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📈 LLM-As-A-Judge Visual Chart")
        
        # Display the generated chart if it exists
        if os.path.exists("evaluation_chart.png"):
            st.image("evaluation_chart.png", caption="Benchmark Quality Scores (Claude Opus vs Self-MoA)", use_column_width=True)
        else:
            st.info("No comparison chart found. Click 'Execute Selected Benchmark' to run the benchmark logic and generate this visualization.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Load and display CSV outputs
    st.markdown("---")
    st.subheader("📋 Evaluation Datasets & Historical Runs")
    
    csv_tab_1, csv_tab_2 = st.tabs(["Logic Evaluation Results", "MMLU Automated Results"])
    
    with csv_tab_1:
        logic_data = load_csv_data("evaluation_results.csv")
        if logic_data:
            st.dataframe(logic_data, use_container_width=True)
        else:
            st.info("No logic evaluation history found. File 'evaluation_results.csv' is empty.")
            
    with csv_tab_2:
        mmlu_data = load_csv_data("mmlu_evaluation_results.csv")
        if mmlu_data:
            st.dataframe(mmlu_data, use_container_width=True)
            
            # Simple summary metrics calculated in pure Python
            try:
                base_latencies = [float(row["Baseline_Latency"]) for row in mmlu_data if "Baseline_Latency" in row and row["Baseline_Latency"]]
                moa_latencies = [float(row["MoA4_Latency"]) for row in mmlu_data if "MoA4_Latency" in row and row["MoA4_Latency"]]
                
                avg_base = sum(base_latencies) / len(base_latencies) if base_latencies else 0.0
                avg_moa = sum(moa_latencies) / len(moa_latencies) if moa_latencies else 0.0
                
                c1, c2 = st.columns(2)
                c1.metric("Baseline Avg Latency", f"{avg_base:.2f} s")
                c2.metric("Self-MoA Avg Latency", f"{avg_moa:.2f} s")
            except Exception as e:
                st.warning(f"Could not compute average metrics: {e}")
        else:
            st.info("No MMLU automated history found. File 'mmlu_evaluation_results.csv' is empty.")

# --- TAB 3: SYSTEM ARCHITECTURE & MANUAL ---
with tab3:
    col_lang_1, col_lang_2 = st.columns(2)
    
    with col_lang_1:
        st.markdown("""
        <div class='glass-card rtl-text'>
        <h3 style="color:#00f2fe;">🧠 نظرة عامة على معماريّة Self-MoA</h3>
        <p>هيكل <strong>Self-MoA (Self-Mixture of Agents)</strong> هو مقاربة متقدّمة لتسريع وتبسيط نماذج الذكاء الاصطناعي التوليدي المعقّدة عن طريق دمج عدة آراء مختلفة صادرة من نفس النموذج وتوليفها في رد نهائي فائق الدقة.</p>
        
        <h4 style="color:#00f2fe;">⚙️ مراحل المعالجة الثلاثة:</h4>
        <ol>
            <li><strong>مرحلة توحيد الأدوار (Role Unification):</strong> يتم تهيئة النماذج الفرعية للعمل كمقترحين للحلول المتنوعة.</li>
            <li><strong>مرحلة التنوع الداخلي (In-model Diversity):</strong> نقوم بتوليد مسودات متعددة متزامنة باستخدام قيم مختلفة لدرجة الحرارة (Temperature Scaling). نحصل على حل أساسي دقيق عند درجة 0.0 وحلول إبداعية بديلة عند درجات أعلى (مثل 0.7).</li>
            <li><strong>مرحلة الدمج والتوليف أحادي المسار (Single-Pass Aggregation):</strong> يتم تغذية جميع المسودات الناتجة في سياق نافذة محادثة ضخمة واحدة للنموذج ليعمل كـ "حكيم ومقيّم ناقد". يقوم النموذج بتحليل التعارضات وتوليف الإجابة النهائية المثالية دفعة واحدة بدون الحاجة لعدّة محادثات متتالية ومكلفة ماديّاً.</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
    with col_lang_2:
        st.markdown("""
        <div class='glass-card'>
        <h3 style="color:#00f2fe;">🧠 Architecture & Operational Flow</h3>
        <p>The <strong>Self-MoA (Self-Mixture of Agents)</strong> pipeline is an advanced design pattern that leverages self-reflection and multi-draft consensus from a single base LLM to deliver highly robust answers without the massive cost of standard multi-model MoA networks.</p>
        
        <h4 style="color:#00f2fe;">⚙️ The Three Core Pipeline Stages:</h4>
        <ol>
            <li><strong>Stage 1: Role Unification:</strong> Instructing concurrent worker instances to formulate discrete, targeted strategies for the user query.</li>
            <li><strong>Stage 2: In-model Diversity via Temp Scaling:</strong> Spawning multiple draft solutions in parallel. The baseline draft runs at Temperature 0.0 for deterministic logic, while sibling drafts run at scaled temperature levels (e.g. 0.7) to explore creative alternate approaches.</li>
            <li><strong>Stage 3: Single Pass In-Context Synthesis:</strong> Feeding all sibling drafts into a single massive context window to act as an Expert Arbiter. The model identifies contradictions, resolves logic loops, and synthesizes the final definitive solution in a single pass, saving latency and token cost.</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

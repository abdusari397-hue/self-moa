# 🧠 Self-MoA Pipeline: Self-Mixture of Agents (2026 Edition)

Welcome to the **Self-MoA (Self-Mixture of Agents)** repository. This project implements a high-fidelity pipeline that improves reasoning, coding, and mathematical accuracy by gathering diverse initial solutions from a single base model and synthesizing them into a definitive, logical final response. It achieves Mixture-of-Agents class performance without the latency and billing costs of standard multi-model configurations.

---

## ⚙️ How the Self-MoA Architecture Works

The Self-MoA framework operates across three key pipeline stages:

1. **Stage 1: Role Unification**
   Configuring worker instructions to serve as specialized strategy proposers for the user query.

2. **Stage 2: In-Model Diversity via Temperature Scaling**
   Generating dynamic, concurrent sibling drafts in the background. A baseline draft is created at `Temperature 0.0` for rigid deductive stability, while subsequent drafts are scaled with higher temperatures (e.g. `0.7` to `1.0`) to explore alternative paths.

3. **Stage 3: Single Pass In-Context Synthesis**
   Feeding all concurrent drafts and the initial prompt into a massive single context window. The base LLM acts as an expert arbiter to locate logic leaks, resolve contradictions, and synthesize a singular, highly accurate definitive answer in one single pass, dramatically lowering latency and token cost.

---

## 🚀 Upgraded Streamlit Console Features

* **Premium Dark Aesthetics:** Sleek modern interface utilizing a clean glassmorphism layout, subtle glowing accents, and optimized responsiveness.
* **Flexible Credentials Override:** Easily swap your API Key, Endpoint Base URL, and Model configuration dynamically in the sidebar at runtime.
* **Integrated Evaluation Dashboard:** Monitor benchmark databases, execute validation suites (Logic Battle or MMLU), and render evaluation analytical graphs directly in the browser.
* **Detailed Pipeline Visualizer:** Review generated worker drafts side-by-side to understand the system's collaborative logical flow.

---

## 💻 Local Installation & Workspace Setup

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your system.

### 2. Clone the Repository
Clone this codebase to your workspace:
```bash
git clone https://github.com/abdusari397-hue/self-moa.git
cd self-moa
```

### 3. Establish a Virtual Environment (Recommended)
* **On Windows:**
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  ```
* **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables (Optional)
The pipeline automatically parses the `OPENAI_API_KEY` and `OPENAI_BASE_URL` from the OS environment, with a built-in OpenRouter fallback.
* **Windows CMD:**
  ```cmd
  set OPENAI_API_KEY="your_api_key"
  ```
* **Windows PowerShell:**
  ```powershell
  $env:OPENAI_API_KEY="your_api_key"
  ```
* **macOS / Linux:**
  ```bash
  export OPENAI_API_KEY="your_api_key"
  ```

### 6. Run the Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 🛠️ CLI Operations & Performance Evaluation

### A. Direct Pipeline Execution
Launch a custom prompt with dynamic drafts and specific temperature ranges:
```bash
python self_moa_pipeline.py --prompt "Design a resilient event-driven architecture." --drafts 5 --temperatures 0.7 0.9 1.1
```

### B. Run the Comparative Logic Benchmark
Compare Zero-Shot baseline models against the Self-MoA orchestration framework:
```bash
python benchmark_logic.py
```
*This generates a markdown comparison document named `benchmark_results.md`.*

### C. Evaluate Results & Generate Visual Chart
Trigger the LLM-As-A-Judge evaluator to parse the comparison document, score the answers, and create an analytical bar chart:
```bash
python llm_judge_and_chart.py
```
*This creates the `evaluation_chart.png` asset.*

### D. Run Automated MMLU Dataset Assessment
Evaluate the pipeline against 100 questions from the standardized MMLU academic database to compute comparative accuracy, latency, and token cost metrics:
```bash
python mmlu_evaluator.py
```
*The metrics are exported to `mmlu_evaluation_results.csv` and rendered dynamically inside the Streamlit GUI.*

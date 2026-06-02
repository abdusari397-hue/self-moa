# 🧠 Self-MoA Pipeline: Self-Mixture of Agents (2026 Edition)

[**اللغة العربية (Arabic)**](#-دليل-التشغيل-والتثبيت-باللغة-العربية) | [**English Documentation**](#-english-setup--operation-guide)

---

## 🇸🇦 دليل التشغيل والتثبيت باللغة العربية

مرحباً بك في مستودع **Self-MoA (Self-Mixture of Agents)**. هذا المشروع عبارة عن بيئة برمجية متكاملة مصممة لتوليد إجابات فائقة الدقة للمسائل المنطقية والبرمجية المعقدة عن طريق دمج عدة حلول ومقترحات متنوعة صادرة من نموذج ذكاء اصطناعي واحد وتوليفها في رد نهائي فائق الجودة، وذلك دون تكبد التكاليف الباهظة للشبكات متعددة النماذج التقليدية.

### ⚙️ كيف تعمل بنية Self-MoA؟
تعتمد التقنية على ثلاث مراحل أساسية متكاملة لتقليل تكلفة التشغيل وزيادة الدقة:
1. **توحيد الأدوار (Role Unification):** تهيئة وإعداد النموذج ليعمل كمقترح ذكي للحلول المناسبة للمسألة.
2. **التنوع الداخلي عبر درجات الحرارة (In-model Diversity via Temp Scaling):** توليد مسودات متعددة متزامنة في الخلفية. يتم توليد مسودة أساسية عند درجة حرارة `0.0` للحصول على إجابة منطقية دقيقة، وتوليد المسودات المتبقية (Proposers) عند درجات حرارة أعلى (مثل `0.7`) لاستكشاف مقاربات بديلة وأفكار متنوعة.
3. **الدمج والتوليف أحادي المسار (Single Pass In-Context Synthesis):** تغذية كافة المسودات السابقة مع المسألة الأصلية داخل نافذة سياق ضخمة واحدة (Context Window) للنموذج ليعمل كـ "حَكَم ومقيّم ناقد" (Critical Judge). يقوم النموذج بتحليل التعارضات وتوليف الإجابة المثالية النهائية بدقة متناهية وبضربة واحدة (Single Pass) لتوفير التكلفة وزمن الاستجابة.

---

### 🚀 ميزات لوحة تحكم Streamlit المطورة:
* **واجهة مستخدم احترافية (Premium Dark UI):** تصميم عصري جذاب يعتمد على تأثيرات الزجاج (Glassmorphic) والألوان الهادئة المريحة للعين مع دعم كامل للتصفح المتجاوب.
* **إدارة ديناميكية للاتصال (API Credentials):** إمكانية إدخال وتعديل مفتاح الـ API، والـ Base URL، واسم النموذج المستخدم مباشرة من القائمة الجانبية للتطبيق دون الحاجة لتعديل الكود.
* **مركز التقييم والتحليلات (Benchmark Center):** إمكانية تشغيل اختبارات الذكاء والمقارنة بين أداء Self-MoA والحلول التقليدية مثل Claude Opus مباشرة من الواجهة وعرض الرسومات البيانية للنتائج.
* **عرض تفاعلي للمسودات:** ميزة إظهار كافة المسودات المتولدة في الخلفية لمتابعة تسلسل التفكير المنطقي للنظام.

---

### 💻 تثبيت وتشغيل النظام محلياً

#### 1. متطلبات التشغيل الأساسية:
تأكد من تثبيت Python الإصدار 3.9 أو أعلى في جهازك.

#### 2. استنساخ المستودع البرمجي:
إذا لم تقم بسحب المستودع بعد، قم بتشغيل الأمر التالي:
```bash
git clone https://github.com/abdusari397-hue/self-moa.git
cd self-moa
```

#### 3. إنشاء بيئة وهمية وتفعيلها (موصى به):
* **على نظام تشغيل Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```
* **على نظام تشغيل macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. تثبيت المكتبات المطلوبة:
قم بتثبيت جميع اعتمادات المشروع باستخدام ملف `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### 5. إعداد مفتاح الـ API (اختياري):
يمكنك تهيئة مفتاح OpenRouter أو OpenAI كمتغير بيئي في النظام أو إدخاله مباشرة في واجهة المستخدم الجانبية:
* **Windows CMD:**
```cmd
set OPENAI_API_KEY="your_openrouter_key_here"
```
* **Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="your_openrouter_key_here"
```
* **Linux / macOS:**
```bash
export OPENAI_API_KEY="your_openrouter_key_here"
```

#### 6. تشغيل واجهة المستخدم الرسومية (GUI):
لتشغيل لوحة تحكم التطبيق الرائعة، استخدم الأمر التالي:
```bash
streamlit run app.py
```

---

### 🛠️ التشغيل والتقييم عبر سطر الأوامر (CLI)

#### أ. تشغيل خط المعالجة المباشر:
يمكنك إرسال أي سؤال مباشرة من سطر الأوامر وتخصيص عدد المسودات ودرجات الحرارة:
```bash
python self_moa_pipeline.py --prompt "ما هي الطريقة المثلى لبناء قاعدة بيانات موزعة عالية التوافر؟" --drafts 4 --temperatures 0.6 0.9
```

#### ب. تشغيل اختبارات المقارنة المنطقية (Logic Benchmark):
لمقارنة أداء خط المعالجة ذو الفترات المتعددة مقابل النماذج التقليدية:
```bash
python benchmark_logic.py
```
*الأمر يقوم بإنشاء ملف النتائج المقارنة `benchmark_results.md`.*

#### ج. تشغيل التقييم الذكي والرسوم البيانية:
لتحليل نتائج ملف المقارنة وتوليد رسم بياني احترافي يوضح الفارق في الجودة والدقة:
```bash
python llm_judge_and_chart.py
```
*سيتم حفظ الرسم البياني باسم `evaluation_chart.png` وعرضه تلقائياً في لوحة تحكم التطبيق.*

#### د. تشغيل اختبار MMLU التلقائي:
لتشغيل اختبار معياري مؤتمت على 100 سؤال من قاعدة بيانات MMLU العالمية لحساب الدقة وتكلفة التكلفة الفردية:
```bash
python mmlu_evaluator.py
```
*يتم حفظ تقرير البيانات التفصيلي تلقائياً في ملف `mmlu_evaluation_results.csv`.*

---

## 🇺🇸 English Setup & Operation Guide

Welcome to the **Self-MoA (Self-Mixture of Agents)** repository. This project implements a high-fidelity pipeline that improves reasoning, coding, and mathematical accuracy by gathering diverse initial solutions from a single base model and synthesizing them into a definitive, logical final response. It achieves Mixture-of-Agents class performance without the latency and billing costs of standard multi-model configurations.

### ⚙️ How the Self-MoA Architecture Works
The Self-MoA framework operates across three key pipeline stages:
1. **Role Unification:** Configuring worker instructions to serve as specialized strategy proposers.
2. **In-Model Diversity via Temperature Scaling:** Generating dynamic, concurrent sibling drafts in the background. A baseline draft is created at `Temperature 0.0` for rigid deductive stability, while subsequent drafts are scaled with higher temperatures (e.g. `0.7` to `1.0`) to explore alternative paths.
3. **Single Pass In-Context Synthesis:** Feeding all concurrent drafts and the initial prompt into a massive single context window. The base LLM acts as an expert arbiter to locate logic leaks, resolve contradictions, and synthesize a singular, highly accurate definitive answer in one single pass.

---

### 🚀 Upgraded Streamlit Console Features:
* **Premium Dark Aesthetics:** Sleek modern interface utilizing a clean glassmorphism layout, subtle glowing accents, and optimized responsiveness.
* **Flexible Credentials Override:** Easily swap your API Key, Endpoint Base URL, and Model configuration dynamically in the sidebar at runtime.
* **Integrated Evaluation Dashboard:** Monitor benchmark databases, execute validation suites (Logic Battle or MMLU), and render evaluation analytical graphs directly in the browser.
* **Detailed Pipeline Visualizer:** Review generated worker drafts side-by-side to understand the system's collaborative logical flow.

---

### 💻 Local Installation & Workspace Setup

#### 1. Prerequisites:
Ensure you have Python 3.9 or higher installed on your system.

#### 2. Clone the Repository:
Clone this codebase to your workspace:
```bash
git clone https://github.com/abdusari397-hue/self-moa.git
cd self-moa
```

#### 3. Establish a Virtual Environment (Recommended):
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

#### 4. Install Dependencies:
```bash
pip install -r requirements.txt
```

#### 5. Configure Environment Variables (Optional):
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

#### 6. Run the Streamlit Dashboard:
```bash
streamlit run app.py
```

---

### 🛠️ CLI Operations & Performance Evaluation

#### A. Direct Pipeline Execution:
Launch a custom prompt with dynamic drafts and specific temperature ranges:
```bash
python self_moa_pipeline.py --prompt "Design a resilient event-driven architecture." --drafts 5 --temperatures 0.7 0.9 1.1
```

#### B. Run the Comparative Logic Benchmark:
Compare Zero-Shot baseline models against the Self-MoA orchestration framework:
```bash
python benchmark_logic.py
```
*This generates a markdown comparison document named `benchmark_results.md`.*

#### C. Evaluate Results & Generate Visual Chart:
Trigger the LLM-As-A-Judge evaluator to parse the comparison document, score the answers, and create an analytical bar chart:
```bash
python llm_judge_and_chart.py
```
*This creates the `evaluation_chart.png` asset.*

#### D. Run Automated MMLU Dataset Assessment:
Evaluate the pipeline against 100 questions from the standardized MMLU academic database to compute comparative accuracy, latency, and token cost metrics:
```bash
python mmlu_evaluator.py
```
*The metrics are exported to `mmlu_evaluation_results.csv` and rendered dynamically inside the Streamlit GUI.*

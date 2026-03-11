import os
import time
import pandas as pd
from datasets import load_dataset
from openai import OpenAI
from tqdm import tqdm

# --- الإعدادات الأساسية لـ Qwen 3.5 ---
API_KEY = os.environ.get("OPENAI_API_KEY", "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")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1") 
MODEL_NAME = "qwen/qwen3.5-flash-02-23" 

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def call_qwen(prompt, temperature=0.0, n=1):
    """دالة الاتصال بـ Qwen لتوليد الردود"""
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            n=n # توليد عدة مسودات في طلب واحد إذا كان الـ API يدعم
        )
        latency = time.time() - start_time
        
        # OpenRouter usage tracking (might fall back to manual calculation if not returned)
        total_tokens = response.usage.total_tokens if response.usage else ((len(prompt) + len(str(response.choices[0].message.content))) // 4)
        
        # حساب التكلفة الافتراضية للنموذج Qwen 3.5 من OpenRouter
        cost = (total_tokens / 1000) * 0.002 
        
        if n == 1:
            return response.choices[0].message.content, latency, cost
        else:
            return [choice.message.content for choice in response.choices], latency, cost
    except Exception as e:
        print(f"Error calling API: {e}")
        error_ans = "Error"
        if n == 1: return error_ans, time.time() - start_time, 0.0
        else: return [error_ans] * n, time.time() - start_time, 0.0

def run_baseline(question):
    """النموذج الأساسي (مسار واحد)"""
    prompt = f"Answer the following multiple-choice question. Provide ONLY the correct letter (A, B, C, or D).\n\nQuestion: {question}"
    answer, latency, cost = call_qwen(prompt, temperature=0.0)
    return answer.strip(), latency, cost

def run_self_moa(question, num_drafts=4):
    """تقنية Self-MoA (توليد ثم تجميع)"""
    # 1. مرحلة المقترح (Proposer) - درجة حرارة 0.7 للتنوع الداخلي
    draft_prompt = f"Solve this question:\n{question}\nExplain your reasoning."
    drafts, draft_lat, draft_cost = call_qwen(draft_prompt, temperature=0.7, n=num_drafts)
    
    # 2. مرحلة المجمع (Aggregator) - درجة حرارة 0.0 للدقة
    aggregator_prompt = "You are an expert evaluator. Review the following proposed solutions to the multiple-choice question.\n"
    aggregator_prompt += f"Question: {question}\n\nProposed Solutions:\n"
    for i, draft in enumerate(drafts):
        aggregator_prompt += f"--- Draft {i+1} ---\n{draft}\n\n"
    
    aggregator_prompt += "Based on the critical synthesis of these drafts, what is the final correct option? Provide ONLY the correct letter (A, B, C, or D)."
    
    final_answer, agg_lat, agg_cost = call_qwen(aggregator_prompt, temperature=0.0)
    
    return final_answer.strip(), (draft_lat + agg_lat), (draft_cost + agg_cost)

def main():
    print("="*60)
    print("🔬 Starting Automated MMLU Benchmark Evaluation For Self-MoA")
    print("="*60)

    # 1. تحميل 100 سؤال من مجموعة بيانات MMLU
    print("📥 Loading MMLU dataset (100 samples)...")
    try:
        # استخدام MMLU كبديل تقريبي لـ MMLU-redux لسهولة الوصول المباشر
        dataset = load_dataset("cais/mmlu", "all", split="test[:100]") 
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    results = []
    
    # 2. حلقة الاختبار
    for i, item in enumerate(tqdm(dataset, desc="Evaluating")):
        # تجهيز السؤال والخيارات
        question_text = f"{item['question']}\nA) {item['choices'][0]}\nB) {item['choices'][1]}\nC) {item['choices'][2]}\nD) {item['choices'][3]}"
        correct_answer = ["A", "B", "C", "D"][item['answer']] # الإجابة الصحيحة كحرف

        # أ. تقييم Baseline
        base_ans, base_lat, base_cost = run_baseline(question_text)
        base_correct = 1 if correct_answer in base_ans else 0

        # ب. تقييم Self-MoA-4
        moa4_ans, moa4_lat, moa4_cost = run_self_moa(question_text, num_drafts=4)
        moa4_correct = 1 if correct_answer in moa4_ans else 0

        # حفظ النتائج
        results.append({
            "Question_ID": i,
            "Baseline_Correct": base_correct,
            "Baseline_Latency": base_lat,
            "Baseline_Cost": base_cost,
            "MoA4_Correct": moa4_correct,
            "MoA4_Latency": moa4_lat,
            "MoA4_Cost": moa4_cost
        })

    # 3. تحليل النتائج النهائية
    df = pd.DataFrame(results)
    
    print("\n" + "*"*30 + " FINAL REPORT " + "*"*30)
    print(f"✅ Baseline Accuracy: {df['Baseline_Correct'].mean() * 100:.2f}%")
    print(f"🚀 Self-MoA-4 Accuracy: {df['MoA4_Correct'].mean() * 100:.2f}%")
    print("-" * 60)
    print(f"⏱️ Average Latency -> Baseline: {df['Baseline_Latency'].mean():.2f}s | Self-MoA-4: {df['MoA4_Latency'].mean():.2f}s")
    print(f"💸 Total Cost -> Baseline: ${df['Baseline_Cost'].sum():.4f} | Self-MoA-4: ${df['MoA4_Cost'].sum():.4f}")
    
    # حفظ في ملف
    df.to_csv("mmlu_evaluation_results.csv", index=False)
    print("💾 Detailed results saved to 'mmlu_evaluation_results.csv'")

if __name__ == "__main__":
    main()

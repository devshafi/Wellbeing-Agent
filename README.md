# Wellbeing-Agent

An agentic mental-health support chatbot (MSc thesis project) that combines empathetic
conversational responses with function-calling access to synthetic health/wearable data
(steps, sleep, heart rate, stress, etc.). User queries are routed by an LLM-based router
to the appropriate strategy, and responses are scored end-to-end by an LLM-judge
evaluation system.

## Architecture

A user query flows through:

1. **Routing** — [`wellbeing-agent/routing/query_router.py`](wellbeing-agent/routing/query_router.py)
   classifies the query as `CONVERSATION`, `FUNCTION_CALLING`, or `HYBRID` using a
   fine-tuned LLM, with a rule-based fallback.
2. **Processing** — the appropriate processor in
   [`wellbeing-agent/processors/`](wellbeing-agent/processors/) handles the query:
   - `conversation_processor.py` — pure empathetic/therapeutic chat.
   - `function_calling_processor.py` — pure health-data retrieval.
   - `hybrid_processor.py` — retrieves health data and wraps it in a therapeutic,
     data-informed response.
3. **Data** — [`wellbeing-agent/function_registry.py`](wellbeing-agent/function_registry.py)
   exposes ~19 `get_*_data()` functions returning synthetic (mock) health metrics.
4. **Orchestration** — [`wellbeing-agent/core/wellbeing_agent.py`](wellbeing-agent/core/wellbeing_agent.py)
   ties routing, processing, and conversation history together.
5. **Models** — [`wellbeing-agent/models/model_manager.py`](wellbeing-agent/models/model_manager.py)
   loads three LoRA-fine-tuned Llama-3.2-3B models (conversation, function-calling, router).
6. **UI** — [`wellbeing-agent/agentic_chat_modular.py`](wellbeing-agent/agentic_chat_modular.py)
   is the Gradio entry point for the chat app, with persistent SQLite conversation history.

## Repository layout

```
dataset/                # Hugging Face-format datasets + CSVs for training both models
figures/                 # Exploratory data analysis / plotting notebook
mh_conversation/         # Conversation model: dataset prep, LoRA fine-tuning (v1-v8), evaluation
mh_function_calling/     # Function-calling model: synthetic data generation, fine-tuning, evaluation
wellbeing-agent/         # The runnable agent application (routing, processors, UI, testing)
requirements.txt         # Main Python dependencies
```

## Evaluation

- **`wellbeing-agent/testing/`** — end-to-end LLM-judge evaluation
  ([`llm_judge_evaluation.py`](wellbeing-agent/testing/llm_judge_evaluation.py)) scores
  agent responses via GPT-4 across six therapeutic-quality dimensions (empathy & tone,
  data integration & accuracy, therapeutic insights, practical guidance, professional
  boundaries & safety, response completeness), plus automated/comprehensive test-query
  runners that generate the input CSVs.
- **`mh_conversation/model_evaluation/`** and **`mh_function_calling/model_evaluation/`** —
  per-model automatic metrics (BLEU/ROUGE for conversation generation; classification
  precision/recall for function-calling accuracy).

## Tech stack

Python; `torch` / `transformers` / `peft` / `trl` for LoRA fine-tuning of Llama-3.2-3B;
Gradio for the chat UI; SQLite for conversation history; OpenAI SDK for the LLM-judge
evaluation; `pandas` / `nltk` / `rouge_score` for metrics.

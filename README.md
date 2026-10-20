# WellbeingAgent: An LLM-Driven Agentic Framework for Personalized Mental Health Support

WellbeingAgent is a research prototype for **personalized, context-aware mental health support**. It coordinates a conversational model and a health-data function-calling model through an **LLM-based orchestrator**. The orchestrator decides whether a query requires conversation, structured health-data retrieval, or both.

> **Research use only.** WellbeingAgent is not a diagnostic tool, a clinical decision-support system, or a replacement for professional mental health care.

## Architecture

The framework uses **LLaMA 3.2-3B-Instruct** in three distinct roles:

| Component | Responsibility | Model adaptation |
| --- | --- | --- |
| **Router/orchestrator** | Classifies a query as `CONVERSATION`, `FUNCTION_CALLING`, or `HYBRID` and selects the execution path | **Base LLaMA 3.2-3B-Instruct with few-shot prompting; not fine-tuned** |
| **Conversational model** | Provides supportive dialogue and generates context-aware responses using retrieved health information when appropriate | LoRA fine-tuned on MentalChat16K |
| **Function-calling model** | Maps natural-language requests to health-data functions and temporal arguments such as `numdays` | LoRA fine-tuned on MindCall |

### Execution pathways

1. **`CONVERSATION`** — A request for supportive or informational dialogue is passed to the conversational model.
2. **`FUNCTION_CALLING`** — A request for personal health measurements is interpreted by the function-calling model, and the selected data-access function is executed.
3. **`HYBRID`** — The system retrieves relevant health information, then supplies those measurements together with the user's request and conversation context to the conversational model for response synthesis.

The router uses few-shot examples with routing rationales. The implemented router also provides a **rule-based fallback** when model routing fails or returns an unrecognized classification.

Key implementation files:

- [Main orchestrator](wellbeing-agent/core/wellbeing_agent.py)
- [Query router](wellbeing-agent/routing/query_router.py)
- [Conversation, function-calling, and hybrid processors](wellbeing-agent/processors/)
- [Model manager](wellbeing-agent/models/model_manager.py)
- [Gradio application](wellbeing-agent/agentic_chat_modular.py)

## Personalized health-data integration

The study describes an integration pipeline for measurements collected from a smartphone, Samsung Galaxy Fit3 wearable, and Renpho devices. Health measurements can be aggregated using Samsung Health and Health Connect and stored in a repository for structured retrieval. The orchestrator requests relevant measurements through the function-calling model when personalized data are needed.

**Important distinction between the manuscript and this public implementation:** the committed [function registry](wellbeing-agent/function_registry.py) currently generates **synthetic/mock measurements**. It does **not** directly connect to the wearable-data repository described in the research study. The registry includes **20 primary health functions**, covering activity, sleep, heart rate, stress, exercise, nutrition, blood metrics, and body composition, plus an `get_activity_data` alias.

The framework also supports conversation context for follow-up requests; the research design describes a bounded history of the most recent 20 dialogue turns.

## Datasets and model development

### MindCall

**MindCall** is a synthetic health function-calling dataset with **5,099 samples**, **20 health functions**, and five query styles:

- Explicit
- Implicit
- Behavioral
- Symptom-based
- Metaphorical

The generation process described in the manuscript used GPT-4, Grok-3, and DeepSeek-R1 to produce candidate samples, followed by validation and normalization. The dataset supports health-function selection and temporal-parameter prediction.

- **Dataset:** [MindCall on Hugging Face](https://huggingface.co/datasets/frshafi/mind_call)
- **DOI:** [10.57967/hf/7390](https://doi.org/10.57967/hf/7390)

### Conversational model

The final conversational model was adapted using **MentalChat16K**. The Mental Health Counseling Conversations (AMoD) dataset was examined during preliminary experiments. The conversational and function-calling models use distinct task-specific LoRA adaptations of LLaMA 3.2-3B-Instruct.

## Evaluation reported in the manuscript

| Component | Evaluation protocol | Selected results |
| --- | --- | --- |
| **Conversational model** | 1,606 held-out MentalChat16K samples; BLEU, ROUGE, and sentence-embedding cosine similarity | Mean similarity increased from **0.772** to **0.810**; similarity ≥0.8 increased from **45.1%** to **65.8%** |
| **Function-calling model** | 765 held-out queries; function selection and temporal-parameter prediction | **81.0%** function accuracy; **81.3%** F1-score; **75.4%** parameter accuracy |
| **Integrated framework** | 250 responses rated independently by GPT-3.5 and GPT-4 across six dimensions | Mean overall LLM-judge score: **8.29/10** |

The six system-level dimensions are therapeutic empathy and tone; data integration and accuracy; therapeutic insights and analysis; practical guidance and strategies; professional boundaries and safety; and response completeness and structure.

The [LLM-judge implementation](wellbeing-agent/testing/llm_judge_evaluation.py) has **GPT-4 as its default model**. Reproducing the manuscript's two-judge protocol requires conducting assessments with both GPT-3.5 and GPT-4 on the corresponding response set. The reported scores describe **LLM-judged response quality**, not clinically validated effectiveness or safety.

The manuscript does not report a separate quantitative evaluation of the router's classification accuracy.

## Repository layout

```text
dataset/                      Dataset artifacts and preparation files
figures/                      Exploratory analysis and plotting
mh_conversation/              Conversational model preparation, fine-tuning, evaluation
mh_function_calling/          Dataset generation, function-calling fine-tuning, evaluation
wellbeing-agent/
  core/                       Orchestrator
  routing/                    LLM query router
  processors/                 Execution pathways
  models/                     Model loading
  testing/                    System-level evaluation
  function_registry.py        Mock health-data functions
  agentic_chat_modular.py     Gradio interface
requirements.txt              Python dependencies
```

## Running the research prototype

The project uses Python, PyTorch, Hugging Face Transformers, PEFT, TRL, and Gradio.

1. Clone this repository and install dependencies from [`requirements.txt`](requirements.txt) in a compatible Python environment.
2. Obtain access to the LLaMA 3.2-3B-Instruct model and the necessary fine-tuned LoRA adapters/checkpoints.
3. Configure the model paths in [`wellbeing-agent/core/wellbeing_agent.py`](wellbeing-agent/core/wellbeing_agent.py). The committed code uses **development-machine-specific absolute paths**, so those paths must be changed before running elsewhere.
4. Configure credentials for any external evaluation service separately. **Never commit API keys or personal health records.**
5. Run the [Gradio entry point](wellbeing-agent/agentic_chat_modular.py) from the configured environment.

**Reproducibility note:** this is a research code repository rather than a fully packaged, one-command deployment. Model adapters, appropriate compute resources, and any nonpublic wearable-health records may need to be supplied separately. The included mock-data registry supports exploration of routing and processing without claiming to reproduce live wearable integration.

## Data and code availability

- **Source code:** https://github.com/devshafi/Wellbeing-Agent
- **MindCall dataset:** https://huggingface.co/datasets/frshafi/mind_call
- **Dataset DOI:** https://doi.org/10.57967/hf/7390

Personal health records used in research are not implied to be publicly available. Their status and any sharing restrictions should be described separately in the manuscript's Data Availability and ethical considerations statements.

## Safety and limitations

WellbeingAgent is a non-clinical research prototype. It may generate incorrect, incomplete, or inappropriate responses. The current system evaluation relies partly on LLM-based judges rather than healthcare professionals or end users. The work does **not** establish clinical effectiveness or autonomous safety in mental health care.

**Do not use this prototype for diagnosis, crisis intervention, treatment decisions, or other clinical purposes.**

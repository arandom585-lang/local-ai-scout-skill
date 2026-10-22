# Repeatable Model Selection, Verification & Licensing Guide

This guide establishes the step-by-step workflow for evaluating, verifying, licensing, and benchmarking local AI models. Follow this protocol to produce grounded, reliable model recommendations without relying on stale static assumptions.

---

## 1. The 7-Step Model Selection Protocol

```
[Step 1: Ingestion & Triage]
       │
       ▼
[Step 2: Memory & Hardware Boundary Calculation]
       │
       ▼
[Step 3: Candidate Discovery & Version Verification]
       │
       ▼
[Step 4: License & Commercial Terms Audit]
       │
       ▼
[Step 5: Safety Margin & Fit Scoring]
       │
       ▼
[Step 6: Structured Recommendation (1 Best-Fit + 2 Alternatives)]
       │
       ▼
[Step 7: Validation Test & Cloud Fallback Assessment]
```

---

## 2. Step 1: Ingestion & Triage Checklist

Gather the following four parameter groups before selecting models:

1. **Intended Task & Domain:**
   * Is this code completion, complex reasoning, general chat, vision OCR, transcription, or tool-calling automation?
   * What is the required context window ($C_{\text{tokens}}$)? (e.g., single-question 4k vs. entire repo 32k–128k).
2. **Hardware Constraints:**
   * GPU model, VRAM capacity, memory bus width.
   * System RAM capacity and generation (DDR4 vs. DDR5).
   * Host OS (Windows, macOS, Linux).
   * Usable storage (NVMe vs. HDD).
3. **Operational Constraints:**
   * Minimum acceptable generation speed (e.g., interactive chat requires $\ge 15\text{ tok/s}$; batch transcription can tolerate slower speeds).
   * Commercial vs. personal use (dictates license requirements).
   * Strict air-gap / zero-telemetry requirements.
4. **Target Runtime:**
   * Beginner / One-click: Ollama, LM Studio, Jan.ai.
   * Power-user / Integrated: llama.cpp server, Tabby, Continue.dev, ComfyUI.
   * High-throughput / Production: vLLM, Aphrodite, ExLlamaV2.

---

## 3. Step 2: Memory & Hardware Boundary Calculation

Apply the Memory Sizing formula from `hardware-compatibility.md`:

$$\text{Max Allocated Budget} = \text{Available VRAM} \times 0.90$$

*Leave a 10% safety margin for OS display overhead, context spikes, and runtime context buffers.*

* **Full GPU Fit:** $M_{\text{total}} \le \text{Max Allocated Budget}$. Result: Maximum inference speed.
* **Hybrid Offload:** $M_{\text{weights}} > \text{VRAM}$, but $M_{\text{total}} \le (\text{VRAM} + \text{RAM} \times 0.70)$. Result: Viable, but tokens/sec will be constrained by system memory bandwidth and PCIe transfers.
* **CPU-Only Fit:** Model fits strictly within physical RAM. Viable only for models $\le 8\text{B}$ parameters unless the user explicitly tolerates non-interactive speeds (< 2 tok/s).

---

## 4. Step 3: Candidate Discovery & Source Verification

Never invent model releases or download URLs. Verify candidate models through standard distribution channels:

### Distribution Source Verification Hierarchy
1. **Official Research Repositories:** Primary releases from organizations (e.g., `meta-llama`, `Qwen`, `deepseek-ai`, `mistralai`, `google`).
2. **Verified Community Quantizers:** For GGUF/EXL2 formats, recommend established, automated quantization pipelines:
   * **Bartowski** (`bartowski` on Hugging Face): High-fidelity GGUFs with automated imatrix calibration.
   * **Unsloth** (`unsloth` on Hugging Face): Dynamic GGUF and FP8 quantizations optimized for low-memory execution.
   * **TheBloke** (Hugging Face - Historical archive): Reliable for legacy architectures, but verify if newer models have superseded older quants.
3. **Ollama Official Library:** When recommending Ollama, reference tags directly from `ollama.com/library` (e.g., `qwen2.5-coder:7b-instruct-q4_K_M`).

### Rule Against Stale Recommendations
* Do not recommend deprecated model generations when modern iterations are available (e.g., do not recommend original Llama-2-7B when Llama-3.1-8B or Qwen-2.5-7B offer 2x–3x higher reasoning benchmarks at comparable memory footprints).
* When web access is available, verify that a candidate model has not been retracted, superseded, or updated with critical bug fixes (e.g., updated tokenizer configurations or RoPE scaling fixes).

---

## 5. Step 4: License & Commercial Terms Audit

Distinguish open-source licenses from open-weights licenses with commercial caps:

| License Classification | Key Permissions | Notable Restrictions & Red Flags | Representative Models |
| :--- | :--- | :--- | :--- |
| **Permissive Open Source (MIT / Apache 2.0)** | Free commercial use, modification, private use, patent grant (Apache). | Attribution required. No user-count or derivative-training restrictions. | Qwen 2.5 (up to 32B), Mistral-7B-v0.3, Whisper, Kokoro-82M |
| **Meta Llama Community License** | Free commercial use up to threshold. | **700 Million Monthly Active User (MAU)** cap requires commercial license from Meta. Prohibits using outputs to improve other models (except Llama derivatives). | Llama 3, Llama 3.1, Llama 3.2 |
| **DeepSeek License** | Free commercial use and modification. | Check specific release terms; requires clear attribution and compliance with local regulatory frameworks. | DeepSeek-Coder-V2, DeepSeek-R1 |
| **Research-Only / Non-Commercial (CC-BY-NC, CPML)** | Free personal, educational, and research use. | **Commercial deployment strictly prohibited.** Any commercial SaaS or internal enterprise workflow violates terms. | Coqui XTTS-v2 (CPML), select academic weights |

> **Audit Rule:** Explicitly inform the user whenever a model carries a conditional commercial clause (e.g., Meta Llama MAU limits) or non-commercial restrictions.

---

## 6. Step 5: Distinguishing Verified Facts from Estimates

Maintain clear epistemological boundaries:

* **Verified Facts:** Specifications recorded in official papers or verified repository cards (e.g., architecture parameters, context window limit, layer count, official license string).
* **Estimates:** Memory footprints calculated via the memory formula, approximate file sizes, and theoretical maximum token generation speeds calculated from hardware bandwidth.
* **Prohibited Behavior:**
  * **Never** invent synthetic benchmark scores (e.g., do not state "Scores 88.4 on HumanEval" unless verified against official published reports).
  * **Never** fabricate tokens-per-second promises on unverified customer hardware (e.g., do not say "You will get 45.2 tokens/second on your laptop"). State theoretical bandwidth ranges instead.

---

## 7. Step 6: Candidate Scoring Heuristic & Structured Delivery

Score candidates along four dimensions (0 to 10 points each):
1. **Task Alignment (30% weight):** Does the model family specialize in the target task?
2. **Hardware Fit & Headroom (30% weight):** Does the model fit cleanly in VRAM with sufficient KV cache headroom?
3. **Execution Latency (20% weight):** Will the user experience acceptable interactive throughput on their hardware bus?
4. **License Compatibility (20% weight):** Does the license match the user's commercial or privacy posture?

### Structured Recommendation Output Template
Deliver the recommendation in the following format:

1. **Executive Summary:** Clear statement of best-fit model and hardware compatibility verdict.
2. **Primary Recommendation (Best Fit):**
   * Model Name & Quantization Tag (e.g., `qwen2.5-coder:14b-instruct-q4_K_M`)
   * Architecture & Parameter Count
   * Estimated Memory Footprint (Weights + KV Cache + Runtime)
   * Why this model is the best fit for the specific hardware
   * Known trade-offs or limitations
3. **Alternative 1 (Performance / Lightweight):** Smaller footprint, faster token speed, lower VRAM consumption.
4. **Alternative 2 (Quality / Workstation Ceiling):** Maximum parameter count viable on the hardware, trading off speed or context length.
5. **Concrete Deployment Commands:** Ready-to-run terminal commands for the target runtime and operating system.
6. **Validation & Benchmarking Procedure:** Instructions to test memory utilization and generation speed.

---

## 8. Step 7: Validation Test & Cloud Fallback Triggers

### Practical Validation Procedure
Instruct the user to verify their deployment using a two-step validation:

1. **Memory Health Check:**
   * Observe active VRAM/RAM allocation before and during generation.
   * If VRAM reaches 98%–100% and generation stalls, reduce context length or switch to a lower quantization.
2. **Standard Diagnostic Test Prompt:**
   * Run a task-specific prompt with known verifiable output to check syntax, reasoning, and latency:
     * *Coding:* `"Write a Python function to parse ISO 8601 timestamps with error handling. Include three unit tests."`
     * *Reasoning:* `"A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Show your step-by-step reasoning."`
     * *JSON Schema:* `"Extract name, age, and skills from: 'Alice is a 29yo cloud engineer who codes in Go and Rust' into valid JSON."`

### When to Trigger Cloud Fallback Recommendations
Always prioritize local models when technically feasible. However, transparently recommend a cloud model API (e.g., Claude 3.5 Sonnet, Claude 3.7 Sonnet) when:
1. **Hardware Impossibility:** The user's hardware (e.g., 8GB system RAM, no discrete GPU) cannot run the minimum parameter threshold needed for the task (e.g., full-repo refactoring across 100k tokens requires a 32B+ model with 20GB+ memory).
2. **Severe Latency Unusability:** Generating a required response would take over 3 minutes (> 1 token/sec) on available CPU-only hardware.
3. **Mission-Critical Accuracy / Safety:** The task requires frontier-tier reasoning (e.g., medical diagnostics, financial contract legal audits) that current sub-14B local models cannot reliably provide without severe hallucination risk.


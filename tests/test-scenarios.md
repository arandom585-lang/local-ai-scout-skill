# Local Model Scout — Functional Test Scenarios

This document defines the functional and behavioral test suite for validating the **Local Model Scout** Claude Agent Skill.

> [!IMPORTANT]
> **Static Validation vs. Behavioral Execution:**
> Passing structural tests or syntax linters verifies only that files exist and adhere to schema formatting. It **does not** prove that an LLM agent will accurately adhere to memory limits, prioritize local models, avoid fabricating benchmarks, or ask the proper follow-up questions.
> Every scenario in this test suite must be evaluated against the defined **Acceptance Criteria** during interactive testing.

---

## Scenario 1: Windows PC with 8 GB RAM and Integrated Graphics (Local Coding)

### Objective
Verify that the skill identifies low-memory constraints, prohibits models that will cause swap thrashing or OOM crashes, asks essential environment questions, and offers appropriately sized compact models or cloud fallbacks.

### User Input
```text
I have a budget Windows 11 laptop with an Intel Core i5-1135G7 CPU, 8 GB RAM, integrated Intel Iris Xe Graphics, and a 256 GB SATA SSD. I want to use a local AI model for Python code assistance and autocomplete in VS Code. What should I install?
```

### Expected Skill Behaviour
1. **Memory Ceiling Calculation:**
   * Acknowledges that Windows 11 reserves $\approx 3.5\text{ GB} - 4.0\text{ GB}$ of RAM for OS and system background tasks.
   * Calculates maximum usable memory for AI runtime + model weights + KV cache at $\le 3.5\text{ GB}$.
   * Recognizes that integrated Intel Iris Xe shares system RAM and has no dedicated VRAM.
2. **Negative Constraint Enforcement:**
   * Explicitly rules out 7B/8B models (e.g., standard 7B Q4 models require $\approx 4.5\text{ GB} - 5.5\text{ GB}$ total RAM), warning that loading them will provoke Windows disk paging/swap file thrashing on the SATA SSD, causing system lockups.
3. **Model Selection:**
   * Recommends a verified ultra-compact sub-3B coding model (e.g., `Qwen2.5-Coder-1.5B-Instruct` or `Qwen2.5-Coder-3B-Instruct` at `Q4_K_M` or `Q5_K_M`) requiring $\approx 1.3\text{ GB} - 2.2\text{ GB}$ total memory.
   * Suggests Fill-in-the-Middle (FIM) autocomplete via `llama.cpp` server, Tabby, or Continue.dev.
4. **Cloud Fallback Guidance:**
   * Transparently informs the user that complex multi-file architectural refactoring across $\ge 8\text{k}$ context tokens exceeds their 8 GB physical capacity and requires a cloud model API (e.g., Claude 3.5 Sonnet).

### Required Follow-Up Questions (If unspecified)
* Confirm whether the user plans to run a web browser or heavier IDE alongside the model (as this further shrinks the usable RAM ceiling from 3.5 GB down to 2.0 GB).

### Hardware Limitations to Consider
* **Bandwidth:** Dual-channel DDR4 memory provides $\approx 25\text{ GB/s} - 35\text{ GB/s}$ bandwidth. Autoregressive token generation is CPU-bound ($\approx 12 - 20\text{ tok/s}$ for a 1.5B model).
* **Storage Latency:** SATA SSD speeds ($\approx 500\text{ MB/s}$) make swap thrashing catastrophic.

### Acceptance Criteria
* [ ] The skill correctly identifies that 8 GB RAM cannot safely run $\ge 7\text{B}$ parameter models.
* [ ] The skill does not hallucinate dedicated VRAM for the Intel Iris Xe GPU.
* [ ] Memory usage estimate remains $\le 3.5\text{ GB}$.
* [ ] Provides working installation commands for the recommended runtime (e.g., `ollama run qwen2.5-coder:1.5b`).
* [ ] Flags cloud API fallback for full-repository reasoning tasks.

---

## Scenario 2: Windows PC with 16 GB RAM and NVIDIA RTX GPU with 8 GB VRAM (Coding & Chat)

### Objective
Verify that the skill manages dedicated VRAM limits, guards against Windows NVIDIA Sysmem Fallback thrashing, and accounts for Key-Value (KV) cache memory growth at extended context lengths.

### User Input
```text
I'm running Windows 11 with 16 GB DDR4 RAM and an NVIDIA GeForce RTX 3070 (8 GB VRAM). I want a local model that can assist with TypeScript/Python programming and also serve as a daily conversational assistant with at least 8k context. What is the best model?
```

### Expected Skill Behaviour
1. **VRAM Budget Accounting:**
   * Calculates: $\text{Total VRAM} = 8.0\text{ GB}$.
   * Deducts Windows Desktop Window Manager (DWM) display overhead ($\approx 1.0\text{ GB} - 1.2\text{ GB}$) and CUDA runtime context ($\approx 0.4\text{ GB}$).
   * Establishes usable VRAM ceiling at $\approx 6.4\text{ GB}$ (with a safe target allocation of $\approx 5.8\text{ GB} - 6.0\text{ GB}$).
2. **KV Cache & Model Precision Trade-off:**
   * Rules out 14B models for 100% GPU offloading ($14\text{B}$ at Q4 takes $\approx 8.9\text{ GB}$ weights alone).
   * Evaluates 7B–8B models:
     * $7\text{B} - 8\text{B}$ weights at Q4_K_M $\approx 4.5\text{ GB} - 5.0\text{ GB}$; at Q5_K_M $\approx 5.2\text{ GB} - 5.5\text{ GB}$.
     * 8k context KV cache in FP16 for 8-head GQA $\approx 1.0\text{ GB}$.
     * Total VRAM required at 8k context $\approx 6.2\text{ GB} - 6.5\text{ GB}$.
3. **OS-Specific Driver Quirk Warning:**
   * Explains the NVIDIA Windows driver "Sysmem Fallback" behavior: exceeding 8 GB by even 100 MB triggers silent paging across PCIe, collapsing generation speed from $\approx 50\text{ tok/s}$ to $\approx 0.5\text{ tok/s}$.
   * Recommends setting "Prefer No Sysmem Fallback" in NVIDIA Control Panel or capping context to 8,192 tokens under FP16 KV cache (or 16k tokens if Q8_0 KV cache is enabled).
4. **Recommendation Structure:**
   * **Best Fit:** `Qwen2.5-Coder-7B-Instruct` (Q5_K_M or Q4_K_M) or `Llama-3.1-8B-Instruct` (Q4_K_M).
   * **Alternative (Deep Reasoning):** `DeepSeek-R1-Distill-Qwen-7B` or `DeepSeek-R1-Distill-Llama-8B` (Q4_K_M).
   * **Alternative (Quality Ceiling with Offloading):** `Qwen2.5-14B-Instruct` with partial GPU offloading ($\approx 24/48$ layers on GPU), noting that token speed will drop to $\approx 6 - 10\text{ tok/s}$.

### Required Follow-Up Questions (If unspecified)
* Ask whether coding autocomplete (inline FIM) or interactive chat is the primary usage pattern.

### Hardware Limitations to Consider
* 8 GB VRAM cannot fit 14B models in full VRAM.
* Unquantized FP16 KV cache beyond 16k tokens will trigger OOM or driver thrashing on an 8 GB card.

### Acceptance Criteria
* [ ] Total VRAM allocation estimate stays strictly under 7.0 GB.
* [ ] Accurately calculates KV cache memory for 8k tokens ($\approx 1.0\text{ GB}$ in FP16).
* [ ] Explains NVIDIA Windows driver memory fallback risks.
* [ ] Recommends a verified 7B–8B model with concrete run commands (e.g., Ollama / LM Studio).

---

## Scenario 3: Workstation with 32 GB RAM and 12 GB VRAM (Local AI Automation & Agents)

### Objective
Verify that the skill evaluates tool-calling capabilities, function-calling benchmark compliance, structured JSON decoding runtimes, and long-context accumulation in multi-step agent workflows.

### User Input
```text
I have a desktop PC with an AMD Ryzen 9 5900X, 32 GB RAM, and an NVIDIA GeForce RTX 4070 (12 GB VRAM) running Ubuntu Linux. I want to build a local autonomous agent workflow that browses web pages, invokes bash scripts, and extracts structured data using JSON function calling. What setup is best?
```

### Expected Skill Behaviour
1. **Task-Specific Criteria Evaluation:**
   * Prioritizes Berkeley Function-Calling Leaderboard (BFCL) performance, JSON schema obedience, and resistance to context degradation.
   * Notes that agent workflows accumulate tool output histories rapidly, requiring at least 16k–32k effective context.
2. **Hardware Budgeting on Linux:**
   * Linux headless or lightweight desktop consumes less VRAM than Windows ($\approx 0.4\text{ GB} - 0.6\text{ GB}$ display/system overhead).
   * Usable VRAM is $\approx 11.0\text{ GB}$.
3. **Candidate Evaluation:**
   * `Qwen2.5-14B-Instruct` (Q4_K_M): $\approx 8.9\text{ GB}$ weights + $1.6\text{ GB}$ KV cache (16k context with Q8_0 KV cache) = $\approx 10.5\text{ GB}$ VRAM. Fits cleanly inside 12 GB VRAM with fast CUDA execution ($\approx 35 - 45\text{ tok/s}$).
   * `Qwen2.5-7B-Instruct` (Q5_K_M): $\approx 5.2\text{ GB}$ weights + $2.0\text{ GB}$ KV cache (16k FP16) = $\approx 7.2\text{ GB}$ VRAM. Leaves ample room for 32k context.
4. **Runtime & Structured Output Recommendation:**
   * Advises running `vLLM` or `llama.cpp` server with grammar-guided decoding (GBNF grammars or Outlines / XGrammar) to mathematically guarantee valid JSON schema adherence.

### Required Follow-Up Questions (If unspecified)
* Inquire about the maximum expected tool output length (e.g., raw web scraping HTML requires larger context windows or HTML-to-markdown preprocessing).

### Hardware Limitations to Consider
* Running 32k context with unquantized FP16 KV cache on a 14B model requires $\approx 6.4\text{ GB}$ just for the cache, which exceeds 12 GB VRAM when added to 8.9 GB weights. Quantized KV cache (`Q8_0` or `Q4_0`) or context capping is mandatory.

### Acceptance Criteria
* [ ] Emphasizes function-calling / tool-use benchmarks (e.g., BFCL).
* [ ] Selects a verified tool-compatible model (e.g., Qwen 2.5 or Llama 3.1).
* [ ] Highlights structured JSON decoding runtimes (vLLM / llama.cpp server with grammars).
* [ ] Correctly budgets context growth for tool-calling history.

---

## Scenario 4: Apple Silicon Laptop with 16 GB Unified Memory (Local Chat & Research)

### Objective
Verify that the skill respects Apple Silicon Unified Memory Architecture (UMA), accounts for macOS system memory reserves and `wired_mem_limit`, evaluates Metal acceleration, and avoids battery-draining configurations.

### User Input
```text
I have an Apple MacBook Air M3 with 16 GB Unified Memory running macOS Sequoia. I want a local conversational assistant for research, drafting, and summarizing long PDFs using LM Studio. I want good reasoning without causing the laptop to overheat or swap to disk.
```

### Expected Skill Behaviour
1. **Unified Memory Accounting:**
   * Identifies that macOS and WindowServer reserve $\approx 4.0\text{ GB} - 4.5\text{ GB}$ of RAM.
   * Explains that macOS enforces a default Metal memory allocation limit (`wired_mem_limit` $\approx 70\% - 75\%$ of physical memory $\approx 11.5\text{ GB}$).
   * Sets safe allocation budget at $\le 9.0\text{ GB}$ to keep memory pressure green in Activity Monitor and avoid NVMe SSD swap paging.
2. **Candidate Evaluation:**
   * Rules out 14B models ($\approx 8.9\text{ GB}$ weights + KV cache + runtime overhead $\ge 10.5\text{ GB}$), which causes memory pressure to turn yellow/red and triggers system swap during multi-tasking.
   * Focuses on 8B parameter models:
     * `Llama-3.1-8B-Instruct` (Q5_K_M): $\approx 5.7\text{ GB}$ weights + $1.0\text{ GB}$ KV cache (8k context) = $\approx 6.7\text{ GB}$ memory. Leaves $> 3.5\text{ GB}$ free for macOS.
     * `DeepSeek-R1-Distill-Qwen-8B` (Q4_K_M): $\approx 5.0\text{ GB}$ weights + $1.2\text{ GB}$ KV cache = $\approx 6.2\text{ GB}$ memory. Strong chain-of-thought reasoning.
     * `Llama-3.2-3B-Instruct` (Q8_0): $\approx 3.4\text{ GB}$ total memory. High speed, low thermals.
3. **Operational Advice:**
   * Recommends Metal GPU offload (`-ngl 99` in llama.cpp or Metal enabled in LM Studio).
   * Advises keeping context to 8k–16k for document summarization unless using a lightweight 3B model.

### Required Follow-Up Questions (If unspecified)
* Ask how large the PDFs typically are (to recommend chunking / RAG vs. in-context stuffing).

### Hardware Limitations to Consider
* MacBook Air lacks active fan cooling; sustained heavy compute on 14B models will trigger thermal throttling.
* 16 GB unified memory cannot run 14B+ models alongside everyday desktop applications without swap sluggishness.

### Acceptance Criteria
* [ ] Recognizes Apple Unified Memory dynamics and safe budget limits ($\le 9.0\text{ GB}$).
* [ ] Avoids recommending 14B or 32B models for a 16 GB MacBook Air.
* [ ] Distinguishes reasoning distillations (DeepSeek-R1) from general chat models.
* [ ] Recommends Metal-accelerated runtimes (LM Studio, llama.cpp, MLX).

---

## Scenario 5: User Who Does Not Know Their Hardware Specifications

### Objective
Verify that the skill detects missing hardware information, avoids making premature recommendations, and provides exact, copy-pasteable diagnostic commands tailored to the user's operating system.

### User Input
```text
I want to run a local AI on my computer so my company data stays private, but I don't know what graphics card or processor I have. Can you just tell me what to download?
```

### Expected Skill Behaviour
1. **Refusal to Guess:**
   * Politely explains that downloading a model without knowing hardware specifications risks downloading multi-gigabyte files that may not load, may crash the computer, or may generate tokens at unplayably slow speeds (< 1 tok/s).
2. **Diagnostic Command Provision:**
   * Inquires which operating system is in use, or proactively provides clean commands for Windows, macOS, and Linux:
     * **Windows (PowerShell):**
       ```powershell
       Get-CimInstance Win32_Processor | Select-Object Name | Format-List
       Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum | Select-Object @{N="RAM_GB";E={[math]::round($_.Sum/1GB,1)}} | Format-List
       Get-CimInstance Win32_VideoController | Select-Object Name, @{N="VRAM_GB";E={[math]::round($_.AdapterRAM/1GB,1)}} | Format-List
       Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N="Free_GB";E={[math]::round($_.Free/1GB,1)}} | Format-List
       # If NVIDIA card installed: nvidia-smi
       ```
     * **macOS (Terminal):**
       ```bash
       system_profiler SPHardwareDataType SPDisplaysDataType | grep -E "Chip:|Memory:|Cores:|Total Number of Cores:|VRAM"
       df -h /
       ```
     * **Linux (Terminal):**
       ```bash
       lscpu | grep "Model name"
       free -h
       nvidia-smi --query-gpu=gpu_name,memory.total --format=csv,noheader 2>/dev/null || lspci | grep -i vga
       df -h /
       ```
3. **Next Steps Instruction:**
   * Tells the user to paste the command output into the chat so the skill can calculate their exact usable memory budget.

### Required Follow-Up Questions
* Ask what operating system they are running (if not already evident).
* Ask what primary task they want to accomplish once hardware is determined.

### Hardware Limitations to Consider
* All hardware specs are unknown; no assumptions can be made.

### Acceptance Criteria
* [ ] Refuses to give a definitive model recommendation without hardware specifications.
* [ ] Provides working, non-destructive diagnostic commands for Windows, macOS, and Linux.
* [ ] Uses list formatting (`Format-List`) for PowerShell to prevent property suppression.
* [ ] Clearly explains what to do with the diagnostic output.

---

## Scenario 6: Local Video Generation with Insufficient Hardware

### Objective
Verify that the skill identifies when a hardware profile is inadequate for a requested workload, provides a realistic assessment of latency and VRAM bottlenecks, avoids false promises of real-time performance, offers the only viable low-spec alternatives, and suggests cloud fallbacks.

### User Input
```text
I want to generate 1080p AI video clips locally on my Windows 10 gaming PC. I have an NVIDIA GeForce RTX 3060 with 8 GB VRAM, an Intel i7-10700K CPU, and 16 GB RAM. Can I run HunyuanVideo, CogVideoX, or Wan2.1?
```

### Expected Skill Behaviour
1. **Realistic Technical Assessment:**
   * Directly informs the user that generating 1080p video locally on an 8 GB VRAM GPU is **not practically viable**.
   * Details the constraints:
     * High-fidelity video DiT models (HunyuanVideo, CogVideoX-5B, Wan2.1-14B) require $\ge 16\text{ GB} - 24\text{ GB}$ VRAM.
     * 1080p video attention latents and VAE decoding cause immediate CUDA Out-of-Memory on 8 GB cards unless extreme spatial/temporal tiling is active.
2. **Usability Reality Check (Bandwidth & Compute Bottleneck):**
   * Explains that running a video DiT model with block swapping across PCIe 3.0/4.0 and 16 GB system RAM will take **15 to 30+ minutes per 3-second clip**, making interactive experimentation grueling.
3. **Constrained Low-Spec Local Options (If user insists on testing):**
   * Recommends restricting expectations to **480p resolution** and short duration (33–49 frames).
   * Candidates: `Wan2.1-1.3B` or `LTX-Video (0.9B)` in FP8 or GGUF format via ComfyUI with `ComfyUI-VideoHelperSuite`, CPU text-encoder offload, and tiled VAE decode.
4. **Pragmatic Alternatives:**
   * Suggests mastering high-quality text-to-image (SDXL or FLUX.1 [schnell] in FP8) which executes in seconds on an 8 GB card.
   * Recommends cloud video generation APIs (e.g., Runway Gen-3, Luma Dream Machine, Kling AI, Google Veo) for production-grade 1080p video.

### Required Follow-Up Questions (If unspecified)
* Inquire whether 480p preview rendering is acceptable or if 1080p output is a hard requirement.

### Hardware Limitations to Consider
* 8 GB VRAM cannot hold 3D video latents for 1080p without OOM.
* 16 GB system RAM leaves minimal buffer for transformer block swapping.

### Acceptance Criteria
* [ ] Explicitly warns that 1080p video generation is unviable on an 8 GB VRAM card.
* [ ] Avoids promising fast generation speeds; provides realistic render time warnings (15–30 minutes).
* [ ] Restricts any local video candidate to compact architectures (Wan2.1-1.3B or LTX-Video) at 480p with tiled VAE.
* [ ] Recommends cloud API alternatives for high-resolution video production.

---

## 7. Acceptance Test Execution Matrix

| Test Scenario | Target Workload | Target Hardware Profile | Pass Condition |
| :--- | :--- | :--- | :--- |
| **Scenario 1** | Local Coding | Windows PC, 8 GB RAM, Integrated Iris Xe | Flags 8 GB constraint, rejects $\ge 7\text{B}$ models, suggests $\le 3\text{B}$ FIM model ($\le 3.5\text{GB}$ footprint). |
| **Scenario 2** | Coding & Chat | Windows PC, 16 GB RAM, RTX 3070 8 GB VRAM | Budgets usable VRAM ($\le 6.4\text{GB}$), accounts for 8k KV cache ($1.0\text{GB}$), warns of NVIDIA Sysmem fallback. |
| **Scenario 3** | Agents / Automation | Linux Desktop, 32 GB RAM, RTX 4070 12 GB VRAM | Prioritizes function calling / BFCL benchmarks, suggests vLLM/llama.cpp grammars, budgets context growth. |
| **Scenario 4** | Chat & Research | Mac M3, 16 GB Unified Memory | Enforces macOS $\le 9.0\text{GB}$ budget, recommends 8B Q5 on Metal, rejects 14B swap sluggishness. |
| **Scenario 5** | Unknown Hardware | OS / Hardware Unknown | Refuses to guess, provides non-destructive OS commands (PowerShell `Format-List`, macOS, Linux). |
| **Scenario 6** | Video Generation | Windows PC, RTX 3060 8 GB VRAM, 16 GB RAM | Rejects 1080p on 8 GB VRAM as unviable, warns of 15–30 min render times, bounds local options to 480p DiT. |


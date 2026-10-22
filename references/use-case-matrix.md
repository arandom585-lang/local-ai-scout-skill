# Local Model Use-Case Matrix

This reference maps common AI tasks to model families, recommended runtimes, evaluation criteria, and operational trade-offs. Use this matrix to identify candidate model architectures before performing detailed hardware constraint checks.

---

## 1. General-Purpose Chat and Reasoning

* **Core Objective:** Conversational interaction, knowledge retrieval, structured synthesis, logical deduction, step-by-step mathematical or analytical reasoning.
* **Key Demands:** Low prompt processing latency, coherent multi-turn context retention, instruction-following fidelity, hallucination resistance.

| Parameter Tier | Typical Active Parameter Range | Representative Model Families | Target Runtimes | Primary Evaluation Benchmarks |
| :--- | :--- | :--- | :--- | :--- |
| **Ultra-Compact (1B–4B)** | 1.5B – 3.8B | Llama 3.2 (1B, 3B), Qwen 2.5 (1.5B, 3B), Gemma 2 (2B), Phi-3.5-mini (3.8B) | Ollama, llama.cpp, LM Studio | IFEval, MMLU-Pro, GSM8K |
| **Standard Desktop (7B–14B)** | 7B – 14.7B | Qwen 2.5 (7B, 14B), Llama 3.1 (8B), Mistral (7B-v0.3), Gemma 2 (9B) | Ollama, llama.cpp, LM Studio, vLLM | MMLU-Redux, Arena-Hard-Auto, AlpacaEval 2.0 |
| **High-Performance (27B–72B)**| 27B – 72B | Qwen 2.5 (32B, 72B), Llama 3.1 (70B), Gemma 2 (27B), Command R+ (104B) | vLLM, llama.cpp, ExLlamaV2, Aphrodite | Chatbot Arena, SimpleQA, GPQA Diamond |
| **Reasoning / Chain-of-Thought** | 7B – 70B (Distilled or Full) | DeepSeek-R1 distills (Qwen/Llama bases 7B, 8B, 14B, 32B, 70B), QwQ-32B | llama.cpp, Ollama, vLLM | AIME 2024, MATH-500, Codeforces |

### Practical Operational Notes
* **Thinking tokens cost context:** Reasoning models (e.g., DeepSeek-R1 distills, QwQ) generate large chains of thought (1,000 to 8,000 tokens) before answering. Ensure the runtime allocates sufficient KV cache memory to prevent context truncation mid-thought.
* **Quantization sensitivity:** Reasoning capabilities degrade more sharply below 4-bit precision (e.g., `Q3_K_M` or lower) compared to generic chat. Prefer at least `Q4_K_M` or `Q5_K_M`.

---

## 2. Coding and Software Development

* **Core Objective:** Code completion (infill/FIM), test generation, repository-scale refactoring, debugging, syntax translation, and API integration.
* **Key Demands:** Fill-in-the-Middle (FIM) support for editor completion, long context retention without needle loss, precise syntax adherence, strict adherence to formatting (JSON/diffs).

| Role | Parameter Range | Representative Model Families | Target Runtimes | Primary Evaluation Benchmarks |
| :--- | :--- | :--- | :--- | :--- |
| **Inline Autocomplete (FIM)** | 1.5B – 7B | Qwen 2.5-Coder (1.5B, 7B), StarCoder2 (3B, 7B), DeepSeek-Coder (1.3B, 6.7B) | Tabby, Continue.dev (via Ollama/llama.cpp), llama.cpp server | Single-line latency (<80ms target), HumanEval-Infill |
| **Interactive Copilot / Chat** | 7B – 14B | Qwen 2.5-Coder-Instruct (7B, 14B), Codestral-22B (requires ~16GB+ VRAM) | Ollama, LM Studio, llama.cpp, vLLM | EvalPlus (HumanEval+, MBPP+), LiveCodeBench |
| **Architectural / Repository Tasks** | 32B – 70B+ (or MoE) | Qwen 2.5-Coder-Instruct (32B), DeepSeek-Coder-V2-Lite (16B total, 2.4B active), DeepSeek-Coder-V2 (236B total, 21B active) | llama.cpp (MoE CPU/GPU split), vLLM | SWE-bench Verified, RepoBench, MultiPL-E |

### Practical Operational Notes
* **FIM Formatting:** Autocomplete requires models fine-tuned with FIM tokens (e.g., `<|fim_prefix|>`, `<|fim_suffix|>`). Generic chat instruction models will produce explanatory text instead of inline completions.
* **MoE Memory vs. Compute:** Mixture-of-Experts models like DeepSeek-Coder-V2-Lite require RAM/VRAM proportional to their *total* parameter count (~16B weights = ~10GB in Q4), but compute latency is tied to *active* parameters (~2.4B), yielding faster token generation per memory gigabyte than dense models.

---

## 3. Vision and Multimodal Understanding

* **Core Objective:** Image question answering, OCR, chart/document analysis, visual inspection, bounding box detection.
* **Key Demands:** High-resolution patch handling, vision encoder memory overhead, cross-modal alignment accuracy.

| Tier | Model Families | Vision Architecture | Recommended Runtimes | Primary Evaluation Benchmarks |
| :--- | :--- | :--- | :--- | :--- |
| **Edge / Mobile (2B–4B)** | Moondream2 (1.8B), SmolVLM (2B), Qwen 2-VL (2B), Llama 3.2-Vision (11B) | SigLIP / CLIP + Compact LLM | llama.cpp (with mmproj), Ollama, transformers | DocVQA, TextVQA, OCRBench |
| **Workstation (7B–14B)** | Qwen 2-VL (7B), Llama 3.2-Vision (11B), MiniCPM-V 2.6 (8B), InternVL2.5 (8B) | Dynamic Resolution ViT + LLM | Ollama, llama.cpp, vLLM, LM Studio | MMBench, MathVista, RealWorldQA |

### Practical Operational Notes
* **Multimodal Projector Weights:** Multimodal models require two weight components: the language model backbone and the vision projection module (`mmproj` in GGUF). Both must reside in memory.
* **Variable Resolution Tile Memory:** Modern vision models (e.g., Qwen 2-VL) slice high-resolution images into multiple 14x14 or 28x28 patches. A single 4K image can expand into 1,000+ visual tokens, drastically expanding KV cache requirements for that single turn.

---

## 4. Embeddings and Reranking

* **Core Objective:** Semantic search, Retrieval-Augmented Generation (RAG), clustering, deduplication, document reranking.
* **Key Demands:** High throughput, low memory footprint, sequence length support (512 to 8192 tokens), embedding dimension efficiency.

| Task | Representative Model Families | Context Window | Recommended Runtimes | Primary Evaluation Benchmarks |
| :--- | :--- | :--- | :--- | :--- |
| **Dense Vector Embeddings** | BAAI/bge-m3, nomic-embed-text-v1.5, text-embeddings-inference (TEI) compatible models, Qwen2-Embedding, all-MiniLM-L6-v2 | 512 – 8,192 tokens | Ollama, HuggingFace TEI, Infinity, ONNX Runtime | MTEB (Massive Text Embedding Benchmark) |
| **Cross-Encoder Reranking** | BAAI/bge-reranker-v2-m3, jina-reranker-v2-base-multilingual | 512 – 8,192 tokens | TEI, sentence-transformers, Infinity | MTEB Retrieval / Reranking |

### Practical Operational Notes
* **Embeddings are lightweight:** Most top-performing embedding models are 100M to 600M parameters (0.3GB – 1.5GB VRAM). They can comfortably run on CPU or share a GPU with a main LLM.
* **Asymmetric Query/Document prefixes:** Models like `nomic-embed-text` and `bge` require specific prompt task prefixes (e.g., `search_query:` vs. `search_document:`). Failure to apply these prefixes degrades retrieval accuracy significantly.

---

## 5. Speech-to-Text (STT) and Audio Transcription

* **Core Objective:** Transcribing recorded speech, live microphone streaming, timestamp alignment, multi-language translation.
* **Key Demands:** Real-Time Factor (RTF) < 1.0, Word Error Rate (WER) minimization, halo hallucination suppression on silence.

| Tier | Model Families | Parameters | Recommended Runtimes | Primary Evaluation Benchmarks |
| :--- | :--- | :--- | :--- | :--- |
| **Fast / Lightweight** | Whisper (tiny, base, small), Moonshine | 39M – 244M | faster-whisper (CTranslate2), whisper.cpp | LibriSpeech WER, RTF on CPU/GPU |
| **High Accuracy / Multilingual** | Whisper (medium, large-v3, large-v3-turbo) | 769M – 1550M | faster-whisper, whisper.cpp, Insanely-Fast-Whisper | Common Voice WER, FLEURS |

### Practical Operational Notes
* **Runtime Selection:** Standard PyTorch Whisper is notoriously resource-inefficient. Use `faster-whisper` (CTranslate2 backend with INT8 compute) or `whisper.cpp` to achieve a 4x–8x speedup and ~70% lower RAM/VRAM footprint.
* **Whisper Large-v3-Turbo:** Delivers near `large-v3` accuracy with reduced decoder layers (4 instead of 32), executing 3x faster with ~1.5GB VRAM under FP16/INT8.

---

## 6. Text-to-Speech (TTS)

* **Core Objective:** Audio synthesis from text, audiobook narration, conversational voice agents.
* **Key Demands:** Natural prosody, low latency (time-to-first-audio chunk < 200ms for dialogue), multi-speaker support, minimal VRAM/RAM overhead.

| Class | Representative Model Families | Footprint | Recommended Runtimes | Primary Evaluation Benchmarks |
| :--- | :--- | :--- | :--- | :--- |
| **Ultra-Lightweight / Real-time** | Piper TTS, Kokoro (82M) | 50MB – 350MB | Kokoro-ONNX, Piper CLI, sherpa-onnx | Character Error Rate (CER), Real-Time Factor (RTF) |
| **Voice Cloning / Expressive** | XTTS-v2, F5-TTS, CosyVoice | 1.5GB – 4GB | ComfyUI-TTS, Official PyTorch repos, Transformers | Speaker Similarity, Naturalness MOS |

### Practical Operational Notes
* **Kokoro-82M:** Produces state-of-the-art voice quality matching multi-gigabyte models while fitting into ~300MB RAM/VRAM. Runs faster than real-time on CPU.
* **Licensing Pitfall:** Many expressive TTS models (e.g., Coqui XTTS-v2 under CPML) prohibit commercial deployment without custom commercial agreements. Always verify license terms for deployment.

---

## 7. Image Generation

* **Core Objective:** Text-to-image synthesis, inpainting, outpainting, image-to-image styling, LoRA adaptation.
* **Key Demands:** High GPU VRAM (for latent diffusion and text encoders), tensor parallel speed, scheduler step efficiency.

| Baseline | Architecture | Text Encoders | Recommended Runtimes | Target Hardware |
| :--- | :--- | :--- | :--- | :--- |
| **Legacy / High Speed** | Stable Diffusion 1.5 | CLIP ViT-L | Automatic1111, ComfyUI, SD.cpp | 4GB – 6GB VRAM (Low-end / Integrated) |
| **Workhorse / General Purpose**| SDXL 1.0, Pony Diffusion, SDXL Turbo | CLIP ViT-L + OpenCLIP ViT-bigG | ComfyUI, Forge, Fooocus | 8GB – 12GB VRAM |
| **Next-Gen Diffusion / DiT** | FLUX.1 [schnell], FLUX.1 [dev], SD 3.5 Medium | T5-XXL + CLIP ViT-L | ComfyUI, Forge (with GGUF/NF4 support) | 12GB – 24GB+ VRAM (or FP8 / Q4 GGUF on 8GB–12GB) |

### Practical Operational Notes
* **Workload-Dependent Memory Scaling:** VRAM consumption is heavily driven by render parameters:
  * *Resolution Scaling:* Attention memory scales quadratically ($O(H \times W)^2$) with pixel count. Generating at 1024x1024 requires ~4x the activation memory of 512x512 unless FlashAttention or tiled VAE decoding is active.
  * *Batch Size:* Keep batch size at 1 on consumer GPUs (8GB–12GB). Generating 4 images in parallel will instantly cause CUDA Out-of-Memory.
* **Text Encoder Offloading:** Models like FLUX.1 utilize a large T5-XXL text encoder (~9GB in FP16, ~4.5GB in FP8). Runtimes like ComfyUI and Forge offload the text encoder to system RAM after computing prompt embeddings, allowing 12B DiT models to run on 8GB–12GB VRAM cards.
* **GGUF and NF4 Formats:** Running FLUX or SDXL in GGUF or bitsandbytes NF4 format reduces transformer weight memory by 50% with minimal perceptual fidelity loss.

---

## 8. Video Generation

* **Core Objective:** Text-to-video, image-to-video, camera trajectory conditioning.
* **Key Demands:** Massive VRAM for 3D spatio-temporal latents, multi-second frame sequences, compute-intensive diffusion steps.

| Architecture | Model Families | Parameter Footprint | Target Runtimes | Hardware Threshold |
| :--- | :--- | :--- | :--- | :--- |
| **Compact Video DiT** | Wan2.1 (1.3B), LTX-Video (0.9B) | 1B – 2B | ComfyUI, Diffusers | 8GB – 12GB VRAM (with FP8/GGUF + CPU offload) |
| **High-Fidelity Video DiT** | Wan2.1 (14B), HunyuanVideo, CogVideoX (5B) | 5B – 14B | ComfyUI, Diffusers (requires torch 2.4+) | 16GB – 24GB+ VRAM (minimum for acceptable speeds) |

### Practical Operational Notes
* **Severe Workload Dependency:** Video VRAM and compute scale along three distinct axes:
  1. *Frame Count:* A 49-frame clip (~2 sec) fits within consumer bounds, whereas an 81-frame or 161-frame sequence requires double to triple the latent VRAM.
  2. *Resolution:* 480p is viable on 8GB–12GB; 720p or 1080p requires either block swapping or a 16GB–24GB GPU.
  3. *VAE Spatial/Temporal Tiling:* Without tiled VAE decoding enabled, memory spikes during final pixel reconstruction and triggers immediate OOM.
* **Feasibility Warning:** Video generation requires tens of seconds to several minutes per clip on consumer GPUs. An 8GB GPU using heavy CPU offload may take 10–20 minutes to generate a 3-second 720p clip.
* **Block Swapping:** Runtimes like ComfyUI with `ComfyUI-VideoHelperSuite` swap transformer blocks sequentially between system RAM and VRAM to prevent OOM errors, but memory bandwidth becomes the primary bottleneck.

---

## 9. Local AI Agents and Automation

* **Core Objective:** Tool calling, JSON schema compliance, autonomous multi-step reasoning, environment observation and action.
* **Key Demands:** Precise tool-call formatting (e.g., standard OpenAI function calling syntax), context resistance to long tool output histories, strict adherence to system constraints.

| Tier | Representative Model Families | Supported Runtimes | Critical Evaluation Criteria |
| :--- | :--- | :--- | :--- |
| **Small Agent (7B–9B)** | Qwen 2.5-7B-Instruct, Llama 3.1-8B-Instruct, Hermes 3 (8B) | Ollama, vLLM, llama.cpp | Berkeley Function-Calling Leaderboard (BFCL), ToolBench |
| **Workhorse Agent (14B–32B)** | Qwen 2.5-14B/32B-Instruct, Command R (35B) | vLLM, llama.cpp, Ollama | BFCL V2/V3, complex multi-tool execution rate |
| **Frontier Local Agent (70B+)**| Qwen 2.5-72B-Instruct, Llama 3.1-70B-Instruct | vLLM, ExLlamaV2, Aphrodite | Long-horizon planning, error recovery, API formatting |

### Practical Operational Notes
* **Schema Adherence via Grammars:** To guarantee valid JSON or function calls from smaller local models (7B–14B), enforce structured outputs using GBNF grammars in `llama.cpp` or JSON schema guided decoding in `vLLM` (Outlines / XGrammar).
* **Context Accumulation:** Multi-step agents accumulate tool outputs (HTML, bash outputs, file contents) rapidly. Ensure the model supports at least 32,768 tokens without degradation.


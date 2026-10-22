# Local Model Scout

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Format: Claude Skill](https://img.shields.io/badge/Claude%20Skill-Specification%20Compliant-green.svg)](SKILL.md)

**Local Model Scout** is a documentation-first Claude Agent Skill that identifies, compares, and recommends the most suitable local AI models for a user's exact hardware profile and use case.

It eliminates the frustrating trial-and-error cycle of downloading 10GB–50GB model checkpoints only to encounter Out-of-Memory (OOM) crashes, catastrophic memory thrashing (e.g., 0.5 tokens/sec generation on Windows PCIe fallback), excessive quantization perplexity loss, or commercial license violations.

---

## The Problem Being Solved

Deploying AI models locally requires balancing complex interdependent constraints:
* **The "File Size != Memory Required" Trap:** An 8B model quantized to Q4_K_M is 4.9 GB on disk, but requires ~6.8 GB of VRAM once the Key-Value (KV) cache, CUDA context, and activation memory are allocated.
* **The Bandwidth Bottleneck:** Token generation speed in autoregressive models is bound by memory bandwidth, not compute. Running an offloaded 30GB model across dual-channel DDR4 RAM (25 GB/s) yields unviable speeds (~1 tok/s), even if the model "fits" into 32GB of RAM.
* **Architecture Mismatches:** Selecting a general chat model for inline code completion lacks Fill-in-the-Middle (FIM) support, leading to unwanted conversational prose instead of code infill.
* **Licensing Pitfalls:** Deploying open-weight models with restrictive non-commercial terms (e.g., CC-BY-NC, CPML) or conditional user thresholds (Meta Llama 3.1 700M MAU limit) into commercial products.

Local Model Scout applies rigorous hardware math and domain evaluation to provide grounded, actionable recommendations before you download a single byte.

---

## Key Capabilities

* **Hardware Boundary Physics:** Accurately calculates total memory budgets ($M_{\text{weights}} + M_{\text{kv\_cache}} + M_{\text{activations}} + M_{\text{overhead}}$) and estimates realistic token generation speeds based on memory bus bandwidth (DDR4/DDR5 vs. GDDR6/6X vs. Apple Unified Memory).
* **Coverage Across 9 Core Domains:**
  1. General-purpose chat and reasoning
  2. Coding and software development
  3. Vision and multimodal understanding
  4. Embeddings and reranking
  5. Speech-to-text (STT)
  6. Text-to-speech (TTS)
  7. Image generation
  8. Video generation
  9. Local AI agents and automation
* **Grounded Licensing Audits:** Differentiates permissive open-source licenses (MIT, Apache 2.0) from open weights with commercial limits (Meta Llama Community, DeepSeek) and research-only licenses (CC-BY-NC).
* **Hardware Profile Extraction:** Provides exact, single-line OS commands for Windows (PowerShell), macOS (Terminal), and Linux to extract CPU, RAM, VRAM, and storage specs when users are uncertain.
* **Multi-Tier Recommendations:** Recommends one Best-Fit model and up to two alternatives (Speed/Efficiency vs. Quality/Workstation Ceiling).
* **Concrete Deployment & Validation:** Delivers copy-paste installation commands (Ollama, llama.cpp, LM Studio, vLLM, ComfyUI) along with a verification test prompt and memory health check.
* **Pragmatic Cloud Fallback Triggers:** Identifies when a workload exceeds local feasibility and recommends cloud models (e.g., Claude 3.5 Sonnet / Claude 3.7 Sonnet) when appropriate, while upholding a local-first philosophy.

---

## Repository Structure

```
local-model-scout/
├── SKILL.md                          # Primary Claude Skill specification and operational instructions
├── README.md                         # Project documentation and user guide
├── LICENSE                           # MIT License
├── CONTRIBUTING.md                   # Contributor guidelines and code of conduct
├── CHANGELOG.md                      # Release history and version tracking
├── .gitignore                        # Git exclusion rules for caches, secrets, and temp files
├── references/
│   ├── use-case-matrix.md            # Mapping tasks to model families, runtimes, and benchmarks
│   ├── hardware-compatibility.md     # Memory estimation formulas, bandwidth physics, and OS quirks
│   └── model-selection-guide.md      # 7-step evaluation protocol, license audit, and verification rules
├── examples/
│   ├── coding-model.json             # Illustrative coding recommendation (RTX 3060 12GB)
│   ├── local-chat.json               # Illustrative chat recommendation (MacBook M3 16GB)
│   └── image-generation.json         # Illustrative image gen recommendation (RTX 4070 12GB)
└── tests/
    ├── test-scenarios.md             # 6 detailed acceptance test scenarios with verification criteria
    └── validate_skill.py             # Automated standard-library structural validation script
```

---

## Installation & Setup

### Method 1: Installing in Claude Code (CLI)

Claude Code discovers skills located in its project-level or global configuration directories.

#### Project-Level Installation (Recommended)
Installing at the project level makes the skill available whenever you work in that repository:
```bash
# From your target repository root:
mkdir -p .claude/skills
cp -r /path/to/local-model-scout .claude/skills/
```

#### User-Level (Global) Installation
To make the skill accessible across all Claude Code sessions on your system:

* **macOS / Linux:**
  ```bash
  mkdir -p ~/.claude/skills
  cp -r /path/to/local-model-scout ~/.claude/skills/
  ```

* **Windows (PowerShell):**
  ```powershell
  New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills"
  Copy-Item -Recurse -Path ".\local-model-scout" -Destination "$HOME\.claude\skills\"
  ```

Once installed, Claude Code automatically indexes the skill and activates it whenever you ask questions about local models, hardware requirements, or offline deployments.

---

### Method 2: Installing in Claude.ai (Web Interface)

Claude.ai supports custom project instructions and project knowledge files:

1. In **Claude.ai**, navigate to **Projects** and click **Create Project**.
2. Name the project **Local Model Scout** (or your custom project name).
3. In the **Project Knowledge** pane, upload:
   * `SKILL.md`
   * `references/use-case-matrix.md`
   * `references/hardware-compatibility.md`
   * `references/model-selection-guide.md`
4. In the **Custom Instructions** field, paste:
   ```text
   You are an expert AI systems engineer equipped with the Local Model Scout skill. Follow the instructions in SKILL.md and referenced guides to gather hardware specifications, calculate memory budgets, and provide grounded, verified local model recommendations.
   ```
5. Start a chat within the project.

---

## Testing & Verification

### 1. Automated Structural Validation
The repository includes a standalone Python validation script that checks file integrity, frontmatter schema compliance, JSON syntax, and markdown cross-references using only the Python standard library:

```bash
python tests/validate_skill.py
```

### 2. Live Behavioral Testing & Limitations of Static Tests
> [!IMPORTANT]
> **Static Validation vs. Behavioral Execution:**
> Passing file existence and schema validation confirms that the skill is syntactically well-formed, but **it does not prove that Claude will execute the skill instructions correctly** in a dynamic conversational context.
>
> LLMs may still hallucinate specs, guess missing GPUs, or overlook KV cache growth if instructions are ambiguous. You must perform manual behavioral testing to verify live adherence.

### 3. Realistic Manual Testing Procedure
To verify that Claude follows the skill instructions in Claude Code or Claude.ai:

1. **Test Missing Hardware Handling:**
   * Prompt: *"What local AI model should I use for coding?"*
   * *Pass Condition:* Claude **must not** guess a GPU or immediately recommend a 14B model. It must prompt for hardware details or provide the OS-specific diagnostic commands from `SKILL.md`.
2. **Test Negative Constraint Enforcement (Low-RAM Scenario):**
   * Prompt: *"I have a Windows laptop with 8GB RAM and integrated Intel graphics. Can I run a 7B or 14B model for coding?"*
   * *Pass Condition:* Claude must explicitly state that 7B/14B models exceed the 3.5GB–4GB usable RAM ceiling, warn about SATA/NVMe swap thrashing, recommend a $\le 3\text{B}$ model (e.g., Qwen2.5-Coder-1.5B/3B), and suggest cloud fallback for larger tasks.
3. **Test VRAM & KV Cache Budgeting (8GB GPU Scenario):**
   * Prompt: *"I have an RTX 3070 8GB on Windows 11. Can I run a 14B coding model with 32k context?"*
   * *Pass Condition:* Claude must reject 14B for full GPU offload, explain Windows DWM overhead ($\approx 1.2\text{GB}$) and KV cache memory ($\approx 4\text{GB}$ for 32k in FP16), and warn about NVIDIA Sysmem Fallback thrashing (0.5 tok/s).
4. **Detailed Test Scenarios:** Consult [`tests/test-scenarios.md`](tests/test-scenarios.md) for all 6 documented scenarios and acceptance criteria.

---

## How to Use the Skill

Ask Claude any question about selecting or running models on local hardware. If you know your hardware details, include them in the prompt. If not, Claude will provide commands to look them up.

### Example Prompts

#### 1. Software Engineering & Coding
> *"I have an NVIDIA RTX 3060 with 12GB VRAM, 32GB DDR4 RAM, and an 8-core CPU on Windows 11. What is the best coding model I can run locally with Ollama for Python and TypeScript development in VS Code?"*

#### 2. Apple Silicon Conversational Reasoning
> *"I'm on an M3 MacBook Air with 16GB Unified Memory. I want a private conversational model that can handle document summarization and complex analytical reasoning without killing my battery. What should I run?"*

#### 3. Image Generation on Consumer GPU
> *"Can I run FLUX.1 on an RTX 4070 12GB? How does it compare to SDXL, what precision should I use in ComfyUI, and will it fit in VRAM?"*

#### 4. Hardware Discovery Assistance
> *"I want to run a local LLM for offline research, but I don't know my exact computer specifications. How do I find out what I have?"*

---

## Example Hardware Profiles & Capabilities

| Hardware Profile | Memory Configuration | Usable AI Memory | Sweet-Spot Model Tiers | Typical Use Cases |
| :--- | :--- | :--- | :--- | :--- |
| **Budget Laptop** | 16GB DDR4/DDR5, Integrated GPU | 8GB–10GB (System RAM) | 1.5B–3B Q8, 7B–8B Q4_K_M (CPU) | Lightweight chat, Whisper transcription, basic code autocomplete |
| **Mainstream Desktop** | RTX 3060 / 4060 (12GB VRAM), 32GB RAM | 9.5GB–10.5GB VRAM | 7B–14B Q4/Q5 (Full VRAM), SDXL FP16 | Full-speed interactive coding, fast chat, high-res image gen |
| **Upper Workstation** | RTX 3090 / 4090 (24GB VRAM), 64GB RAM | 21GB–22.5GB VRAM | 32B Q4/Q5, 70B Q3/Q4 (partial offload), FLUX.1 FP8 | Enterprise-grade coding, 32k context, complex DiT image gen |
| **Apple Silicon (M-Series)**| 36GB–64GB Unified Memory | 25GB–50GB Unified | 14B–32B Q5/Q8, 70B Q4_K_M (Full Metal GPU) | High-context research, massive documents, quiet battery operation |

---

## Limitations

* **Documentation & Consultation Skill:** This skill guides and evaluates; it does not automatically execute model downloads or run automated benchmark test suites on your machine.
* **Theoretical Speed Bounds:** Generation speed figures are theoretical approximations based on hardware memory bandwidth. Real-world performance will vary based on system thermal limits, background applications, OS display scaling, and runtime binary versions.
* **Dynamic Model Ecosystem:** Open-weight models evolve rapidly. While this skill provides principles, formulas, and verified architectures, users should verify the latest releases on Hugging Face and Ollama for newly published checkpoints.

---

## Contributing

Contributions to improve hardware profiles, benchmarks, and runtime guidance are welcome. Please read our [Contributor Guidelines](CONTRIBUTING.md) for details on our code of conduct, development workflow, and testing requirements:

1. Fork the repository.
2. Create a topic branch (`git checkout -b feature/new-hardware-profile`).
3. Ensure all tests pass (`python tests/validate_skill.py`).
4. Keep `SKILL.md` strictly aligned with official Claude Skill frontmatter standards.
5. Submit a detailed Pull Request. See [CONTRIBUTING.md](CONTRIBUTING.md) and track version updates in [CHANGELOG.md](CHANGELOG.md).

---

## License

This project is licensed under the [MIT License](LICENSE).


# Hardware Compatibility & Memory Engineering Guide

This guide establishes the mathematical and architectural principles required to assess whether a local AI model can execute on target hardware with acceptable performance.

---

## 1. Core Hardware Subsystems

Local AI execution stresses four primary subsystems:

1. **VRAM (Video RAM):** Dedicated high-bandwidth memory (GDDR6, GDDR6X, HBM) on discrete GPUs. Required for fast autoregressive token generation and diffusion processing.
2. **Unified Memory (UMA):** Shared physical memory found on Apple Silicon (M-series chips) and some modern APUs (AMD Strix Point). High memory bandwidth (100 GB/s to 800+ GB/s) accessible by both CPU and GPU cores.
3. **System RAM (DDR4 / DDR5):** Standard host memory. Highly scalable in capacity (32GB, 64GB, 128GB+), but restricted in bandwidth (30 GB/s to 90 GB/s).
4. **Storage (NVMe vs. SATA / HDD):** Determines model weight load times into memory and swap behavior. Loading a 16GB model takes ~3 seconds on a PCIe Gen4 NVMe (5,000 MB/s), ~30 seconds on a SATA SSD (500 MB/s), and over 3 minutes on a mechanical HDD (80 MB/s).

---

## 2. Memory Estimation Framework

Never determine model viability solely by comparing model file size to available memory. Total memory allocation ($M_{\text{total}}$) consists of four additive components:

$$M_{\text{total}} = M_{\text{weights}} + M_{\text{kv\_cache}} + M_{\text{activations}} + M_{\text{runtime\_overhead}}$$

### Component 1: Weight Memory ($M_{\text{weights}}$)
Model parameters ($\text{Param Count}$ in billions) multiplied by the average bits-per-weight, plus quantization block scales and metadata:

$$M_{\text{weights}} \approx \text{Params (Billions)} \times \text{Bytes-per-Weight}$$

| Quantization Format | Effective Bits / Weight | Multiplier (Bytes / Param) | Retention / Perceptual Quality |
| :--- | :--- | :--- | :--- |
| **FP16 / BF16** | 16.0 | 2.000 | Baseline unquantized accuracy |
| **Q8_0 (8-bit)** | 8.5 | 1.062 | Indistinguishable from FP16 (<0.1% perplexity delta) |
| **Q6_K (6-bit)** | 6.5 | 0.812 | Near-lossless (<0.5% perplexity delta) |
| **Q5_K_M (5-bit)** | 5.5 | 0.687 | Sweet spot for quality-to-size (<1.0% perplexity delta) |
| **Q4_K_M (4-bit)** | 4.5 | 0.562 | Recommended desktop standard (~1.5% perplexity delta) |
| **Q3_K_M (3-bit)** | 3.5 | 0.437 | Noticeable reasoning degradation; usable only for simple chat |
| **Q2_K (2-bit)** | 2.5 | 0.312 | Severe degradation, repetitive loops, hallucination prone |

*Example:* An 8B parameter model at `Q4_K_M` requires:
$$8 \times 0.562 \approx 4.50\text{ GB (Weights)}$$
A 70B parameter model at `Q4_K_M` requires:
$$70 \times 0.562 \approx 39.34\text{ GB (Weights)}$$

---

### Component 2: Key-Value (KV) Cache Memory ($M_{\text{kv\_cache}}$)
The KV cache stores intermediate attention states across all processed context tokens. It scales linearly with context length, layer count, and hidden dimensions:

$$M_{\text{kv\_cache}} = 2 \times n_{\text{layers}} \times n_{\text{kv\_heads}} \times d_{\text{head}} \times C_{\text{tokens}} \times B_{\text{element}}$$

Where:
* $n_{\text{layers}}$ = Number of transformer layers.
* $n_{\text{kv\_heads}}$ = Number of key-value attention heads. Modern models use **Grouped-Query Attention (GQA)** where $n_{\text{kv\_heads}} \ll n_{\text{attention\_heads}}$ (typically 8 heads), reducing KV cache size by 4x to 8x compared to Multi-Head Attention (MHA).
* $d_{\text{head}}$ = Dimension per head (typically 128).
* $C_{\text{tokens}}$ = Context length in tokens (e.g., 4,096; 32,768; 131,072).
* $B_{\text{element}}$ = Bytes per element (2 bytes for FP16, 1 byte for Q8_0, 0.5 bytes for Q4_0).

#### Practical KV Cache Sizing Rules

Each token requires storing both Key and Value attention states across all layers:
$$\text{Bytes per token} = 2 \times n_{\text{layers}} \times n_{\text{kv\_heads}} \times d_{\text{head}} \times B_{\text{element}}$$

* **Llama 3.1 8B** ($n_{\text{layers}}=32, n_{\text{kv\_heads}}=8, d_{\text{head}}=128$):
  * Elements per token: $2 \times 32 \times 8 \times 128 = 65,536$ elements ($128\text{ KiB/token}$ in FP16, $64\text{ KiB/token}$ in Q8_0)
  * **FP16 KV Cache ($B=2$):**
    * At 4,096 context: $\approx 0.50\text{ GiB}$ ($0.54\text{ GB}$)
    * At 16,384 context: $\approx 2.00\text{ GiB}$ ($2.15\text{ GB}$)
    * At 32,768 context: $\approx 4.00\text{ GiB}$ ($4.29\text{ GB}$)
    * At 131,072 context: $\approx 16.00\text{ GiB}$ ($17.18\text{ GB}$)
  * **Q8_0 Quantized KV Cache ($B=1$):**
    * At 4,096 context: $\approx 0.25\text{ GiB}$
    * At 16,384 context: $\approx 1.00\text{ GiB}$
    * At 32,768 context: $\approx 2.00\text{ GiB}$
    * At 131,072 context: $\approx 8.00\text{ GiB}$

* **Qwen 2.5 72B** ($n_{\text{layers}}=80, n_{\text{kv\_heads}}=8, d_{\text{head}}=128$):
  * Elements per token: $2 \times 80 \times 8 \times 128 = 163,840$ elements ($320\text{ KiB/token}$ in FP16, $160\text{ KiB/token}$ in Q8_0)
  * **FP16 KV Cache ($B=2$):**
    * At 8,192 context: $\approx 2.50\text{ GiB}$ ($2.68\text{ GB}$)
    * At 32,768 context: $\approx 10.00\text{ GiB}$ ($10.74\text{ GB}$)
    * At 131,072 context: $\approx 40.00\text{ GiB}$ ($42.95\text{ GB}$)
  * **Q8_0 Quantized KV Cache ($B=1$):**
    * At 8,192 context: $\approx 1.25\text{ GiB}$
    * At 32,768 context: $\approx 5.00\text{ GiB}$
    * At 131,072 context: $\approx 20.00\text{ GiB}$

> [!TIP]
> **KV Cache Quantization (`--cache-type-k q8_0 --cache-type-v q8_0`):** Enabling 8-bit KV caching cuts KV memory by exactly 50% with near-zero accuracy penalty. Enabling 4-bit (`q4_0`) cuts KV memory by 75%, which is critical when attempting 32k–128k context on consumer GPUs with 8GB–16GB VRAM.

---

### Component 3 & 4: Activation Memory & Runtime Overhead
* **Activation Working Buffers:** $0.2\text{ GB} - 1.5\text{ GB}$ depending on batch size and hidden layer dimensions during the forward pass.
* **CUDA / Driver Context:** Modern NVIDIA drivers and CUDA runtimes claim $300\text{ MB} - 800\text{ MB}$ of VRAM immediately upon initialization.
* **OS Desktop Display Overhead:** Windows Desktop Window Manager (DWM) or macOS WindowServer reserves $500\text{ MB} - 1.5\text{ GB}$ of VRAM on the primary display adapter. A "12GB GPU" running Windows 11 typically has only **10.5GB to 11.0GB usable VRAM** before launching any model.

---

## 3. Launch Feasibility vs. Practical Performance

A critical error in local AI evaluation is treating **loading viability** as **practical usability**.

### The Memory Bandwidth Bottleneck
Autoregressive token generation (outputting one token after another) is **memory-bandwidth bound**, not compute bound. To generate a single token, the processor must read every active parameter from memory into the compute registers:

$$\text{Theoretical Max Speed (Tokens/Second)} \approx \frac{\text{Memory Bandwidth (GB/s)}}{\text{Model Memory Footprint (GB)}}$$

| Hardware Class | Typical Memory Bus | Memory Bandwidth | 8B Q4 Model (4.5GB) Max Speed | 70B Q4 Model (40GB) Max Speed |
| :--- | :--- | :--- | :--- | :--- |
| **System DDR4 (Dual Channel)** | 128-bit DDR4-3200 | ~25.6 GB/s | 5.6 tok/s | 0.6 tok/s (Unusable) |
| **System DDR5 (Dual Channel)** | 128-bit DDR5-6000 | ~50 - 60 GB/s | 11 - 13 tok/s | 1.2 - 1.5 tok/s (Impractical) |
| **NVIDIA RTX 4060 (8GB)** | 128-bit GDDR6 | 272 GB/s | 60 tok/s | Cannot fit in VRAM |
| **NVIDIA RTX 4070 (12GB)** | 192-bit GDDR6X | 504 GB/s | 100+ tok/s | Cannot fit in VRAM |
| **NVIDIA RTX 3090 / 4090 (24GB)**| 384-bit GDDR6X | 936 - 1008 GB/s | 150+ tok/s | Requires partial split or 2x GPUs |
| **Apple M4 Pro (Unified)** | 256-bit LPDDR5X | 273 GB/s | ~55 tok/s | Cannot fit in 24GB/48GB |
| **Apple M2 / M3 Max (Unified)** | 512-bit LPDDR5 | 300 - 400 GB/s | ~70 tok/s | 8 - 10 tok/s (Usable) |
| **Apple M2 / M3 Ultra (Unified)**| 1024-bit LPDDR5 | 800 GB/s | 130+ tok/s | 18 - 20 tok/s (Comfortable) |

### CPU-Only and Partial GPU Offloading Realities
1. **CPU-Only Inference:**
   * Models up to 8B (`Q4_K_M`) run at 8–15 tok/s on modern AVX-512 / AVX2 CPUs with dual-channel DDR5.
   * Models $\ge 14\text{B}$ drop below 5 tok/s on CPU, becoming tedious for interactive dialogue.
2. **Partial Offloading (e.g., 20 of 32 layers on GPU, 12 layers on CPU):**
   * The pipeline can only move as fast as its slowest link. The PCIe bus transfer (PCIe 4.0 x16 $\approx 31.5\text{ GB/s}$) and system RAM latency will bottleneck the GPU layers.
   * Partial offloading is valuable for **fitting** models into memory, but expect generation speeds to align closer to system RAM speeds than GPU speeds.

---

## 4. Operating System & Platform Specifics

### Apple Silicon (macOS)
* **Unified Memory Dynamic Allocation:** macOS enforces a default system ceiling on how much memory a single Metal process can allocate (`wired_mem_limit`). Typically, macOS reserves 25% of total RAM for system processes.
  * Example: A 16GB Mac allows approximately 11GB–12GB for Metal allocations without sysctl overrides.
  * To unlock up to 85% memory on macOS for local models, run:
    ```bash
    sudo sysctl iogpu.wired_mem_limit=XXXXX
    ```
* **Performance:** Metal compute is highly optimized in `llama.cpp` and `MLX`. Apple Silicon excels at large memory footprint models (32B–70B) on high-spec configurations (64GB–128GB unified memory) that would otherwise require multi-thousand dollar multi-GPU server setups.

### Windows (DirectX / CUDA / Vulkan)
* **NVIDIA Sysmem Fallback Behavior:** Modern NVIDIA Windows drivers (release 536+) feature a fallback mechanism: when VRAM is exceeded by even 1MB, the driver offloads memory into system RAM rather than crashing with an Out-of-Memory (OOM) error.
  * **The Problem:** This causes generation speeds to collapse from 80 tok/s to 0.5 tok/s without warning.
  * **Solution:** In the NVIDIA Control Panel under *3D Settings* $\rightarrow$ *CUDA - Sysmem Fallback Policy*, change setting to **"Prefer No Sysmem Fallback"**. This forces clean OOM errors rather than silent, catastrophic thrashing.

### Linux (CUDA / ROCm / Vulkan)
* **ROCm Compatibility:** AMD GPUs under Linux require specific ROCm kernel drivers and GFX architecture targeting. For consumer RDNA3 cards (e.g., RX 7900 XTX / 7800 XT):
  ```bash
  export HSA_OVERRIDE_GFX_VERSION=11.0.0
  export HCC_AMDGPU_TARGET=gfx1100
  ```
* **Hugepages & NUMA:** On multi-socket systems or servers running vLLM, configure Transparent Hugepages (THP) and `numactl --interleave=all` to prevent NUMA bus memory bottlenecks.

---

## 5. Diagnostic Commands: How to Extract Hardware Profiles

When the user is uncertain of their hardware configuration, instruct them to execute the appropriate OS diagnostic command:

### Windows (PowerShell)
```powershell
# Extract CPU, System RAM, GPU, and Free Storage with clean list formatting
Get-CimInstance Win32_Processor | Select-Object Name | Format-List
Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum | Select-Object @{N="RAM_GB";E={[math]::round($_.Sum/1GB,1)}} | Format-List
Get-CimInstance Win32_VideoController | Select-Object Name, @{N="Reported_VRAM_GB";E={[math]::round($_.AdapterRAM/1GB,1)}} | Format-List
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N="Free_GB";E={[math]::round($_.Free/1GB,1)}} | Format-List
```
> [!NOTE]
> *NVIDIA VRAM Accuracy Note:* WMI `Win32_VideoController.AdapterRAM` uses a 32-bit signed integer that caps or misreports dedicated VRAM above 4GB on modern GPUs. If you have an NVIDIA card, always run `nvidia-smi` or verify **Dedicated GPU Memory** in **Windows Task Manager $\rightarrow$ Performance $\rightarrow$ GPU**.

### macOS (Terminal)
```bash
# Extract Chip, Total Memory, and Core counts
system_profiler SPHardwareDataType SPDisplaysDataType | grep -E "Chip:|Memory:|Cores:|Total Number of Cores:|VRAM"
# Check available disk storage
df -h /
```

### Linux (Terminal)
```bash
# CPU and Core info
lscpu | grep -E "Model name|Core\(s\) per socket|Socket\(s\)"
# RAM capacity
free -h
# GPU check (NVIDIA)
nvidia-smi --query-gpu=gpu_name,memory.total,driver_version --format=csv,noheader || lspci | grep -i vga
# Storage
df -h /
```

---

## 6. Common Compatibility Failures & Troubleshooting Matrix

| Symptom | Root Cause | Engineering Solution |
| :--- | :--- | :--- |
| `CUDA out of memory` during first prompt | Context length exceeds available VRAM after loading weights. | 1. Reduce context parameter (e.g., `num_ctx 4096` instead of `32768`).<br>2. Enable 8-bit/4-bit KV cache (`--cache-type-k q8_0`).<br>3. Lower GPU layer offload (`-ngl`) by 2–4 layers. |
| Model runs at 0.5–1.0 tok/s on an RTX card | NVIDIA driver thrashing across PCIe bus due to Sysmem Fallback. | Set "Prefer No Sysmem Fallback" in driver or choose a smaller quant (`Q4_K_M` instead of `Q8_0`). |
| Incoherent output / endless loops on high context | Context exceeds native RoPE limit without proper frequency scaling. | Check model native context limit. Add RoPE scaling parameters (`--rope-scaling yarn` or `--rope-freq-scale`) if extending beyond native window. |
| `llama_model_loader: unknown tensor architecture` | Runtime binary is older than model architecture (e.g., trying to run Qwen 2.5 or Gemma 2 on obsolete llama.cpp builds). | Update `llama.cpp` or `Ollama` to the latest release version. |
| Image generation OOMs on 8GB/12GB cards (FLUX / SDXL) | Text encoder and UNet/DiT loaded simultaneously into VRAM. | Enable CPU text encoder offloading (`--lowvram` in ComfyUI / Forge) and use FP8 or GGUF transformer weights. |


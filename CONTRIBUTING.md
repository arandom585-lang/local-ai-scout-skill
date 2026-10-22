# Contributing to Local Model Scout

Thank you for your interest in contributing to **Local Model Scout**!

Local Model Scout is a documentation-first Claude Agent Skill designed to give users accurate, grounded, and mathematically sound local model recommendations. We welcome contributions that improve hardware profiles, keep runtime recommendations modern, and refine memory estimation formulas.

---

## Code of Conduct & Contribution Principles

When contributing to this project, you must adhere to the following core tenets:

1. **No Fabricated Benchmarks or Performance Claims:**
   * Never invent synthetic benchmark numbers (e.g., HumanEval, MMLU, GSM8K). Only cite official technical reports or verified public benchmark leaderboards.
   * Never promise exact tokens-per-second speeds on unverified hardware. Frame speed estimates as theoretical upper bounds based on memory bandwidth physics.
2. **Mathematical Rigor in Memory Sizing:**
   * Distinguish between model weight size, KV cache memory, activation memory, and runtime/driver overhead ($M_{\text{total}} = M_{\text{weights}} + M_{\text{kv\_cache}} + M_{\text{activations}} + M_{\text{overhead}}$).
   * Differentiate FP16 KV cache ($B=2$) from quantized KV cache ($B=1$ for Q8_0).
3. **Spec Compliance:**
   * Do not invent unsupported YAML frontmatter fields in `SKILL.md`. Only `name` and `description` are standard and supported.
   * The skill name must strictly follow the Claude skill naming format: lowercase alphanumeric and hyphens (`^[a-z0-9-]+$`).
4. **Zero-Dependency Philosophy:**
   * Structural test scripts (`tests/validate_skill.py`) must rely solely on the Python standard library. Do not add external dependencies.

---

## How to Contribute

### 1. Propose Changes or Report Issues
* Check existing GitHub Issues to see if your proposal or bug has already been reported.
* Open an Issue detailing:
  * Hardware specifics (OS, GPU, VRAM, RAM generation, PCIe/bus width).
  * Observed runtime behavior (e.g., unexpected OOM, driver sysmem fallback, kernel memory limits).
  * Proposed improvements to formulas or candidate matrices.

### 2. Local Development Workflow
1. Fork and clone the repository.
2. Make targeted, well-documented changes in Markdown or JSON files.
3. If modifying or adding JSON examples in `examples/`, ensure they include all required structural sections (`meta`, `user_input`, `hardware_budget_analysis`, `candidate_comparison`, `recommendation`, `deployment_and_validation`) and explicitly label illustrative data under `meta.data_nature`.
4. Run the automated structural validation test suite:
   ```bash
   python tests/validate_skill.py
   ```
   All tests must pass before submitting your pull request.

### 3. Pull Request Guidelines
* Keep PRs scoped to a single clear enhancement (e.g., updating a runtime command, adding a new hardware profile, or fixing documentation typos).
* Ensure all internal Markdown links and file references resolve properly.
* Update `CHANGELOG.md` under `[Unreleased]` with a brief description of your change.

---

## License

By contributing to Local Model Scout, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).


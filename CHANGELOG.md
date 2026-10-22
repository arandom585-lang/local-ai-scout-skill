# Changelog

All notable changes to the **Local Model Scout** Claude Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-23

### Added
* **Initial Release of Local Model Scout Claude Skill.**
* **Core Skill Specification (`SKILL.md`):** Complete 5-phase interaction workflow supporting 9 core AI model domains with compliant YAML frontmatter.
* **Domain Use-Case Matrix (`references/use-case-matrix.md`):** Comprehensive mapping of AI workloads to model architectures, target runtimes, and evaluation benchmarks.
* **Hardware & Memory Guide (`references/hardware-compatibility.md`):** Mathematical memory estimation formulas distinguishing weight precision, FP16 vs. Q8_0 KV cache sizing, runtime overhead, and memory bandwidth bounds.
* **Selection & Licensing Guide (`references/model-selection-guide.md`):** 7-step repeatable model evaluation protocol, licensing compliance checks, and cloud fallback heuristics.
* **Illustrative Examples (`examples/`):**
  * `coding-model.json`: Software engineering recommendation on an RTX 3060 12GB desktop.
  * `local-chat.json`: Conversational reasoning recommendation on an Apple M3 16GB MacBook.
  * `image-generation.json`: Diffusion Transformer (DiT) recommendation on an RTX 4070 12GB desktop.
* **Test Suite (`tests/`):**
  * `test-scenarios.md`: 6 acceptance test scenarios detailing inputs, expected behaviors, hardware limits, and acceptance criteria.
  * `validate_skill.py`: Zero-dependency Python validation script checking file structure, frontmatter specification compliance, JSON schemas, and markdown link resolution.
* **Project Documentation (`README.md`, `LICENSE`, `CONTRIBUTING.md`):** MIT license, installation instructions for Claude Code and Claude.ai, and contributor guidelines.


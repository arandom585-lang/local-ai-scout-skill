#!/usr/bin/env python3
"""
validate_skill.py - Automated structural validation for Local Model Scout Claude Skill.

Standard library only. Validates:
1. SKILL.md existence and non-emptiness.
2. YAML frontmatter parsing, required fields ('name', 'description'), and unsupported field rejection.
3. Skill name compliance with official Claude Skills specification (^[a-z0-9-]+$).
4. Presence and non-emptiness of all reference files in references/.
5. JSON syntax and schema completeness for all example files in examples/.
6. Resolution of all internal markdown file links in README.md and SKILL.md.
7. Presence and non-emptiness of core project files (LICENSE, README.md, tests/test-scenarios.md).
"""

import sys
import os
import re
import json
from pathlib import Path


class SkillValidator:
    def __init__(self, root_dir: Path):
        self.root = root_dir.resolve()
        self.passed = 0
        self.failed = 0
        self.errors = []

    def log_pass(self, test_name: str, detail: str = ""):
        self.passed += 1
        msg = f"[PASS] {test_name}"
        if detail:
            msg += f" - {detail}"
        print(msg)

    def log_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"[FAIL] {test_name} - {reason}")

    def test_core_files_exist(self):
        core_files = [
            "SKILL.md",
            "README.md",
            "LICENSE",
            ".gitignore",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "references/use-case-matrix.md",
            "references/hardware-compatibility.md",
            "references/model-selection-guide.md",
            "examples/coding-model.json",
            "examples/local-chat.json",
            "examples/image-generation.json",
            "tests/test-scenarios.md",
        ]
        for rel_path in core_files:
            file_path = self.root / rel_path
            if not file_path.exists():
                self.log_fail("Core File Existence", f"Missing required file: {rel_path}")
            elif file_path.stat().st_size == 0:
                self.log_fail("Non-Empty Files", f"Required file is empty (0 bytes): {rel_path}")
            else:
                self.log_pass("File Present & Non-Empty", rel_path)

    def test_skill_frontmatter(self):
        skill_path = self.root / "SKILL.md"
        if not skill_path.exists():
            self.log_fail("SKILL.md Frontmatter", "SKILL.md does not exist.")
            return

        content = skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
        if not match:
            self.log_fail("SKILL.md Frontmatter", "YAML frontmatter block ('---') missing or malformed.")
            return

        raw_yaml = match.group(1)
        fields = {}
        for line in raw_yaml.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                fields[k.strip()] = v.strip()

        # Check required fields
        if "name" not in fields or not fields["name"]:
            self.log_fail("SKILL.md Frontmatter", "Missing required 'name' field in frontmatter.")
        else:
            name = fields["name"]
            # Validate name follows Claude skill naming rules: lowercase alphanumeric + hyphens
            if not re.match(r"^[a-z0-9-]+$", name):
                self.log_fail("SKILL.md Name Spec", f"Skill name '{name}' must match '^[a-z0-9-]+$'.")
            else:
                self.log_pass("SKILL.md Name Spec", f"Valid skill name: '{name}'")

        if "description" not in fields or not fields["description"]:
            self.log_fail("SKILL.md Frontmatter", "Missing required 'description' field in frontmatter.")
        else:
            self.log_pass("SKILL.md Description Spec", f"Description present ({len(fields['description'])} chars).")

        # Disallow invented or unsupported frontmatter keys
        allowed_keys = {"name", "description"}
        unsupported = set(fields.keys()) - allowed_keys
        if unsupported:
            self.log_fail("SKILL.md Frontmatter Spec", f"Unsupported frontmatter fields detected: {unsupported}")
        else:
            self.log_pass("SKILL.md Frontmatter Strictness", "No unsupported frontmatter keys found.")

    def test_json_examples(self):
        examples_dir = self.root / "examples"
        if not examples_dir.exists():
            self.log_fail("Examples Directory", "examples/ directory missing.")
            return

        json_files = list(examples_dir.glob("*.json"))
        if not json_files:
            self.log_fail("JSON Examples", "No JSON files found in examples/.")
            return

        required_keys = {
            "meta",
            "user_input",
            "hardware_budget_analysis",
            "candidate_comparison",
            "recommendation",
            "deployment_and_validation",
        }

        for jf in json_files:
            rel_name = jf.relative_to(self.root).as_posix()
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                self.log_pass("JSON Syntax Valid", rel_name)
            except Exception as e:
                self.log_fail("JSON Syntax Valid", f"Error in {rel_name}: {e}")
                continue

            missing = required_keys - set(data.keys())
            if missing:
                self.log_fail("JSON Structure", f"{rel_name} missing required keys: {missing}")
            else:
                self.log_pass("JSON Structure", f"{rel_name} contains all required structural sections.")

            # Validate illustrative nature is labeled
            meta = data.get("meta", {})
            if "data_nature" not in meta:
                self.log_fail("JSON Transparency", f"{rel_name} meta section must clearly label data_nature.")
            else:
                self.log_pass("JSON Transparency", f"{rel_name} explicitly labels illustrative data.")

    def test_internal_file_references(self):
        doc_files = ["README.md", "SKILL.md", "tests/test-scenarios.md", "CONTRIBUTING.md", "CHANGELOG.md"]
        ref_pattern = re.compile(
            r'(?:references/[a-zA-Z0-9_\-]+\.md|examples/[a-zA-Z0-9_\-]+\.json|tests/[a-zA-Z0-9_\-]+\.md|LICENSE|SKILL\.md|CONTRIBUTING\.md|CHANGELOG\.md|\.gitignore)'
        )

        for doc_rel in doc_files:
            doc_path = self.root / doc_rel
            if not doc_path.exists():
                continue

            text = doc_path.read_text(encoding="utf-8")
            matches = set(ref_pattern.findall(text))
            for ref in matches:
                target = self.root / ref
                if not target.exists():
                    self.log_fail("Internal Link Resolution", f"Broken link '{ref}' referenced in {doc_rel}")
                else:
                    self.log_pass("Internal Link Resolution", f"{doc_rel} -> {ref} exists.")

    def run_all(self) -> int:
        print("=" * 65)
        print(f"Running Local Model Scout Skill Validation Suite: {self.root}")
        print("=" * 65)

        self.test_core_files_exist()
        self.test_skill_frontmatter()
        self.test_json_examples()
        self.test_internal_file_references()

        print("=" * 65)
        print(f"Validation Summary: {self.passed} passed, {self.failed} failed.")
        print("=" * 65)

        if self.failed > 0:
            print("\nFailures:")
            for test_name, reason in self.errors:
                print(f"  * {test_name}: {reason}")
            return 1

        print("\nAll automated structural tests PASSED successfully.")
        return 0


if __name__ == "__main__":
    skill_root = Path(__file__).resolve().parent.parent
    validator = SkillValidator(skill_root)
    sys.exit(validator.run_all())


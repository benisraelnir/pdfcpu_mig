#!/usr/bin/env python3
"""
BE Testing - CLI Contract Validation Tests

Generated pytest script to validate the CLI spec against the running application.
Each command is tested as a parameterized test case using pytest.

This script supports two modes:
1. SRC Validation: Tests commands and captures outputs (no expected_stdout/stderr)
2. DST Contract Validation: Tests commands and validates outputs match expected

Generated at: 2026-02-23T23:17:35.598469+00:00
Project: pdfcpumig
Milestone: 1
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

# =============================================================================
# Test Configuration (embedded from spec validation)
# =============================================================================

# Parse JSON at runtime to handle null -> None, true -> True, false -> False
TEST_CASES = json.loads(r'''[
    {
        "name": "test_no_args_prints_usage",
        "category": "HELP_OUTPUT",
        "description": "Running pdfcpu with no arguments prints general usage to stderr and exits 0",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu is a tool for PDF manipulation",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_no_args",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help' with no topic prints general usage to stderr",
        "command": "pdfcpu",
        "args": [
            "help"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu is a tool for PDF manipulation",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_validate_topic",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help validate' prints detailed validate usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "validate"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Check inFile for specification compliance",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_version_topic",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help version' prints version usage help",
        "command": "pdfcpu",
        "args": [
            "help",
            "version"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu version",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_paper_topic",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help paper' prints paper sizes usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "paper"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Print a list of supported paper sizes",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_selectedpages_topic",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help selectedpages' prints selectedpages usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "selectedpages"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Print definition of the -pages flag",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_prefix_matching_val",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help val' uses prefix matching to show validate help",
        "command": "pdfcpu",
        "args": [
            "help",
            "val"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Check inFile for specification compliance",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu help' with more than one topic argument prints error",
        "command": "pdfcpu",
        "args": [
            "help",
            "validate",
            "extra"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Too many arguments",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_unknown_topic",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu help nonexistent' prints unknown help topic message",
        "command": "pdfcpu",
        "args": [
            "help",
            "nonexistent"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Unknown help topic",
        "timeout_seconds": 10
    },
    {
        "name": "test_version_output",
        "category": "VERSION_OUTPUT",
        "description": "Running 'pdfcpu version' prints version string to stdout",
        "command": "pdfcpu",
        "args": [
            "version"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_version_shows_commit",
        "category": "VERSION_OUTPUT",
        "description": "Running 'pdfcpu version' prints commit info to stdout",
        "command": "pdfcpu",
        "args": [
            "version"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "commit:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_version_shows_config",
        "category": "VERSION_OUTPUT",
        "description": "Running 'pdfcpu version' prints config path to stdout",
        "command": "pdfcpu",
        "args": [
            "version"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "config:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_version_prefix_matching_ver",
        "category": "VERSION_OUTPUT",
        "description": "Running 'pdfcpu ver' uses prefix matching to invoke the version command",
        "command": "pdfcpu",
        "args": [
            "ver"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_version_extra_args_fails",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu version extraarg' fails with usage info and exit code 1",
        "command": "pdfcpu",
        "args": [
            "version",
            "extraarg"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu version",
        "timeout_seconds": 10
    },
    {
        "name": "test_paper_output",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu paper' prints supported paper sizes to stderr",
        "command": "pdfcpu",
        "args": [
            "paper"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "ISO 216:1975 A:",
        "timeout_seconds": 10
    },
    {
        "name": "test_paper_contains_a4",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu paper' includes A4 in the paper sizes list",
        "command": "pdfcpu",
        "args": [
            "paper"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "A4",
        "timeout_seconds": 10
    },
    {
        "name": "test_paper_contains_letter",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu paper' includes Letter in the paper sizes list",
        "command": "pdfcpu",
        "args": [
            "paper"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "Letter",
        "timeout_seconds": 10
    },
    {
        "name": "test_paper_contains_japan_sizes",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu paper' includes Japanese paper sizes",
        "command": "pdfcpu",
        "args": [
            "paper"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "JIS-B0",
        "timeout_seconds": 10
    },
    {
        "name": "test_selectedpages_output",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu selectedpages' prints page selection syntax to stderr",
        "command": "pdfcpu",
        "args": [
            "selectedpages"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "selects pages for processing",
        "timeout_seconds": 10
    },
    {
        "name": "test_selectedpages_contains_even_odd",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu selectedpages' documents 'even' and 'odd' selectors",
        "command": "pdfcpu",
        "args": [
            "selectedpages"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "even",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_no_args_shows_usage",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu validate' with no input files prints usage and exits 1",
        "command": "pdfcpu",
        "args": [
            "validate"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_with_pages_flag_shows_usage",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu validate' with -pages flag (not supported for validate) prints usage and exits 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-pages",
            "1-3",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "Running 'pdfcpu validate' with an invalid mode value prints usage and exits 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-mode",
            "invalid",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu validate",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "%PDF-1.4 minimal"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Running 'pdfcpu validate' on a nonexistent file fails with exit code 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "--",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file or directory",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_valid_pdf_relaxed",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate' on a valid PDF in default (relaxed) mode succeeds",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_valid_pdf_strict_mode",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -mode strict' on a valid PDF succeeds",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-mode",
            "strict",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf that passes strict validation"
    },
    {
        "name": "test_validate_strict_mode_short_flag",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -m s' uses short flag for strict mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "s",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_relaxed_mode_explicit",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -mode relaxed' explicitly uses relaxed mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-mode",
            "relaxed",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_relaxed_mode_short_r",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -m r' uses short 'r' for relaxed mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "r",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_invalid_pdf_fails",
        "category": "FILE_INPUT",
        "description": "Running 'pdfcpu validate' on an invalid/corrupt PDF fails with exit code 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-c",
            "disable",
            "--",
            "testdata/invalid.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "testdata/invalid.pdf",
                "content": "This is not a valid PDF file"
            }
        },
        "cleanup": {
            "delete_files": [
                "testdata/invalid.pdf"
            ]
        }
    },
    {
        "name": "test_validate_empty_file_fails",
        "category": "BOUNDARY",
        "description": "Running 'pdfcpu validate' on an empty file fails with exit code 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-c",
            "disable",
            "--",
            "testdata/empty.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "testdata/empty.pdf",
                "content": ""
            }
        },
        "cleanup": {
            "delete_files": [
                "testdata/empty.pdf"
            ]
        }
    },
    {
        "name": "test_validate_multiple_files",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate' with multiple valid PDF files validates all of them",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-c",
            "disable",
            "--",
            "testdata/valid1.pdf",
            "testdata/valid2.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires valid PDF fixtures at testdata/valid1.pdf and testdata/valid2.pdf"
    },
    {
        "name": "test_validate_prefix_matching_val",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu val' uses prefix matching to invoke validate command",
        "command": "pdfcpu",
        "args": [
            "val",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_with_verbose_flag",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -v' enables verbose logging during validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-v",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_with_quiet_flag",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -q' suppresses output during validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-q",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf. With -q, no output should appear."
    },
    {
        "name": "test_validate_strict_fails_on_relaxed_only_pdf",
        "category": "FILE_INPUT",
        "description": "Running 'pdfcpu validate -mode strict' on a PDF that only passes relaxed validation should fail with exit code 1 and suggest relaxed mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-mode",
            "strict",
            "-c",
            "disable",
            "--",
            "testdata/relaxed_only.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "try -mode=relaxed",
        "timeout_seconds": 30,
        "notes": "Requires a PDF fixture that passes relaxed but fails strict validation"
    },
    {
        "name": "test_unknown_command",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu nonexistent' with an unknown command prints error and exits 1",
        "command": "pdfcpu",
        "args": [
            "nonexistent"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "unknown command",
        "timeout_seconds": 10
    },
    {
        "name": "test_ambiguous_command_prefix",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu p' which is an ambiguous prefix (matches paper, pages, pagelayout, pagemode, permissions, portfolio, poster, properties) prints error and exits 1",
        "command": "pdfcpu",
        "args": [
            "p"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "ambiguous command",
        "timeout_seconds": 10
    },
    {
        "name": "test_config_disable_flag",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu version' with -c disable skips config loading",
        "command": "pdfcpu",
        "args": [
            "version",
            "-c",
            "disable"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_config_nonexistent_dir",
        "category": "INVALID_OPTIONS",
        "description": "Running a command with -conf pointing to a nonexistent directory fails with error",
        "command": "pdfcpu",
        "args": [
            "version",
            "-conf",
            "/nonexistent/config/dir"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "does not exist",
        "timeout_seconds": 10
    },
    {
        "name": "test_config_not_a_directory",
        "category": "INVALID_OPTIONS",
        "description": "Running a command with -conf pointing to a file (not directory) fails with error",
        "command": "pdfcpu",
        "args": [
            "version",
            "-conf",
            "/dev/null"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "not a directory",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_non_pdf_extension",
        "category": "BOUNDARY",
        "description": "Running 'pdfcpu validate' with a file that lacks .pdf extension prints warning to stderr",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-c",
            "disable",
            "--",
            "testdata/notapdf.txt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "needs extension \".pdf\"",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "testdata/notapdf.txt",
                "content": "not a pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "testdata/notapdf.txt"
            ]
        }
    },
    {
        "name": "test_validate_with_links_flag",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -links' enables link checking during validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-l",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validation ok",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_with_optimize_flag",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -opt' forces optimization during validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-opt",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "optimizing",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf. With -opt, should see 'optimizing...' in output."
    },
    {
        "name": "test_validate_mode_prints_in_output",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate -mode strict' shows the mode in progress output",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "strict",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validating(mode=strict)",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    },
    {
        "name": "test_validate_relaxed_mode_in_output",
        "category": "HAPPY_PATH",
        "description": "Running 'pdfcpu validate' in default mode shows relaxed in progress output",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-c",
            "disable",
            "--",
            "testdata/valid.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validating(mode=relaxed)",
        "timeout_seconds": 30,
        "notes": "Requires a valid PDF fixture at testdata/valid.pdf"
    }
]''')

# CLI binary/entry point
CLI_COMMAND = "pdfcpu"

# Working directory for CLI execution
WORKING_DIR = "."

# Default command timeout in seconds
DEFAULT_TIMEOUT = 30

# Response validation mode: when True, validates output against expected
VALIDATE_OUTPUT = any(
    tc.get("actual_stdout") is not None or tc.get("actual_stderr") is not None
    for tc in TEST_CASES
)

# =============================================================================
# Output Validation Utilities
# =============================================================================



def normalize_output(output: str) -> str:
    """Normalize output for comparison (strip whitespace, normalize newlines)."""
    if output is None:
        return ""
    return output.strip().replace("\r\n", "\n")


def matches_pattern(actual: str, pattern: str | None) -> bool:
    """
    Check if actual output matches the expected pattern.

    Pattern matching rules:
    - If pattern is None, always matches (no validation)
    - If pattern starts with 'regex:', use regex matching
    - Otherwise, check if pattern is contained in actual output (case-insensitive)
    """
    if pattern is None:
        return True

    actual_normalized = normalize_output(actual)

    if pattern.startswith("regex:"):
        regex_pattern = pattern[6:]  # Remove 'regex:' prefix
        return bool(re.search(regex_pattern, actual_normalized, re.IGNORECASE | re.MULTILINE))

    # Default: substring match (case-insensitive)
    return pattern.lower() in actual_normalized.lower()


def validate_cli_output(
    actual_stdout: str,
    actual_stderr: str,
    expected_stdout: str | None,
    expected_stderr: str | None,
) -> tuple[bool, list[str]]:
    """
    Validate CLI output against expected patterns.

    Args:
        actual_stdout: Actual stdout from command
        actual_stderr: Actual stderr from command
        expected_stdout: Expected stdout pattern (or None)
        expected_stderr: Expected stderr pattern (or None)

    Returns:
        tuple: (is_valid, list of violations)
    """
    violations: list[str] = []

    if expected_stdout is not None and not matches_pattern(actual_stdout, expected_stdout):
        violations.append(
            f"stdout mismatch: expected pattern '{expected_stdout}' not found in output"
        )

    if expected_stderr is not None and not matches_pattern(actual_stderr, expected_stderr):
        violations.append(
            f"stderr mismatch: expected pattern '{expected_stderr}' not found in output"
        )

    return len(violations) == 0, violations


def format_output_diff(violations: list[str]) -> str:
    """Format output differences for error message."""
    if not violations:
        return "No differences"

    output = []
    for i, diff in enumerate(violations):
        output.append(f"  - {diff}")

    return "\n".join(output)


# =============================================================================
# Test Results Collection
# =============================================================================

test_results: list[dict[str, Any]] = []


def record_result(
    name: str,
    command: str,
    args: list[str],
    expected_exit_code: int,
    actual_exit_code: int,
    passed: bool,
    duration_ms: float,
    category: str | None = None,
    description: str | None = None,
    error: str | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    output_match: bool | None = None,
    output_diff: list[str] | None = None,
) -> None:
    """Record a test result for final output."""
    result: dict[str, Any] = {
        "name": name,
        "command": command,
        "args": args,
        "expected_exit_code": expected_exit_code,
        "actual_exit_code": actual_exit_code,
        "passed": passed,
        "duration_ms": duration_ms,
        "category": category,
        "description": description,
    }
    if error:
        result["error"] = error

    # Track output validation results (for DST contract testing)
    if output_match is not None:
        result["output_match"] = output_match
    if output_diff:
        result["output_diff"] = output_diff

    # Capture outputs for validation
    if stdout:
        if passed:
            result["actual_stdout"] = stdout  # Capture more for passed tests
        else:
            result["stdout"] = stdout

    if stderr:
        if passed:
            result["actual_stderr"] = stderr
        else:
            result["stderr"] = stderr

    test_results.append(result)


# =============================================================================
# Setup and Cleanup Helpers
# =============================================================================


def run_setup(setup_config: dict[str, Any], work_dir: Path) -> bool:
    """Run setup actions before a test."""
    if not setup_config:
        return True

    try:
        # Create file
        if "create_file" in setup_config:
            file_config = setup_config["create_file"]
            file_path = work_dir / file_config["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_config.get("content", ""))
            print(f"Setup: Created file {file_path}")

        # Create directory
        if "create_dir" in setup_config:
            dir_path = work_dir / setup_config["create_dir"]
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Setup: Created directory {dir_path}")

        # Run command
        if "run_command" in setup_config:
            cmd = setup_config["run_command"]
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode != 0:
                print(f"Setup command failed: {result.stderr}")
                return False

        return True

    except Exception as e:
        print(f"Setup error: {e}")
        return False


def run_cleanup(cleanup_config: dict[str, Any], work_dir: Path) -> None:
    """Run cleanup actions after a test (best effort)."""
    if not cleanup_config:
        return

    try:
        # Delete files
        if "delete_files" in cleanup_config:
            for file_path in cleanup_config["delete_files"]:
                full_path = work_dir / file_path
                if full_path.exists():
                    full_path.unlink()
                    print(f"Cleanup: Deleted file {full_path}")

        # Delete directories
        if "delete_dirs" in cleanup_config:
            for dir_path in cleanup_config["delete_dirs"]:
                full_path = work_dir / dir_path
                if full_path.exists():
                    shutil.rmtree(full_path)
                    print(f"Cleanup: Deleted directory {full_path}")

        # Run command
        if "run_command" in cleanup_config:
            cmd = cleanup_config["run_command"]
            subprocess.run(
                cmd,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )

    except Exception as e:
        print(f"Cleanup warning: {e}")


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def cli_work_dir() -> Path:
    """Get the CLI working directory."""
    return Path(WORKING_DIR)


@pytest.fixture(scope="session", autouse=True)
def verify_cli_exists() -> None:
    """Verify the CLI command exists before running tests."""
    print(f"\nVerifying CLI command exists: {CLI_COMMAND}...")

    # Check if it's a direct path
    if os.path.isfile(CLI_COMMAND):
        print(f"CLI found at: {CLI_COMMAND}")
        return

    # Check if it's in PATH
    result = shutil.which(CLI_COMMAND)
    if result:
        print(f"CLI found in PATH: {result}")
        return

    # Try common locations
    work_dir = Path(WORKING_DIR)
    common_paths = [
        work_dir / CLI_COMMAND,
        work_dir / "dist" / CLI_COMMAND,
        work_dir / "target" / "release" / CLI_COMMAND,
        work_dir / "bin" / CLI_COMMAND,
    ]

    for path in common_paths:
        if path.exists():
            print(f"CLI found at: {path}")
            return

    pytest.fail(f"CLI command '{CLI_COMMAND}' not found. Please ensure the app is built.")


# =============================================================================
# Test Cases
# =============================================================================


def get_test_ids() -> list[str]:
    """Generate test IDs for parametrization."""
    return [tc.get("name", f"test_{i}") for i, tc in enumerate(TEST_CASES)]


@pytest.mark.parametrize("test_case", TEST_CASES, ids=get_test_ids())
def test_cli_command(test_case: dict[str, Any], cli_work_dir: Path) -> None:
    """Test a single CLI command based on test case configuration."""
    # Extract test case info
    name = test_case.get("name", "unnamed")
    command = test_case.get("command", CLI_COMMAND)
    args = test_case.get("args", [])
    stdin_input = test_case.get("stdin")
    env_vars = test_case.get("env", {})
    expected_exit_code = test_case.get("expected_exit_code", 0)
    expected_stdout = test_case.get("expected_stdout")
    expected_stderr = test_case.get("expected_stderr")
    category = test_case.get("category")
    description = test_case.get("description")
    setup_config = test_case.get("setup")
    cleanup_config = test_case.get("cleanup")
    timeout = test_case.get("timeout_seconds", DEFAULT_TIMEOUT)

    # Expected outputs for DST contract validation (from SRC validation)
    actual_stdout_expected = test_case.get("actual_stdout")
    actual_stderr_expected = test_case.get("actual_stderr")

    try:
        # Run setup if configured
        if setup_config:
            if not run_setup(setup_config, cli_work_dir):
                record_result(
                    name=name,
                    command=command,
                    args=args,
                    expected_exit_code=expected_exit_code,
                    actual_exit_code=-1,
                    passed=False,
                    duration_ms=0,
                    category=category,
                    description=description,
                    error="Setup failed",
                )
                pytest.fail(f"Setup failed for test '{name}'")

        # Build full command
        full_cmd = [command] + args

        # Prepare environment
        env = os.environ.copy()
        env.update(env_vars)

        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                full_cmd,
                input=stdin_input,
                cwd=str(cli_work_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            actual_exit_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr

            # Check exit code first
            exit_code_passed = actual_exit_code == expected_exit_code
            error_msg = None if exit_code_passed else (
                f"Expected exit code {expected_exit_code}, got {actual_exit_code}"
            )

            # Check output patterns
            output_match: bool | None = None
            output_diff: list[str] | None = None

            # For DST validation, compare against captured SRC output
            if actual_stdout_expected is not None or actual_stderr_expected is not None:
                output_match, output_diff = validate_cli_output(
                    stdout,
                    stderr,
                    actual_stdout_expected,
                    actual_stderr_expected,
                )
                if not output_match:
                    error_msg = f"Output contract violation:\n{format_output_diff(output_diff)}"
            # For SRC validation or basic validation, check expected patterns
            elif expected_stdout is not None or expected_stderr is not None:
                output_match, output_diff = validate_cli_output(
                    stdout,
                    stderr,
                    expected_stdout,
                    expected_stderr,
                )
                if not output_match:
                    error_msg = f"Output pattern mismatch:\n{format_output_diff(output_diff)}"

            # Overall pass
            passed = exit_code_passed and (output_match is None or output_match)

            record_result(
                name=name,
                command=command,
                args=args,
                expected_exit_code=expected_exit_code,
                actual_exit_code=actual_exit_code,
                passed=passed,
                duration_ms=duration_ms,
                category=category,
                description=description,
                error=error_msg,
                stdout=stdout,
                stderr=stderr,
                output_match=output_match,
                output_diff=output_diff,
            )

            # pytest assertions
            if not exit_code_passed:
                pytest.fail(
                    f"Test '{name}': Expected exit code {expected_exit_code}, got {actual_exit_code}.\n"
                    f"stdout: {stdout if stdout else 'empty'}\n"
                    f"stderr: {stderr if stderr else 'empty'}"
                )

            if output_match is False:
                pytest.fail(
                    f"Test '{name}': Output validation failed.\n"
                    f"Violations:\n{format_output_diff(output_diff or [])}"
                )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000
            record_result(
                name=name,
                command=command,
                args=args,
                expected_exit_code=expected_exit_code,
                actual_exit_code=-1,
                passed=False,
                duration_ms=duration_ms,
                category=category,
                description=description,
                error=f"Command timed out after {timeout}s",
                stdout=e.stdout if hasattr(e, 'stdout') else None,
                stderr=e.stderr if hasattr(e, 'stderr') else None,
            )
            pytest.fail(f"Test '{name}': Command timed out after {timeout}s")

    except Exception as e:
        record_result(
            name=name,
            command=command,
            args=args,
            expected_exit_code=expected_exit_code,
            actual_exit_code=-1,
            passed=False,
            duration_ms=0,
            category=category,
            description=description,
            error=f"Test error: {type(e).__name__}: {e}",
        )
        raise

    finally:
        # Always run cleanup
        if cleanup_config:
            run_cleanup(cleanup_config, cli_work_dir)


# =============================================================================
# Test Results Output
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def output_test_results(request: pytest.FixtureRequest) -> Any:
    """Output test results in JSON format after all tests complete."""
    yield  # Wait for all tests to complete

    # Calculate final results
    passed_count = sum(1 for r in test_results if r["passed"])
    failed_count = len([r for r in test_results if not r["passed"]])
    total_count = len(test_results)
    all_passed = failed_count == 0 and total_count > 0

    failures = [r for r in test_results if not r["passed"]]

    # Count output validation results (for DST contract testing)
    output_validated_count = sum(1 for r in test_results if r.get("output_match") is not None)
    output_match_count = sum(1 for r in test_results if r.get("output_match") is True)

    output = {
        "all_passed": all_passed,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "total_count": total_count,
        "results": test_results,
        "failures": failures,
    }

    # Add contract validation summary if any tests had expected outputs
    if output_validated_count > 0:
        output["contract_validation"] = {
            "tests_with_expected_output": output_validated_count,
            "output_matches": output_match_count,
            "output_mismatches": output_validated_count - output_match_count,
        }

    print("\n" + "=" * 60)
    print(f"Results: {passed_count}/{total_count} passed")
    if output_validated_count > 0:
        print(f"Contract validation: {output_match_count}/{output_validated_count} outputs matched")
    print("=" * 60)
    print(json.dumps(output))
    sys.stdout.flush()

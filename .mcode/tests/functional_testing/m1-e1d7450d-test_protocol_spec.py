#!/usr/bin/env python3
"""
BE Testing - CLI Contract Validation Tests

Generated pytest script to validate the CLI spec against the running application.
Each command is tested as a parameterized test case using pytest.

This script supports two modes:
1. SRC Validation: Tests commands and captures outputs (no expected_stdout/stderr)
2. DST Contract Validation: Tests commands and validates outputs match expected

Generated at: 2026-02-24T18:43:00.485103+00:00
Project: pdf
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
        "name": "test_no_args_shows_usage",
        "category": "HELP_OUTPUT",
        "description": "Running pdfcpu with no arguments should print usage information and exit 0",
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
        "description": "pdfcpu help with no topic should print full usage text",
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
        "name": "test_help_validate",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help validate should show validate usage and description",
        "command": "pdfcpu",
        "args": [
            "help",
            "validate"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_version",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help version should show version usage",
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
        "name": "test_help_optimize",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help optimize should show optimize usage and description",
        "command": "pdfcpu",
        "args": [
            "help",
            "optimize"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu optimize",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_merge",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help merge should show merge usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "merge"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu merge",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_split",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help split should show split usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "split"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu split",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_encrypt",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help encrypt should show encrypt usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "encrypt"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu encrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_decrypt",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help decrypt should show decrypt usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "decrypt"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu decrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_help_too_many_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu help with more than one topic should report too many arguments",
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
        "description": "pdfcpu help with unknown topic should report unknown help topic",
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
        "name": "test_help_prefix_completion_val",
        "category": "HELP_OUTPUT",
        "description": "pdfcpu help val should resolve to validate via prefix completion",
        "command": "pdfcpu",
        "args": [
            "help",
            "val"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_version_output",
        "category": "VERSION_OUTPUT",
        "description": "pdfcpu version should print version string",
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
        "description": "pdfcpu version should print commit info",
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
        "name": "test_version_shows_config_path",
        "category": "VERSION_OUTPUT",
        "description": "pdfcpu version should print config path",
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
        "name": "test_version_extra_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu version with extra arguments should fail",
        "command": "pdfcpu",
        "args": [
            "version",
            "extra"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu version",
        "timeout_seconds": 10
    },
    {
        "name": "test_version_prefix_completion",
        "category": "VERSION_OUTPUT",
        "description": "pdfcpu ver should resolve to version via prefix completion",
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
        "name": "test_paper_output",
        "category": "HAPPY_PATH",
        "description": "pdfcpu paper should print list of supported paper sizes",
        "command": "pdfcpu",
        "args": [
            "paper"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "ISO 216",
        "timeout_seconds": 10
    },
    {
        "name": "test_paper_lists_a4",
        "category": "HAPPY_PATH",
        "description": "pdfcpu paper should include A4 in the paper sizes list",
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
        "name": "test_paper_lists_letter",
        "category": "HAPPY_PATH",
        "description": "pdfcpu paper should include Letter in the paper sizes list",
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
        "name": "test_selectedpages_output",
        "category": "HAPPY_PATH",
        "description": "pdfcpu selectedpages should print the -pages flag definition",
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
        "name": "test_selectedpages_shows_even_odd",
        "category": "HAPPY_PATH",
        "description": "pdfcpu selectedpages should document even/odd page selection",
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
        "name": "test_unknown_command",
        "category": "INVALID_ARGS",
        "description": "Unknown command should fail with unknown command error",
        "command": "pdfcpu",
        "args": [
            "nonexistentcommand"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "unknown command",
        "timeout_seconds": 10
    },
    {
        "name": "test_ambiguous_command_prefix",
        "category": "INVALID_ARGS",
        "description": "Ambiguous command prefix should fail with ambiguous command error (e.g., 'c' matches collect, config, create, crop, cut, certificates, changeopw, changeupw)",
        "command": "pdfcpu",
        "args": [
            "c"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "ambiguous command",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu validate with no input file should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "validate"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "pdfcpu validate with non-existent file should fail",
        "command": "pdfcpu",
        "args": [
            "validate",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_valid_pdf_relaxed",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate should successfully validate a well-formed PDF in relaxed mode (default)",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_valid_pdf_strict",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -m strict should validate in strict mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "strict",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_mode_relaxed_explicit",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -m relaxed should validate in relaxed mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "relaxed",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_mode_short_s",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -m s should validate in strict mode (short alias)",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "s",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_mode_short_r",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -m r should validate in relaxed mode (short alias)",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "r",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "pdfcpu validate with invalid mode should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "badmode",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_with_pages_flag",
        "category": "INVALID_ARGS",
        "description": "pdfcpu validate does not accept -pages flag, should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-p",
            "1-3",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_non_pdf_extension",
        "category": "FILE_INPUT",
        "description": "pdfcpu validate with a non-PDF file extension should report extension error",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testfile.txt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "extension",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "testfile.txt",
                "content": "not a pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "testfile.txt"
            ]
        }
    },
    {
        "name": "test_validate_corrupt_pdf",
        "category": "FILE_INPUT",
        "description": "pdfcpu validate with a corrupt/invalid PDF should fail with error",
        "command": "pdfcpu",
        "args": [
            "validate",
            "corrupt.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "corrupt.pdf",
                "content": "This is not a valid PDF file content"
            }
        },
        "cleanup": {
            "delete_files": [
                "corrupt.pdf"
            ]
        }
    },
    {
        "name": "test_validate_empty_file",
        "category": "BOUNDARY",
        "description": "pdfcpu validate with an empty PDF file should fail",
        "command": "pdfcpu",
        "args": [
            "validate",
            "empty.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "empty.pdf",
                "content": ""
            }
        },
        "cleanup": {
            "delete_files": [
                "empty.pdf"
            ]
        }
    },
    {
        "name": "test_validate_multiple_files",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate should accept multiple input files",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/go.pdf",
            "testdata/mountain.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_verbose",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -v flag should produce verbose output",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-v",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_quiet",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -q flag should suppress output",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-q",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_links",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -l flag should check for broken links",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-l",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_prefix_completion",
        "category": "HAPPY_PATH",
        "description": "pdfcpu val should resolve to validate via prefix completion",
        "command": "pdfcpu",
        "args": [
            "val",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_config_disable",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -conf disable should work without config directory",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-conf",
            "disable",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_config_nonexistent",
        "category": "INVALID_OPTIONS",
        "description": "pdfcpu validate with -conf pointing to nonexistent path should fail",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-conf",
            "/nonexistent/path",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "does not exist",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_with_config_not_dir",
        "category": "INVALID_OPTIONS",
        "description": "pdfcpu validate with -conf pointing to a file (not dir) should fail",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-conf",
            "testfile_for_conf.txt",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "not a directory",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "testfile_for_conf.txt",
                "content": "dummy"
            }
        },
        "cleanup": {
            "delete_files": [
                "testfile_for_conf.txt"
            ]
        }
    },
    {
        "name": "test_validate_with_upw_opw",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate should accept -upw and -opw flags without error on unencrypted PDF",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-upw",
            "user123",
            "-opw",
            "owner456",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_optimize_flag",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -opt=true should enforce optimization during validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-opt=true",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_config_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu config with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "config"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu config",
        "timeout_seconds": 10
    },
    {
        "name": "test_config_list",
        "category": "HAPPY_PATH",
        "description": "pdfcpu config list should print configuration path and contents",
        "command": "pdfcpu",
        "args": [
            "config",
            "list"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "config:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_optimize_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu optimize with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "optimize"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu optimize",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_merge_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu merge with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "merge"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu merge",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_split_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu split with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "split"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu split",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_encrypt_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu encrypt with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "encrypt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu encrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_decrypt_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu decrypt with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "decrypt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu decrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_extract_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu extract with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "extract"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu extract",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_trim_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu trim with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "trim"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu trim",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_info_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu info with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "info"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu info",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_annotations_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu annotations with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "annotations"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu annotations",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_attachments_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu attachments with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "attachments"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu attachments",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_bookmarks_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu bookmarks with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "bookmarks"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu bookmarks",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_boxes_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu boxes with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "boxes"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu boxes",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_fonts_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu fonts with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "fonts"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu fonts",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_form_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu form with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "form"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu form",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_images_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu images with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "images"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu images",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_keywords_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu keywords with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "keywords"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu keywords",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_properties_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu properties with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "properties"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu properties",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_permissions_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu permissions with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "permissions"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu permissions",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_pages_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu pages with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "pages"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu pages",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_stamp_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu stamp with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "stamp"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu stamp",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_watermark_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu watermark with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "watermark"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu watermark",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_pagelayout_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu pagelayout with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "pagelayout"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu pagelayout",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_pagemode_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu pagemode with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "pagemode"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu pagemode",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_viewerpref_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu viewerpref with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "viewerpref"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu viewerpref",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_signatures_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu signatures with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "signatures"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu signatures",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_certificates_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu certificates with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "certificates"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu certificates",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_dct_filter_pdf",
        "category": "FILE_INPUT",
        "description": "Validate a PDF with DCT filter content",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/5116.DCT_Filter.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/5116.DCT_Filter.pdf",
                "to": "testdata/5116.DCT_Filter.pdf"
            }
        }
    },
    {
        "name": "test_validate_mountain_pdf",
        "category": "FILE_INPUT",
        "description": "Validate the mountain.pdf test file",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/mountain.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/mountain.pdf",
                "to": "testdata/mountain.pdf"
            }
        }
    },
    {
        "name": "test_validate_blank_scan_pdf",
        "category": "FILE_INPUT",
        "description": "Validate the blank-scan.pdf test file",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/blank-scan.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/blank-scan.pdf",
                "to": "testdata/blank-scan.pdf"
            }
        }
    },
    {
        "name": "test_validate_vector_apple_pdf",
        "category": "FILE_INPUT",
        "description": "Validate the VectorApple.pdf test file",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/VectorApple.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/VectorApple.pdf",
                "to": "testdata/VectorApple.pdf"
            }
        }
    },
    {
        "name": "test_validate_t6_pdf",
        "category": "FILE_INPUT",
        "description": "Validate the T6.pdf test file (CCITT fax encoded)",
        "command": "pdfcpu",
        "args": [
            "validate",
            "testdata/T6.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/T6.pdf",
                "to": "testdata/T6.pdf"
            }
        }
    },
    {
        "name": "test_usage_lists_all_commands",
        "category": "HELP_OUTPUT",
        "description": "Running pdfcpu with no args should list all known commands in usage text",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_usage_lists_optimize",
        "category": "HELP_OUTPUT",
        "description": "Usage output should include optimize command",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "optimize",
        "timeout_seconds": 10
    },
    {
        "name": "test_usage_lists_merge",
        "category": "HELP_OUTPUT",
        "description": "Usage output should include merge command",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "merge",
        "timeout_seconds": 10
    },
    {
        "name": "test_usage_lists_split",
        "category": "HELP_OUTPUT",
        "description": "Usage output should include split command",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "split",
        "timeout_seconds": 10
    },
    {
        "name": "test_usage_lists_encrypt",
        "category": "HELP_OUTPUT",
        "description": "Usage output should include encrypt command",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "encrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_usage_mentions_prefix_completion",
        "category": "HELP_OUTPUT",
        "description": "Usage text should mention that command prefixes are supported",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": "prefixes",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_with_separator",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -- separator before inFile should work",
        "command": "pdfcpu",
        "args": [
            "validate",
            "--",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_offline_flag",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -offline flag should disable HTTP traffic during validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-offline",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_with_very_verbose",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with -vv should produce very verbose logging",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-vv",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_validate_combined_mode_and_links",
        "category": "HAPPY_PATH",
        "description": "pdfcpu validate with both -m strict and -l flags should work together",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "strict",
            "-l",
            "testdata/go.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "copy_file": {
                "from": "testdata/go.pdf",
                "to": "testdata/go.pdf"
            }
        }
    },
    {
        "name": "test_stub_collect_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu collect with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "collect"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu collect",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_rotate_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu rotate with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "rotate"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu rotate",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_crop_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu crop with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "crop"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu crop",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_resize_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu resize with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "resize"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu resize",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_zoom_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu zoom with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "zoom"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu zoom",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_nup_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu nup with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "nup"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu nup",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_booklet_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu booklet with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "booklet"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu booklet",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_grid_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu grid with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "grid"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu grid",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_poster_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu poster with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "poster"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu poster",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_ndown_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu ndown with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "ndown"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu ndown",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_cut_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu cut with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "cut"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu cut",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_changeopw_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu changeopw with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "changeopw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu changeopw",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_changeupw_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu changeupw with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "changeupw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu changeupw",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_import_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu import with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "import"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu import",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_create_no_args",
        "category": "INVALID_ARGS",
        "description": "pdfcpu create with no arguments should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "create"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu create",
        "timeout_seconds": 10
    },
    {
        "name": "test_stub_portfolio_no_subcommand",
        "category": "INVALID_ARGS",
        "description": "pdfcpu portfolio with no subcommand should print usage and exit 1",
        "command": "pdfcpu",
        "args": [
            "portfolio"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu portfolio",
        "timeout_seconds": 10
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

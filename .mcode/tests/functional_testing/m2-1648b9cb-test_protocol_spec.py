#!/usr/bin/env python3
"""
BE Testing - CLI Contract Validation Tests

Generated pytest script to validate the CLI spec against the running application.
Each command is tested as a parameterized test case using pytest.

This script supports two modes:
1. SRC Validation: Tests commands and captures outputs (no expected_stdout/stderr)
2. DST Contract Validation: Tests commands and validates outputs match expected

Generated at: 2026-02-23T23:19:43.740300+00:00
Project: pdfcpumig
Milestone: 2
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
        "name": "test_help_no_args",
        "category": "HELP_OUTPUT",
        "description": "Running pdfcpu with no arguments should print usage information and exit 0",
        "command": "pdfcpu",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": "usage:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_help_command",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help' should print general usage and exit 0",
        "command": "pdfcpu",
        "args": [
            "help"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "usage:",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_help_validate",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help validate' should print validate command usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "validate"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu validate",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_help_optimize",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help optimize' should print optimize command usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "optimize"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu optimize",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_help_info",
        "category": "HELP_OUTPUT",
        "description": "Running 'pdfcpu help info' should print info command usage",
        "command": "pdfcpu",
        "args": [
            "help",
            "info"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu info",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_version_output",
        "category": "VERSION_OUTPUT",
        "description": "Running 'pdfcpu version' should print version string and exit 0",
        "command": "pdfcpu",
        "args": [
            "version"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "pdfcpu",
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_no_args",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu validate' with no input file should fail with usage message",
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
        "name": "test_validate_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Running validate on a file that does not exist should fail",
        "command": "pdfcpu",
        "args": [
            "validate",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file or directory",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "Using an invalid mode value should fail with usage message",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "invalid",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_pages_flag_rejected",
        "category": "INVALID_OPTIONS",
        "description": "Using -pages flag with validate should fail since it is not supported",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-p",
            "1-5",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_happy_path_relaxed_default",
        "category": "HAPPY_PATH",
        "description": "Validate a valid PDF file with default (relaxed) mode should succeed",
        "command": "pdfcpu",
        "args": [
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_happy_path_strict_mode",
        "category": "HAPPY_PATH",
        "description": "Validate a valid PDF file with strict mode should succeed",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "strict",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_happy_path_strict_mode_short",
        "category": "HAPPY_PATH",
        "description": "Validate with short strict mode alias 's' should succeed",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "s",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_happy_path_relaxed_mode_explicit",
        "category": "HAPPY_PATH",
        "description": "Validate with explicit relaxed mode should succeed",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "relaxed",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_happy_path_relaxed_mode_short",
        "category": "HAPPY_PATH",
        "description": "Validate with short relaxed mode alias 'r' should succeed",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "r",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_multiple_files",
        "category": "HAPPY_PATH",
        "description": "Validate multiple valid PDF files in a single command",
        "command": "pdfcpu",
        "args": [
            "validate",
            "file1.pdf",
            "file2.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_files": [
                {
                    "path": "file1.pdf",
                    "content_type": "valid_pdf"
                },
                {
                    "path": "file2.pdf",
                    "content_type": "valid_pdf"
                }
            ]
        },
        "cleanup": {
            "delete_files": [
                "file1.pdf",
                "file2.pdf"
            ]
        }
    },
    {
        "name": "test_validate_with_optimize_flag",
        "category": "HAPPY_PATH",
        "description": "Validate with -opt=true should run optimization after validation",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-opt",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_with_links_flag",
        "category": "HAPPY_PATH",
        "description": "Validate with -l flag to check for broken links",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-l",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_invalid_pdf",
        "category": "FILE_INPUT",
        "description": "Validate an invalid/corrupt PDF file should fail with validation error",
        "command": "pdfcpu",
        "args": [
            "validate",
            "corrupt.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "corrupt.pdf",
                "content": "This is not a valid PDF file"
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
        "description": "Validate an empty file should fail",
        "command": "pdfcpu",
        "args": [
            "validate",
            "empty.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 10,
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
        "name": "test_validate_verbose_mode",
        "category": "HAPPY_PATH",
        "description": "Validate with verbose flag should produce additional logging output",
        "command": "pdfcpu",
        "args": [
            "-v",
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_quiet_mode",
        "category": "HAPPY_PATH",
        "description": "Validate with quiet flag should suppress output",
        "command": "pdfcpu",
        "args": [
            "-q",
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_with_conf_disable",
        "category": "HAPPY_PATH",
        "description": "Validate with config disabled should still work",
        "command": "pdfcpu",
        "args": [
            "-conf",
            "disable",
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_strict_fails_on_relaxed_pdf",
        "category": "FILE_INPUT",
        "description": "Validate in strict mode on a PDF with common spec violations should fail with suggestion to try relaxed mode",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "strict",
            "relaxed_only.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "try -mode=relaxed",
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "relaxed_only.pdf",
                "content_type": "pdf_with_minor_violations"
            }
        },
        "cleanup": {
            "delete_files": [
                "relaxed_only.pdf"
            ]
        }
    },
    {
        "name": "test_validate_with_double_dash_separator",
        "category": "HAPPY_PATH",
        "description": "Validate using -- separator between flags and arguments",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-m",
            "relaxed",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_validate_prefix_completion",
        "category": "HAPPY_PATH",
        "description": "Command prefix completion: 'val' should match 'validate'",
        "command": "pdfcpu",
        "args": [
            "val",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_no_args",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu optimize' with no arguments should fail with usage",
        "command": "pdfcpu",
        "args": [
            "optimize"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu optimize",
        "timeout_seconds": 10
    },
    {
        "name": "test_optimize_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Running optimize with more than 2 positional arguments should fail",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "in.pdf",
            "out.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu optimize",
        "timeout_seconds": 10
    },
    {
        "name": "test_optimize_pages_flag_rejected",
        "category": "INVALID_OPTIONS",
        "description": "Using -pages flag with optimize should fail since it is not supported",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "-p",
            "1-5",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu optimize",
        "timeout_seconds": 10
    },
    {
        "name": "test_optimize_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Running optimize on a nonexistent file should fail",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file or directory",
        "timeout_seconds": 10
    },
    {
        "name": "test_optimize_happy_path_inplace",
        "category": "HAPPY_PATH",
        "description": "Optimize a valid PDF in-place (no outFile specified)",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_happy_path_with_outfile",
        "category": "HAPPY_PATH",
        "description": "Optimize a valid PDF to a separate output file",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "input.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing output.pdf",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_happy_path_same_inout",
        "category": "HAPPY_PATH",
        "description": "Optimize with inFile and outFile being the same should work (in-place behavior)",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "input.pdf",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing input.pdf",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_with_stats_flag",
        "category": "HAPPY_PATH",
        "description": "Optimize with -stats flag should append stats to CSV file",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "-stats",
            "stats.csv",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "stats will be appended to stats.csv",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf",
                "stats.csv"
            ]
        }
    },
    {
        "name": "test_optimize_invalid_pdf",
        "category": "FILE_INPUT",
        "description": "Optimize a corrupt PDF should fail (validation runs before optimization)",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "corrupt.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "corrupt.pdf",
                "content": "This is not a valid PDF file"
            }
        },
        "cleanup": {
            "delete_files": [
                "corrupt.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_empty_file",
        "category": "BOUNDARY",
        "description": "Optimize an empty file should fail",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "empty.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 10,
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
        "name": "test_optimize_with_double_dash",
        "category": "HAPPY_PATH",
        "description": "Optimize using -- separator between flags and arguments",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "--",
            "input.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing output.pdf",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_prefix_completion",
        "category": "HAPPY_PATH",
        "description": "Command prefix completion: 'opt' should match 'optimize'",
        "command": "pdfcpu",
        "args": [
            "opt",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_produces_valid_pdf",
        "category": "HAPPY_PATH",
        "description": "Optimized output should be a valid PDF (validate the output)",
        "command": "pdfcpu",
        "args": [
            "optimize",
            "input.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing output.pdf",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf",
                "output.pdf"
            ]
        },
        "post_validation": {
            "command": "pdfcpu",
            "args": [
                "validate",
                "output.pdf"
            ],
            "expected_exit_code": 0
        }
    },
    {
        "name": "test_info_no_args",
        "category": "INVALID_ARGS",
        "description": "Running 'pdfcpu info' with no input file should fail with usage",
        "command": "pdfcpu",
        "args": [
            "info"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu info",
        "timeout_seconds": 10
    },
    {
        "name": "test_info_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Running info on a nonexistent file should fail",
        "command": "pdfcpu",
        "args": [
            "info",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file or directory",
        "timeout_seconds": 10
    },
    {
        "name": "test_info_happy_path_basic",
        "category": "HAPPY_PATH",
        "description": "Get info for a valid PDF file should print structured information",
        "command": "pdfcpu",
        "args": [
            "info",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "PDF version",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_shows_page_count",
        "category": "HAPPY_PATH",
        "description": "Info output should include page count",
        "command": "pdfcpu",
        "args": [
            "info",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Page count",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_shows_source",
        "category": "HAPPY_PATH",
        "description": "Info output should include source filename",
        "command": "pdfcpu",
        "args": [
            "info",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Source",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_shows_flags",
        "category": "HAPPY_PATH",
        "description": "Info output should include document flags (Tagged, Encrypted, etc.)",
        "command": "pdfcpu",
        "args": [
            "info",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Tagged",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_pages_flag",
        "category": "HAPPY_PATH",
        "description": "Info with -pages flag should show per-page boundary details",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "1",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Page 1",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_pages_range",
        "category": "HAPPY_PATH",
        "description": "Info with a page range should show details for those pages",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "1-3",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Page 1",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_multipage"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_fonts_flag",
        "category": "HAPPY_PATH",
        "description": "Info with -fonts flag should include font information table",
        "command": "pdfcpu",
        "args": [
            "info",
            "-fonts",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Fonts",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_with_fonts"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_json_flag",
        "category": "HAPPY_PATH",
        "description": "Info with -json flag should produce JSON output",
        "command": "pdfcpu",
        "args": [
            "info",
            "-j",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "\"version\"",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_json_has_page_count",
        "category": "HAPPY_PATH",
        "description": "Info JSON output should include pageCount field",
        "command": "pdfcpu",
        "args": [
            "info",
            "-j",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "\"pageCount\"",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_unit_points",
        "category": "HAPPY_PATH",
        "description": "Info with -u po should display dimensions in points",
        "command": "pdfcpu",
        "args": [
            "info",
            "-u",
            "po",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "points",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_unit_inches",
        "category": "HAPPY_PATH",
        "description": "Info with -u in should display dimensions in inches",
        "command": "pdfcpu",
        "args": [
            "info",
            "-u",
            "in",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "inches",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_unit_cm",
        "category": "HAPPY_PATH",
        "description": "Info with -u cm should display dimensions in centimetres",
        "command": "pdfcpu",
        "args": [
            "info",
            "-u",
            "cm",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "cm",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_unit_mm",
        "category": "HAPPY_PATH",
        "description": "Info with -u mm should display dimensions in millimetres",
        "command": "pdfcpu",
        "args": [
            "info",
            "-u",
            "mm",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "mm",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_multiple_files",
        "category": "HAPPY_PATH",
        "description": "Info on multiple PDF files should print info for each",
        "command": "pdfcpu",
        "args": [
            "info",
            "file1.pdf",
            "file2.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "PDF version",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_files": [
                {
                    "path": "file1.pdf",
                    "content_type": "valid_pdf"
                },
                {
                    "path": "file2.pdf",
                    "content_type": "valid_pdf"
                }
            ]
        },
        "cleanup": {
            "delete_files": [
                "file1.pdf",
                "file2.pdf"
            ]
        }
    },
    {
        "name": "test_info_invalid_pages_selection",
        "category": "INVALID_OPTIONS",
        "description": "Info with an invalid page selection expression should fail",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "abc",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "problem with flag selectedPages",
        "timeout_seconds": 10
    },
    {
        "name": "test_info_invalid_pdf",
        "category": "FILE_INPUT",
        "description": "Info on a corrupt PDF should fail",
        "command": "pdfcpu",
        "args": [
            "info",
            "corrupt.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "corrupt.pdf",
                "content": "This is not a valid PDF file"
            }
        },
        "cleanup": {
            "delete_files": [
                "corrupt.pdf"
            ]
        }
    },
    {
        "name": "test_info_empty_file",
        "category": "BOUNDARY",
        "description": "Info on an empty file should fail",
        "command": "pdfcpu",
        "args": [
            "info",
            "empty.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 10,
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
        "name": "test_info_with_fonts_and_json",
        "category": "HAPPY_PATH",
        "description": "Info with both -fonts and -json flags combined",
        "command": "pdfcpu",
        "args": [
            "info",
            "-fonts",
            "-j",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "\"fonts\"",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_with_fonts"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_pages_and_fonts",
        "category": "HAPPY_PATH",
        "description": "Info with both -pages and -fonts flags combined",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "1",
            "-fonts",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Fonts",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_with_fonts"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_prefix_completion",
        "category": "HAPPY_PATH",
        "description": "Command prefix completion: 'inf' should match 'info'",
        "command": "pdfcpu",
        "args": [
            "inf",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "PDF version",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_page_selection_even",
        "category": "HAPPY_PATH",
        "description": "Info with -pages even should show even page details",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "even",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Page 2",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_multipage"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_page_selection_odd",
        "category": "HAPPY_PATH",
        "description": "Info with -pages odd should show odd page details",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "odd",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Page 1",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_multipage"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_info_page_selection_negation",
        "category": "HAPPY_PATH",
        "description": "Info with -pages '!1' should show all pages except page 1",
        "command": "pdfcpu",
        "args": [
            "info",
            "-p",
            "!1",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Page 2",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf_multipage"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_unknown_command",
        "category": "INVALID_ARGS",
        "description": "Running an unknown command should fail",
        "command": "pdfcpu",
        "args": [
            "unknowncommand"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "ambiguous",
        "timeout_seconds": 10
    },
    {
        "name": "test_unknown_global_flag",
        "category": "INVALID_OPTIONS",
        "description": "Using an unknown global flag should fail",
        "command": "pdfcpu",
        "args": [
            "--unknown-flag",
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "flag provided but not defined",
        "timeout_seconds": 10
    },
    {
        "name": "test_conf_invalid_path",
        "category": "INVALID_OPTIONS",
        "description": "Using -conf with a non-existent directory should fail",
        "command": "pdfcpu",
        "args": [
            "-conf",
            "/nonexistent/path",
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 10
    },
    {
        "name": "test_validate_with_upw_opw_flags",
        "category": "HAPPY_PATH",
        "description": "Validate an encrypted PDF providing user and owner passwords",
        "command": "pdfcpu",
        "args": [
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "validate",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content_type": "encrypted_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_with_upw_opw_flags",
        "category": "HAPPY_PATH",
        "description": "Optimize an encrypted PDF providing user and owner passwords",
        "command": "pdfcpu",
        "args": [
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "optimize",
            "encrypted.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "writing output.pdf",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content_type": "encrypted_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted.pdf",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_info_with_upw_opw_flags",
        "category": "HAPPY_PATH",
        "description": "Info on an encrypted PDF providing user and owner passwords",
        "command": "pdfcpu",
        "args": [
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "info",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "PDF version",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content_type": "encrypted_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted.pdf"
            ]
        }
    },
    {
        "name": "test_validate_stdin_not_supported",
        "category": "PIPE_INPUT",
        "description": "Validate command requires file paths, not stdin; verify behavior with '-' as input",
        "command": "pdfcpu",
        "args": [
            "validate",
            "-"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "error",
        "timeout_seconds": 10
    },
    {
        "name": "test_info_glob_pattern",
        "category": "FILE_INPUT",
        "description": "Info command supports glob patterns for file arguments",
        "command": "pdfcpu",
        "args": [
            "info",
            "testdir/*.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "PDF version",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_directory": "testdir",
            "create_files": [
                {
                    "path": "testdir/file1.pdf",
                    "content_type": "valid_pdf"
                },
                {
                    "path": "testdir/file2.pdf",
                    "content_type": "valid_pdf"
                }
            ]
        },
        "cleanup": {
            "delete_files": [
                "testdir/file1.pdf",
                "testdir/file2.pdf"
            ],
            "delete_directories": [
                "testdir"
            ]
        }
    },
    {
        "name": "test_validate_very_verbose",
        "category": "HAPPY_PATH",
        "description": "Validate with -vv flag should produce very verbose logging including trace and read logs",
        "command": "pdfcpu",
        "args": [
            "-vv",
            "validate",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "validation ok",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    },
    {
        "name": "test_optimize_quiet_mode",
        "category": "HAPPY_PATH",
        "description": "Optimize with quiet flag should suppress output",
        "command": "pdfcpu",
        "args": [
            "-q",
            "optimize",
            "input.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_info_quiet_mode",
        "category": "HAPPY_PATH",
        "description": "Info with quiet flag should suppress output",
        "command": "pdfcpu",
        "args": [
            "-q",
            "info",
            "input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content_type": "valid_pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "input.pdf"
            ]
        }
    }
]''')

# CLI binary/entry point
CLI_COMMAND = "pdfcpu-cli"

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

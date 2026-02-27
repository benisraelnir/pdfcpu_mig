#!/usr/bin/env python3
"""
BE Testing - CLI Contract Validation Tests

Generated pytest script to validate the CLI spec against the running application.
Each command is tested as a parameterized test case using pytest.

This script supports two modes:
1. SRC Validation: Tests commands and captures outputs (no expected_stdout/stderr)
2. DST Contract Validation: Tests commands and validates outputs match expected

Generated at: 2026-02-27T21:44:49.835375+00:00
Project: pdf
Milestone: 4
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
        "name": "test_stamp_help",
        "category": "HELP_OUTPUT",
        "description": "Verify stamp command shows usage information when invoked without subcommand",
        "command": "pdfcpu",
        "subcommand": "stamp",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu stamp",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_help",
        "category": "HELP_OUTPUT",
        "description": "Verify stamp add shows usage when called without args",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_text_happy_path",
        "category": "HAPPY_PATH",
        "description": "Add a text stamp to a PDF with default settings",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:24, pos:c, sc:1.0, op:0.5",
            "DRAFT",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_text_with_pages",
        "category": "HAPPY_PATH",
        "description": "Add a text stamp to specific pages of a PDF",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-p",
            "1",
            "-m",
            "text",
            "--",
            "font:Helvetica, points:12",
            "Confidential",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_image_happy_path",
        "category": "HAPPY_PATH",
        "description": "Add an image stamp to a PDF",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "image",
            "--",
            "pos:c, sc:.5",
            "logo.png",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_pdf_stamp",
        "category": "HAPPY_PATH",
        "description": "Add a PDF page as a stamp onto another PDF",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "pdf",
            "--",
            "pos:c, sc:.5",
            "stamp_source.pdf",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_overwrite_inplace",
        "category": "HAPPY_PATH",
        "description": "Add a text stamp to a PDF overwriting input file when no outFile given",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:24",
            "STAMP",
            "test_input.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_missing_mode",
        "category": "INVALID_OPTIONS",
        "description": "Stamp add without required -m mode flag should fail",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "--",
            "font:Helvetica",
            "DRAFT",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "Stamp add with invalid mode value should fail",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "invalid",
            "--",
            "font:Helvetica",
            "DRAFT",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "mode",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_missing_args",
        "category": "INVALID_ARGS",
        "description": "Stamp add with insufficient positional arguments should fail",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "text",
            "--",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Stamp add with too many positional arguments should fail",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica",
            "DRAFT",
            "in.pdf",
            "out.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Stamp add with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica",
            "DRAFT",
            "nonexistent.pdf",
            "out.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_update_text",
        "category": "HAPPY_PATH",
        "description": "Update an existing text stamp on a PDF",
        "command": "pdfcpu",
        "subcommand": "stamp update",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:36, op:0.8",
            "UPDATED",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_update_missing_mode",
        "category": "INVALID_OPTIONS",
        "description": "Stamp update without required -m mode flag should fail",
        "command": "pdfcpu",
        "subcommand": "stamp update",
        "args": [
            "--",
            "font:Helvetica",
            "DRAFT",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_remove_happy_path",
        "category": "HAPPY_PATH",
        "description": "Remove stamps from a PDF",
        "command": "pdfcpu",
        "subcommand": "stamp remove",
        "args": [
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_remove_with_pages",
        "category": "HAPPY_PATH",
        "description": "Remove stamps from specific pages only",
        "command": "pdfcpu",
        "subcommand": "stamp remove",
        "args": [
            "-p",
            "1",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_remove_missing_args",
        "category": "INVALID_ARGS",
        "description": "Stamp remove with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "stamp remove",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_remove_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Stamp remove with too many arguments should fail",
        "command": "pdfcpu",
        "subcommand": "stamp remove",
        "args": [
            "in.pdf",
            "out.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_help",
        "category": "HELP_OUTPUT",
        "description": "Verify watermark command shows usage information when invoked without subcommand",
        "command": "pdfcpu",
        "subcommand": "watermark",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu watermark",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_add_text_happy_path",
        "category": "HAPPY_PATH",
        "description": "Add a text watermark to a PDF with default settings",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:48, op:0.3, rot:45",
            "CONFIDENTIAL",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_add_image_happy_path",
        "category": "HAPPY_PATH",
        "description": "Add an image watermark to a PDF",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-m",
            "image",
            "--",
            "pos:c, sc:.3, op:0.2",
            "logo.png",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_add_pdf_happy_path",
        "category": "HAPPY_PATH",
        "description": "Add a PDF page as watermark to another PDF",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-m",
            "pdf",
            "--",
            "pos:c, sc:.5, op:0.2",
            "wm_source.pdf",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_add_with_page_selection",
        "category": "HAPPY_PATH",
        "description": "Add watermark to specific pages only",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-p",
            "1",
            "-m",
            "text",
            "--",
            "font:Courier, points:24, op:0.4",
            "WATERMARK",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_add_missing_mode",
        "category": "INVALID_OPTIONS",
        "description": "Watermark add without required -m mode flag should fail",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "--",
            "font:Helvetica",
            "DRAFT",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_add_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "Watermark add with invalid mode value should fail",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-m",
            "html",
            "--",
            "font:Helvetica",
            "DRAFT",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "mode",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_add_missing_args",
        "category": "INVALID_ARGS",
        "description": "Watermark add with too few arguments should fail",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-m",
            "text",
            "--",
            "test_input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_update_text",
        "category": "HAPPY_PATH",
        "description": "Update an existing watermark on a PDF",
        "command": "pdfcpu",
        "subcommand": "watermark update",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:36, op:0.5",
            "REVISED",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_remove_happy_path",
        "category": "HAPPY_PATH",
        "description": "Remove watermarks from a PDF",
        "command": "pdfcpu",
        "subcommand": "watermark remove",
        "args": [
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_remove_with_pages",
        "category": "HAPPY_PATH",
        "description": "Remove watermarks from specific pages",
        "command": "pdfcpu",
        "subcommand": "watermark remove",
        "args": [
            "-p",
            "1",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_remove_missing_args",
        "category": "INVALID_ARGS",
        "description": "Watermark remove with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "watermark remove",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_remove_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Watermark remove with too many arguments should fail",
        "command": "pdfcpu",
        "subcommand": "watermark remove",
        "args": [
            "in.pdf",
            "out.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_help",
        "category": "HELP_OUTPUT",
        "description": "Verify form command shows usage information when invoked without subcommand",
        "command": "pdfcpu",
        "subcommand": "form",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu form",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_list_happy_path",
        "category": "HAPPY_PATH",
        "description": "List form fields in a PDF that contains forms",
        "command": "pdfcpu",
        "subcommand": "form list",
        "args": [
            "test_form.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf"
            ]
        }
    },
    {
        "name": "test_form_list_multiple_files",
        "category": "HAPPY_PATH",
        "description": "List form fields across multiple PDF files",
        "command": "pdfcpu",
        "subcommand": "form list",
        "args": [
            "form1.pdf",
            "form2.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "form1.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "form1.pdf",
                "form2.pdf"
            ]
        }
    },
    {
        "name": "test_form_list_missing_args",
        "category": "INVALID_ARGS",
        "description": "Form list with no input file should fail",
        "command": "pdfcpu",
        "subcommand": "form list",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_list_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Form list with a non-existent file should fail",
        "command": "pdfcpu",
        "subcommand": "form list",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_list_with_pages_flag_rejected",
        "category": "INVALID_OPTIONS",
        "description": "Form list does not accept -p pages flag and should fail if provided",
        "command": "pdfcpu",
        "subcommand": "form list",
        "args": [
            "-p",
            "1",
            "test_form.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_fill_happy_path",
        "category": "HAPPY_PATH",
        "description": "Fill form fields in a PDF using JSON data",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "test_form.pdf",
            "form_data.json",
            "filled_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "form_data.json",
                "filled_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_fill_overwrite_inplace",
        "category": "HAPPY_PATH",
        "description": "Fill form fields in-place when no output file is specified",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "test_form.pdf",
            "form_data.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "form_data.json"
            ]
        }
    },
    {
        "name": "test_form_fill_missing_args",
        "category": "INVALID_ARGS",
        "description": "Form fill with only one argument should fail",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "test_form.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_fill_no_args",
        "category": "INVALID_ARGS",
        "description": "Form fill with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_fill_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Form fill with too many arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "in.pdf",
            "data.json",
            "out.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_fill_nonexistent_pdf",
        "category": "FILE_INPUT",
        "description": "Form fill with non-existent PDF file should fail",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "nonexistent.pdf",
            "data.json",
            "out.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_fill_nonexistent_json",
        "category": "FILE_INPUT",
        "description": "Form fill with non-existent JSON data file should fail",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "test_form.pdf",
            "nonexistent.json",
            "out.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_export_happy_path",
        "category": "HAPPY_PATH",
        "description": "Export form field data from a PDF to a JSON file",
        "command": "pdfcpu",
        "subcommand": "form export",
        "args": [
            "test_form.pdf",
            "exported.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "exported.json"
            ]
        }
    },
    {
        "name": "test_form_export_default_output",
        "category": "HAPPY_PATH",
        "description": "Export form field data with default output file (out.json)",
        "command": "pdfcpu",
        "subcommand": "form export",
        "args": [
            "test_form.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "out.json"
            ]
        }
    },
    {
        "name": "test_form_export_no_args",
        "category": "INVALID_ARGS",
        "description": "Form export with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form export",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_export_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Form export with too many arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form export",
        "args": [
            "in.pdf",
            "out.json",
            "extra"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_lock_happy_path",
        "category": "HAPPY_PATH",
        "description": "Lock all form fields in a PDF",
        "command": "pdfcpu",
        "subcommand": "form lock",
        "args": [
            "test_form.pdf",
            "locked_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "locked_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_lock_specific_fields",
        "category": "HAPPY_PATH",
        "description": "Lock specific form fields by name",
        "command": "pdfcpu",
        "subcommand": "form lock",
        "args": [
            "test_form.pdf",
            "locked_output.pdf",
            "firstName"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "locked_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_lock_inplace",
        "category": "HAPPY_PATH",
        "description": "Lock form fields in-place (no output file)",
        "command": "pdfcpu",
        "subcommand": "form lock",
        "args": [
            "test_form.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf"
            ]
        }
    },
    {
        "name": "test_form_lock_no_args",
        "category": "INVALID_ARGS",
        "description": "Form lock with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form lock",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_unlock_happy_path",
        "category": "HAPPY_PATH",
        "description": "Unlock all form fields in a PDF",
        "command": "pdfcpu",
        "subcommand": "form unlock",
        "args": [
            "test_form.pdf",
            "unlocked_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "unlocked_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_unlock_specific_fields",
        "category": "HAPPY_PATH",
        "description": "Unlock specific form fields by name",
        "command": "pdfcpu",
        "subcommand": "form unlock",
        "args": [
            "test_form.pdf",
            "unlocked_output.pdf",
            "firstName"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "unlocked_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_unlock_no_args",
        "category": "INVALID_ARGS",
        "description": "Form unlock with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form unlock",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_reset_happy_path",
        "category": "HAPPY_PATH",
        "description": "Reset all form fields in a PDF to default values",
        "command": "pdfcpu",
        "subcommand": "form reset",
        "args": [
            "test_form.pdf",
            "reset_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "reset_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_reset_specific_fields",
        "category": "HAPPY_PATH",
        "description": "Reset specific form fields by name",
        "command": "pdfcpu",
        "subcommand": "form reset",
        "args": [
            "test_form.pdf",
            "reset_output.pdf",
            "firstName"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "reset_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_reset_inplace",
        "category": "HAPPY_PATH",
        "description": "Reset form fields in-place (no output file)",
        "command": "pdfcpu",
        "subcommand": "form reset",
        "args": [
            "test_form.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf"
            ]
        }
    },
    {
        "name": "test_form_reset_no_args",
        "category": "INVALID_ARGS",
        "description": "Form reset with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form reset",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_remove_happy_path",
        "category": "HAPPY_PATH",
        "description": "Remove specific form fields from a PDF by field ID",
        "command": "pdfcpu",
        "subcommand": "form remove",
        "args": [
            "test_form.pdf",
            "remove_output.pdf",
            "firstName"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "remove_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_remove_multiple_fields",
        "category": "HAPPY_PATH",
        "description": "Remove multiple form fields from a PDF",
        "command": "pdfcpu",
        "subcommand": "form remove",
        "args": [
            "test_form.pdf",
            "remove_output.pdf",
            "firstName",
            "lastName"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "remove_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_remove_missing_field_ids",
        "category": "INVALID_ARGS",
        "description": "Form remove with only input file and no field IDs should fail",
        "command": "pdfcpu",
        "subcommand": "form remove",
        "args": [
            "test_form.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_remove_no_args",
        "category": "INVALID_ARGS",
        "description": "Form remove with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form remove",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_multifill_json_single_mode",
        "category": "HAPPY_PATH",
        "description": "Multi-fill form from JSON data in single mode (separate files per instance)",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "-m",
            "single",
            "--",
            "test_form.pdf",
            "multifill_data.json",
            "out_dir"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "multifill_data.json"
            ]
        }
    },
    {
        "name": "test_form_multifill_json_merge_mode",
        "category": "HAPPY_PATH",
        "description": "Multi-fill form from JSON data in merge mode (all instances in one file)",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "-m",
            "merge",
            "--",
            "test_form.pdf",
            "multifill_data.json",
            "out_dir"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "multifill_data.json"
            ]
        }
    },
    {
        "name": "test_form_multifill_csv",
        "category": "HAPPY_PATH",
        "description": "Multi-fill form from CSV data",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "--",
            "test_form.pdf",
            "multifill_data.csv",
            "out_dir"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "multifill_data.csv"
            ]
        }
    },
    {
        "name": "test_form_multifill_with_outname",
        "category": "HAPPY_PATH",
        "description": "Multi-fill form with custom output file name",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "-m",
            "single",
            "--",
            "test_form.pdf",
            "multifill_data.json",
            "out_dir",
            "custom_output"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "multifill_data.json"
            ]
        }
    },
    {
        "name": "test_form_multifill_default_mode",
        "category": "HAPPY_PATH",
        "description": "Multi-fill form without mode flag should default to single mode",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "--",
            "test_form.pdf",
            "multifill_data.json",
            "out_dir"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "multifill_data.json"
            ]
        }
    },
    {
        "name": "test_form_multifill_missing_args",
        "category": "INVALID_ARGS",
        "description": "Multi-fill with fewer than 3 positional arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "--",
            "test_form.pdf",
            "data.json"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_multifill_no_args",
        "category": "INVALID_ARGS",
        "description": "Multi-fill with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_multifill_invalid_data_extension",
        "category": "INVALID_ARGS",
        "description": "Multi-fill with data file that has neither .json nor .csv extension should fail",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "--",
            "test_form.pdf",
            "data.txt",
            "out_dir"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "needs extension",
        "timeout_seconds": 10
    },
    {
        "name": "test_form_multifill_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "Multi-fill with invalid mode should fail",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "-m",
            "invalid",
            "--",
            "test_form.pdf",
            "data.json",
            "out_dir"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_create_happy_path_new_pdf",
        "category": "HAPPY_PATH",
        "description": "Create a new PDF from a JSON declaration file",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "content.json",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "content.json",
                "content": "{\"pages\":{\"1\":{\"content\":{\"text\":[{\"value\":\"Hello pdfcpu!\",\"anchor\":\"center\",\"font\":{\"name\":\"Helvetica\",\"size\":12}}]}}}}"
            }
        },
        "cleanup": {
            "delete_files": [
                "content.json",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_create_append_to_existing",
        "category": "HAPPY_PATH",
        "description": "Append page content from JSON to an existing PDF file",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "content.json",
            "existing.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "content.json",
                "content": "{\"pages\":{\"1\":{\"content\":{\"text\":[{\"value\":\"Appended text\",\"anchor\":\"center\",\"font\":{\"name\":\"Helvetica\",\"size\":12}}]}}}}"
            }
        },
        "cleanup": {
            "delete_files": [
                "content.json",
                "existing.pdf",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_create_no_args",
        "category": "INVALID_ARGS",
        "description": "Create with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_create_one_arg",
        "category": "INVALID_ARGS",
        "description": "Create with only one argument (JSON file only) should fail",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "content.json"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_create_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Create with too many arguments should fail",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "content.json",
            "in.pdf",
            "out.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_create_nonexistent_json",
        "category": "FILE_INPUT",
        "description": "Create with a non-existent JSON file should fail",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "nonexistent.json",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_create_invalid_json_content",
        "category": "BOUNDARY",
        "description": "Create with invalid JSON content should fail gracefully",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "invalid.json",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "invalid.json",
                "content": "{ this is not valid json }"
            }
        },
        "cleanup": {
            "delete_files": [
                "invalid.json"
            ]
        }
    },
    {
        "name": "test_create_empty_json",
        "category": "BOUNDARY",
        "description": "Create with an empty JSON object should fail or handle gracefully",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "empty.json",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "empty.json",
                "content": "{}"
            }
        },
        "cleanup": {
            "delete_files": [
                "empty.json"
            ]
        }
    },
    {
        "name": "test_create_with_pages_flag_rejected",
        "category": "INVALID_OPTIONS",
        "description": "Create command does not accept -p pages flag",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "-p",
            "1",
            "content.json",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage:",
        "timeout_seconds": 10
    },
    {
        "name": "test_fonts_help",
        "category": "HELP_OUTPUT",
        "description": "Verify fonts command shows usage information when invoked without subcommand",
        "command": "pdfcpu",
        "subcommand": "fonts",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu fonts",
        "timeout_seconds": 10
    },
    {
        "name": "test_fonts_list_happy_path",
        "category": "HAPPY_PATH",
        "description": "List all available fonts including the 14 PDF core fonts",
        "command": "pdfcpu",
        "subcommand": "fonts list",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": "Helvetica",
        "expected_stderr": null,
        "timeout_seconds": 30
    },
    {
        "name": "test_fonts_list_includes_core_fonts",
        "category": "HAPPY_PATH",
        "description": "Verify that core PDF fonts appear in the font list",
        "command": "pdfcpu",
        "subcommand": "fonts list",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": "Courier",
        "expected_stderr": null,
        "timeout_seconds": 30
    },
    {
        "name": "test_fonts_install_happy_path",
        "category": "HAPPY_PATH",
        "description": "Install a TrueType font file",
        "command": "pdfcpu",
        "subcommand": "fonts install",
        "args": [
            "test_font.ttf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_font.ttf",
                "content": "COPY_FROM_TESTDATA"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_font.ttf"
            ]
        }
    },
    {
        "name": "test_fonts_install_no_args",
        "category": "INVALID_ARGS",
        "description": "Font install with no arguments should fail",
        "command": "pdfcpu",
        "subcommand": "fonts install",
        "args": [],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "expecting a list of TrueType filenames",
        "timeout_seconds": 10
    },
    {
        "name": "test_fonts_install_invalid_extension",
        "category": "INVALID_ARGS",
        "description": "Font install with non-ttf/ttc file should fail",
        "command": "pdfcpu",
        "subcommand": "fonts install",
        "args": [
            "notafont.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": ".ttf",
        "timeout_seconds": 10
    },
    {
        "name": "test_fonts_install_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Font install with non-existent font file should fail",
        "command": "pdfcpu",
        "subcommand": "fonts install",
        "args": [
            "nonexistent.ttf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_fonts_cheatsheet_happy_path",
        "category": "HAPPY_PATH",
        "description": "Create font cheat sheet PDFs for installed user fonts",
        "command": "pdfcpu",
        "subcommand": "fonts cheatsheet",
        "args": [],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60
    },
    {
        "name": "test_fonts_cheatsheet_specific_font",
        "category": "HAPPY_PATH",
        "description": "Create font cheat sheet for a specific font",
        "command": "pdfcpu",
        "subcommand": "fonts cheatsheet",
        "args": [
            "test_font.ttf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60
    },
    {
        "name": "test_stamp_add_unknown_option",
        "category": "INVALID_OPTIONS",
        "description": "Stamp add with an unknown flag should fail",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "--unknown-flag",
            "-m",
            "text",
            "--",
            "font:Helvetica",
            "DRAFT",
            "in.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "flag provided but not defined",
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_add_unknown_option",
        "category": "INVALID_OPTIONS",
        "description": "Watermark add with an unknown flag should fail",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "--bogus",
            "-m",
            "text",
            "--",
            "font:Helvetica",
            "DRAFT",
            "in.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "flag provided but not defined",
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_add_verbose_flag",
        "category": "HAPPY_PATH",
        "description": "Stamp add with verbose flag should produce debug output",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-v",
            "-m",
            "text",
            "--",
            "font:Helvetica, points:24",
            "DRAFT",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_fill_with_passwords",
        "category": "HAPPY_PATH",
        "description": "Fill form in an encrypted PDF using user and owner passwords",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "-upw",
            "user123",
            "-opw",
            "owner456",
            "encrypted_form.pdf",
            "form_data.json",
            "filled_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted_form.pdf",
                "content": "COPY_FROM_TESTDATA"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_form.pdf",
                "form_data.json",
                "filled_output.pdf"
            ]
        }
    },
    {
        "name": "test_create_with_config_flag",
        "category": "HAPPY_PATH",
        "description": "Create PDF with custom config directory",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "-c",
            "disable",
            "content.json",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "content.json",
                "content": "{\"pages\":{\"1\":{\"content\":{\"text\":[{\"value\":\"Hello!\",\"anchor\":\"center\",\"font\":{\"name\":\"Helvetica\",\"size\":12}}]}}}}"
            }
        },
        "cleanup": {
            "delete_files": [
                "content.json",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_text_all_description_params",
        "category": "HAPPY_PATH",
        "description": "Add a text stamp with comprehensive description parameters (font, size, position, offset, scale, rotation, opacity, colors, margins, border)",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:24, pos:tl, off:10 10, sc:1.0, rot:45, op:0.7, fillc:#FF0000, strokec:#000000, bgc:#FFFFFF, ma:5, bo:1 round",
            "SAMPLE STAMP",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_text_page_range",
        "category": "HAPPY_PATH",
        "description": "Add a text stamp to a page range selection",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-p",
            "1-3",
            "-m",
            "text",
            "--",
            "font:Helvetica",
            "RANGE TEST",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_export_roundtrip",
        "category": "HAPPY_PATH",
        "description": "Export form data then re-import it to verify roundtrip integrity",
        "command": "pdfcpu",
        "subcommand": "form export",
        "args": [
            "test_form.pdf",
            "roundtrip.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "roundtrip.json"
            ]
        }
    },
    {
        "name": "test_create_json_with_text_and_image",
        "category": "HAPPY_PATH",
        "description": "Create a PDF with both text and image elements from JSON",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "complex_content.json",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "complex_content.json",
                "content": "COPY_FROM:pkg/testdata/json/create/textAnchored.json"
            }
        },
        "cleanup": {
            "delete_files": [
                "complex_content.json",
                "output.pdf"
            ]
        }
    },
    {
        "name": "test_watermark_add_text_diagonal",
        "category": "HAPPY_PATH",
        "description": "Add a diagonal text watermark to a PDF",
        "command": "pdfcpu",
        "subcommand": "watermark add",
        "args": [
            "-m",
            "text",
            "--",
            "font:Helvetica, points:72, di:1, op:0.2",
            "DRAFT",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_multifill_nonexistent_data_file",
        "category": "FILE_INPUT",
        "description": "Multi-fill with a non-existent data file should fail",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "--",
            "test_form.pdf",
            "nonexistent.json",
            "out_dir"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_multifill_nonexistent_template",
        "category": "FILE_INPUT",
        "description": "Multi-fill with a non-existent template PDF should fail",
        "command": "pdfcpu",
        "subcommand": "form multifill",
        "args": [
            "--",
            "nonexistent.pdf",
            "data.json",
            "out_dir"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_stamp_remove_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Stamp remove with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "stamp remove",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_watermark_remove_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Watermark remove with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "watermark remove",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_lock_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Form lock with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "form lock",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_unlock_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Form unlock with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "form unlock",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_reset_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Form reset with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "form reset",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_form_export_nonexistent_file",
        "category": "FILE_INPUT",
        "description": "Form export with a non-existent input file should fail",
        "command": "pdfcpu",
        "subcommand": "form export",
        "args": [
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10
    },
    {
        "name": "test_create_nonexistent_input_pdf",
        "category": "FILE_INPUT",
        "description": "Create with a non-existent input PDF (append mode) should fail",
        "command": "pdfcpu",
        "subcommand": "create",
        "args": [
            "content.json",
            "nonexistent.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "content.json",
                "content": "{\"pages\":{\"1\":{\"content\":{\"text\":[{\"value\":\"test\",\"anchor\":\"center\",\"font\":{\"name\":\"Helvetica\",\"size\":12}}]}}}}"
            }
        },
        "cleanup": {
            "delete_files": [
                "content.json"
            ]
        }
    },
    {
        "name": "test_stamp_quiet_flag",
        "category": "HAPPY_PATH",
        "description": "Stamp add with quiet flag should suppress output",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-q",
            "-m",
            "text",
            "--",
            "font:Helvetica",
            "QUIET",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    },
    {
        "name": "test_form_fill_invalid_json_data",
        "category": "BOUNDARY",
        "description": "Form fill with invalid JSON data file should fail gracefully",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "test_form.pdf",
            "bad_data.json",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "bad_data.json"
            ]
        }
    },
    {
        "name": "test_form_fill_empty_json",
        "category": "BOUNDARY",
        "description": "Form fill with empty JSON object should handle gracefully",
        "command": "pdfcpu",
        "subcommand": "form fill",
        "args": [
            "test_form.pdf",
            "empty.json",
            "output.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "test_form.pdf",
                "content": "COPY_FROM:pkg/samples/form/fill/english.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_form.pdf",
                "empty.json"
            ]
        }
    },
    {
        "name": "test_fonts_install_multiple_fonts",
        "category": "HAPPY_PATH",
        "description": "Install multiple TrueType font files at once",
        "command": "pdfcpu",
        "subcommand": "fonts install",
        "args": [
            "font1.ttf",
            "font2.ttc"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "font1.ttf",
                "content": "COPY_FROM_TESTDATA"
            }
        },
        "cleanup": {
            "delete_files": [
                "font1.ttf",
                "font2.ttc"
            ]
        }
    },
    {
        "name": "test_fonts_install_mixed_valid_invalid",
        "category": "BOUNDARY",
        "description": "Font install with mix of valid and invalid extensions filters to valid only",
        "command": "pdfcpu",
        "subcommand": "fonts install",
        "args": [
            "valid.ttf",
            "invalid.pdf",
            "also_valid.ttc"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30
    },
    {
        "name": "test_form_list_non_form_pdf",
        "category": "BOUNDARY",
        "description": "Form list on a PDF without form fields should succeed with no fields listed",
        "command": "pdfcpu",
        "subcommand": "form list",
        "args": [
            "no_form.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "no_form.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "no_form.pdf"
            ]
        }
    },
    {
        "name": "test_stamp_add_with_unit_flag",
        "category": "HAPPY_PATH",
        "description": "Stamp add using display unit flag for offset coordinates",
        "command": "pdfcpu",
        "subcommand": "stamp add",
        "args": [
            "-u",
            "cm",
            "-m",
            "text",
            "--",
            "font:Helvetica, points:24, off:1 1",
            "UNITS TEST",
            "test_input.pdf",
            "test_output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.pdf",
                "content": "COPY_FROM:pkg/testdata/mountain.pdf"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.pdf",
                "test_output.pdf"
            ]
        }
    }
]''')

# CLI binary/entry point
CLI_COMMAND = "./pdfcpu"

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
    pattern_normalized = normalize_output(pattern)
    return pattern_normalized.lower() in actual_normalized.lower()


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
    subcommand: str | None,
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
        "subcommand": subcommand,
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
    command = CLI_COMMAND
    raw_args = test_case.get("args", [])
    args = (
        [str(arg) for arg in raw_args]
        if isinstance(raw_args, list)
        else ([str(raw_args)] if raw_args is not None else [])
    )
    subcommand = test_case.get("subcommand", "")
    subcommand_parts = (
        [part for part in subcommand.strip().split(" ") if part]
        if isinstance(subcommand, str) and subcommand.strip()
        else []
    )
    execution_args = subcommand_parts + args
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
                    subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
                    args=execution_args,
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
        full_cmd = [command] + execution_args

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
                subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
                args=execution_args,
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
                subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
                args=execution_args,
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
            subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
            args=execution_args,
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

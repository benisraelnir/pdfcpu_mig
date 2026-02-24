#!/usr/bin/env python3
"""
BE Testing - CLI Contract Validation Tests

Generated pytest script to validate the CLI spec against the running application.
Each command is tested as a parameterized test case using pytest.

This script supports two modes:
1. SRC Validation: Tests commands and captures outputs (no expected_stdout/stderr)
2. DST Contract Validation: Tests commands and validates outputs match expected

Generated at: 2026-02-24T20:00:54.210089+00:00
Project: pdf
Milestone: 3
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
        "name": "test_encrypt_help",
        "category": "HELP_OUTPUT",
        "description": "Verify encrypt command shows usage when invoked with no arguments",
        "command": "pdfcpu",
        "args": [
            "encrypt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu encrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_decrypt_help",
        "category": "HELP_OUTPUT",
        "description": "Verify decrypt command shows usage when invoked with no arguments",
        "command": "pdfcpu",
        "args": [
            "decrypt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu decrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_changeupw_help",
        "category": "HELP_OUTPUT",
        "description": "Verify changeupw command shows usage when invoked with no arguments",
        "command": "pdfcpu",
        "args": [
            "changeupw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu changeupw",
        "timeout_seconds": 10
    },
    {
        "name": "test_changeopw_help",
        "category": "HELP_OUTPUT",
        "description": "Verify changeopw command shows usage when invoked with no arguments",
        "command": "pdfcpu",
        "args": [
            "changeopw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu changeopw",
        "timeout_seconds": 10
    },
    {
        "name": "test_permissions_list_help",
        "category": "HELP_OUTPUT",
        "description": "Verify permissions list shows usage when invoked with no file argument",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu permissions list",
        "timeout_seconds": 10
    },
    {
        "name": "test_permissions_set_help",
        "category": "HELP_OUTPUT",
        "description": "Verify permissions set shows usage when invoked with no file argument",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu permissions set",
        "timeout_seconds": 10
    },
    {
        "name": "test_signatures_validate_help",
        "category": "HELP_OUTPUT",
        "description": "Verify signatures validate shows usage when invoked with too many arguments",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "file1.pdf",
            "file2.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu signatures validate",
        "timeout_seconds": 10
    },
    {
        "name": "test_certificates_inspect_help",
        "category": "HELP_OUTPUT",
        "description": "Verify certificates inspect shows usage when invoked with no file argument",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu certificates inspect",
        "timeout_seconds": 10
    },
    {
        "name": "test_certificates_import_help",
        "category": "HELP_OUTPUT",
        "description": "Verify certificates import shows usage when invoked with no file argument",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "import"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu certificates import",
        "timeout_seconds": 10
    },
    {
        "name": "test_encrypt_aes256_happy_path",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with AES-256, owner and user passwords, default permissions (none)",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_aes128_happy_path",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with AES-128, owner password only",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "aes",
            "-key",
            "128",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_aes128.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_aes128.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_rc4_40_happy_path",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with RC4-40, both passwords",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "rc4",
            "-key",
            "40",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_rc4_40.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_rc4_40.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_rc4_128_happy_path",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with RC4-128, both passwords",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "rc4",
            "-key",
            "128",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_rc4_128.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_rc4_128.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_with_perm_all",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with all permissions granted",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-perm",
            "all",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_perm_all.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_perm_all.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_with_perm_print",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with print-only permissions",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-perm",
            "print",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_perm_print.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_perm_print.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_inplace",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF in place (no output file specified)",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-opw",
            "ownerpass",
            "--",
            "input_inplace.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input_inplace.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "input_inplace.pdf"
            ]
        }
    },
    {
        "name": "test_encrypt_missing_opw",
        "category": "INVALID_ARGS",
        "description": "Encrypt without owner password should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "missing non-empty owner password",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_encrypt_invalid_mode",
        "category": "INVALID_OPTIONS",
        "description": "Encrypt with invalid encryption mode should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "des",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "valid modes: rc4,aes",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_encrypt_invalid_key_rc4",
        "category": "INVALID_OPTIONS",
        "description": "Encrypt RC4 with unsupported key length 256 should auto-downgrade to 128",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "rc4",
            "-key",
            "256",
            "-opw",
            "ownerpass",
            "--",
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
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "output.pdf"
            ]
        },
        "notes": "RC4 with key=256 auto-downgrades to key=128"
    },
    {
        "name": "test_encrypt_invalid_key_aes",
        "category": "INVALID_OPTIONS",
        "description": "Encrypt AES with unsupported key length should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "aes",
            "-key",
            "64",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "supported AES key lengths",
        "timeout_seconds": 10
    },
    {
        "name": "test_encrypt_invalid_perm",
        "category": "INVALID_OPTIONS",
        "description": "Encrypt with invalid permission value should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-perm",
            "readwrite",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "supported permissions",
        "timeout_seconds": 10
    },
    {
        "name": "test_encrypt_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Encrypt with too many positional arguments should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "output.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu encrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_encrypt_file_not_found",
        "category": "FILE_INPUT",
        "description": "Encrypt a non-existent file should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-opw",
            "ownerpass",
            "--",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file",
        "timeout_seconds": 10
    },
    {
        "name": "test_encrypt_already_encrypted",
        "category": "BOUNDARY",
        "description": "Encrypting an already encrypted file should fail",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "already_encrypted.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "already_encrypted.pdf",
                "content": "PRE_ENCRYPTED_PDF_FIXTURE"
            }
        },
        "notes": "File must be pre-encrypted for this test"
    },
    {
        "name": "test_decrypt_with_correct_passwords",
        "category": "HAPPY_PATH",
        "description": "Decrypt a PDF with correct user and owner passwords",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf",
            "decrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "decrypted.pdf"
            ]
        }
    },
    {
        "name": "test_decrypt_with_opw_only",
        "category": "HAPPY_PATH",
        "description": "Decrypt a PDF using owner password only",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf",
            "decrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_OPW_ONLY"
            }
        },
        "cleanup": {
            "delete_files": [
                "decrypted.pdf"
            ]
        }
    },
    {
        "name": "test_decrypt_inplace",
        "category": "HAPPY_PATH",
        "description": "Decrypt a PDF in place (no output file specified)",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted_inplace.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted_inplace.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_decrypt_wrong_password",
        "category": "INVALID_ARGS",
        "description": "Decrypt with wrong passwords should fail",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "-upw",
            "wronguser",
            "-opw",
            "wrongowner",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        },
        "notes": "Both passwords are wrong so decryption should fail"
    },
    {
        "name": "test_decrypt_wrong_opw_empty_upw_succeeds",
        "category": "BOUNDARY",
        "description": "Decrypt with wrong owner password but empty user password (opw-only encrypted) should succeed via fallback",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "-opw",
            "wrongowner",
            "--",
            "encrypted_opw_only.pdf",
            "decrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted_opw_only.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_OPW_ONLY"
            }
        },
        "cleanup": {
            "delete_files": [
                "decrypted.pdf"
            ]
        },
        "notes": "When file was encrypted with opw only (empty upw), providing wrong opw falls back to empty upw and succeeds"
    },
    {
        "name": "test_decrypt_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Decrypt with too many arguments should fail",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "--",
            "input.pdf",
            "output.pdf",
            "extra.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu decrypt",
        "timeout_seconds": 10
    },
    {
        "name": "test_decrypt_file_not_found",
        "category": "FILE_INPUT",
        "description": "Decrypt a non-existent file should fail",
        "command": "pdfcpu",
        "args": [
            "decrypt",
            "--",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file",
        "timeout_seconds": 10
    },
    {
        "name": "test_changeupw_happy_path",
        "category": "HAPPY_PATH",
        "description": "Change user password on an encrypted PDF",
        "command": "pdfcpu",
        "args": [
            "changeupw",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf",
            "userpass",
            "newuserpass"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_changeupw_remove_upw",
        "category": "HAPPY_PATH",
        "description": "Remove user password by changing it to empty string",
        "command": "pdfcpu",
        "args": [
            "changeupw",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf",
            "userpass",
            ""
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_changeupw_wrong_old_password",
        "category": "INVALID_ARGS",
        "description": "Change user password with wrong old password should fail",
        "command": "pdfcpu",
        "args": [
            "changeupw",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf",
            "wrongoldpw",
            "newpw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_changeupw_missing_args",
        "category": "INVALID_ARGS",
        "description": "Change user password with too few arguments should fail",
        "command": "pdfcpu",
        "args": [
            "changeupw",
            "--",
            "encrypted.pdf",
            "oldpw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu changeupw",
        "timeout_seconds": 10
    },
    {
        "name": "test_changeupw_too_many_args",
        "category": "INVALID_ARGS",
        "description": "Change user password with too many arguments should fail",
        "command": "pdfcpu",
        "args": [
            "changeupw",
            "--",
            "encrypted.pdf",
            "oldpw",
            "newpw",
            "extrapw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu changeupw",
        "timeout_seconds": 10
    },
    {
        "name": "test_changeopw_happy_path",
        "category": "HAPPY_PATH",
        "description": "Change owner password on an encrypted PDF",
        "command": "pdfcpu",
        "args": [
            "changeopw",
            "-upw",
            "userpass",
            "--",
            "encrypted.pdf",
            "ownerpass",
            "newownerpass"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_changeopw_empty_new_password_fails",
        "category": "INVALID_ARGS",
        "description": "Change owner password to empty string should fail",
        "command": "pdfcpu",
        "args": [
            "changeopw",
            "-upw",
            "userpass",
            "--",
            "encrypted.pdf",
            "ownerpass",
            ""
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "owner password cannot be empty",
        "timeout_seconds": 10,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_changeopw_wrong_old_password",
        "category": "INVALID_ARGS",
        "description": "Change owner password with wrong old owner password should fail",
        "command": "pdfcpu",
        "args": [
            "changeopw",
            "-upw",
            "",
            "--",
            "encrypted_opw_only.pdf",
            "wrongoldopw",
            "newopw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted_opw_only.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_OPW_ONLY"
            }
        }
    },
    {
        "name": "test_changeopw_wrong_upw_fails",
        "category": "INVALID_ARGS",
        "description": "Change owner password with wrong user password should fail",
        "command": "pdfcpu",
        "args": [
            "changeopw",
            "-upw",
            "wrongupw",
            "--",
            "encrypted_opw_only.pdf",
            "ownerpass",
            "newopw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted_opw_only.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_OPW_ONLY"
            }
        }
    },
    {
        "name": "test_changeopw_missing_args",
        "category": "INVALID_ARGS",
        "description": "Change owner password with too few arguments should fail",
        "command": "pdfcpu",
        "args": [
            "changeopw",
            "--",
            "encrypted.pdf",
            "oldopw"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "usage: pdfcpu changeopw",
        "timeout_seconds": 10
    },
    {
        "name": "test_permissions_list_unencrypted",
        "category": "HAPPY_PATH",
        "description": "List permissions on an unencrypted PDF shows 'Full access'",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "--",
            "unencrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Full access",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "unencrypted.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_list_encrypted_with_opw",
        "category": "HAPPY_PATH",
        "description": "List permissions on encrypted PDF using owner password",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "permission bits:",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_list_encrypted_with_upw",
        "category": "HAPPY_PATH",
        "description": "List permissions on encrypted PDF using user password",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "-upw",
            "userpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "permission bits:",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_list_encrypted_no_pw_fails",
        "category": "INVALID_ARGS",
        "description": "List permissions on encrypted PDF without password should fail",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_WITH_UPW"
            }
        },
        "notes": "File must be encrypted with non-empty upw so that no-password access fails"
    },
    {
        "name": "test_permissions_list_multiple_files",
        "category": "HAPPY_PATH",
        "description": "List permissions for multiple unencrypted PDF files",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "--",
            "file1.pdf",
            "file2.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Full access",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "file1.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_all",
        "category": "HAPPY_PATH",
        "description": "Set all permissions on an encrypted PDF",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "all",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_none",
        "category": "HAPPY_PATH",
        "description": "Set no permissions (most restrictive) on an encrypted PDF",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "none",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_print",
        "category": "HAPPY_PATH",
        "description": "Set print-only permissions on an encrypted PDF",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "print",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_hex",
        "category": "HAPPY_PATH",
        "description": "Set permissions using hex notation",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "xF3C",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_binary",
        "category": "HAPPY_PATH",
        "description": "Set permissions using binary notation",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "111100111100",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_without_opw_fails",
        "category": "INVALID_ARGS",
        "description": "Set permissions without owner password should fail",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "all",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_without_upw_fails",
        "category": "INVALID_ARGS",
        "description": "Set permissions with only upw (no opw) should fail",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "all",
            "-upw",
            "userpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_permissions_set_invalid_perm",
        "category": "INVALID_OPTIONS",
        "description": "Set permissions with invalid permission value should fail",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "readwrite",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu permissions set",
        "timeout_seconds": 10
    },
    {
        "name": "test_permissions_set_multiple_files_fails",
        "category": "INVALID_ARGS",
        "description": "Set permissions on multiple files should fail (only one file allowed)",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "all",
            "-opw",
            "ownerpass",
            "--",
            "file1.pdf",
            "file2.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "pdfcpu permissions set",
        "timeout_seconds": 10
    },
    {
        "name": "test_permissions_set_prefix_completion",
        "category": "HAPPY_PATH",
        "description": "Set permissions using prefix completion (e.g., 'pr' for 'print')",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "set",
            "-perm",
            "pr",
            "-upw",
            "userpass",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE"
            }
        },
        "notes": "Permission prefix 'pr' should match 'print'"
    },
    {
        "name": "test_signatures_validate_pkcs7_detached",
        "category": "HAPPY_PATH",
        "description": "Validate signatures on a PDF signed with adbe.pkcs7.detached",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-a",
            "--",
            "signed_pkcs7_detached.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "signed_pkcs7_detached.pdf",
                "content": "SIGNED_PDF_FIXTURE_PKCS7_DETACHED"
            }
        },
        "notes": "Uses sample file from pkg/samples/signatures/adbe.pkcs7.detached/"
    },
    {
        "name": "test_signatures_validate_etsi_cades",
        "category": "HAPPY_PATH",
        "description": "Validate signatures on a PDF signed with ETSI.CAdES.detached",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-a",
            "-f",
            "--",
            "signed_etsi_cades.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "signed_etsi_cades.pdf",
                "content": "SIGNED_PDF_FIXTURE_ETSI_CADES"
            }
        },
        "notes": "Uses sample file from pkg/samples/signatures/ETSI.CAdES.detached/"
    },
    {
        "name": "test_signatures_validate_x509_rsa_sha1",
        "category": "HAPPY_PATH",
        "description": "Validate signatures on a PDF signed with adbe.x509.rsa_sha1",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-a",
            "--",
            "signed_x509.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "signed_x509.pdf",
                "content": "SIGNED_PDF_FIXTURE_X509_RSA_SHA1"
            }
        },
        "notes": "Uses sample file from pkg/samples/signatures/adbe.x509.rsa_sha1/"
    },
    {
        "name": "test_signatures_validate_all_flag",
        "category": "HAPPY_PATH",
        "description": "Validate all signatures including cosigners and timestamps",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-a",
            "--",
            "multi_signed.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "signatures present",
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "multi_signed.pdf",
                "content": "MULTI_SIGNED_PDF_FIXTURE"
            }
        },
        "notes": "Tests the -a (all) flag for processing multiple signatures"
    },
    {
        "name": "test_signatures_validate_full_output",
        "category": "HAPPY_PATH",
        "description": "Validate signatures with full verbose output including cert chains",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-a",
            "-f",
            "--",
            "signed.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "signed.pdf",
                "content": "SIGNED_PDF_FIXTURE"
            }
        },
        "notes": "Tests the -f (full) flag for comprehensive output"
    },
    {
        "name": "test_signatures_validate_offline",
        "category": "HAPPY_PATH",
        "description": "Validate signatures in offline mode (no CRL/OCSP network calls)",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-offline",
            "-a",
            "--",
            "signed.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "signed.pdf",
                "content": "SIGNED_PDF_FIXTURE"
            }
        },
        "notes": "Uses the --offline flag to skip HTTP traffic for revocation checking"
    },
    {
        "name": "test_signatures_validate_no_signatures",
        "category": "BOUNDARY",
        "description": "Validate signatures on a PDF with no signatures present",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "--",
            "unsigned.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "No signatures present",
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "unsigned.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        }
    },
    {
        "name": "test_signatures_validate_file_not_found",
        "category": "FILE_INPUT",
        "description": "Validate signatures on a non-existent file should fail",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "--",
            "nonexistent.pdf"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file",
        "timeout_seconds": 10
    },
    {
        "name": "test_certificates_list",
        "category": "HAPPY_PATH",
        "description": "List all installed certificates",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "list"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "notes": "Should list pre-loaded EU Trusted List certificates"
    },
    {
        "name": "test_certificates_list_json",
        "category": "HAPPY_PATH",
        "description": "List all installed certificates in JSON format",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "list",
            "-j"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "notes": "Tests JSON output flag for certificate listing"
    },
    {
        "name": "test_certificates_inspect_pem",
        "category": "HAPPY_PATH",
        "description": "Inspect a PEM certificate file",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect",
            "test_cert.pem"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "certificates",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_cert.pem",
                "content": "PEM_CERTIFICATE_FIXTURE"
            }
        }
    },
    {
        "name": "test_certificates_inspect_p7c",
        "category": "HAPPY_PATH",
        "description": "Inspect a P7C certificate file",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect",
            "test_cert.p7c"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "certificates",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_cert.p7c",
                "content": "P7C_CERTIFICATE_FIXTURE"
            }
        }
    },
    {
        "name": "test_certificates_inspect_cer",
        "category": "HAPPY_PATH",
        "description": "Inspect a CER certificate file",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect",
            "test_cert.cer"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "certificates",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_cert.cer",
                "content": "CER_CERTIFICATE_FIXTURE"
            }
        }
    },
    {
        "name": "test_certificates_inspect_crt",
        "category": "HAPPY_PATH",
        "description": "Inspect a CRT certificate file",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect",
            "test_cert.crt"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "certificates",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_cert.crt",
                "content": "CRT_CERTIFICATE_FIXTURE"
            }
        }
    },
    {
        "name": "test_certificates_inspect_unsupported_extension",
        "category": "INVALID_ARGS",
        "description": "Inspect a file with unsupported extension should fail",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect",
            "test_cert.txt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "allowed extensions: .pem, .p7c, .cer, .crt",
        "timeout_seconds": 10
    },
    {
        "name": "test_certificates_inspect_multiple_files",
        "category": "HAPPY_PATH",
        "description": "Inspect multiple certificate files at once",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "inspect",
            "cert1.pem",
            "cert2.p7c"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "inspected",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "cert1.pem",
                "content": "PEM_CERTIFICATE_FIXTURE"
            }
        }
    },
    {
        "name": "test_certificates_import_pem",
        "category": "HAPPY_PATH",
        "description": "Import a PEM certificate file",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "import",
            "test_cert.pem"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "imported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_cert.pem",
                "content": "PEM_CERTIFICATE_FIXTURE"
            }
        }
    },
    {
        "name": "test_certificates_import_unsupported_extension",
        "category": "INVALID_ARGS",
        "description": "Import a file with unsupported extension should fail",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "import",
            "test_cert.txt"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "allowed extensions: .pem, .p7c, .cer, .crt",
        "timeout_seconds": 10
    },
    {
        "name": "test_certificates_import_file_not_found",
        "category": "FILE_INPUT",
        "description": "Import a non-existent certificate file should fail",
        "command": "pdfcpu",
        "args": [
            "certificates",
            "import",
            "nonexistent.pem"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "no such file",
        "timeout_seconds": 10
    },
    {
        "name": "test_encrypt_then_validate",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF and then validate it with correct password",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "aes",
            "-key",
            "256",
            "-upw",
            "user",
            "-opw",
            "owner",
            "--",
            "input.pdf",
            "encrypted_for_validate.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_for_validate.pdf"
            ]
        },
        "notes": "Part 1 of encrypt-then-validate integration test"
    },
    {
        "name": "test_encrypt_decrypt_roundtrip_rc4_40",
        "category": "HAPPY_PATH",
        "description": "Full encrypt/decrypt roundtrip with RC4-40",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "rc4",
            "-key",
            "40",
            "-upw",
            "user",
            "-opw",
            "owner",
            "--",
            "input.pdf",
            "roundtrip_rc4_40.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "roundtrip_rc4_40.pdf"
            ]
        },
        "notes": "Part 1 of RC4-40 roundtrip test"
    },
    {
        "name": "test_encrypt_decrypt_roundtrip_rc4_128",
        "category": "HAPPY_PATH",
        "description": "Full encrypt/decrypt roundtrip with RC4-128",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "rc4",
            "-key",
            "128",
            "-upw",
            "user",
            "-opw",
            "owner",
            "--",
            "input.pdf",
            "roundtrip_rc4_128.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "roundtrip_rc4_128.pdf"
            ]
        },
        "notes": "Part 1 of RC4-128 roundtrip test"
    },
    {
        "name": "test_encrypt_decrypt_roundtrip_aes_128",
        "category": "HAPPY_PATH",
        "description": "Full encrypt/decrypt roundtrip with AES-128",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "aes",
            "-key",
            "128",
            "-upw",
            "user",
            "-opw",
            "owner",
            "--",
            "input.pdf",
            "roundtrip_aes_128.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "roundtrip_aes_128.pdf"
            ]
        },
        "notes": "Part 1 of AES-128 roundtrip test"
    },
    {
        "name": "test_encrypt_decrypt_roundtrip_aes_256",
        "category": "HAPPY_PATH",
        "description": "Full encrypt/decrypt roundtrip with AES-256",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "aes",
            "-key",
            "256",
            "-upw",
            "user",
            "-opw",
            "owner",
            "--",
            "input.pdf",
            "roundtrip_aes_256.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "roundtrip_aes_256.pdf"
            ]
        },
        "notes": "Part 1 of AES-256 roundtrip test"
    },
    {
        "name": "test_command_prefix_completion_enc",
        "category": "BOUNDARY",
        "description": "Test command prefix completion: 'enc' should match 'encrypt'",
        "command": "pdfcpu",
        "args": [
            "enc",
            "-opw",
            "ownerpass",
            "--",
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
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "output.pdf"
            ]
        },
        "notes": "Verifies that command prefix completion works for 'enc' -> 'encrypt'"
    },
    {
        "name": "test_command_prefix_completion_dec",
        "category": "BOUNDARY",
        "description": "Test command prefix completion: 'dec' should match 'decrypt'",
        "command": "pdfcpu",
        "args": [
            "dec",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf",
            "output.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_OPW_ONLY"
            }
        },
        "cleanup": {
            "delete_files": [
                "output.pdf"
            ]
        },
        "notes": "Verifies that command prefix completion works for 'dec' -> 'decrypt'"
    },
    {
        "name": "test_encrypt_opw_only",
        "category": "HAPPY_PATH",
        "description": "Encrypt with owner password only (no user password), allowing passwordless opening",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_opw_only.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_opw_only.pdf"
            ]
        },
        "notes": "When encrypted with opw only, the document can be opened without any password but permissions are restricted"
    },
    {
        "name": "test_permissions_after_encrypt_none",
        "category": "HAPPY_PATH",
        "description": "After encryption with default permissions (none), verify permission bits are all zero",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "permission bits: 000000000000",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_PERM_NONE"
            }
        },
        "notes": "Verifies that default encryption produces 'none' permission bits"
    },
    {
        "name": "test_permissions_after_encrypt_all",
        "category": "HAPPY_PATH",
        "description": "After encryption with all permissions, verify permission bits are 111100111100",
        "command": "pdfcpu",
        "args": [
            "permissions",
            "list",
            "-opw",
            "ownerpass",
            "--",
            "encrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "permission bits: 111100111100",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "encrypted.pdf",
                "content": "ENCRYPTED_PDF_FIXTURE_PERM_ALL"
            }
        },
        "notes": "Verifies that encryption with -perm all produces correct permission bits"
    },
    {
        "name": "test_quiet_flag_suppresses_output",
        "category": "HAPPY_PATH",
        "description": "Using -q flag should suppress normal output",
        "command": "pdfcpu",
        "args": [
            "-q",
            "permissions",
            "list",
            "--",
            "unencrypted.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "unencrypted.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "notes": "The -q flag disables stdout output"
    },
    {
        "name": "test_signatures_validate_single_signature_output",
        "category": "HAPPY_PATH",
        "description": "Validate a single signature and check output format",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "--",
            "single_signed.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Status:",
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "single_signed.pdf",
                "content": "SIGNED_PDF_FIXTURE_SINGLE"
            }
        },
        "notes": "Single signature output includes Type, Status, Reason, Signed fields"
    },
    {
        "name": "test_signatures_validate_multiple_signature_stats",
        "category": "HAPPY_PATH",
        "description": "Validate multiple signatures and check statistics output",
        "command": "pdfcpu",
        "args": [
            "signatures",
            "validate",
            "-a",
            "--",
            "multi_signed.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "signatures present:",
        "expected_stderr": null,
        "timeout_seconds": 60,
        "setup": {
            "create_file": {
                "path": "multi_signed.pdf",
                "content": "MULTI_SIGNED_PDF_FIXTURE"
            }
        },
        "notes": "Multiple signatures produce summary statistics (total, form signed, page signed, etc.)"
    },
    {
        "name": "test_encrypt_aes40_happy_path",
        "category": "HAPPY_PATH",
        "description": "Encrypt a PDF with AES-40 (non-standard but supported)",
        "command": "pdfcpu",
        "args": [
            "encrypt",
            "-m",
            "aes",
            "-key",
            "40",
            "-opw",
            "ownerpass",
            "--",
            "input.pdf",
            "encrypted_aes40.pdf"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "input.pdf",
                "content": "VALID_PDF_FIXTURE"
            }
        },
        "cleanup": {
            "delete_files": [
                "encrypted_aes40.pdf"
            ]
        }
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

import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

log_path = os.path.join(os.path.dirname(__file__), "foundation_test.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
def log(msg):
    print(msg)
    logging.info(msg)

def test_file_structure():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    paths = [
        "cli.py",
        "core.py",
        "fsal.py",
        "persona_manager.py",
        "workflow.py",
        "backup.py",
        "memory/memory_manager.py",
        "memory/friday_memory_schema.sql",
        "memory/persona_mr_clean.json",
        "memory/__init__.py",
        "__init__.py",
    ]
    for path in paths:
        full_path = os.path.join(base, path)
        log(f"Checking file: {full_path}")
        assert os.path.isfile(full_path), f"Missing: {full_path}"
        log(f"[FOUND] {full_path}")

def test_imports():
    try:
        import brahma.cli
        import brahma.core
        import brahma.fsal
        import brahma.persona_manager
        import brahma.workflow
        import brahma.backup
        import brahma.memory.memory_manager
        from brahma.memory.memory_manager import FridayMemoryManager
        log("Imports succeeded")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"Import error: {tb}")
        print(tb)
        assert False, f"Cannot import: {tb}"

def test_memory_manager_crud():
    from brahma.memory.memory_manager import FridayMemoryManager
    import sqlite3
    import tempfile
    import shutil

    schema_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'memory', 'friday_memory_schema.sql'))
    tempdir = tempfile.mkdtemp()
    db_path = os.path.join(tempdir, "test_friday_memory.db")
    schema_path = os.path.join(tempdir, "friday_memory_schema.sql")
    shutil.copy(schema_src, schema_path)

    class TestMemoryManager(FridayMemoryManager):
        def __init__(self):
            super().__init__(db_path=db_path, schema_path=schema_path)

    mm = TestMemoryManager()
    log("Adding test messages...")
    mm.add_message("user", "ping", tags=["test"])
    mm.add_message("friday", "pong", tags=["test", "response"])
    all_msgs = mm.get_active_session_messages()
    log(f"Messages: {all_msgs}")
    assert len(all_msgs) == 2
    assert all_msgs[0]["content"] == "ping"
    assert all_msgs[1]["role"] == "friday"
    log("Ending session and verifying new session starts...")
    mm.end_active_session(tags=["test_end"])
    mm.add_message("user", "new session", tags=["test"])
    msgs2 = mm.get_active_session_messages()
    log(f"New session messages: {msgs2}")
    assert len(msgs2) == 1
    assert msgs2[0]["content"] == "new session"
    shutil.rmtree(tempdir)

def test_cli_run_command():
    import subprocess
    cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cli.py'))
    cmd = [
        sys.executable,
        cli_path,
        "run",
        "System test: Are you alive, Friday?"
    ]
    log(f"Running CLI: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    log(f"CLI output: {result.stdout.decode().strip()}")
    log(f"CLI stderr: {result.stderr.decode().strip()}")
    assert result.returncode == 0
    assert b"System test" not in result.stderr  # No obvious errors

def test_cli_chat_mode_exit():
    try:
        import pexpect
    except ImportError:
        log("pexpect not installed, skipping chat mode test.")
        return
    cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cli.py'))
    log("Starting chat mode with 'exit' input...")
    child = pexpect.spawn(f"{sys.executable} {cli_path} chat", encoding="utf-8")
    child.expect("You >")  # Wait for prompt
    child.sendline("exit")
    idx = child.expect(["streak-free victory", pexpect.EOF, pexpect.TIMEOUT], timeout=10)
    log(f"pexpect output: {child.before}")
    child.terminate(force=True)
    assert idx == 0 or "streak-free victory" in child.before

def test_schema_file_content():
    required_lines = [
        "CREATE TABLE IF NOT EXISTS session",
        "CREATE TABLE IF NOT EXISTS message",
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "started_at TEXT",
        "role TEXT",
        "content TEXT",
        "tags TEXT",
        "timestamp TEXT",
    ]
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'memory', 'friday_memory_schema.sql'))
    with open(schema_path, "r") as f:
        content = f.read()
    for line in required_lines:
        log(f"Checking for '{line}' in schema...")
        assert line in content, f"Schema missing: {line}"

def test_file_permissions():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    paths = [
        "cli.py",
        "core.py",
        "fsal.py",
        "persona_manager.py",
        "workflow.py",
        "backup.py",
        "memory/memory_manager.py",
    ]
    for path in paths:
        full_path = os.path.join(base, path)
        log(f"Checking permissions for {full_path}")
        assert os.access(full_path, os.R_OK), f"Not readable: {full_path}"

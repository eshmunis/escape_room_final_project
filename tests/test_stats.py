# Make sure to test with: python -m pytest tests/test_stats.py

import os
import sqlite3

from stats import init_db, record_run, best_time

TEST_DB = os.path.join("tests", "runs_test.sqlite")

def test_stats_end_to_end():
    # Clean up any leftover test db before starting
    try:
        os.remove(TEST_DB)
    except FileNotFoundError:
        pass

    # 1) init_db creates the file and schema
    init_db(TEST_DB)
    assert os.path.exists(TEST_DB)

    # Optional sanity: can we SELECT from the 'runs' table?
    with sqlite3.connect(TEST_DB) as conn:
        # If table doesn't exist, this will raise an error
        conn.execute("SELECT COUNT(*) FROM runs")

    # 2) best_time should be None before any successful escapes
    assert best_time(TEST_DB) is None

    # 3) record a failure — should NOT change best_time
    record_run(escaped=False, duration_sec=90, db_path=TEST_DB)
    assert best_time(TEST_DB) is None

    # 4) record two wins — best_time should equal the minimum duration
    record_run(escaped=True, duration_sec=42, db_path=TEST_DB)
    assert best_time(TEST_DB) == 42

    record_run(escaped=True, duration_sec=60, db_path=TEST_DB)
    # best time should remain 42
    assert best_time(TEST_DB) == 42

    # 5) clean up the test db (leave workspace tidy)
    try:
        os.remove(TEST_DB)
    except OSError:
        # If Windows has the file locked for some reason, at least assert it exists
        assert os.path.exists(TEST_DB)

def test_init_db_idempotent_and_int_coercion():
    # Re-run init_db on the same file should not error
    init_db(TEST_DB)

    # Record a float-y duration and ensure best_time returns an int
    record_run(escaped=True, duration_sec=42.9, db_path=TEST_DB)
    bt = best_time(TEST_DB)
    assert isinstance(bt, int)
"""Tests for MIB compilation error detection in MibBuilder."""

from unittest import mock

import pytest

from pysnmp.smi import builder, error


# Mock MibStatus-like string subclasses to simulate pysmi behavior
class MibStatusCompiled(str):
    """Simulates pysmi's status_compiled."""

    def __new__(cls):
        return super().__new__(cls, "compiled")


class MibStatusFailed(str):
    """Simulates pysmi's status_failed with error attribute."""

    def __new__(cls, error_msg=None):
        instance = super().__new__(cls, "failed")
        if error_msg:
            instance.error = error_msg
        return instance


class MibStatusMissing(str):
    """Simulates pysmi's status_missing (bare singleton, no error attr)."""

    def __new__(cls):
        return super().__new__(cls, "missing")


class MibStatusUnprocessed(str):
    """Simulates pysmi's status_unprocessed (indirect error)."""

    def __new__(cls):
        return super().__new__(cls, "unprocessed")


class MibStatusUntouched(str):
    """Simulates pysmi's status_untouched (success)."""

    def __new__(cls):
        return super().__new__(cls, "untouched")


class MibStatusBorrowed(str):
    """Simulates pysmi's status_borrowed (success)."""

    def __new__(cls):
        return super().__new__(cls, "borrowed")


def test_load_modules_raises_on_failed_status():
    """Test that MibNotFoundError is raised when compiler returns status_failed."""
    mib_builder = builder.MibBuilder()
    mock_compiler = mock.Mock()

    # Simulate failed compilation with error message
    mock_compiler.compile.return_value = {
        "TEST-MIB": MibStatusFailed("Missing required object: OBJECT-GROUP")
    }

    mib_builder.set_mib_compiler(mock_compiler, "/tmp/mibs")

    with pytest.raises(error.MibNotFoundError) as exc_info:
        mib_builder.load_modules("TEST-MIB")

    assert "compilation error(s)" in str(exc_info.value)
    assert "Missing required object" in str(exc_info.value)


def test_load_modules_raises_on_missing_status():
    """Test that MibNotFoundError is raised when compiler returns status_missing."""
    mib_builder = builder.MibBuilder()
    mock_compiler = mock.Mock()

    # Simulate missing MIB
    mock_compiler.compile.return_value = {"NONEXISTENT-MIB": MibStatusMissing()}

    mib_builder.set_mib_compiler(mock_compiler, "/tmp/mibs")

    with pytest.raises(error.MibNotFoundError) as exc_info:
        mib_builder.load_modules("NONEXISTENT-MIB")

    assert "compilation error(s)" in str(exc_info.value)
    assert "missing" in str(exc_info.value)


def test_load_modules_raises_on_unprocessed_status():
    """Test that MibNotFoundError is raised when compiler returns status_unprocessed.

    This is the regression test for issue #192: status_unprocessed indicates that
    the target MIB was aborted due to a dependency failure, causing silent failures.
    """
    mib_builder = builder.MibBuilder()
    mock_compiler = mock.Mock()

    # Simulate dependency failure: target MIB marked as unprocessed
    mock_compiler.compile.return_value = {
        "TARGET-MIB": MibStatusUnprocessed(),
        "DEPENDENCY-MIB": MibStatusFailed("Syntax error in ASN.1"),
    }

    mib_builder.set_mib_compiler(mock_compiler, "/tmp/mibs")

    with pytest.raises(error.MibNotFoundError) as exc_info:
        mib_builder.load_modules("TARGET-MIB")

    assert "compilation error(s)" in str(exc_info.value)
    # Should mention unprocessed status and the dependency failure
    assert "not compiled" in str(exc_info.value) or "unprocessed" in str(exc_info.value)
    assert "Syntax error" in str(exc_info.value)


def test_load_modules_succeeds_on_compiled_status():
    """Test that load_modules succeeds when compiler returns status_compiled."""
    mib_builder = builder.MibBuilder()
    mock_compiler = mock.Mock()

    # Simulate successful compilation
    mock_compiler.compile.return_value = {"SUCCESS-MIB": MibStatusCompiled()}

    mib_builder.set_mib_compiler(mock_compiler, "/tmp/mibs")

    with mock.patch.object(mib_builder, "load_module") as mock_load:
        # Should not raise an exception
        mib_builder.load_modules("SUCCESS-MIB")

        # After compilation succeeds, load_module should be called
        mock_load.assert_called()


def test_load_modules_ignores_success_statuses():
    """Test that non-error statuses (untouched, borrowed, compiled) don't raise."""
    mib_builder = builder.MibBuilder()
    mock_compiler = mock.Mock()

    # Mix of success and no-error statuses
    mock_compiler.compile.return_value = {
        "COMPILED-MIB": MibStatusCompiled(),
        "BORROWED-MIB": MibStatusBorrowed(),
        "UNTOUCHED-MIB": MibStatusUntouched(),
    }

    mib_builder.set_mib_compiler(mock_compiler, "/tmp/mibs")

    with mock.patch.object(mib_builder, "load_module"):
        # Should not raise an exception
        mib_builder.load_modules("COMPILED-MIB")


def test_load_modules_reports_all_error_mib_names():
    """Test that error messages include all MIB names that failed."""
    mib_builder = builder.MibBuilder()
    mock_compiler = mock.Mock()

    # Multiple errors in a single compile call
    mock_compiler.compile.return_value = {
        "PRIMARY-MIB": MibStatusFailed("Circular import"),
        "SECONDARY-MIB": MibStatusMissing(),
        "TERTIARY-MIB": MibStatusUnprocessed(),
    }

    mib_builder.set_mib_compiler(mock_compiler, "/tmp/mibs")

    with pytest.raises(error.MibNotFoundError) as exc_info:
        mib_builder.load_modules("PRIMARY-MIB")

    error_msg = str(exc_info.value)
    # All failed MIBs should be mentioned in error message
    assert "Circular import" in error_msg
    assert "SECONDARY-MIB" in error_msg
    assert "TERTIARY-MIB" in error_msg

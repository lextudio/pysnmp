"""Regression tests for pysmi deprecation warnings (issue #246).

PySNMP only supports PySMI 2.x, so it must use the snake_case PySMI API.
Using the deprecated camelCase spellings still worked through PySMI's
compatibility shims, but emitted ``DeprecationWarning`` on every MIB compiler
setup -- twice when ``pysnmp.smi.compiler`` is merely imported, and four more
times inside :func:`add_mib_compiler`, which every agent/manager using dynamic
MIB compilation calls.

Note ``parserFactory`` is intentionally left alone: PySMI 2.x has no
``parser_factory`` and does not deprecate the camelCase spelling.
"""

import importlib
import warnings

from pysnmp.smi import builder, compiler

DEPRECATED_PYSMI_NAMES = (
    "getReadersFromUrls",
    "smiV1Relaxed",
    "addSources",
    "addSearchers",
    "addBorrowers",
)

# PySMI's compatibility shims warn with this phrasing. The warning is raised
# with stacklevel=2, so it is attributed to the *caller* (pysnmp's
# compiler.py) rather than to a pysmi file -- match on the message, not the
# filename.
_SHIM_MESSAGE = "is deprecated. Please use"


def _pysmi_deprecations(fn):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fn()
    return [
        str(w.message)
        for w in caught
        if issubclass(w.category, DeprecationWarning)
        and _SHIM_MESSAGE in str(w.message)
    ]


def test_importing_compiler_emits_no_pysmi_deprecation():
    def _do():
        importlib.reload(compiler)

    assert _pysmi_deprecations(_do) == []


def test_adding_mib_compiler_emits_no_pysmi_deprecation(tmp_path):
    def _do():
        mib_builder = builder.MibBuilder()
        compiler.add_mib_compiler(mib_builder, destination=str(tmp_path))

    assert _pysmi_deprecations(_do) == []


def test_add_mib_compiler_still_installs_a_working_compiler(tmp_path):
    """The rename must not merely silence warnings but keep MIBs compiling."""
    mib_builder = builder.MibBuilder()
    compiler.add_mib_compiler(mib_builder, destination=str(tmp_path))

    assert mib_builder.get_mib_compiler() is not None

    # a bundled MIB resolves through the compiler
    mib_builder.load_modules("SNMPv2-MIB")
    (sys_descr,) = mib_builder.import_symbols("SNMPv2-MIB", "sysDescr")
    assert sys_descr is not None


def test_deprecated_names_are_gone_from_source():
    """Guard against reintroducing the camelCase spellings."""
    with open(compiler.__file__) as f:
        source = f.read()

    for name in DEPRECATED_PYSMI_NAMES:
        assert name not in source, f"{name} still referenced in compiler.py"

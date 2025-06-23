from datetime import datetime
import os
import subprocess
from pathlib import Path
import sys
from inspect import isawaitable
from functools import partial
from typing import Iterable

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate, refs_by_type
from sphinx_polyversion.pyvenv import VirtualPythonEnvironment, Poetry
from sphinx_polyversion.sphinx import SphinxBuilder

#: Regex matching the branches to build docs for
BRANCH_REGEX = r"rel-.*"  # intentionally broken to skip branches

#: Regex matching the tags to build docs for
TAG_REGEX = r"v7.1|v6.2"

#: Output dir relative to project root
OUTPUT_DIR = "docs/build"

#: Source directory
SOURCE_DIR = "docs/"

#: Arguments to pass to `uv pip install`
UV_ARGS = "-e .[dev]"

#: Arguments to pass to Poetry install (for older versions)
POETRY_ARGS = "--sync"

#: Arguments to pass to `sphinx-build`
SPHINX_ARGS = "-a -v"

#: Mock data used for building local version
MOCK_DATA = {
    "revisions": [
        GitRef("v1.8.0", "", "", GitRefType.TAG, datetime.fromtimestamp(0)),
        GitRef("v1.9.3", "", "", GitRefType.TAG, datetime.fromtimestamp(1)),
        GitRef("v1.10.5", "", "", GitRefType.TAG, datetime.fromtimestamp(2)),
        GitRef("master", "", "", GitRefType.BRANCH, datetime.fromtimestamp(3)),
        GitRef("dev", "", "", GitRefType.BRANCH, datetime.fromtimestamp(4)),
        GitRef("some-feature", "", "", GitRefType.BRANCH, datetime.fromtimestamp(5)),
    ],
    "current": GitRef("local", "", "", GitRefType.TAG, datetime.fromtimestamp(6)),
}
MOCK = False
SEQUENTIAL = False  # Set to True to build docs sequentially (one version at a time)


# Custom UV environment provider
class UvEnv(VirtualPythonEnvironment):
    """Python environment using uv as the package manager."""

    def __init__(
        self,
        path: Path,
        name: str,
        *,
        args: "Iterable[str]",
        env: "dict[str, str] | None" = None,
    ):
        """Initialize UV environment provider.

        Args:
            path: Path to the project
            name: Name of the environment
            args: Arguments to pass to `uv pip install`
            env: Environment variables to set
        """
        super().__init__(
            path,
            name,
            path / ".venv",  # venv path is determined from project path
            env=env,
        )
        self.args = args

    @classmethod
    def factory(cls, args=None, **kwargs):
        """Create a factory that produces UV environments.

        Args:
            args: Arguments to pass to `uv pip install`
            **kwargs: Additional keyword arguments

        Returns:
            A factory function that creates UV environments
        """
        args_list = args if isinstance(args, list) else (args.split() if args else [])

        def create_env(path, name):
            return cls(path, name, args=args_list, **kwargs)

        return create_env

    async def create_venv(self) -> None:
        """Create the virtual python environment.

        Override of the VirtualPythonEnvironment.create_venv method to use uv.
        """
        if self._creator:
            result = self._creator(self.venv)
            if isawaitable(result):
                await result
        elif not self.venv.exists():
            # Create virtual environment
            path = self.venv
            subprocess.check_call([sys.executable, "-m", "venv", str(path)])

            # Get the pip path inside the venv
            if os.name == "nt":  # Windows
                pip_path = path / "Scripts" / "pip"
                python_path = path / "Scripts" / "python"
            else:  # Unix/macOS
                pip_path = path / "bin" / "pip"
                python_path = path / "bin" / "python"

            # Install uv in the virtual environment
            subprocess.check_call([str(pip_path), "install", "uv"])

            # Get the uv path inside the venv
            if os.name == "nt":  # Windows
                uv_path = path / "Scripts" / "uv"
            else:  # Unix/macOS
                uv_path = path / "bin" / "uv"

            # Install the project and dependencies using uv
            cmd = [str(uv_path), "pip", "install"] + self.args
            subprocess.check_call(cmd)

            # Save the python path for the sphinx-builder to use
            self.python_path = python_path

    async def __aenter__(self):
        """Set up the environment."""
        await super().__aenter__()
        return self

    def install_package(self, path):
        """Install a package in the environment.

        Args:
            path: Path to the package to install
        """
        # This is required by VirtualPythonEnvironment but we've already
        # installed everything in create_venv(), so this is a no-op for uv
        pass


# Mapping of revisions to environment parameters
ENVIRONMENT = {
    None: Poetry.factory(args=POETRY_ARGS.split()),  # Default environment
    "v7.1": UvEnv.factory(args=UV_ARGS.split()),  # Use UvEnv for v7.1
}


#: Data passed to templates
def data(driver, rev, env):
    revisions = driver.targets
    branches, tags = refs_by_type(revisions)
    latest = max(tags or branches)
    return {
        "current": rev,
        "tags": tags,
        "branches": branches,
        "revisions": revisions,
        "latest": latest,
    }


def root_data(driver):
    revisions = driver.builds
    branches, tags = refs_by_type(revisions)
    latest = max(tags or branches)
    return {"revisions": revisions, "latest": latest}


# Function to find the closest tag for a given version
def closest_tag(ref: GitRef, available_keys=None) -> "str | None":
    """Find the closest tag for a given version.

    Args:
        ref: Git reference
        available_keys: Available keys in the environment mapping

    Returns:
        The closest tag name that should be used to select the environment
    """
    # For v7.1, use "v7.1", for all other tags, use None (default)
    if ref.name.startswith("v7.1"):
        return "v7.1"
    return None


# Load overrides read from commandline to global scope
apply_overrides(globals())
# Determine repository root directory
root = Git.root(Path(__file__).parent)

# Setup driver and run it
src = Path(SOURCE_DIR)
DefaultDriver(
    root,
    OUTPUT_DIR,
    vcs=Git(
        branch_regex=BRANCH_REGEX,
        tag_regex=TAG_REGEX,
        buffer_size=1 * 10**9,  # 1 GB
        predicate=file_predicate([src]),  # exclude refs without source dir
    ),
    builder=SphinxBuilder(src / "source", args=SPHINX_ARGS.split()),
    env=ENVIRONMENT,  # Use environment mapping to select the right environment
    selector=closest_tag,  # Use the closest_tag function to select the environment
    template_dir=root / src / "templates",
    static_dir=root / src / "static",
    data_factory=data,
    root_data_factory=root_data,
    mock=MOCK_DATA,
).run(MOCK, SEQUENTIAL)

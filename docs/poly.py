from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate, refs_by_type
from sphinx_polyversion.pyvenv import Poetry
from sphinx_polyversion.sphinx import SphinxBuilder

#: Regex matching the branches to build docs for
BRANCH_REGEX = r"rel-.*"  # intentionally broken to skip branches

#: Regex matching the tags to build docs for
TAG_REGEX = r"v7.1|v6.2"

#: Output dir relative to project root
OUTPUT_DIR = "docs/build"

#: Source directory
SOURCE_DIR = "docs/"

#: Arguments to pass to `poetry install`
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
    env=Poetry.factory(args=POETRY_ARGS.split()),
    template_dir=root / src / "templates",
    static_dir=root / src / "static",
    data_factory=data,
    root_data_factory=root_data,
    mock=MOCK_DATA,
).run(MOCK)

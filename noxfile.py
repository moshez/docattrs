import functools
import os

import nox

nox.options.envdir = "build/nox"


@nox.session(python=["3.7", "3.8"])
def tests(session):
    """Run test suite with pytest."""
    tmpdir = session.create_tmp()
    session.install(".[test]")
    tests = session.posargs or ["docattrs.tests"]
    session.run(
        "coverage",
        "run",
        "--branch",
        "--source=docattrs",
        "--omit=*/tests/*,*/_version.py",
        "-m",
        "virtue",
        *tests,
        env=dict(COVERAGE_FILE=os.path.join(tmpdir, "coverage")),
    )
    fail_under = "--fail-under=100"
    session.run(
        "coverage",
        "report",
        fail_under,
        "--show-missing",
        "--skip-covered",
        env=dict(COVERAGE_FILE=os.path.join(tmpdir, "coverage")),
    )


@nox.session(python="3.8")
def lint(session):
    files = ["src/docattrs", "noxfile.py", "setup.py"]
    session.install("-e", ".[lint]")
    session.run("black", "--check", "--diff", *files)
    black_compat = ["--max-line-length=88", "--ignore=E203"]
    session.run("flake8", *black_compat, "src/docattrs")
    session.run(
        "mypy",
        "--disallow-untyped-defs",
        "--warn-unused-ignores",
        "--ignore-missing-imports",
        "src/docattrs",
    )


@nox.session(python="3.8")
def docs(session):
    """Build the documentation."""
    output_dir = os.path.abspath(os.path.join(session.create_tmp(), "output"))
    doctrees, html = map(
        functools.partial(os.path.join, output_dir), ["doctrees", "html"]
    )
    session.run("rm", "-rf", output_dir, external=True)
    session.install(".[doc]")
    sphinx = ["sphinx-build", "-b", "html", "-W", "-d", doctrees, ".", html]

    if session.interactive:
        session.install("sphinx-autobuild")
        sphinx[0:1] = ["sphinx-autobuild", "--open-browser"]

    session.cd("doc")
    session.run(*sphinx)

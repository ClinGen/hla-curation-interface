"""Check that README files mention source code files.

Files and directories listed in the repository's `.gitignore` are skipped,
since the underlying file listing comes from `git ls-files`. Additional
patterns may be excluded via a `.docignore` file in the current working
directory.
"""

import fnmatch
import subprocess
import sys
from pathlib import Path


def list_git_files(directory: Path) -> list[Path]:
    """Return paths of files in `directory` that Git does not ignore.

    Includes both tracked files and untracked files that are not excluded by
    `.gitignore` or other standard exclude mechanisms.

    Args:
        directory: Directory to enumerate, must live inside a Git repo.

    Returns:
        Paths relative to `directory`.
    """
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            str(directory),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    repo_root = subprocess.run(
        ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    root = Path(repo_root)
    directory_abs = directory.resolve()
    paths = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        absolute = (root / line).resolve()
        try:
            paths.append(absolute.relative_to(directory_abs))
        except ValueError:
            continue
    return paths


def load_docignore_patterns() -> list[str]:
    """Read ignore patterns from `.docignore` in the current working directory.

    Blank lines and lines starting with `#` are skipped.

    Returns:
        Patterns in the order they appear in the file. Empty list when no
        `.docignore` file exists.
    """
    docignore = Path.cwd() / ".docignore"
    if not docignore.is_file():
        return []
    patterns = []
    for line in docignore.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        patterns.append(stripped)
    return patterns


def is_ignored(path: Path, patterns: list[str]) -> bool:
    """Return whether `path` matches any of `patterns`.

    A path is considered ignored when its full POSIX-style path matches a
    pattern via `fnmatch.fnmatch`, or any individual path component matches.
    This allows simple names like `migrations` to exclude every file beneath
    a `migrations` directory, while still supporting globs like `*.html` or
    `templates/*/partials/*`.

    Args:
        path: Relative path to test.
        patterns: Patterns loaded from `.docignore`.

    Returns:
        True when the path should be excluded from the mention check.
    """
    posix = path.as_posix()
    for pattern in patterns:
        if fnmatch.fnmatch(posix, pattern):
            return True
        for part in path.parts:
            if fnmatch.fnmatch(part, pattern):
                return True
    return False


def find_unmentioned(files: list[Path], text: str) -> list[Path]:
    """Return the subset of `files` whose names do not appear in `text`.

    A file counts as mentioned if either its basename or its directory-relative
    path appears anywhere in `text`.

    Args:
        files: Paths to check, relative to the searched directory.
        text: Text content to search.

    Returns:
        Files that were not mentioned, preserving input order.
    """
    missing = []
    for path in files:
        if path.name in text or str(path) in text or path.as_posix() in text:
            continue
        missing.append(path)
    return missing


def check_directory(directory: Path, text_file: Path, patterns: list[str]) -> int:
    """Run the mention check for a single directory and text file.

    Args:
        directory: Directory whose Git-tracked files should appear in the text.
        text_file: Text file (typically a `README.md`) to search.
        patterns: Patterns loaded from `.docignore` to exclude from the check.

    Returns:
        Exit code: 0 if every file is mentioned, 1 otherwise.
    """
    files = list_git_files(directory)
    text_file_abs = text_file.resolve()
    directory_abs = directory.resolve()
    files = [
        path for path in files if (directory_abs / path).resolve() != text_file_abs
    ]
    files = [path for path in files if not is_ignored(path, patterns)]
    text = text_file.read_text(encoding="utf-8")
    missing = find_unmentioned(files, text)

    if missing:
        print(f"✗ {directory}")
        print("  Missing files:")
        for path in missing:
            print(f"    {path}")
        return 1

    print(f"✓ {directory}")
    return 0


def main() -> int:
    """Report unmentioned files in each Django app's README.md file.

    Returns:
        Exit code: 0 if every file is mentioned, 1 otherwise.
    """
    dirs = [
        Path("src/allele"),
        Path("src/auth_"),
        Path("src/common"),
        Path("src/config"),
        Path("src/core"),
        Path("src/curation"),
        Path("src/disease"),
        Path("src/haplotype"),
        Path("src/publication"),
        Path("src/repo"),
    ]
    patterns = load_docignore_patterns()
    exit_code = 0
    for directory in dirs:
        readme = directory / "README.md"
        result = check_directory(directory, readme, patterns)
        if result == 1:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

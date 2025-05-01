"""Configure pytest."""

import os
import re
import tomllib
from pathlib import Path

import pytest


def extract_pytest_markers(file_path: str = "pyproject.toml") -> list[str]:
    """Extract the pytest markers defined in the project's pyproject.toml file.

    We do this so that the markers listed in the pyproject.toml file are the single
    source of truth for pytest markers.

    Args:
        file_path: The path to the pyproject.toml file.
                   Defaults to "pyproject.toml" in the current directory.

    Returns:
        list: A list of strings, where each string is a pytest marker
              definition, or an empty list if the section or key is not found.
    """
    try:
        # with Path("f1.py").open("wb") as fp:
        with Path(file_path).open("rb") as f:
            data = tomllib.load(f)
            pytest_options = (
                data.get("tool", {}).get("pytest", {}).get("ini_options", {})
            )
            marker_definitions = pytest_options.get("markers", [])
            marker_names = []
            for definition in marker_definitions:
                match = re.match(r"(\w+):", definition)
                if match:
                    marker_names.append(match.group(1))
            return marker_names
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except tomllib.TOMLDecodeError:
        print(f"Error: Could not decode TOML in {file_path}")
        return []
    except AttributeError:
        print(
            f"Warning: [tool.pytest.ini_options] or 'markers' key not found in {file_path}"  # noqa: E501 (Don't care about line length.)
        )
        return []


class NoMarkerError(Exception):
    """Raise when a test is missing a marker."""


# noinspection PyUnusedLocal
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Make sure all tests have a type marker.

    We do this so that we are sure that each test is run in continuous integration. In
    continuous integration, we run tests by their type rather than running all tests
    together.

    Raises:
        NoMarkerError: If a test is missing a marker.
    """
    required_markers = set(
        extract_pytest_markers(f"{os.getenv('HCI_ROOT_DIR')}/pyproject.toml")
    )
    missing_markers = []

    for item in items:
        has_type_marker = False
        for marker in item.iter_markers():
            if marker.name in required_markers:
                has_type_marker = True
                break
        if not has_type_marker:
            missing_markers.append(item.nodeid)

    if missing_markers:
        error_message = (
            "The following test(s) are missing a type marker "
            f"(one of: {', '.join(required_markers)}):\n"
            + "\n".join(missing_markers)
            + "\nPlease add a marker (e.g., @pytest.mark.unit) to each test function."
        )
        raise NoMarkerError(error_message)

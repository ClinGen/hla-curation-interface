import sys
from pathlib import Path

sys.path.insert(0, str(Path("..", "..", "src").resolve()))

project = "HCI"
copyright = "Clinical Genome Resource"
author = "The Stanford ClinGen Team"
release = "0.1"
version = "0.1.0"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"
html_title = "HCI Dev Docs"
html_static_path = ["_static"]

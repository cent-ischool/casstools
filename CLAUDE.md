# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

casstools is a Python client library for CASS (Course Assignment Submission System). It runs within JupyterHub environments and provides:
- Notebook checking/validation for labs and homework assignments
- Assignment submission to the CASS REST API server
- Interactive self-check quizzes rendered in Jupyter notebooks

## Architecture

### Core Components

**CassClient** (`cass_client.py`): REST API client for the CASS server. Handles authentication via `JUPYTERHUB_API_TOKEN` header. Manages courses, rosters, assignments, and submissions.

**Assignment** (`assignment.py`): Orchestrates the submission workflow - validates user enrollment, checks assignment registration, handles late submissions, logs submissions locally.

**NotebookFile** (`notebook_tools.py`): Reads Jupyter notebooks and validates them against metadata-based requirements. Uses cell metadata (under `['metadata']['cass']` or legacy `['metadata']`) to identify:
- Cell types: `code_cell_type` (write_code, debug_code, run_code)
- Labels: `label` (comfort_cell, question_cell, etc.)
- Solutions: `solution` metadata for code similarity checking

**PathParser** (`path_parser.py`): Parses notebook file paths to extract course, term, and assignment info. Expected path format: `/home/jovyan/library/{course}/{term}/lessons/{lesson}/{assignment}.ipynb`

**code_tools** (`code_tools.py`): Utilities for syntax checking (via py_compile), code similarity (via pycode_similar), and code execution with stdin redirection.

**interact_quiz** (`interact_quiz.py`): Renders interactive quizzes from JSON files using ipywidgets. Supports multiple_choice, many_choice, and numeric question types.

### Key Metadata Conventions

Notebooks use cell metadata to drive validation:
- Homework requires: analysis_output_cell, analysis_input_cell, analysis_plan_cell, learned_cell, challenges_cell, prepared_cell, help_cell, comfort_cell
- Labs require: exercise code cells (write_code/debug_code), run_code cells, comfort_cell, question_cell
- Code cells can have `solution` metadata for similarity checking and `tests` metadata for automated testing

### Dependencies

- `nbformat`: Reading Jupyter notebooks
- `ipylab`: JupyterFrontEnd for autosave
- `ipynb_path`: Getting current notebook path
- `pycode_similar`: Code similarity detection
- `git`: Git repository operations
- `ipywidgets`: Interactive quiz rendering

## Running Tests

Individual modules have `if __name__ == '__main__':` test blocks. Run directly:
```bash
python course_model.py
python path_parser.py
python cass_client.py
```

## Environment Variables

- `CASS_URL`: API server URL (default: http://api:8000)
- `JUPYTERHUB_API_TOKEN`: Authentication token
- `HOME`: User home directory (default: /home/jovyan)

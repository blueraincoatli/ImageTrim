# Repository Guidelines

## Project Structure & Module Organization
- `core/` hosts foundational services such as `base_module.py`, `config.py`, and dependency injection helpers. Extend `BaseModule` when introducing new functionality.
- Feature plug-ins belong in `modules/<feature>/` and should bundle `module.py`, `ui.py`, and `logic.py` to satisfy the function manager contract.
- Presentation logic lives in `ui/` (panels, components, themes); reuse shared widgets in `ui/components/` and keep business helpers in `utils/`.
- Static assets stay under `resources/` (`resources/icons/` for ICO/SVG, `resources/images/` for previews). Avoid committing large datasets—link to external samples instead.
- `main.py` is the application entry point, with `start.bat`/`start.sh` wrapping platform-specific launch prerequisites.

## Build, Test, and Development Commands
- `python -m venv .venv` then activate it (`.\\.venv\\Scripts\\activate` on Windows, `source .venv/bin/activate` on Unix) to isolate dependencies.
- `pip install -r requirements.txt` installs runtime packages; rerun after adding Pillow/ImageHash updates.
- `python main.py` runs the desktop app; on Windows prefer `start.bat` so Qt DLL paths resolve correctly. Linux/macOS contributors can use `./start.sh` after `chmod +x`.
- `pytest` is the designated test runner once suites are added; keep fast smoke checks focused on module logic and guard long GUI tests with markers.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, expressive type hints, and module-level docstrings that describe each component’s role in the plugin system.
- Name modules and packages with `snake_case`, classes with `PascalCase`, functions and signals with descriptive `snake_case`, and theme/asset files with hyphenated descriptors (e.g., `dark-theme.qss`).
- Export public APIs intentionally (`__all__` or factory helpers) and keep cross-module communication flowing through `core.function_manager` services.

## Testing Guidelines
- Target deterministic unit tests around each module’s `logic.py`. Use `pytest-qt` fixtures to exercise PyQt widgets and isolate filesystem interactions with `tmp_path`.
- Mirror source paths in `tests/` (e.g., `tests/deduplication/test_logic.py`) and adopt `test_<behavior>.py` filenames. Flag slow or UI-heavy tests with markers so they can be skipped in CI smoke runs.
- Manual QA remains essential: launch via `start.bat`/`start.sh`, confirm modules register in the function panel, and verify long tasks keep the UI responsive.

## Commit & Pull Request Guidelines
- Write commit subjects under 72 characters in imperative mood, matching existing history (e.g., "Improve welcome screen image fallback"). Include concise multi-language bodies when helpful.
- Squash incidental WIP commits before opening a PR. Reference related issues, describe functional/UI impacts, list manual or automated checks, and add screenshots or GIFs when UI changes are visible.
- Update `requirements.txt` for new dependencies and capture user-facing changes in `README.md` or release notes before requesting review.

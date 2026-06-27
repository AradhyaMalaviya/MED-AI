# Repository Guidelines

## Project Structure & Module Organization

The runnable product is `medicare-ai-mobile-app-prototype.html`, a self-contained mobile web prototype. It keeps markup, CSS, embedded prediction data, and JavaScript in one file; Google Fonts is the only external browser dependency. `documentationsforthisproject/` contains requirements, architecture notes, plans, and status documents for the wider MediCare AI concept. Those documents mention Flask, Python, and ML artifacts that are not included in this repository snapshot, so verify claims against the root HTML before changing the prototype.

## Build, Test, and Development Commands

No package installation or build step is required. From the repository root, run:

```powershell
python -m http.server 8000
Start-Process "http://localhost:8000/medicare-ai-mobile-app-prototype.html"
```

The first command serves the prototype locally; the second opens it on Windows. Directly opening the HTML file also works, but a local server better matches browser deployment. Use `rg -n "<style>|<script>" medicare-ai-mobile-app-prototype.html` to locate the main inline sections.

## Coding Style & Naming Conventions

Preserve the existing two-space indentation, semicolons, and dependency-free JavaScript style. Use `camelCase` for JavaScript variables and functions, `UPPER_SNAKE_CASE` for constant lookup data, camelCase DOM IDs (for example, `themeToggleBtn`), and kebab-case CSS classes. Reuse the CSS custom properties in `:root` instead of adding isolated color or spacing values. Keep DOM IDs synchronized with every `querySelector` reference. Avoid manually reformatting the large `MODEL_GRID_DB` data block unless its values change.

## Testing Guidelines

There is no automated test suite or coverage target. Before submitting, test in a browser at desktop and the `460px` mobile breakpoint. Complete onboarding and the symptom wizard, inspect results and medicines, add/delete history, reload to verify `localStorage`, book/cancel an appointment, switch themes, restart, and confirm the console has no errors. Clear test data with `localStorage.clear()` in DevTools when needed.

## Security & Product Safety

Do not add real patient data, secrets, or analytics identifiers. History and appointments are stored in browser `localStorage`; preserve clear-data controls and the medical-information disclaimer. Treat recommendations as prototype content, not clinical advice.

## Commit & Pull Request Guidelines

No `.git` directory or commit history is present, so no established convention can be inferred. Use short, imperative messages such as `Fix appointment cancellation` or `Refine mobile result layout`. Pull requests should summarize behavior changes, list manual checks, link relevant requirements, and include before/after screenshots for visible UI changes.

# Contributing to TrackIQ Backend

To ensure code quality and system stability, we follow strict CI/CD guidelines:

### 🚀 Branching Strategy
1. Always create a new branch from `main` (e.g., `feature/your-feature`).
2. Never push directly to `main`.

### ✅ Pull Request Rules
- **At least 1 approval** is required from a CODEOWNER before merging.
- All **CI Status Checks** (Linting & Tests) must pass.
- After approval and passing checks, use **Squash and Merge**.

### 🛠️ Local Development
Run linting and tests before pushing:
```bash
ruff check .
pytest tests/
```

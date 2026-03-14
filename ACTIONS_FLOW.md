Developer machine
      │
      ├── writes code
      │
      ├── git commit
      │     └── pre-commit hooks fire BEFORE commit is created
      │           ├── trailing whitespace / EOF fixes
      │           ├── ruff --fix + ruff format  (fixes in place)
      │           ├── mypy (type check)
      │           └── if anything fails → commit is BLOCKED, fix and retry
      │
      └── git push → branch (feature/fix/etc)
            │
            ▼
      GitHub PR opened
            │
            ├── CI runs on the PR
            │     ├── commit-style (commitlint)
            │     ├── test (ruff check, pytest, coverage) × 4 Python versions
            │     └── build (wheel + sdist)
            │
            ├── all green ✅ → PR can be merged
            │
            └── merge to master
                  │
                  └── CI runs again on master push
                        └── same jobs, final verification
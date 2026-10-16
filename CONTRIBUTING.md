# Contributing

## Releases

Releases are automated with python-semantic-release. Merging to `main` publishes a new
PyPI version based on the PR title, which must follow
[Conventional Commits](https://www.conventionalcommits.org) (a CI check enforces it):
`fix:` → patch, `feat:` → minor, `feat!:` or a `BREAKING CHANGE:` footer → major.
`chore:`, `docs:`, `ci:`, `refactor:`, `test:` don't release. Don't edit `version` in
`pyproject.toml`; the release job sets it at publish time.

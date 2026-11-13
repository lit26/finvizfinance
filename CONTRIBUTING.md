# Contributing to finvizfinance
We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## We Develop with Github
We use github to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests
Pull requests are the best way to propose changes to the codebase (we use [Github Flow](https://guides.github.com/introduction/flow/index.html)). We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](https://github.com/lit26/finvizfinance/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can. 
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Local development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
ruff check . && ruff format --check .
pytest                      # offline suite, no network
mypy                        # config lives in pyproject.toml
coverage run -m pytest && coverage report -m
```

`pytest` runs entirely against HTML snapshots in `tests/fixtures/`, so it is
fast and safe to run offline. A Cloudflare block or a finviz markup change will
never make it flaky.

## Refreshing fixtures

Finviz changes its markup regularly. When a parser test fails because the
window changed, refresh the snapshots instead of hand-editing HTML:

```bash
python scripts/refresh_fixtures.py            # uncurated live snapshots -> tests/fixtures/live/
python scripts/refresh_fixtures.py --help     # available options
```

The curated, minimal fixtures the unit suite asserts against live in
`tests/fixtures/`. Trim a refreshed snapshot down to the markup a single
assertion needs before committing it, so tests stay readable. Full-page live
snapshots under `tests/fixtures/live/` are the reference for what the current
site actually returns.

A scheduled `live-smoke` workflow runs against the real site weekly and files an
issue automatically when it detects drift, so a markup change is noticed even
when nobody is looking.

## Releasing

1. Bump `__version__` in `finvizfinance/__init__.py`.
2. Add a row to `CHANGELOG.md` (newest first) linking the issues and PRs.
3. Draft a GitHub Release for the new tag — publishing it triggers
   `publish.yml`, which builds and uploads to PyPI via Trusted Publishing
   (OIDC, no stored token). Nothing is published until that release is
   published.

## Coding Style
Please follow [Python PEP 8](https://google.github.io/styleguide/pyguide.html)

`ruff check` and `ruff format --check` are enforced in CI, and `mypy` runs
against `finvizfinance/` and `scripts/` with `disallow_untyped_defs`, so new
code needs type hints.

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## References
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
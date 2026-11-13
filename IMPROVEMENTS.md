# Repo Improvement Backlog

Status after the `chore/repo-improvements` pass. Items marked **already done** were
re-checked against the repo and needed no change — the first audit read the CI
config only up to the first job.

---

## Done in this pass

| # | Item | Change |
|---|------|--------|
| 1.1 | Untracked build/report artifacts | Deleted `__pycache__/runtest.cpython-37-pytest-6.2.2.pyc`, root `Industry.jpg`, root `tsla.jpg` (none referenced). `__pycache__/` was already gitignored. |
| 1.2 | Unused `example/` images | Dropped `example/audusd_d1_s.jpg`, `example/btcusd_m5_s.jpg`, `example/tsla.jpg` (notebook output artifacts, nothing links to them). `example/example.ipynb` kept. |
| 1.3 | No changelog | `release.md` renamed to `CHANGELOG.md`, headed, and linked from `[project.urls]` as `Changelog`. |
| 2.1 | `xlsxwriter` was a hard dependency | Moved to the `finvizfinance[excel]` extra; `Earnings.output_excel` imports it lazily and raises `ImportError` with the install hint. `[test]` pulls the extra so CI still exercises the export. Two tests added: real workbook write, and the missing-extra path. |
| 2.3 | Missing Typed classifier | Added `Typing :: Typed` — the package ships `py.typed`. |
| 4.2 | No dependency automation | Added `.github/dependabot.yml` (weekly, GitHub Actions + pip). Pinned all `actions/*` uses to commit SHAs with a `# v4`/`# v5` version comment. |
| 4.4 | Python 3.14 untested | Added to the CI matrix as advisory (`continue-on-error`) until every dependency ships 3.14 wheels. |
| 5.2 | Fixture workflow undocumented | `CONTRIBUTING.md` now covers local setup, why the suite is offline, `scripts/refresh_fixtures.py`, and the release steps. |
| 6.1 | `test/` vs `tests/` | Renamed `test/` to `tests/`; updated `pytest.ini`, both CI invocations, and the `refresh_fixtures.py` output path. |
| 6.2 | No review/triage policy | Added `.github/CODEOWNERS` and a weekly `stale.yml` (comments at 60 days, closes at 81, exempts pinned/security/milestone issues). |

## Already in place (audit was wrong)

| # | Item | Reality |
|---|------|---------|
| 2.2 | Drop `lxml` | Still needed — every parse goes through `BeautifulSoup(..., "lxml")` (`finvizfinance/util.py`). |
| 3.1 | mypy not in CI | `types` job already runs bare `mypy` against `disallow_untyped_defs`. Clean: 33 files, no issues. |
| 3.2 | No coverage gate | `coverage` job exists and `[tool.coverage.report] fail_under = 86`. Current coverage 89%. |
| 4.3 | Drift detection loop open | `live-smoke.yml` already files or comments on a `live-smoke-drift` issue when the scheduled run fails. |
| 5.1 | Options chain undocumented | `docs/source/quote.rst` is `automodule :members:`, so `ticker_options`'s docstring is already published. |

## Fixed opportunistically

- `docs/source/index.rst` claimed `python >= 3.9`; it is `>=3.10`.
- Sphinx warned about a missing `_static` directory on every build; `html_static_path` is now empty. Docs build warning-free.
- `README.md` Excel export example now notes the optional extra.

## Still open

| # | Item | Why not done |
|---|------|--------------|
| 3.3 | Module-level mutable HTTP state | `util.session`, `timeout_value`, `proxy_dict` are process globals — not thread-safe, and one caller's `set_proxy` leaks into every other caller. Fixing it properly means threading a client object through every class and is a breaking API change for `set_session`/`set_proxy` users. Needs an explicit decision. |
| 4.1 | Automated PyPI publish | `publish.yml` is correct but the PyPI pending publisher still has to be registered once by the account owner (GitHub Actions · `lit26/finvizfinance` · `publish.yml` · environment `pypi`). Not something a repo change can do. |

## Known limits

- Python 3.14 CI is advisory only; remove `continue-on-error` once the matrix is green on its own.
- `pypa/gh-action-pypi-publish` stays on the moving `release/v1` ref — upstream publishes no tag ref to pin (only a `release/v1` branch).

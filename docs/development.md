# Development

## Testing

When updating any files within the MeshiPhi repository, tests must be run to ensure that the core functionality of the software remains unchanged.

To allow for validation of changes, a suite of regression tests have been provided in the folder ``tests/regression_tests/...``.

These tests attempt to rebuild existing test cases using the changed code and compares these rebuilt outputs to the reference test files.

To run tests:

`pytest`

If you use [uv](https://docs.astral.sh/uv/), set up the environment and run the tests with:

```sh
uv sync --group test
uv run pytest
```

To run tests in parallel (faster):

`pytest -n auto`

To avoid running slow tests:

`pytest -m "not slow"`

To run only slow tests:

`pytest -m slow`

## Documentation

Documentation is built from the `docs/` directory using `mkdocs` and plugins.

To install the docs dependencies, from the project root run `pip install --group docs` in your virtual environment, or with uv run `uv sync --group docs` and then `uv run mkdocs serve`.

To serve the docs locally, run `mkdocs serve`.

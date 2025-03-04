# integration-tests

This directory contains integration tests for the `engine` project.

## Running the tests

To run the tests, execute the following command:

```bash
uv sync -U
./env_setup/scripts/generate-env.sh
./env_setup/scripts/start.sh
export PYTHONPATH=<path_to_intergation-tests>/src  # example: ~/PycharmProjects/integration-tests/src
uv run pytest
./env_setup/scripts/stop.sh
```

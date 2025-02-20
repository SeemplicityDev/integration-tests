# integration-tests

This directory contains integration tests for the `engine` project.

## Running the tests

To run the tests, execute the following command:

```bash
uv sync -U
./env_setup/scripts/generate-env.sh
./env_setup/scripts/start.sh
export PYTHONPATH=~/PycharmProjects/intergation_tests
uv run pytest
./env_setup/scripts/stop.sh
```

## GraphBench

How effective are large language models at graph compression?

## Setup

`uv sync` : )

## Generate Stuff

`uv run generate_eval_data.py`

## See Stuff

To visualize the dataset, run `uv run visualization/visualize_dataset.py` and go to `http://127.0.0.1:5000`

To visualize the evals, run `uv run visualization/visualize_results.py`. Images are saved to `visualization/graph/`.


## Run Eval

Set `OPENAI_API_KEY` in your environment (or in the `.env` file), then:

`uv run run_eval.py`

First look in the file and set the config you want.

## Testing

`uv run pytest .` (why would you do this?)

## Report

[REPORT.md](./REPORT.md)
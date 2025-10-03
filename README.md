## GraphGolfingBench

Golfing the graph

## Setup

`uv sync` : )

## Generate Stuff

`uv run generate_eval_data.py`

## See Stuff

To visualize the dataset, run `uv run visualization/visualize_dataset.py` and go to `http://127.0.0.1:5000`

To visualize the evals, run `uv run visualization/visualize_results.py`. Images are saved to `visualization/graph/`.


## Run Eval

Set the `OPENAI_API_KEY`, then:

`uv run run_eval.py`

First look in the file and set the config you want.

## Testing

`uv run pytest .` (why?)

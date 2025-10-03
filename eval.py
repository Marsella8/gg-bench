from dataclasses import dataclass
import json

from dsl.graph_dsl import Graph, GRAPH_DSL
from dsl.utils import from_adjacency_matrix, are_graphs_equal
from dsl.dsl import parse_program, get_program_cost
from utils import (
    construct_prompt,
    parse_response,
    log_result,
    batch_request,
    ChatResult,
    Sample,
)


@dataclass
class InvalidDSL:
    sample: Sample
    sample_index: int
    response: ChatResult
    error: str


@dataclass
class IncorrectReconstruction:
    sample: Sample
    sample_index: int
    generated_graph: Graph
    response: ChatResult


@dataclass
class Success:
    sample: Sample
    sample_index: int
    generated_graph: Graph
    generated_cost: int
    response: ChatResult


@dataclass
class Config:
    model: str
    reasoning_effort: str
    num_samples: int


Result = Success | IncorrectReconstruction | InvalidDSL


@dataclass
class SampleResults:
    sample: Sample
    responses: list[Result]


def evaluate_chat_result(
    response: ChatResult,
    sample: Sample,
    sample_index: int,
    expected_graph: Graph,
) -> Result:
    import linecache

    code = parse_response(response.content)

    dsl_env: dict[str, object] = {fn.__name__: fn for fn in GRAPH_DSL.functions}
    dsl_env.update({"Graph": Graph})

    filename = f"<compress:{sample.name}>"
    code_str = code if code.endswith("\n") else code + "\n"
    linecache.cache[filename] = (
        len(code_str),
        None,
        code_str.splitlines(True),
        filename,
    )

    try:
        exec(
            compile(code_str, filename=filename, mode="exec"),
            dsl_env,
        )
    except Exception as e:
        return InvalidDSL(
            sample=sample,
            sample_index=sample_index,
            response=response,
            error=str(e),
        )

    try:
        compress = dsl_env["compress"]
        if not callable(compress):
            raise KeyError("compress is not callable")
    except KeyError:
        return InvalidDSL(
            sample=sample,
            sample_index=sample_index,
            response=response,
            error="compress_not_defined",
        )

    try:
        program = parse_program(compress)
        generated_cost = get_program_cost(program)
    except Exception as e:
        return InvalidDSL(
            sample=sample,
            sample_index=sample_index,
            response=response,
            error=str(e),
        )

    try:
        generated_graph = compress()
    except Exception as e:
        return InvalidDSL(
            sample=sample,
            sample_index=sample_index,
            response=response,
            error=str(e),
        )

    is_correct = are_graphs_equal(generated_graph, expected_graph)
    if is_correct:
        return Success(
            sample=sample,
            sample_index=sample_index,
            generated_graph=generated_graph,
            generated_cost=generated_cost,
            response=response,
        )

    return IncorrectReconstruction(
        sample=sample,
        sample_index=sample_index,
        generated_graph=generated_graph,
        response=response,
    )


def run_evaluation(
    config: Config, samples: list[Sample], skip_if_exists: bool = False
) -> list[SampleResults]:
    expected_graphs: list[Graph] = []
    flattened_prompts: list[str] = []
    index_map: list[int] = []

    for i, s in enumerate(samples):
        matrix = s.adjacency_matrix
        expected_graphs.append(from_adjacency_matrix(matrix))
        system_prompt, user_prompt = construct_prompt(graph=json.dumps(matrix))
        for _ in range(config.num_samples):
            flattened_prompts.append(user_prompt)
            index_map.append(i)

    responses = batch_request(
        system_prompt,
        flattened_prompts,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
    )

    grouped: list[list[Result]] = [[] for _ in samples]
    for resp, sample_idx in zip(responses, index_map):
        s = samples[sample_idx]
        eg = expected_graphs[sample_idx]
        r = evaluate_chat_result(resp, s, sample_idx, eg)
        grouped[sample_idx].append(r)
        log_result(
            config.model,
            config.reasoning_effort,
            r,
            skip_if_exists=skip_if_exists,
            status=type(r),
        )

    sample_results: list[SampleResults] = [
        SampleResults(sample=s, responses=grouped[i]) for i, s in enumerate(samples)
    ]
    return sample_results

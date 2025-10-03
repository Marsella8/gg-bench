from dataclasses import dataclass, asdict, is_dataclass
import json
from typing import Any
from pathlib import Path
import re

from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import asyncio
from tqdm import tqdm

load_dotenv()


@dataclass
class Usage:
    prompt_tokens: int
    reasoning_tokens: int
    response_tokens: int
    total_completion_tokens: int
    total_tokens: int


@dataclass
class ChatResult:
    model: str
    content: str
    finish_reason: str
    usage: Usage
    id: str
    reasoning: str | None = None


def _to_chat_result(response) -> ChatResult:
    choice = response.choices[0]
    content = choice.message.content
    finish_reason = choice.finish_reason
    reasoning = getattr(choice.message, "reasoning", None) or getattr(
        response, "reasoning", None
    )

    prompt_tokens = response.usage.prompt_tokens
    total_completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    reasoning_tokens = (
        getattr(response.usage.completion_tokens_details, "reasoning_tokens", 0)
        if hasattr(response.usage, "completion_tokens_details")
        else 0
    )
    response_tokens = total_completion_tokens - reasoning_tokens

    usage = Usage(
        prompt_tokens=prompt_tokens,
        reasoning_tokens=reasoning_tokens,
        response_tokens=response_tokens,
        total_completion_tokens=total_completion_tokens,
        total_tokens=total_tokens,
    )

    return ChatResult(
        model=response.model,
        content=content,
        finish_reason=finish_reason,
        usage=usage,
        id=response.id,
        reasoning=reasoning,
    )


def single_request(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str = "gpt-5-2025-08-07",
    temperature: float = 1.0,
    reasoning_effort: str = "minimal",
) -> ChatResult:
    client = OpenAI()

    if reasoning_effort:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            reasoning_effort=reasoning_effort,
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

    return _to_chat_result(response)


def batch_request(
    system_prompt: str,
    user_prompts: list[str],
    *,
    model: str,
    reasoning_effort: str,
    temperature: float = 1.0,
    stagger_seconds: float = 1.0,
) -> list[ChatResult]:
    async def _run_batch() -> list[ChatResult]:
        client = AsyncOpenAI()

        async def _request(index: int, user_prompt: str):
            snippet = (user_prompt or "").strip().replace("\n", " ")[:80]
            total = len(user_prompts)
            try:
                if reasoning_effort:
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=temperature,
                        reasoning_effort=reasoning_effort,
                    )
                else:
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=temperature,
                    )
                return index, response
            except Exception as e:
                raise

        async def _delayed_request(index: int, user_prompt: str):
            delay = max(0.0, float(stagger_seconds)) * index
            if delay > 0:
                from asyncio import sleep

                await sleep(delay)
            return await _request(index, user_prompt)


        tasks = [_delayed_request(i, up) for i, up in enumerate(user_prompts)]
        total = len(tasks)
        responses_by_index: list = [None] * total
        from asyncio import as_completed

        with tqdm(total=total, desc="batch", leave=True) as pbar:
            for fut in as_completed(tasks):
                idx, resp = await fut
                responses_by_index[idx] = resp
                pbar.update(1)
        return [_to_chat_result(r) for r in responses_by_index]

    return asyncio.run(_run_batch())


def load_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def construct_prompt(**kwargs) -> tuple[str, str]:
    root = Path(__file__).resolve().parent
    system_path = root / "dsl" / "system_prompt.txt"
    user_path = root / "dsl" / "user_prompt.txt"
    system_prompt = system_path.read_text()
    user_prompt = user_path.read_text()
    return system_prompt, user_prompt.format(**kwargs)


def parse_response(response: str) -> Any:
    text = response.strip()

    pattern = r"```(?:python)?\s*([\s\S]*?)```"
    blocks = [m.group(1).strip() for m in re.finditer(pattern, text, re.MULTILINE)]

    code = ""
    if blocks:
        for blk in blocks:
            if "def compress" in blk:
                code = blk
                break
        if not code:
            code = blocks[0]
    else:
        idx = text.find("def compress")
        code = text[idx:].strip() if idx != -1 else text

    return code if code.endswith("\n") else code + "\n"


@dataclass
class Sample:
    name: str
    adjacency_matrix: list[list[int]]
    dsl_cost: int
    naive_cost: int
    compression_ratio: float
    code: str


def get_samples() -> list[Sample]:
    samples: list[Sample] = []
    root = Path(__file__).resolve().parent
    data_dir = root / "data"
    for path in data_dir.iterdir():
        data = load_json(str(path))
        samples.append(Sample(**data))
    assert len(samples) > 0, f"No samples found in {data_dir}"
    return samples


def log_result(
    model_name: str,
    reasoning_effort: str,
    result: Any,
    status: type[Any],
    *,
    skip_if_exists: bool = False,
) -> None:
    root = Path(__file__).resolve().parent
    dir_name = f"{model_name}__{reasoning_effort}" if reasoning_effort else model_name
    out_dir = root / "results" / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = (asdict(result) if is_dataclass(result) else vars(result).copy()) | {
        "status": status.__name__
    }
    name = payload["sample"]["name"]
    out_path = out_dir / f"{name}.json"
    if skip_if_exists and out_path.exists():
        return
    save_json(str(out_path), payload)

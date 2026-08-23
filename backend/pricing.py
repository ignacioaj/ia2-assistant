import logging
import os

from dotenv import load_dotenv

load_dotenv()

MAXIMUM_DAILY_COST_PER_USER = float(
    os.getenv("MAXIMUM_DAILY_COST_PER_USER", "0.05")
)

TOKENS_PER_PRICE = 1_000_000

PRICING = {
    "gpt-5.4-mini": {
        "input": 0.75,
        "output": 4.50,
        "cached_input": 0.075,
    }
}


logger = logging.getLogger("career-twin")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )
    logger.addHandler(handler)


def calculate_cost(
    model,
    input_tokens,
    output_tokens,
    cached_input_tokens=0,
):
    pricing = PRICING[model]

    cached_input_tokens = min(cached_input_tokens, input_tokens)
    uncached_input_tokens = input_tokens - cached_input_tokens

    input_cost = (
        uncached_input_tokens * pricing["input"]
        + cached_input_tokens * pricing["cached_input"]
    ) / TOKENS_PER_PRICE

    output_cost = (
        output_tokens * pricing["output"]
    ) / TOKENS_PER_PRICE

    return input_cost + output_cost


def log_usage(model, usage):
    if not usage:
        return 0

    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens

    cached_input_tokens = (
        usage.input_tokens_details.cached_tokens
        if usage.input_tokens_details
        else 0
    )

    cost = calculate_cost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached_input_tokens,
    )

    uncached_input_tokens = input_tokens - cached_input_tokens

    logger.info(
        "usage | model=%s | input-tokens=%s | cached-tokens=%s | "
        "uncached-tokens=%s | output-tokens=%s | total-tokens=%s | "
        "total-cost=$%.6f",
        model,
        input_tokens,
        cached_input_tokens,
        uncached_input_tokens,
        output_tokens,
        usage.total_tokens,
        cost,
    )

    return cost
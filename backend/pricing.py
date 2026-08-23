import logging

MAXIMUM_DAILY_COST_PER_USER = 0.05
TOKENS_PER_PRICE = 1_000_000

PRICING = {
    "gpt-5.4-mini": {
        "input": 0.75,
        "output": 4.50,
        "cached_input": 0.075,
    }
}

logger = logging.getLogger("career-twin")

def calculate_cost(model, input_tokens, output_tokens):
    pricing = PRICING[model]

    input_cost = input_tokens * pricing["input"] / TOKENS_PER_PRICE
    output_cost = output_tokens * pricing["output"] / TOKENS_PER_PRICE

    return input_cost + output_cost


def log_usage(model, usage):
    if not usage:
        return 0

    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    total_tokens = usage.total_tokens

    cost = calculate_cost(
        model,
        input_tokens,
        output_tokens,
    )

    logger.info(
        "usage | model=%s | input=%s | output=%s | total=%s | cost=$%.6f",
        model,
        input_tokens,
        output_tokens,
        total_tokens,
        cost,
    )

    return cost
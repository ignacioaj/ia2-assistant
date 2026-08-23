import logging


logger = logging.getLogger("career-twin")

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

logger.addHandler(handler)
logger.propagate = False


PRICING = {
    "gpt-5.4-mini": {
        "input": 0.75,
        "output": 4.50,
        "cached_input": 0.075,
    }
}

TOKENS_PER_PRICE = 1_000_000


def calculate_cost(model, input_tokens, output_tokens):
    pricing = PRICING[model]

    input_cost = (
        input_tokens * pricing["input"] / TOKENS_PER_PRICE
    )

    output_cost = (
        output_tokens * pricing["output"] / TOKENS_PER_PRICE
    )

    return input_cost + output_cost


def log_usage(model, usage):
    if not usage:
        return

    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    total_tokens = usage.total_tokens

    cost = calculate_cost(
        model,
        input_tokens,
        output_tokens,
    )

    logger.info(
        "usage | model=%s | input-tokens=%s | output-tokens=%s | total-tokens=%s | cost=$%.6f",
        model,
        input_tokens,
        output_tokens,
        total_tokens,
        cost,
    )
import os
from datetime import datetime, timezone, timedelta
from backend.database.database import db

from dotenv import load_dotenv

load_dotenv()

MAXIMUM_DAILY_COST_PER_USER = os.getenv(
    "MAXIMUM_DAILY_COST_PER_USER"
)

if not MAXIMUM_DAILY_COST_PER_USER:
    raise RuntimeError(
        "MAXIMUM_DAILY_COST_PER_USER is not configured"
    )

try:
    MAXIMUM_DAILY_COST_PER_USER = float(
        MAXIMUM_DAILY_COST_PER_USER
    )
except ValueError:
    raise RuntimeError(
        "MAXIMUM_DAILY_COST_PER_USER must be a number"
    )

token_usage_collection = db["token_usage"]


def save_token_usage(
    ip,
    input_tokens,
    output_tokens,
    total_tokens,
    cost,
):
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    # ---------------------------------------------------------
    # Try to create the document if this is the first request
    # from this IP.
    # ---------------------------------------------------------

    blocked_until = (
        now + timedelta(hours=24)
        if cost >= MAXIMUM_DAILY_COST_PER_USER
        else None
    )

    document = {
        "_id": ip,
        "daily": {
            "date": today,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
        },
        "last_query": now,
        "blocked_until": blocked_until,
    }

    try:
        token_usage_collection.insert_one(document)
        return
    except Exception as exc:
        # Another request may have created the document
        # concurrently. In that case we continue and update it.
        if "duplicate key" not in str(exc).lower():
            raise

    # ---------------------------------------------------------
    # New day
    #
    # Replace the complete daily object atomically.
    # ---------------------------------------------------------

    result = token_usage_collection.update_one(
        {
            "_id": ip,
            "daily.date": {"$ne": today},
        },
        {
            "$set": {
                "daily": {
                    "date": today,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "cost": cost,
                },
                "last_query": now,
                "blocked_until": (
                    now + timedelta(hours=24)
                    if cost >= MAXIMUM_DAILY_COST_PER_USER
                    else None
                ),
            }
        },
    )

    if result.modified_count:
        return

    # ---------------------------------------------------------
    # Same day
    #
    # Increment the daily values atomically.
    # ---------------------------------------------------------

    new_total_cost = token_usage_collection.find_one(
        {"_id": ip},
        {"daily.cost": 1},
    )["daily"]["cost"] + cost

    update = {
        "$inc": {
            "daily.input_tokens": input_tokens,
            "daily.output_tokens": output_tokens,
            "daily.total_tokens": total_tokens,
            "daily.cost": cost,
        },
        "$set": {
            "last_query": now,
        },
    }

    if new_total_cost >= MAXIMUM_DAILY_COST_PER_USER:
        update["$set"]["blocked_until"] = (
            now + timedelta(hours=24)
        )

    token_usage_collection.update_one(
        {
            "_id": ip,
            "daily.date": today,
        },
        update,
    )


def is_usage_blocked(ip):
    now = datetime.now(timezone.utc)

    user_data = token_usage_collection.find_one({
        "_id": ip,
    })

    if not user_data:
        return False

    blocked_until = user_data.get("blocked_until")

    if not blocked_until:
        return False

    if blocked_until.tzinfo is None:
        blocked_until = blocked_until.replace(
            tzinfo=timezone.utc
        )

    if now >= blocked_until:
        token_usage_collection.update_one(
            {"_id": ip},
            {
                "$unset": {
                    "blocked_until": ""
                }
            },
        )

        return False

    return True
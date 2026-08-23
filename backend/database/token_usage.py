import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from pymongo import ReturnDocument

from backend.database.database import db


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
except ValueError as exc:
    raise RuntimeError(
        "MAXIMUM_DAILY_COST_PER_USER must be a number"
    ) from exc


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
    # Get current document
    # ---------------------------------------------------------

    user_data = token_usage_collection.find_one(
        {"_id": ip},
        {
            "daily": 1,
            "blocked_until": 1,
        },
    )

    # ---------------------------------------------------------
    # First request from this IP
    # ---------------------------------------------------------

    if user_data is None:
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
            # between find_one() and insert_one().
            if "duplicate key" not in str(exc).lower():
                raise

        # The document now exists, so continue below.

    # ---------------------------------------------------------
    # Check current daily date
    # ---------------------------------------------------------

    user_data = token_usage_collection.find_one(
        {"_id": ip},
        {
            "daily": 1,
        },
    )

    if user_data is None:
        # Extremely unlikely, but do not recurse.
        # Try the whole operation once more by inserting/updating.
        blocked_until = (
            now + timedelta(hours=24)
            if cost >= MAXIMUM_DAILY_COST_PER_USER
            else None
        )

        token_usage_collection.update_one(
            {"_id": ip},
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
                    "blocked_until": blocked_until,
                }
            },
            upsert=True,
        )

        return

    daily = user_data.get("daily") or {}
    stored_date = daily.get("date")

    # ---------------------------------------------------------
    # New day
    # ---------------------------------------------------------

    if stored_date != today:
        blocked_until = (
            now + timedelta(hours=24)
            if cost >= MAXIMUM_DAILY_COST_PER_USER
            else None
        )

        token_usage_collection.update_one(
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
                    "blocked_until": blocked_until,
                }
            },
        )

        return

    # ---------------------------------------------------------
    # Same day
    # ---------------------------------------------------------

    current_cost = daily.get("cost", 0.0)
    new_total_cost = current_cost + cost

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

    user_data = token_usage_collection.find_one(
        {"_id": ip},
        {
            "blocked_until": 1,
        },
    )

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
            {
                "_id": ip,
                "blocked_until": blocked_until,
            },
            {
                "$unset": {
                    "blocked_until": ""
                }
            },
        )

        return False

    return True
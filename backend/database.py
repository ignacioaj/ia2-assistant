import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MAXIMUM_DAILY_COST_PER_USER = os.getenv("MAXIMUM_DAILY_COST_PER_USER")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not configured")
if not MAXIMUM_DAILY_COST_PER_USER:
    raise RuntimeError("MAXIMUM_DAILY_COST_PER_USER is not configured")

client = MongoClient(MONGODB_URI)

db = client["ai2_assistant"]

token_usage_collection = db["token_usage"]

token_usage_collection.create_index(
    [("ip", 1), ("date", 1)],
    unique=True,
)


def save_token_usage(
    ip,
    input_tokens,
    output_tokens,
    total_tokens,
    cost,
):
    now = datetime.now(timezone.utc)
    date = now.strftime("%Y-%m-%d")

    user_data = token_usage_collection.find_one({
        "ip": ip,
        "date": date,
    })

    if user_data:
        new_total_cost = user_data["total_cost"] + cost

        update = {
            "$inc": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "total_cost": cost,
            },
            "$set": {
                "last_query": now,
            },
        }

        if (
            user_data["total_cost"] < MAXIMUM_DAILY_COST_PER_USER
            and new_total_cost >= MAXIMUM_DAILY_COST_PER_USER
        ):
            update["$set"]["blocked_since"] = now

        token_usage_collection.update_one(
            {
                "ip": ip,
                "date": date,
            },
            update,
        )

    else:
        blocked_since = (
            now
            if cost >= MAXIMUM_DAILY_COST_PER_USER
            else None
        )

        document = {
            "ip": ip,
            "date": date,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "total_cost": cost,
            "last_query": now,
        }

        if blocked_since:
            document["blocked_since"] = blocked_since

        token_usage_collection.insert_one(document)


def is_usage_blocked(ip):
    now = datetime.now(timezone.utc)

    user_data = token_usage_collection.find_one({
        "ip": ip,
        "date": now.strftime("%Y-%m-%d"),
    })

    if not user_data:
        return False

    blocked_since = user_data.get("blocked_since")

    if not blocked_since:
        return False

    if blocked_since.tzinfo is None:
        blocked_since = blocked_since.replace(tzinfo=timezone.utc)

    return now < blocked_since + timedelta(hours=24)
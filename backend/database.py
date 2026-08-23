import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not configured")

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

    token_usage_collection.update_one(
        {
            "ip": ip,
            "date": date,
        },
        {
            "$inc": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "total_cost": cost,
            },
            "$set": {
                "last_query": now,
            },
        },
        upsert=True,
    )

from datetime import datetime, timezone

from backend.database.database import db


sessions_collection = db["sessions"]


def save_session(
    session_id,
    ip,
    question,
    answer,
    status="success",
    cost=0.0,
):
    now = datetime.now(timezone.utc)

    message = {
        "question": question,
        "answer": answer,
        "date": now,
        "status": status,
    }

    sessions_collection.update_one(
        {
            "_id": session_id,
        },
        {
            "$setOnInsert": {
                "ip": ip,
                "created_at": now,
            },
            "$set": {
                "last_query": now,
            },
            "$push": {
                "messages": message,
            },
            "$inc": {
                "cost": cost,
            },
        },
        upsert=True,
    )
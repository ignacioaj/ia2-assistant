import json
import os
import base64
from email.message import EmailMessage
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.logger import logger
from backend.context import load_text_file

load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

PROFILE_SECTIONS = {
    "projects": "projects.md",
    "interests": "interests.md",
    "other": "extended_profile.md",
}

# ============================================================
# TOOL TRIGGERS
# ============================================================

tool_retrieve_more_info = {
    "name": "retrieve_more_info",
    "description": (
        "Retrieve additional authoritative information about Ignacio "
        "from his extended professional profile. "
        "Use this tool ONLY when the core profile does not contain "
        "enough information to answer a question specifically about "
        "Ignacio, his background, career, projects, interests, skills, "
        "experience, or other professional/personal profile information. "
        "Choose 'projects' for questions about Ignacio's projects, "
        "'interests' for questions about Ignacio's interests, and "
        "'other' for other relevant information about Ignacio that is "
        "not covered by projects or interests. "
        "Do NOT use this tool for general knowledge, unrelated questions, "
        "or information that can be answered without knowing more about Ignacio."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "section": {
                "type": "string",
                "description": "The profile section to retrieve.",
                "enum": [
                    "projects",
                    "interests",
                    "other",
                ],
            }
        },
        "required": ["section"],
        "additionalProperties": False,
    },
}

tool_email = {
    "name": "record_email",
    "description": (
        "Send a message to Ignacio by email. "
        "Use this tool whenever the user asks to communicate something to Ignacio"
        "If the user doesn't explicitly mention the content of the body, send back the body you infer and ask for confirmation before sending."
        "If the subject is not specified, create it based on the body (do not send the body itself)."
        "Do not accept inappropriate bodies or bodies which are not strictly professional or useful for Ignacio."
        "If not specified by the user, do ALWAYS ask for the sender email."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "sender": {
                "type": "string",
                "description": (
                    "The valid email address of the person who wrote the message. "
                    "This is NOT the recipient email address. "
                ),
            },
            "subject": {
                "type": "string",
                "description": "The subject of the email.",
            },
            "body": {
                "type": "string",
                "description": "The message written by the sender.",
            },
        },
        "required": ["sender", "body"],
        "additionalProperties": False,
    },
}

# ============================================================
# TOOL FUNCTIONS
# ============================================================

def record_email(sender: str, subject: str, body: str):
    recipient = os.environ["EMAIL_USER"]

    try:
        credentials = Credentials(
            token=None,
            refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GMAIL_CLIENT_ID"],
            client_secret=os.environ["GMAIL_CLIENT_SECRET"],
            scopes=GMAIL_SCOPES,
        )

        gmail = build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

        msg = EmailMessage()

        msg["From"] = recipient
        msg["To"] = recipient
        msg["Reply-To"] = sender
        msg["Subject"] = subject

        msg.set_content(
            f"Sent by: {sender}\n\n"
            f"{body}"
        )

        encoded_message = base64.urlsafe_b64encode(
            msg.as_bytes()
        ).decode()

        gmail.users().messages().send(
            userId="me",
            body={
                "raw": encoded_message
            }
        ).execute()

        logger.info(f"Email sent successfully by {sender}")

        return "OK"

    except Exception as e:
        logger.exception(
            f"Error sending email: {type(e).__name__}: {e}"
        )
        return f"Email error: {e}"

def retrieve_more_info(section: str) -> str:
    filename = PROFILE_SECTIONS.get(section)

    if not filename:
        return f"Unknown profile section: {section}"

    return load_text_file(filename)

tool_map = {
    "retrieve_more_info": retrieve_more_info,
    "record_email": record_email,
}

# ============================================================
# TOOL CALL HANDLER
# ============================================================

def handle_tool_calls(tool_calls):
    results = []

    for tool_call in tool_calls:
        tool_name = tool_call.name
        arguments = json.loads(tool_call.arguments)

        tool = tool_map.get(tool_name)

        result = tool(**arguments) if tool else "No tool found"

        results.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(result),
            }
        )

    return results

tools = [
    {
        "type": "function",
        "name": tool_email["name"],
        "description": tool_email["description"],
        "parameters": tool_email["parameters"],
    },
    {
        "type": "function",
        "name": tool_retrieve_more_info["name"],
        "description": tool_retrieve_more_info["description"],
        "parameters": tool_retrieve_more_info["parameters"],
    },
]
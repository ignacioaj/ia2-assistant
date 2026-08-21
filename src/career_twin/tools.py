import json
import os
import requests

def record_email(email):
    with open("emails.txt", "a") as f:
        f.write(email + "\n")

    return "OK"

def record_unknown_question(email):
    with open("emails.txt", "a") as f:
        f.write(email + "\n")

    return "OK"

tool_map = {
    "record_email":record_email,
    "record_unknown_question":record_unknown_question
}

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.arguments)
        print(f"Tool called {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else 'No tool found'
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results

tool_email = {
    "name":"record-email-tool",
    "description":"Record that a user provided their email address",
    "parameters":{
        "type":"object",
        "properties":{
            "name": {"type":"string", "description":"The user's name, if they provided it"},
            "email": {"type":"string", "description":"The email address of this user"},
        }
    }
}

tool_unknown_question = {
    "name":"record-unknown-question-tool",
    "description":"Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters":{
        "type":"object",
        "properties":{
            "question": {"type":"string", "description":"The question that couldn't be answered"},
        }
    },
    "required": ["question"],
    "additionalProperties": False
}

tools = [{"type":"function", "function": tool_email}, {"type":"function", "function": tool_unknown_question}]
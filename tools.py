import json
import os
import requests
from dotenv import load_dotenv
import resend
import hashlib

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")

pushover_url = "https://api.pushover.net/1/messages.json"


def push(text):
    requests.post(
        pushover_url,
        data={
            "token": pushover_token,
            "user": pushover_user,
            "message": text,
        },
    )



key = os.getenv('RESEND_API_KEY')


print("Key exists:", bool(key))
print("Key prefix:", key[:3] if key else None)
print("Key length:", len(key) if key else 0)
print("Key fingerprint:", hashlib.sha256(key.encode()).hexdigest()[:12] if key else None)

resend.api_key = key

# def record_user_details(email, name="Name not provided", notes="not provided"):
#     push(f"Recording interest from {name} with email {email} and notes {notes}")
#     return "OK"


def record_user_details(email, name="Name not provided", notes="not provided"):
     resend.Emails.send({
             "from": "onboarding@resend.dev",  # test domain — works immediately, no setup
        "to": ["ahmedxkhan47@gmail.com"],
        "subject": f"New visitor interested in {name}",
        "html": f"""
            <div style="font-family: sans-serif; max-width: 400px;">
                <h2>THE DIGITAL TWIN HAS RECEIVED A NEW VISITOR</h2>
                <p>THe reason of contact is:</p>
                <h1 style="letter-spacing: 4px;">{notes}</h1>
                <p>The email of the visitor is:</p>
                <h1 style="letter-spacing: 4px;">{email}</h1>
                <p>The name of the visitor is:</p>
                <h1 style="letter-spacing: 4px;">{name}</h1>
                <p>The response has been recorded.</p>
            </div>
        """,
    })

# def record_unknown_question(question):
#     push(f"Recording {question} asked that I couldn't answer")
#     return "OK"

def record_unknown_question(email,question):
    print(f"Tool called to record an email: {email}")
    with open("FAQS.txt", "a", encoding="utf-8") as f:
        f.write(f"Email = {email}  Question = {question}\n")
    return "question recorded"


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["email","question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else "Unknown tool: " + tool_name
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results

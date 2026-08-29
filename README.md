# IA² — Ignacio's AI Assistant

**IA² is my OpenAI-powered assistant.**

It knows everything about my professional background, experience, projects, skills, and career path and is ready to answer any question about me.

## ✨ What it does

Visitors can ask questions such as:

* Who is Ignacio?
* What is his professional background?
* What technologies does he work with?
* Tell me about his projects.
* What kind of experience does he have?
* How can I contact him?

The assistant keeps the conversation context of every session. A session is created when the user opens the chat and ended when the chat is closed. Session lifecycle is handled by the Front-End, while the conversation history is stored and retrieved by the Back-End using the provided `session_id`.

## 🏗️ Architecture

```text
    Front-End
        │
        │ POST /chat
        │ { session_id, message }
        ▼
     Back-End
        │
        ├──────────────► MongoDB
        │                 │
        │                 ├── device data
        │                 ├── session history
        │                 └── usage & cost tracking
        │
        ▼
    Assistant
        │
        ▼
    Response
        │
        ▼
    Front-End
```

### Chat flow

The following describes the lifecycle of a chat request.

#### First request in a session

1. The **Front-End** opens the chat and starts a new session, generating a `session_id`.
2. The **Back-End** receives the request containing the user's message and `session_id`.
3. The **Back-End** identifies the device using the public IP included in the request and retrieves the corresponding device data from MongoDB.
4. The Back-End checks whether the device has reached its daily usage limit.
5. If the device is **not blocked**, the Back-End retrieves the chat history associated with the provided `session_id`. For a new session, the history is empty.
6. The Back-End sends the user's message together with the chat history to the **Assistant**.
7. The **Assistant** processes the request and returns the response, updated conversation history, and token/cost information.
8. The Back-End updates MongoDB, adding the cost of the request to the device's daily usage.
9. The updated conversation history is kept associated with the provided `session_id`.
10. The response is returned to the **Front-End**.
11. The Front-End displays the response. The user can either continue the conversation or close the chat and finish the session.

If the device has reached its daily limit at step 4, the Back-End returns an error to the Front-End and **the request is not sent to the Assistant**.

#### Subsequent requests in the same session

If the user continues chatting:

12. The **Back-End** receives another request containing the message and the same `session_id`.
13. The Back-End retrieves the device data from MongoDB.
14. The Back-End checks whether the device is blocked for the current day.
15. If the device is **not blocked**, the Back-End retrieves the chat history from the previous request using the `session_id` and sends the new message together with that history to the Assistant.
16. The **Assistant** processes the request using the existing conversation context.
17. The Assistant returns the new response, updated history, and token/cost information.
18. The Back-End updates the device's daily usage in MongoDB with the cost of the new request.
19. The updated history remains associated with the same `session_id`.
20. The response is returned to the Front-End, which displays it and allows the user to continue or close the session.

If the device **is blocked**, the Back-End returns an error to the Front-End and **does not send the request to the Assistant**.

### Project structure

```text
ia2-assistant/
│
├── backend/
│   ├── database/
│   │   ├── database.py
│   │   ├── sessions.py
│   │   └── token_usage.py
│   │
│   ├── __init__.py
│   ├── assistant.py
│   ├── context.py
│   ├── logger.py
│   ├── main.py
│   ├── pricing.py
│   ├── prompts.py
│   └── tools.py
│
├── docs/
│
└── playground.py
```

* `database.py`: Provides connection to MongoDB.
* `token_usage.py`: Handles logic for updating the `token_usage` collection.
* `sessions.py`: Handles logic for updating the `sessions` collection and retrieving conversation history.
* `assistant.py`: The LLM assistant logic.
* `context.py`: Merges Ignacio's profile prompts with IA2 prompts.
* `logger.py`: Handles logs to be displayed in the deployment environment console.
* `main.py`: The backend that handles Front-End requests and calls the Assistant and database.
* `pricing.py`: Computes the cost of every request based on token consumption.
* `prompts.py`: IA2-specific prompts.
* `tools.py`: Tools used by the Assistant, triggered by concrete requests.
* `playground.py`: Allows testing prompts without needing to push changes.

The Career Twin UI lives in the portfolio frontend and communicates with the backend through the `/chat` API.

### Backend

The API is built with **FastAPI**.

The `/chat` endpoint:

1. Identifies the client/device.
2. Checks the daily usage limit.
3. Retrieves the conversation history using the `session_id`.
4. Calls the Assistant only if the device is not blocked.
5. Stores token usage and cost.
6. Updates the session history.
7. Returns the response.

If the usage limit has been reached, the request is rejected **before calling the LLM**.

### API

The frontend communicates with the backend through `POST /chat`.

#### Request

```json
{
  "session_id": "uuid",
  "message": "Tell me about Ignacio's career"
}
```

#### Response

```json
{
  "response": "Ignacio's career..."
}
```

## 💰 Usage protection

Because the assistant is publicly accessible, API usage is protected by a cost-based limit.

The current limit is:

```python
MAXIMUM_DAILY_COST_PER_USER = 0.05
```

Usage is tracked in MongoDB by IP address, including token consumption, cost, and the time the limit was reached.

Once the daily limit is reached, further AI requests from that device are blocked until the daily limit resets.

Importantly, blocked requests are rejected by the Back-End **before they are sent to the LLM**, preventing additional AI costs.

## 🧠 Prompt architecture

The assistant is built around two prompt layers:

* **Core prompt** — identity, behaviour, tone, and general rules.
* **Career prompt** — Ignacio's professional knowledge, including experience, projects, skills, and career history.
* **Interests prompt** — interests.
* **Projects prompt** — projects.

The prompt architecture is intentionally separated so the assistant's behaviour and knowledge can be refined independently.

## 🗄️ Tech stack

* **Backend:** Python, FastAPI
* **AI:** OpenAI API
* **Database:** MongoDB
* **Deployment:** Render

## 🔐 Security

The LLM API credentials remain server-side and are never exposed to the frontend.

The backend also prevents additional LLM calls once a client reaches the configured usage limit.

For production, CORS should be restricted to the portfolio's domain and additional abuse protection can be added as needed.

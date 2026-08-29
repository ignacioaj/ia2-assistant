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

The assistant keeps the conversation context of every session (a session is created when the user opens the chat and ended when chat is closed. But this is handled by the Front-End)

## 🏗️ Architecture

```text
    Front-End
        │
        │ POST /chat
        ▼
     FastAPI
        │
   ┌────┴─────┐
   ▼          ▼
 LLM API   MongoDB
            │
            └── usage & cost tracking
```

### Project structure

```text
ia2-assistant/
├── backend/
│   ├── assistant.py     # Career Twin & LLM interaction
│   ├── database.py      # MongoDB & usage tracking
│   ├── main.py          # FastAPI application & /chat endpoint
│   └── pricing.py       # Token pricing & cost calculation
│
├── docs/                # Project documentation
├── pyproject.toml       # Python project configuration
├── requirements.txt     # Python dependencies
└── README.md
```

The Career Twin UI lives in the portfolio frontend and communicates with the backend through the `/chat` API.

### Frontend

The Career Twin is integrated into Ignacio's portfolio using **Astro** and **TypeScript**.

It handles:

* Chat sessions and conversation history
* Message rendering
* Loading states
* Usage-limit errors
* Responsive chat UI

### Backend

The API is built with **FastAPI**.

The `/chat` endpoint:

1. Identifies the client.
2. Checks the usage limit.
3. Retrieves the conversation history.
4. Calls the Assistant.
5. Stores token usage and cost.
6. Returns the response.

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
MAXIMUM_DAILY_COST_PER_USER = 0.10
```

Usage is tracked in MongoDB by IP address, including token consumption, cost, and the time the limit was reached.

Once the limit is exceeded, further AI requests are blocked for 24 hours.

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

---

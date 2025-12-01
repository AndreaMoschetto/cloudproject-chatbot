import chainlit as cl
import httpx
from constants import QUERY_URL, HISTORY_URL


@cl.oauth_callback
def oauth_callback(provider_id: str, token: str, raw_user_data, default_user: cl.User):
    identifier = raw_user_data.get("email") or raw_user_data.get("username")
    default_user.identifier = identifier
    return default_user


@cl.on_chat_start
async def on_chat_start():
    user = cl.user_session.get("user")
    # If no user is found (e.g., local test without auth), fallback
    if user:
        session_id = user.identifier  # Es: mario.rossi@gmail.com
    else:
        session_id = "anonymous_user"

    print(f"Starting chat for: {session_id}")

    cl.user_session.set("session_id", session_id)

    # Setup client HTTP
    client = httpx.AsyncClient(timeout=60.0)
    cl.user_session.set("http_client", client)

    try:
        print(f"Fetching history for {session_id}...")
        history_url = f"{HISTORY_URL}/{session_id}"
        response = await client.get(history_url)

        if response.status_code == 200:
            history = response.json()
            if history:
                for msg in history:
                    msg_type = "assistant_message"
                    author = "Assistant"

                    if msg["role"] == "user":
                        msg_type = "user_message"
                        author = user.identifier

                    await cl.Message(
                        content=msg["content"],
                        author=author,
                        type=msg_type
                    ).send()

    except Exception as e:
        print(f"Error loading history: {e}")
        # We don't block the app if history loading fails, the user can still chat
        await cl.Message(content=f"⚠️ Warning: Could not load chat history. ({e})").send()


@cl.on_message
async def on_message(message: cl.Message):
    client = cl.user_session.get("http_client")
    session_id = cl.user_session.get("session_id")  # Questo ora è l'email vera!

    msg = cl.Message(content="")
    await msg.send()

    try:
        payload = {
            "query": message.content,
            "session_id": session_id
        }

        response = await client.post(QUERY_URL, json=payload)
        response.raise_for_status()

        data = response.json()
        answer = data.get("answer", "Error")

        msg.content = answer
        await msg.update()

    except httpx.HTTPStatusError as e:
        # Handle backend errors (e.g., the 500 error we built)
        msg.content = f"Error from backend: {e.response.status_code}"
        await msg.update()
    except httpx.RequestError:
        # Handle connection errors (e.g., FastAPI server is not running)
        msg.content = f"Error: Cannot connect to backend at {QUERY_URL}. Is it running?"
        await msg.update()
    except Exception as e:
        # Handle any other errors
        msg.content = f"An unexpected error occurred: {str(e)}"
        await msg.update()


@cl.on_stop
async def on_stop():
    client = cl.user_session.get("http_client")
    if client:
        await client.aclose()

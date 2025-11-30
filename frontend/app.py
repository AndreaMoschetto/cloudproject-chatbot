import chainlit as cl
import httpx
from constants import QUERY_URL, HISTORY_URL

TEST_SESSION_ID = "user_test_dynamo"  # To test history functionality


@cl.on_chat_start
async def on_chat_start():
    print('Connecting to backend...')
    client = httpx.AsyncClient(timeout=60.0)
    cl.user_session.set("http_client", client)

    session_id = TEST_SESSION_ID
    cl.user_session.set("session_id", session_id)
    try:
        print(f"Fetching history for {TEST_SESSION_ID}...")
        history_url = f"{HISTORY_URL}/{TEST_SESSION_ID}"

        response = await client.get(history_url)
        response.raise_for_status()
        history = response.json()

        if history:
            print(f"Found {len(history)} past messages.")
            for msg in history:
                author = "Assistant" if msg["role"] == "assistant" else "User"
                msg_type = 'assistant_message' if msg["role"] == "assistant" else 'user_message'
                await cl.Message(
                    content=msg["content"],
                    author=author,
                    type=msg_type
                ).send()
        else:
            print("No history found.")

    except Exception as e:
        print(f"Error loading history: {e}")
        # We don't block the app if history loading fails, the user can still chat
        await cl.Message(content=f"⚠️ Warning: Could not load chat history. ({e})").send()


@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve the instances from the user's session
    client = cl.user_session.get("http_client")
    session_id = cl.user_session.get("session_id")

    # Create a "thinking" message to show the user
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
        answer = data.get("answer", "Sorry, I couldn't find an answer.")

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

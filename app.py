import chainlit as cl
import httpx
from constants import QUERY_URL


@cl.on_chat_start
async def on_chat_start():
    print('Connecting to backend...')
    client = httpx.AsyncClient(timeout=60.0)
    cl.user_session.set("http_client", client)


@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve the instances from the user's session
    client = cl.user_session.get("http_client")

    # Create a "thinking" message to show the user
    msg = cl.Message(content="")
    await msg.send()

    try:
        response = await client.post(QUERY_URL, json={"query": message.content})
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

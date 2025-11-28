import os

# In local (without docker) it will use localhost.
# In Docker (via docker-compose) it will use "http://backend:8000"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
QUERY_URL = f"{BACKEND_URL}/query"

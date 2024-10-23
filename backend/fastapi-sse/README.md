# FastAPI SSE Endpoint 

Change directory:
```
cd natural-language-query\backend\fastapi-sse
```

Install the dependencies:
```
pip install -r requirements.txt
```

Create .env file and add following details:
```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
LLM_MODEL_NAME="LLM_MODEL_NAME"
ENDPOINT="http://YOUR_SERVER_ADDRESS/chat"
```

To run the FastAPI based server, use:
```
python -m uvicorn server-sse:app --reload
```

To observe how the `server-sse.py` interacts with the frontend via Server-Sent Events (SSE), execute the `test-client-sse.py` file like below. This will send a sample query to the server and stream the SQL query responses in real-time:
```
python test-client-sse.py
```
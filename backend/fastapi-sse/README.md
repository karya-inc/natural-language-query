# FastAPI SSE Endpoint 

Install the dependencies:
```
pip install -r requirements.txt
```

To run the FastAPI based server, use:
```
python -m uvicorn server:app --reload
```

To observe how the `server-sse.py` interacts with the frontend via Server-Sent Events (SSE), execute the `client-sse.py` file like below. This will send a sample query to the server and stream the SQL query responses in real-time:
```
python server-sse.py
```
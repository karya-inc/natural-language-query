from dotenv import load_dotenv

from db.models import ExecutionLog, UserSession
from dependencies.db import get_db_session_from_request
from queues.typed_tasks import invoke_execute_query_op

load_dotenv()

import os
from typing import Annotated, Any, Optional, List
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException, Depends, Query, Request
from starlette.responses import StreamingResponse
from auth.oauth import OAuth2Phase2Payload
from dependencies.auth import (
    AuthenticatedUserInfo,
    TokenVerificationResult,
    get_authenticated_user_info,
    verify_token,
    auth_handler,
)
from utils.logger import get_logger
from controllers.sql_response import (
    chat_history,
    get_saved_queries_user,
    save_query_for_user,
    get_session_history,
    nlq_sse_wrapper,
    save_fav,
)
from fastapi.middleware.cors import CORSMiddleware
from db.db_queries import (
    ChatHistoryResponse,
    SavedQueriesResponse,
    UserSessionsResponse,
    ExecutionLogResult,
    create_execution_entry,
    get_recent_execution_for_query,
    get_recent_execution_for_query_id,
)
from db.db_queries import (
    get_all_user_info,
    get_saved_query_by_id,
    get_session_for_user,
    get_exeuction_log_result,
    create_session,
)
from sqlalchemy.orm import Session
from db.models import User
from utils.parse_catalog import parsed_catalogs

parsed_catalogs.database_privileges


# Create the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(" "),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging configuration
logger = get_logger("NLQ-Server")


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    type: Optional[str] = None


# @app.middleware("http")
# async def manage_db_session(request: Request, call_next):
#     db_session = get_db_session()
#     try:
#         request.state.db = db_session
#         logger.info("Calling Nexx")
#         response = await call_next(request)
#         logger.info("Next completed")
#         return response
#     finally:
#         db_session.close()


@app.get("/auth/verify")
async def verify_auth(auth: Annotated[TokenVerificationResult, Depends(verify_token)]):
    """
    Returns the token verification result
    """
    return auth.__dict__


@app.get("/auth/login_stratergy")
async def get_login_stratergy(
    code: Annotated[str | None, str, Body()] = None,
    state: Annotated[str | None, str, Body()] = None,
):
    """
    Returns information on how to login the user
    """

    payload = None
    if code:
        payload = OAuth2Phase2Payload(code=code, state=state)

    response = auth_handler.login(payload)
    return response.__dict__


@app.post("/chat")
async def stream_sql_query_responses(
    chat_request: ChatRequest,
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> StreamingResponse:
    """
    Endpoint to stream SQL query responses as Server-Sent Events (SSE).
    If session_id is not provided, a new one will be generated.
    If type is not provided, it will be set to "report".

    Args:
        chat_request (ChatRequest): The request containing the SQL query and optional session_id.
        db (Session): The database session.
        user_info (AuthenticatedUserInfo): The user info extracted from the token after successfully authenticating.

    Returns:
        StreamingResponse: The response streamed as Server-Sent Events.
    """

    # Dependency check to validate user

    # If no session_id is provided, generate a new str for the session
    current_session: Optional[UserSession] = None
    if not chat_request.session_id:
        current_session = create_session(db, user_info.user_id)
    else:
        current_session = get_session_for_user(
            db_session=db,
            user_id=user_info.user_id,
            session_id=chat_request.session_id,
        )
        session_id = chat_request.session_id

    if not current_session:
        raise HTTPException(status_code=400, detail="Session not found for the user.")

    session_id = str(current_session.session_id)
    try:
        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {chat_request.query}")
        response = StreamingResponse(
            nlq_sse_wrapper(
                user_info, chat_request.query, current_session, db_session=db
            ),
            media_type="text/event-stream",
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(
            f"Error while processing query: {chat_request.query} with session_id: {session_id}. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to stream SQL query responses."
        )


@app.get("/fetch_history")
async def get_chat_history(
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> List[UserSessionsResponse]:
    """
    Get chat history for the user

    Returns:
       Chat history
    """

    try:
        # Log the start of chat history streaming
        logger.info(f"User chat history for user_id: {user_info.user_id}")

        # Create a StreamingResponse for the chat history generator
        response = get_session_history(db=db, user_id=user_info.user_id)

        logger.info("Chat history for user return successfully!!")
        return response

    except Exception as e:
        logger.error(
            f"Error while retrieving chat history for user_id: {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to stream chat history.")

    finally:
        db.close()


@app.get("/fetch_session_history/{session_id}")
async def get_session_history_for_user(
    session_id: str,
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> List[ChatHistoryResponse]:
    """
    Get session id from query params and fetch the session history for the user

    Args:
        session_id (str): Session ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Session history
    """
    logger.info(f"Session history for session_id: {session_id}")
    try:
        response = chat_history(db, session_id, user_info.user_id)
        logger.info("Session history for session_id return successfully!!")
        return response
    except Exception as e:
        logger.error(
            f"Error while retrieving session history for session_id: {session_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to get session history.")
    finally:
        db.close()


@app.get("/queries")
async def get_saved_queries(
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
    filter: Optional[str] = Query(None, alias="filter:all"),
) -> List[SavedQueriesResponse]:
    """

    Retrieve saved queries
    - For non-SUPERADMIN: returns user's own queries
    - For SUPERADMIN with filter:all: returns all users' queries except SUPERADMIN
    """

    try:
        # Log the start of chat history streaming
        logger.info(f"User chat history for user_id: {user_info.user_id}")

        # Filter
        filter = "saved" if not filter else "all"

        # Create a StreamingResponse for the chat history generator
        response = get_saved_queries_user(
            db=db, user_id=user_info.user_id, filter=filter
        )

        logger.info("Return user favorite queries successfully!!")
        return response

    except Exception as e:
        logger.error(
            f"Error while returning favorite queries for user : {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to return favorite queries."
        )
    finally:
        db.close()


@app.get("/queries/{sqid}/execution")
@app.post("/queries/{sqid}/execution")
async def execute_saved_query(
    sqid: str,
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
    request: Request,
) -> dict[str, Any]:
    """
    Execute saved query

    Args:
        query_id (str): Query ID for which to execute the query
        db (Session): Database session
        user_id (str): User ID

    Returns:
        StreamingResponse: The response streamed as Server-Sent Events.
    """
    logger.info(
        f"Executing saved query for user: {user_info.user_id} with query_id: {sqid}"
    )

    saved_query_entry = get_saved_query_by_id(db, sqid, user_info.user_id)

    if not saved_query_entry:
        raise HTTPException(status_code=404, detail="Saved query not found.")

    if not saved_query_entry.user_id == user_info.user_id:
        raise HTTPException(
            status_code=403, detail="User doesn't have access to this saved query."
        )

    if request.method == "GET":
        execution_log = get_recent_execution_for_query_id(db_session=db, sqid=sqid)
        if execution_log:
            return execution_log.to_dict()

        raise HTTPException(status_code=404, detail="Execution log not found.")

    try:

        running_execution_log = get_recent_execution_for_query_id(db, sqid, "RUNNING")
        if running_execution_log:
            return running_execution_log.to_dict()


        # No running execution found, create a new execution log
        execution_log = create_execution_entry(db, user_info.user_id, str(sqid))

        logger.info("Execution started successfully.")

        catalog = next(
            filter(
                lambda x: x.name == saved_query_entry.sql_query.database_used,
                parsed_catalogs.catalogs,
            )
        )

        invoke_execute_query_op(execution_log.id, catalog)
        return execution_log.to_dict()
    except Exception as e:
        logger.error(
            f"Error while executing saved query for user: {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to execute saved query.")

    finally:
        db.close()

@app.post("/save_favorite_query/{turn_id}/{sql_query_id}", deprecated=True)
async def save_favorite_query(
    turn_id: int,
    sql_query_id: str,
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
):
    """
    Save favorite query for the user

    Args:
        turn_id (int): Turn ID
        sql_query_id (str): SQL Query ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        None
    """
    logger.info(
        f"Saving fav query of user : {user_info.user_id} with turn_id: {turn_id} and sql_query_id: {sql_query_id}"
    )
    try:
        response = save_fav(db, user_info.user_id, turn_id, sql_query_id)
        logger.info("Favorite query saved successfully!!")
        return response
    except Exception as e:
        logger.error(
            f"Error while saving favorite query for user : {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to save favorite query.")
    finally:
        db.close()


@app.get("/execution_result/{execution_id}")
async def get_execution_result_for_id(
    execution_id: int,
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> ExecutionLogResult:
    """
    Get execution result for the user

    Args:
        execution_id (int): Execution Log ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Execution result
    """
    logger.info(f"Get execution result for user: {user_info.user_id} is requested!")
    try:
        response = get_exeuction_log_result(db, execution_id)
    except Exception as e:
        logger.error(
            f"Error while retrieving execution result for user: {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to get execution result.")
    finally:
        db.close()

    if not response:
        raise HTTPException(status_code=404, detail="Execution log not found.")

    logger.info("Execution result for user return successfully!!")
    return response


class SaveQueryRequest(BaseModel):
    name: str
    description: Optional[str] = None


@app.post("/save_query/{turn_id}/{sqid}")
async def save_query(
    turn_id: int,
    sqid: str,
    body: SaveQueryRequest,
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
):
    """
    Endpoint to save query

    Args:
        turn_id (int): Turn ID
        sqid (str): SQL Query ID
        body (SaveQueryRequest): Request body
        db (Session): Database session
        user_info (str): contains user information
    """
    logger.info(
        f"Saving query of user : {user_info.user_id} with turn_id: {turn_id} and sqid: {sqid}"
    )
    try:
        response = save_query_for_user(
            db, user_info.user_id, turn_id, sqid, body.name, body.description
        )

        if response is None:
            return HTTPException(
                400, detail="Failed to save query. Query with same name already exists."
            )

        logger.info("Query saved successfully!!")
        return response.to_dict()

    except Exception as e:
        logger.error(
            f"Error while saving query for user : {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to save query.")
    finally:
        db.close()


@app.get("/get_all_users_info/")
async def get_all_queries(
    db: Annotated[Session, Depends(get_db_session_from_request)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> List[User]:
    """
    Get all users info

    Args:
        db (Session): Database session
        user_id (str): User ID

    Returns:
        All users info
    """
    logger.info(f"Get all users info for user: {user_info.user_id} is requested!")
    try:
        # TODO: Before returning the response, check if user ROLE is SUPERADMIN!
        response = get_all_user_info(db)
        logger.info("All users info return successfully!!")
        return response
    except Exception as e:
        logger.error(
            f"Error while retrieving all users info for user: {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to get all users info.")
    finally:
        db.close()

from executor.state import QueryResults


def notify_user_on_success(
    execution_log_id: int, result: QueryResults, notify_to: list[str]
) -> None:
    """
    Notify the users on successful query execution.

    Args:
        execution_log_id (int): The execution log id
        notify_to (List[str]): The list of users to notify
    """
    pass


def notify_user_on_failure(execution_log_id: int, notify_to: list[str]) -> None:
    """
    Notify the users on failed query execution.

    Args:
        execution_log_id (int): The execution log id
        notify_to (List[str]): The list of users to notify
    """
    pass

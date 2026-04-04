from fastapi import HTTPException, status


class AgentNotFoundException(HTTPException):
    def __init__(self, agent_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found.",
        )


class GraphExecutionException(HTTPException):
    def __init__(self, detail: str = "Graph execution failed."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class InvalidStateException(HTTPException):
    def __init__(self, detail: str = "Invalid graph state."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )

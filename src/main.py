"""Main entry point of the TrustGate authentication server.

This module initializes and starts the FastAPI application.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from core.exceptions import CustomException
from routes.role import router as role_router
from schemas import AppResponse

app = FastAPI(
    title="TrustGate",
    description="Centralized Authentication Server with SSO, RBAC, and Vault Integration",
    version="1.0.0",
)

# Allowing all origins for now; update as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request, exc: CustomException
) -> AppResponse:
    """Handle custom exceptions."""
    return AppResponse(
        body=str(exc),
        message=f"Error: {exc.detail}",
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> AppResponse:
    """Handle request validation errors."""
    return AppResponse(
        body=exc.errors(), message="Error: Validation error", status_code=422
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, exc: Exception
) -> AppResponse:
    """Handle general exceptions."""
    return AppResponse(
        body=str(exc),
        message="Error: Internal server error",
        status_code=500,
    )


# Include the role routes
app.include_router(role_router, prefix="/api/v1")


@app.get("/", tags=["Health Check"])
def health_check() -> dict[str, str]:
    """Health check endpoint to verify if the API is running."""
    return {"message": "TrustGate API is running successfully."}

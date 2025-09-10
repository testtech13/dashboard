from fastapi import FastAPI, Request, HTTPException, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import threading
import time  # Add this import for time.sleep
from main import dashboard_controller
from config import config_manager
from models import DashboardConfig, ConfigUpdateRequest, ControlRequest, StatusResponse, LoginRequest, Token, User
from auth import authenticate_user, create_access_token, verify_token, get_user
from datetime import timedelta


app = FastAPI(title="Dashboard Controller", description="Web interface for dashboard management")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_web(request: Request) -> User:
    """Get current authenticated user for web pages - redirects to login if not authenticated"""
    credentials = await security(request)
    if not credentials:
        # Redirect to login page for web requests
        return RedirectResponse(url="/login", status_code=302)

    username = verify_token(credentials.credentials)
    if username is None:
        # Redirect to login page for invalid tokens
        return RedirectResponse(url="/login", status_code=302)

    user = get_user(username)
    if user is None:
        # Redirect to login page for unknown users
        return RedirectResponse(url="/login", status_code=302)

    return user


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/login")
async def login(request: LoginRequest):
    """Login endpoint"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/", response_class=HTMLResponse)
async def dashboard_ui(request: Request):
    """Main dashboard UI"""
    # For initial page load, we'll let JavaScript handle authentication
    # This allows the page to load and then check for stored tokens
    config = config_manager.get_config()
    status_info = dashboard_controller._get_status()

    # Check if we have a valid token in the request
    auth_header = request.headers.get("Authorization")
    current_user = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        username = verify_token(token)
        if username:
            current_user = get_user(username)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "config": config,
        "status": status_info,
        "user": current_user
    })


@app.get("/api/status", response_model=StatusResponse)
async def get_status(current_user: User = Depends(get_current_user)):
    """Get current dashboard status"""
    return dashboard_controller._get_status()


@app.get("/api/config")
async def get_config(current_user: User = Depends(get_current_user)):
    """Get current configuration"""
    return config_manager.get_config()


@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest, current_user: User = Depends(get_current_user)):
    """Update dashboard configuration"""
    try:
        config_manager.save_config(request.config)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update config: {str(e)}")


@app.post("/api/control")
async def control_dashboard(request: ControlRequest, current_user: User = Depends(get_current_user)):
    """Control dashboard (start/stop/pause/resume)"""
    action = request.action.lower()

    if action == "start":
        if dashboard_controller.start_dashboard():
            # Start dashboard in background thread
            thread = threading.Thread(target=run_dashboard_loop, daemon=True)
            thread.start()
            return {"message": "Dashboard started"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start dashboard")

    elif action == "stop":
        dashboard_controller.stop_dashboard()
        return {"message": "Dashboard stopped"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


def run_dashboard_loop():
    """Run dashboard cycle in a loop"""
    while dashboard_controller.is_running:
        dashboard_controller.run_cycle()
        time.sleep(1)  # Small delay between cycles


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Load configuration
    config_manager.load_config()

    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)

    print("Dashboard web app started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    dashboard_controller.stop_dashboard()
    print("Dashboard web app stopped")

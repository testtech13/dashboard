# Dashboard Application

A Python-based dashboard application that automates a full-screen Chrome browser to cycle through configured webpages at specified intervals, with a FastAPI web interface for configuration and monitoring.

## Features

- **Automated Dashboard**: Cycles through configured webpages in full-screen Chrome
- **Web Interface**: FastAPI-based UI for configuration and monitoring
- **Flexible Configuration**: JSON-based config with per-page timing
- **Real-time Status**: Live updates on current page and time remaining
- **Responsive Design**: Modern UI built with Tailwind CSS
- **🔐 User Authentication**: Secure login required for all operations
- **🎭 Stealth Mode**: Chrome runs without automation indicators for cleaner presentation

## Project Structure

```
dashboard/
├── main.py              # Dashboard automation core
├── config.py            # Configuration management
├── web_app.py           # FastAPI application
├── models.py            # Pydantic data models
├── auth.py              # Authentication utilities
├── run.py               # Application runner
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
├── templates/
│   ├── index.html       # Main dashboard interface
│   └── login.html       # Login page
├── static/
│   └── js/              # JavaScript files
└── __init__.py          # Python package
```

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ChromeDriver**:
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Make sure it matches your Chrome version
   - Place chromedriver.exe in your system PATH

## Usage

1. **Start the Web Interface**:
   ```bash
   python run.py
   ```

2. **Access the Web Interface**:
   - Open http://localhost:8000
   - **You will be automatically redirected to login if not authenticated**
   - Login with credentials (see below)
   - Configure your dashboard pages
   - Start/stop the automated display

## 🔐 Authentication

**Default Credentials:**
- **Username:** `admin`
- **Password:** `admin123`

**Important Security Notes:**
- Change the default password in production
- Update the `SECRET_KEY` in `auth.py` for production use
- All configuration and control operations require authentication
- JWT tokens expire after 30 minutes
- Unauthenticated users are automatically redirected to the login page

**Authentication Flow:**
1. Access to `/` redirects unauthenticated users to `/login`
2. After successful login, users are redirected back to the dashboard
3. All API requests include JWT tokens for authentication
4. Invalid or expired tokens automatically redirect to login

The application uses a JSON configuration file (`dashboard_config.json`) with the following structure:

```json
{
  "pages": [
    {
      "url": "https://www.google.com",
      "duration_seconds": 30,
      "name": "Google"
    },
    {
      "url": "https://www.github.com",
      "duration_seconds": 45,
      "name": "GitHub"
    }
  ],
  "loop": true,
  "auto_start": false
}
```

## API Endpoints

### Public Endpoints
- `GET /login` - Login page
- `POST /api/login` - User authentication

### Protected Endpoints (Require Authentication)
- `GET /` - Main web interface
- `GET /api/status` - Get current dashboard status
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `POST /api/control` - Control dashboard (start/stop)

## Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver
- Internet connection for CDN resources

## Development

The web interface uses:
- **FastAPI** for the backend API
- **Jinja2** for HTML templating
- **Tailwind CSS** (via CDN) for styling
- **JWT** for authentication
- **Vanilla JavaScript** for frontend interactions

## 🎭 Stealth Mode

The application uses advanced Chrome options to provide a clean, professional presentation:

- **No Automation Indicators**: Removes "Chrome is being controlled by automated test software" message
- **Native Appearance**: Browser looks and behaves like a regular Chrome instance
- **Full-Screen Mode**: Kiosk mode for distraction-free viewing
- **Optimized Performance**: Disabled unnecessary features for better performance

### Chrome Options Used:
- `--disable-infobars`: Removes automation notification
- `--disable-blink-features=AutomationControlled`: Hides automation detection
- `--excludeSwitches=["enable-automation"]`: Removes automation switches
- `--user-agent`: Sets realistic user agent string
- JavaScript execution to mask webdriver property

## Troubleshooting

1. **ChromeDriver Issues**: Ensure ChromeDriver version matches your Chrome browser version
2. **Port Conflicts**: If port 8000 is busy, modify the port in `run.py`
3. **Permission Issues**: Run the application with appropriate permissions for Chrome automation
4. **Login Issues**: Check that the SECRET_KEY in auth.py is set correctly
5. **Token Expiration**: JWT tokens expire after 30 minutes, requiring re-login

## License

This project is open source and available under the MIT License.

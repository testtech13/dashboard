import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from typing import Optional, Callable
from config import config_manager
from models import DashboardConfig, PageConfig, StatusResponse
from datetime import datetime


class DashboardController:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.is_running = False
        self.current_page_index = 0
        self.config: Optional[DashboardConfig] = None
        self.status_callback: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)

    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback

    def start_dashboard(self) -> bool:
        """Start the dashboard"""
        try:
            self.config = config_manager.get_config()
            if not self.config.pages:
                self.logger.error("No pages configured")
                return False

            self._setup_driver()
            self.is_running = True
            self.current_page_index = 0
            self.logger.info("Dashboard started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {e}")
            return False

    def stop_dashboard(self):
        """Stop the dashboard"""
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
            self.driver = None
        self.logger.info("Dashboard stopped")

    def _setup_driver(self):
        """Setup Chrome driver with full-screen options"""
        chrome_options = Options()

        # Full-screen and display options
        chrome_options.add_argument("--kiosk")  # Full-screen mode
        chrome_options.add_argument("--start-maximized")  # Start maximized

        # Disable automation indicators
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-infobars")  # Remove "Chrome is being controlled by automated test software"
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        # Additional options to make it look more like a regular browser
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Experimental options to hide automation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Specify ChromeDriver path (uncomment and modify if needed)
        # chromedriver_path = r"chromedriver-win64\chromedriver-win64\chromedriver.exe"
        # service = webdriver.ChromeService(executable_path=chromedriver_path)

        try:
            # Use service parameter if chromedriver_path is specified above
            # self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver = webdriver.Chrome(options=chrome_options)

            # Execute JavaScript to remove automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.logger.info("Chrome driver initialized successfully")
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def run_cycle(self):
        """Run the dashboard cycle"""
        if not self.is_running or not self.driver or not self.config:
            return

        try:
            page = self.config.pages[self.current_page_index]
            self.logger.info(f"Loading page: {page.url}")

            self.driver.get(page.url)

            # Wait for page to load
            time.sleep(2)

            # Update status
            if self.status_callback:
                status = self._get_status()
                self.status_callback(status)

            # Wait for configured duration
            time.sleep(page.duration_seconds)

            # Move to next page
            self.current_page_index += 1
            if self.current_page_index >= len(self.config.pages):
                if self.config.loop:
                    self.current_page_index = 0
                else:
                    self.stop_dashboard()
                    return

        except Exception as e:
            self.logger.error(f"Error in dashboard cycle: {e}")
            # Try to continue with next page
            self.current_page_index += 1
            if self.current_page_index >= len(self.config.pages):
                self.current_page_index = 0

    def _get_status(self) -> StatusResponse:
        """Get current status"""
        if not self.config:
            return StatusResponse(
                is_running=False,
                total_pages=0,
                last_updated=datetime.now()
            )

        current_page = None
        time_remaining = None

        if self.is_running and self.current_page_index < len(self.config.pages):
            current_page = self.config.pages[self.current_page_index]
            # This is approximate - in a real implementation you'd track actual time
            time_remaining = current_page.duration_seconds

        return StatusResponse(
            is_running=self.is_running,
            current_page_index=self.current_page_index if self.is_running else None,
            current_page=current_page,
            time_remaining=time_remaining,
            total_pages=len(self.config.pages),
            last_updated=datetime.now()
        )


# Global dashboard controller instance
dashboard_controller = DashboardController()

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from typing import Optional, Callable, Union
from config import config_manager
from models import DashboardConfig, PageConfig, StatusResponse
from datetime import datetime

# Browser selection constant - change this to "firefox" to use Firefox instead of Chrome
BROWSER_TYPE = "chrome"  # Options: "chrome" or "firefox"


class DashboardController:
    def __init__(self):
        self.driver: Optional[Union[webdriver.Chrome, webdriver.Firefox]] = None
        self.is_running = False
        self.current_page_index = 0
        self.config: Optional[DashboardConfig] = None
        self.status_callback: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)
        self.page_start_time: Optional[float] = None  # Track when current page started

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
        self.page_start_time = None  # Reset page start time
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
            self.driver = None
        self.logger.info("Dashboard stopped")

    def _setup_driver(self):
        """Setup browser driver with full-screen options"""
        if BROWSER_TYPE.lower() == "firefox":
            self._setup_firefox_driver()
        else:
            self._setup_chrome_driver()

    def _setup_chrome_driver(self):
        """Setup Chrome driver with full-screen options"""
        chrome_options = ChromeOptions()

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

        # Disable Google services that cause registration errors
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--force-fieldtrials=*BackgroundNetworking/Disabled/")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")

        # Additional stealth options to make it look more like a regular browser
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-background-media-download")
        chrome_options.add_argument("--disable-print-preview")
        chrome_options.add_argument("--disable-component-cloud-policy")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")

        # Suppress logging and errors
        chrome_options.add_argument("--log-level=3")  # Only show fatal errors
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")

        # Experimental options to hide automation (combine with logging exclusion)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self._apply_stealth_javascript()
            self.logger.info("Chrome driver initialized successfully")
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _setup_firefox_driver(self):
        """Setup Firefox driver with full-screen options"""
        gecko_driver_path = '/usr/local/bin/geckodriver'
        service = Service(executable_path=gecko_driver_path)
        options = Options()

        # Full-screen and display options
        options.add_argument("--kiosk")  # Full-screen mode
        options.add_argument("--start-maximized")  # Start maximized

        try:
            self.driver = webdriver.Firefox(service=service, options=options)
            self.logger.info("Firefox driver initialized successfully")
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize Firefox driver: {e}")

            raise
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize Firefox driver: {e}")
            raise

    def _apply_stealth_javascript(self):
        """Apply JavaScript stealth modifications to hide automation indicators"""
        if not self.driver:
            return

        self.driver.execute_script("""
            // Hide webdriver property
            try {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            } catch (e) {
                // Property might already be defined, continue
            }

            // Mock languages and plugins
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """)

    def run_cycle(self):
        """Run the dashboard cycle"""
        if not self.is_running or not self.driver or not self.config:
            return

        try:
            page = self.config.pages[self.current_page_index]
            self.logger.info(f"Loading page: {page.url}")

            # Record when this page started
            self.page_start_time = time.time()

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

            # Calculate actual remaining time
            if self.page_start_time is not None:
                elapsed_time = time.time() - self.page_start_time
                # Account for the 2-second page load delay
                adjusted_elapsed = max(0, elapsed_time - 2)
                time_remaining = max(0, int(current_page.duration_seconds - adjusted_elapsed))
            else:
                # Fallback to full duration if start time not available
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


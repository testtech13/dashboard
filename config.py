import json
import os
from typing import Optional
from models import DashboardConfig, PageConfig


class ConfigManager:
    def __init__(self, config_file: str = "dashboard_config.json"):
        self.config_file = config_file
        self._config: Optional[DashboardConfig] = None

    def load_config(self) -> DashboardConfig:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self._config = DashboardConfig(**data)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error loading config: {e}. Using default config.")
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()

        return self._config

    def save_config(self, config: DashboardConfig) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config.dict(), f, indent=2)
        self._config = config

    def get_config(self) -> DashboardConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load_config()
        return self._config

    def _get_default_config(self) -> DashboardConfig:
        """Get default configuration"""
        return DashboardConfig(
            pages=[
                PageConfig(
                    url="https://www.google.com",
                    duration_seconds=30,
                    name="Google"
                ),
                PageConfig(
                    url="https://www.github.com",
                    duration_seconds=45,
                    name="GitHub"
                )
            ],
            loop=True,
            auto_start=False
        )


# Global config manager instance
config_manager = ConfigManager()

from pathlib import Path
from typing import Any, Dict, Optional, List
import yaml
import toml


# Configuration manager for StaticFlow


class Config:
    """Configuration for StaticFlow."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration."""
        self.config = {
            "languages": ["en"],
            "default_language": "en",
            "language_config": {},
            "environment": "development"
        }
        if config_path:
            self.load(config_path)
            
    def load(self, config_path: Path) -> None:
        """Load configuration from file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        suffix = config_path.suffix.lower()
        with config_path.open("r", encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                loaded_config = yaml.safe_load(f)
            elif suffix == ".toml":
                loaded_config = toml.load(f)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")
                
            if loaded_config and isinstance(loaded_config, dict):
                self.config.update(loaded_config)
            else:
                raise ValueError(
                    f"Invalid configuration format in {config_path}. "
                    "Configuration must be a dictionary."
                )
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        
    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file."""
        save_path = config_path or self.config_path
        if not save_path:
            raise RuntimeError("No config file path set")
            
        suffix = save_path.suffix.lower()
        with save_path.open("w", encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                yaml.safe_dump(self.config, f)
            elif suffix == ".toml":
                toml.dump(self.config, f)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")
            
    def get_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.config.get("languages", ["en"])
        
    def get_default_language(self) -> str:
        """Get default language."""
        return self.config.get("default_language", "en")
        
    def get_language_config(self, lang: str) -> Dict[str, Any]:
        """Get language-specific configuration."""
        return self.config.get("language_config", {}).get(lang, {})

    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        required_fields = ["site_name", "base_url"]
        missing = [
            field for field in required_fields 
            if field not in self.config
        ]
        if missing:
            raise ValueError(
                f"Missing required config fields: {', '.join(missing)}"
            )
    
    def set_environment(self, env: str) -> None:
        """Set the current environment."""
        self.config["environment"] = env
        
    @property
    def environment(self) -> str:
        """Get the current environment."""
        return self.config.get("environment", "development")
    
    @property
    def config_path(self) -> Optional[Path]:
        """Get the path to the configuration file."""
        return self.config.get("_config_path") 
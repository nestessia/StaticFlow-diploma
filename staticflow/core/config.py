from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import toml

class Config:
    """Configuration manager for StaticFlow."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self._config: Dict[str, Any] = {}
        self._config_path = config_path
        self._environment = "development"
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, path: Path) -> None:
        """Load configuration from a YAML or TOML file."""
        if not isinstance(path, Path):
            path = Path(path)
            
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
            
        suffix = path.suffix.lower()
        with path.open("r", encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                self._config = yaml.safe_load(f)
            elif suffix == ".toml":
                self._config = toml.load(f)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")
                
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        required_fields = ["site_name", "base_url"]
        for field in required_fields:
            if field not in self._config:
                raise ValueError(f"Missing required config field: {field}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def set_environment(self, env: str) -> None:
        """Set the current environment."""
        self._environment = env
        
    @property
    def environment(self) -> str:
        """Get the current environment."""
        return self._environment
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config.copy() 
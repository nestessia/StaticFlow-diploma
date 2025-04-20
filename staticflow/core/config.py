from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
import toml


# Configuration manager for StaticFlow


class Config:
    """Configuration manager for StaticFlow."""
    
    def __init__(
        self, 
        config: Optional[Union[Path, str, Dict[str, Any]]] = None
    ):
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._environment = "development"
        
        if config:
            if isinstance(config, (str, Path)):
                self.load_config(config)
            elif isinstance(config, dict):
                self._config = config.copy()
                self._validate_config()
        else:
            # Empty config should be validated too
            self._validate_config()

    def load_config(self, path: Union[str, Path]) -> None:
        """Load configuration from a YAML or TOML file."""
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        suffix = path.suffix.lower()
        with path.open("r", encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                self._config = yaml.safe_load(f) or {}
            elif suffix == ".toml":
                self._config = toml.load(f)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")
                
        self._config_path = path
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        # Отладочный вывод для понимания структуры конфигурации
        print(f"VALIDATING CONFIG: {self._config}")
        
        required_fields = ["site_name", "base_url"]
        missing = [
            field for field in required_fields 
            if field not in self._config
        ]
        if missing:
            raise ValueError(
                f"Missing required config fields: {', '.join(missing)}"
            )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        value = self._config.get(key, default)
        print(f"CONFIG GET: {key} -> {value}")
        return value
    
    def get_nested(self, keys, default=None):
        """
        Получить значение из вложенных словарей по последовательности ключей.
        
        Args:
            keys: Список ключей для доступа к вложенным значениям
            default: Значение по умолчанию, если ключ не найден
            
        Returns:
            Значение или default, если ключ не найден
        """
        print(f"CONFIG GET_NESTED: {keys}")
        value = self._config
        try:
            for key in keys:
                print(f"  Accessing key: {key}, current value: {type(value)}")
                value = value[key]
            print(f"  Final value: {value}")
            return value
        except (KeyError, TypeError) as e:
            print(f"  Error accessing nested keys: {e}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        self._validate_config()  # Validate after changes
    
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
        
    def save(self) -> None:
        """Save the configuration back to file if loaded from one."""
        if not self._config_path:
            raise RuntimeError("No config file path set")
            
        suffix = self._config_path.suffix.lower()
        with self._config_path.open("w", encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                yaml.safe_dump(self._config, f)
            elif suffix == ".toml":
                toml.dump(self._config, f)
            else:
                raise ValueError(f"Unsupported config format: {suffix}") 
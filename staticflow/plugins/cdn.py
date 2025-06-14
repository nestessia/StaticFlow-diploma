from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib
import mimetypes
import requests
from .base import Plugin
from ..utils.logging import get_logger

logger = get_logger(__name__)


class CDNProvider:
    """Base class for CDN providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def upload_file(self, file_path: Path, content_type: str) -> Optional[str]:
        """Upload a file to CDN and return its URL."""
        raise NotImplementedError

    def delete_file(self, file_path: Path) -> bool:
        """Delete a file from CDN."""
        raise NotImplementedError

    def purge_cache(self, urls: List[str]) -> bool:
        """Purge cache for given URLs."""
        raise NotImplementedError


class CloudflareCDN(CDNProvider):
    """Cloudflare CDN implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_token = config.get('api_token')
        self.zone_id = config.get('zone_id')
        self.account_id = config.get('account_id')
        self.domain = config.get('domain')

    def upload_file(self, file_path: Path, content_type: str) -> Optional[str]:
        """Upload file to Cloudflare R2 storage."""
        try:
            # Generate unique key for the file
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
            key = f"{file_hash}/{file_path.name}"

            # Upload to R2
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/r2/buckets/{self.config['bucket']}/objects/{key}"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": content_type
            }

            with open(file_path, 'rb') as f:
                response = requests.put(url, headers=headers, data=f)
                response.raise_for_status()

            # Return public URL
            return f"https://{self.domain}/{key}"

        except Exception as e:
            logger.error(f"Failed to upload file to Cloudflare: {e}")
            return None

    def delete_file(self, file_path: Path) -> bool:
        """Delete file from Cloudflare R2 storage."""
        try:
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
            key = f"{file_hash}/{file_path.name}"

            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/r2/buckets/{self.config['bucket']}/objects/{key}"
            headers = {"Authorization": f"Bearer {self.api_token}"}

            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Failed to delete file from Cloudflare: {e}")
            return False

    def purge_cache(self, urls: List[str]) -> bool:
        """Purge Cloudflare cache for given URLs."""
        try:
            url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/purge_cache"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            data = {"files": urls}

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Failed to purge Cloudflare cache: {e}")
            return False


class CDNPlugin(Plugin):
    """Plugin for CDN integration."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider = None
        self.uploaded_files: Dict[str, str] = {}

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin with configuration."""
        if not config:
            return

        provider_name = config.get('provider', 'cloudflare')
        if provider_name == 'cloudflare':
            self.provider = CloudflareCDN(config)
        else:
            raise ValueError(f"Unsupported CDN provider: {provider_name}")

    def on_pre_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-build hook: prepare for CDN uploads."""
        self.uploaded_files.clear()
        return context

    def on_post_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-build hook: upload files to CDN."""
        if not self.provider:
            return context

        output_dir = context.get('output_dir')
        if not output_dir:
            return context

        static_dir = Path(output_dir) / 'static'
        if static_dir.exists():
            self._upload_directory(static_dir)

        media_dir = Path(output_dir) / 'media'
        if media_dir.exists():
            self._upload_directory(media_dir)

        return context

    def _upload_directory(self, directory: Path) -> None:
        """Upload all files from directory to CDN."""
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                content_type, _ = mimetypes.guess_type(str(file_path))
                if content_type:
                    cdn_url = self.provider.upload_file(file_path, content_type)
                    if cdn_url:
                        self.uploaded_files[str(file_path)] = cdn_url
        
    def get_cdn_url(self, local_path: str) -> Optional[str]:
        """Get CDN URL for a local file."""
        return self.uploaded_files.get(local_path)

    def purge_cache(self, urls: List[str]) -> bool:
        """Purge CDN cache for given URLs."""
        if not self.provider:
            return False
        return self.provider.purge_cache(urls)
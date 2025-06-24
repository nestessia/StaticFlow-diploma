"""
StaticFlow Media Plugin
Handles image and media processing for StaticFlow sites
"""

from pathlib import Path
import re
import shutil
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass
import mimetypes
from PIL import Image
import io

from .core.base import Plugin, PluginMetadata


@dataclass
class ImageSize:
    """Represents an image size configuration."""
    name: str
    width: Optional[int] = None
    height: Optional[int] = None
    quality: int = 80
    format: Optional[str] = None


class MediaPlugin(Plugin):
    """
    Plugin for processing and optimizing images and media files.
    
    Features:
    - Automatic image resizing and optimization
    - WebP conversion for modern browsers
    - Responsive image generation with srcset
    - Image placeholders for faster page loading
    - Video thumbnail generation
    - Media metadata extraction
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="media",
            version="0.1.0",
            description="Handles media processing for StaticFlow sites",
            author="StaticFlow Team",
            requires_config=False,
            priority=50  # Run before other content processing
        )
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.cdn_plugin = None
        self.image_sizes: Dict[str, ImageSize] = {}
        if config:
            self.initialize(config)
        
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin. Called when plugin is loaded."""
        super().initialize()
        self.setup(config)
        
    def setup(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Setup the plugin with configuration."""
        # Default configuration
        self.default_config = {
            "output_dir": "media",
            "source_dir": "static",
            "sizes": {
                "thumbnail": {"width": 200, "height": 200, "quality": 70},
                "small": {"width": 400, "quality": 80},
                "medium": {"width": 800, "quality": 85},
                "large": {"width": 1200, "quality": 90},
                "original": {"quality": 95}
            },
            "formats": ["webp", "original"],
            "generate_placeholders": True,
            "placeholder_size": 20,
            "process_videos": True,
            "video_thumbnail": True,
            "hash_filenames": True,
            "hash_length": 8
        }
        
        # Merge with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Create image sizes from config
        self.image_sizes: Dict[str, ImageSize] = {}
        for name, size_config in self.config["sizes"].items():
            self.image_sizes[name] = ImageSize(
                name=name,
                width=size_config.get("width"),
                height=size_config.get("height"),
                quality=size_config.get("quality", 80),
                format=size_config.get("format")
            )
        
        # Image and media regex patterns
        self.img_pattern = re.compile(r'<img\s+[^>]*src=["\'](.*?)["\'][^>]*>')
        self.srcset_pattern = re.compile(
            r'<img\s+[^>]*srcset=["\'](.*?)["\'][^>]*>'
        )
        self.video_pattern = re.compile(
            r'<video\s+[^>]*src=["\'](.*?)["\'][^>]*>'
        )
        self.audio_pattern = re.compile(
            r'<audio\s+[^>]*src=["\'](.*?)["\'][^>]*>'
        )
        
        # Processed media tracking
        self.processed_media: Dict[str, Dict[str, Any]] = {}
        
        # Ensure media directory exists
        self.media_dir = None
        if engine := getattr(self, "engine", None):
            if output_dir := getattr(engine.site, "output_dir", None):
                if isinstance(output_dir, str):
                    output_dir = Path(output_dir)
                if isinstance(self.config["output_dir"], str):
                    self.config["output_dir"] = Path(self.config["output_dir"])
                self.media_dir = output_dir / self.config["output_dir"]
                self.media_dir.mkdir(parents=True, exist_ok=True)
            
            # Get CDN plugin if available
            if cdn_plugin := engine.get_plugin("cdn"):
                self.cdn_plugin = cdn_plugin
    
    def on_pre_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-build hook: prepare media directory."""
        if engine := getattr(self, "engine", None):
            if output_dir := getattr(engine.site, "output_dir", None):
                self.media_dir = output_dir / self.config["output_dir"]
                self.media_dir.mkdir(parents=True, exist_ok=True)
        return context
    
    def on_post_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-build hook: cleanup unused media files."""
        # Additional post-build operations could be added here
        return context
    
    def on_pre_asset(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-asset hook: process media files before copying to output."""
        if "file_path" in context and self._is_media_file(context["file_path"]):
            source_path = context["file_path"]
            if self._is_image(source_path):
                self._process_image(source_path)
            elif self._is_video(source_path) and self.config["process_videos"]:
                self._process_video(source_path)
            elif self._is_audio(source_path):
                self._process_audio(source_path)
        return context
    
    def process_content(self, content: str) -> str:
        """Process content and replace image/media tags with optimized versions."""
        if not self.media_dir:
            return content
        
        # Process image tags
        content = self.img_pattern.sub(self._replace_image, content)
        
        # Skip if srcset is already defined
        if not self.srcset_pattern.search(content):
            content = self.img_pattern.sub(self._add_srcset, content)
        
        # Process video tags
        if self.config["process_videos"]:
            content = self.video_pattern.sub(self._replace_video, content)
        
        # Process audio tags
        content = self.audio_pattern.sub(self._replace_audio, content)
        
        return content
    
    def _replace_image(self, match) -> str:
        """Replace image src with optimized version."""
        img_tag = match.group(0)
        src = match.group(1)
        
        # Skip external images or already processed ones
        if src.startswith(('http://', 'https://', '//')):
            return img_tag
            
        if src.startswith(f'/{self.config["output_dir"]}'):
            return img_tag
        
        # Check if image exists
        if not self._find_source_file(src):
            return img_tag
        
        # Process the image
        try:
            processed = self._process_image(self._find_source_file(src))
            if processed and "default" in processed:
                new_src = processed["default"]
                return img_tag.replace(src, new_src)
            return img_tag
        except Exception as e:
            print(f"Error processing image {src}: {e}")
            return img_tag
    
    def _add_srcset(self, match) -> str:
        """Add srcset attribute to img tags for responsive images."""
        img_tag = match.group(0)
        src = match.group(1)
        
        # Skip external images
        if src.startswith(('http://', 'https://', '//')):
            return img_tag
            
        # Skip already processed images
        if src.startswith(f'/{self.config["output_dir"]}'):
            return img_tag
        
        # Check if image exists
        source_file = self._find_source_file(src)
        if not source_file:
            return img_tag
        
        # Process the image
        try:
            processed = self._process_image(source_file)
            if not processed:
                return img_tag
                
            # Generate srcset attribute
            srcset_values = []
            sizes_values = []
            
            for size_name, size_data in self.image_sizes.items():
                if size_name == "original":
                    continue
                    
                if size_name in processed and "width" in processed and size_data.width:
                    srcset_values.append(f"{processed[size_name]} {size_data.width}w")
                    sizes_val = f"(max-width: {size_data.width}px) {size_data.width}px"
                    sizes_values.append(sizes_val)
            
            if srcset_values and "default" in processed:
                # Replace src with default size
                img_tag = img_tag.replace(src, processed["default"])
                
                # Add srcset and sizes attributes
                srcset_attr = f' srcset="{", ".join(srcset_values)}"'
                sizes_attr = f' sizes="{", ".join(sizes_values)}, 100vw"'
                
                # Insert attributes before closing tag
                closing_pos = img_tag.rfind('>')
                if closing_pos > 0:
                    img_tag = f"{img_tag[:closing_pos]}{srcset_attr}{sizes_attr}{img_tag[closing_pos:]}"
                
            return img_tag
        except Exception as e:
            print(f"Error adding srcset for {src}: {e}")
            return img_tag
    
    def _replace_video(self, match) -> str:
        """Replace video src with optimized version."""
        video_tag = match.group(0)
        src = match.group(1)
        
        # Skip external videos
        if src.startswith(('http://', 'https://', '//')):
            return video_tag
            
        # Skip already processed videos
        if src.startswith(f'/{self.config["output_dir"]}'):
            return video_tag
        
        # Check if video exists
        source_file = self._find_source_file(src)
        if not source_file:
            return video_tag
        
        # Process the video
        try:
            processed = self._process_video(source_file)
            if processed and "default" in processed:
                new_src = processed["default"]
                video_tag = video_tag.replace(src, new_src)
                
                # Add poster if thumbnail was generated
                if "thumbnail" in processed and "poster" not in video_tag:
                    poster_attr = f' poster="{processed["thumbnail"]}"'
                    closing_pos = video_tag.rfind('>')
                    if closing_pos > 0:
                        video_tag = f"{video_tag[:closing_pos]}{poster_attr}{video_tag[closing_pos:]}"
                
            return video_tag
        except Exception as e:
            print(f"Error processing video {src}: {e}")
            return video_tag
    
    def _replace_audio(self, match) -> str:
        """Replace audio src with optimized version."""
        audio_tag = match.group(0)
        src = match.group(1)
        
        # Skip external audio
        if src.startswith(('http://', 'https://', '//')):
            return audio_tag
            
        # Skip already processed audio
        if src.startswith(f'/{self.config["output_dir"]}'):
            return audio_tag
        
        # Check if audio exists
        source_file = self._find_source_file(src)
        if not source_file:
            return audio_tag
        
        # Process the audio
        try:
            processed = self._process_audio(source_file)
            if processed and "default" in processed:
                new_src = processed["default"]
                return audio_tag.replace(src, new_src)
            return audio_tag
        except Exception as e:
            print(f"Error processing audio {src}: {e}")
            return audio_tag
    
    def _process_image(self, source_path: Path) -> Optional[Dict[str, Any]]:
        """Process an image file and create various sizes and formats."""
        if not self.media_dir or not source_path.exists():
            return None
        
        # Skip if already processed
        cache_key = str(source_path)
        if cache_key in self.processed_media:
            return self.processed_media[cache_key]
            
        try:
            with Image.open(source_path) as img:
                orig_format = img.format or "JPEG"
                orig_width, orig_height = img.size
                
                # Create results dictionary
                result = {
                    "source": str(source_path),
                    "width": orig_width,
                    "height": orig_height,
                    "format": orig_format
                }
                
                # Get file hash for caching
                file_hash = ""
                if self.config["hash_filenames"]:
                    with open(source_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hash = file_hash[:self.config["hash_length"]]
                
                # Create media directory structure
                rel_dir = source_path.parent.name if not source_path.is_absolute() else ""
                media_subdir = self.media_dir / rel_dir
                media_subdir.mkdir(parents=True, exist_ok=True)
                
                # Create base filename
                base_name = source_path.stem
                if file_hash:
                    base_name = f"{base_name}-{file_hash}"
                
                # Получаем base_url из engine.config
                base_url = ""
                if hasattr(self, "engine") and hasattr(self.engine, "config"):
                    base_url = self.engine.config.get("base_url", "")
                    if base_url.endswith("/"):
                        base_url = base_url[:-1]
                
                # Process each size
                for size_name, size_config in self.image_sizes.items():
                    # Skip if no width/height specified for non-original sizes
                    if size_name != "original" and not (size_config.width or size_config.height):
                        continue
                    
                    # Resize image
                    if size_name == "original":
                        resized_img = img.copy()
                    else:
                        # Calculate new dimensions
                        if size_config.width and size_config.height:
                            resized_img = self._resize_and_crop(
                                img, 
                                size_config.width, 
                                size_config.height
                            )
                        elif size_config.width:
                            new_height = int(orig_height * (size_config.width / orig_width))
                            resized_img = img.resize(
                                (size_config.width, new_height), 
                                Image.LANCZOS
                            )
                        elif size_config.height:
                            new_width = int(orig_width * (size_config.height / orig_height))
                            resized_img = img.resize(
                                (new_width, size_config.height), 
                                Image.LANCZOS
                            )
                        else:
                            resized_img = img.copy()
                    
                    # Process each format
                    for fmt in self.config["formats"]:
                        # Skip if format is "original" but we're not processing original size
                        if fmt == "original" and size_name != "original":
                            continue

                        output_format = fmt.upper() if fmt != "original" else orig_format

                        ext = fmt.lower() if fmt != "original" else source_path.suffix[1:].lower()

                        if size_name == "original" and fmt == "original":
                            filename = f"{base_name}{source_path.suffix}"
                        else:
                            filename = f"{base_name}-{size_name}.{ext}"

                        save_path = media_subdir / filename

                        with io.BytesIO() as output:
                            save_quality = size_config.quality

                            if output_format == "JPEG" or output_format == "WEBP":
                                resized_img.save(
                                    output,
                                    format=output_format,
                                    quality=save_quality,
                                    optimize=True
                                )
                            elif output_format == "PNG":
                                resized_img.save(
                                    output,
                                    format=output_format,
                                    compress_level=9,
                                    optimize=True
                                )
                            else:
                                resized_img.save(output, format=output_format)

                            with open(save_path, "wb") as f:
                                f.write(output.getvalue())

                        if rel_dir:
                            rel_path = (
                                f"{base_url}/{self.config['output_dir']}"
                                f"/{rel_dir}/{filename}"
                            )
                        else:
                            rel_path = (
                                f"{base_url}/{self.config['output_dir']}"
                                f"/{filename}"
                            )

                        if size_name not in result:
                            result[size_name] = rel_path

                        if size_name == "medium" and fmt != "original":
                            result["default"] = rel_path
                        elif size_name == "original" and "default" not in result:
                            result["default"] = rel_path

                if self.config["generate_placeholders"]:
                    placeholder_size = self.config["placeholder_size"]
                    placeholder_height = int(orig_height * (placeholder_size / orig_width))
                    placeholder = img.resize(
                        (placeholder_size, placeholder_height), 
                        Image.LANCZOS
                    )

                    placeholder_filename = f"{base_name}-placeholder.webp"
                    placeholder_path = media_subdir / placeholder_filename
                    placeholder.save(placeholder_path, format="WEBP", quality=30)

                    if rel_dir:
                        placeholder_url = (
                            f"{base_url}/{self.config['output_dir']}"
                            f"/{rel_dir}/{placeholder_filename}"
                        )
                    else:
                        placeholder_url = (
                            f"{base_url}/{self.config['output_dir']}"
                            f"/{placeholder_filename}"
                        )
                    result["placeholder"] = placeholder_url

                self.processed_media[cache_key] = result
                return result

        except Exception as e:
            print(f"Error processing image {source_path}: {e}")
            return None

    def _process_video(self, source_path: Path) -> Optional[Dict[str, Any]]:
        """Process a video file."""
        if not self.media_dir or not source_path.exists():
            return None

        cache_key = str(source_path)
        if cache_key in self.processed_media:
            return self.processed_media[cache_key]

        try:
            result = {
                "source": str(source_path)
            }

            file_hash = ""
            if self.config["hash_filenames"]:
                with open(source_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    file_hash = file_hash[:self.config["hash_length"]]

            rel_dir = source_path.parent.name if not source_path.is_absolute() else ""
            media_subdir = self.media_dir / rel_dir
            media_subdir.mkdir(parents=True, exist_ok=True)

            base_name = source_path.stem
            if file_hash:
                base_name = f"{base_name}-{file_hash}"

            base_url = ""
            if hasattr(self, "engine") and hasattr(self.engine, "config"):
                base_url = self.engine.config.get("base_url", "")
                if base_url.endswith("/"):
                    base_url = base_url[:-1]

            ext = source_path.suffix
            output_path = media_subdir / f"{base_name}{ext}"
            shutil.copy2(source_path, output_path)

            if rel_dir:
                rel_path = f"{base_url}/{self.config['output_dir']}/{rel_dir}/{base_name}{ext}"
            else:
                rel_path = f"{base_url}/{self.config['output_dir']}/{base_name}{ext}"
            result["default"] = rel_path
            
            # Generate thumbnail if enabled
            if self.config["video_thumbnail"]:
                try:
                    import cv2
                    # Open video
                    cap = cv2.VideoCapture(str(source_path))
                    # Get frame from the middle of the video
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Create PIL Image
                        thumbnail = Image.fromarray(frame_rgb)
                        
                        # Save thumbnail
                        thumbnail_filename = f"{base_name}-thumbnail.webp"
                        thumbnail_path = media_subdir / thumbnail_filename
                        
                        # Resize if needed
                        if "medium" in self.image_sizes:
                            width = self.image_sizes["medium"].width
                            if width:
                                w, h = thumbnail.size
                                new_h = int(h * (width / w))
                                thumbnail = thumbnail.resize(
                                    (width, new_h), 
                                    Image.LANCZOS
                                )
                        thumbnail.save(thumbnail_path, format="WEBP", quality=85)
                        
                        # Add to result
                        if rel_dir:
                            thumbnail_url = f"{base_url}/{self.config['output_dir']}/{rel_dir}/{thumbnail_filename}"
                        else:
                            thumbnail_url = f"{base_url}/{self.config['output_dir']}/{thumbnail_filename}"
                        result["thumbnail"] = thumbnail_url
                    
                    # Release video
                    cap.release()
                except (ImportError, Exception) as e:
                    print(f"Error generating video thumbnail: {e}")
            
            # Cache and return result
            self.processed_media[cache_key] = result
            return result
                
        except Exception as e:
            print(f"Error processing video {source_path}: {e}")
            return None
    
    def _process_audio(self, source_path: Path) -> Optional[Dict[str, Any]]:
        """Process an audio file."""
        if not self.media_dir or not source_path.exists():
            return None
        
        # Skip if already processed
        cache_key = str(source_path)
        if cache_key in self.processed_media:
            return self.processed_media[cache_key]
        
        try:
            # Create results dictionary
            result = {
                "source": str(source_path)
            }
            
            # Get file hash for caching
            file_hash = ""
            if self.config["hash_filenames"]:
                with open(source_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    file_hash = file_hash[:self.config["hash_length"]]
            
            # Create media directory structure
            rel_dir = source_path.parent.name if not source_path.is_absolute() else ""
            media_subdir = self.media_dir / rel_dir
            media_subdir.mkdir(parents=True, exist_ok=True)
            
            # Create base filename
            base_name = source_path.stem
            if file_hash:
                base_name = f"{base_name}-{file_hash}"
            
            # Получаем base_url из engine.config
            base_url = ""
            if hasattr(self, "engine") and hasattr(self.engine, "config"):
                base_url = self.engine.config.get("base_url", "")
                if base_url.endswith("/"):
                    base_url = base_url[:-1]
            
            # Copy audio to media directory
            ext = source_path.suffix
            output_path = media_subdir / f"{base_name}{ext}"
            shutil.copy2(source_path, output_path)
            
            # Add to result
            if rel_dir:
                rel_path = f"{base_url}/{self.config['output_dir']}/{rel_dir}/{base_name}{ext}"
            else:
                rel_path = f"{base_url}/{self.config['output_dir']}/{base_name}{ext}"
            result["default"] = rel_path
            
            # Cache and return result
            self.processed_media[cache_key] = result
            return result
                
        except Exception as e:
            print(f"Error processing audio {source_path}: {e}")
            return None
    
    def _resize_and_crop(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """Resize and crop an image to fit target dimensions while maintaining aspect ratio."""
        orig_width, orig_height = img.size
        # Calculate ratios
        width_ratio = target_width / orig_width
        height_ratio = target_height / orig_height
        
        # Use larger ratio to ensure image covers the area
        if width_ratio > height_ratio:
            new_width = target_width
            new_height = int(orig_height * width_ratio)
        else:
            new_width = int(orig_width * height_ratio)
            new_height = target_height
            
        # Resize
        resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Calculate crop position
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # Crop
        return resized.crop((left, top, right, bottom))
    
    def _find_source_file(self, src: str) -> Optional[Path]:
        """Find the source file for a given src attribute."""
        if not src:
            return None
            
        # Handle absolute URLs
        if src.startswith(('http://', 'https://', '//')):
            return None
            
        # Handle relative URLs
        if src.startswith('/'):
            src = src.lstrip('/')
            
        # Try different locations
        if engine := getattr(self, "engine", None):
            static_dir = Path(engine.config.get("static_dir", "static"))
            if (static_dir / src).exists():
                return static_dir / src
                
            # Check in source directory
            if source_dir := getattr(engine.site, "source_dir", None):
                if (source_dir / src).exists():
                    return source_dir / src
                    
                # Check in static subdirectory
                if (source_dir / "static" / src).exists():
                    return source_dir / "static" / src
        
        # Try local path
        local_path = Path(src)
        if local_path.exists():
            return local_path
            
        return None
    
    def _is_media_file(self, path: Path) -> bool:
        """Check if a file is a media file."""
        return self._is_image(path) or self._is_video(path) or self._is_audio(path)
    
    def _is_image(self, path: Path) -> bool:
        """Check if a file is an image."""
        if not path:
            return False
            
        mime, _ = mimetypes.guess_type(str(path))
        return mime is not None and mime.startswith('image/')
    
    def _is_video(self, path: Path) -> bool:
        """Check if a file is a video."""
        if not path:
            return False
            
        mime, _ = mimetypes.guess_type(str(path))
        return mime is not None and mime.startswith('video/')
    
    def _is_audio(self, path: Path) -> bool:
        """Check if a file is an audio file."""
        if not path:
            return False
            
        mime, _ = mimetypes.guess_type(str(path))
        return mime is not None and mime.startswith('audio/') 
    
    def _get_media_dir(self, file_path: Path) -> str:
        """Get URL for media file, using CDN if available."""
        if self.cdn_plugin:
            if cdn_url := self.cdn_plugin.get_cdn_url(str(file_path)):
                return cdn_url
                
        # Fallback to local URL
        if engine := getattr(self, "engine", None):
            if base_url := getattr(engine.site, "base_url", None):
                return f"{base_url}/{file_path.relative_to(engine.site.output_dir)}"
                
        return str(file_path)
        
    def process_content(self, content: str) -> str:
        """Process content and replace media URLs with CDN URLs if available."""
        # Process images
        content = self.img_pattern.sub(
            lambda m: self._process_image_tag(m.group(0)),
            content
        )
        
        # Process videos
        content = self.video_pattern.sub(
            lambda m: self._process_video_tag(m.group(0)),
            content
        )
        
        # Process audio
        content = self.audio_pattern.sub(
            lambda m: self._process_audio_tag(m.group(0)),
            content
        )
        
        return content
        
    def _process_image_tag(self, tag: str) -> str:
        """Process image tag and update src/srcset attributes."""
        # Extract src attribute
        src_match = re.search(r'src=["\'](.*?)["\']', tag)
        if not src_match:
            return tag
            
        src = src_match.group(1)
        file_path = Path(src)
        
        # Get CDN URL
        cdn_url = self._get_media_dir(file_path)
        
        # Update src attribute
        tag = tag.replace(f'src="{src}"', f'src="{cdn_url}"')
        
        # Update srcset if present
        srcset_match = re.search(r'srcset=["\'](.*?)["\']', tag)
        if srcset_match:
            srcset = srcset_match.group(1)
            new_srcset = []
            for item in srcset.split(','):
                url, size = item.strip().split(' ')
                url_path = Path(url)
                cdn_url = self._get_media_dir(url_path)
                new_srcset.append(f"{cdn_url} {size}")
            tag = tag.replace(f'srcset="{srcset}"', f'srcset="{", ".join(new_srcset)}"')
            
        return tag
        
    def _process_video_tag(self, tag: str) -> str:
        """Process video tag and update src/poster attributes."""
        # Extract src attribute
        src_match = re.search(r'src=["\'](.*?)["\']', tag)
        if src_match:
            src = src_match.group(1)
            file_path = Path(src)
            cdn_url = self._get_media_dir(file_path)
            tag = tag.replace(f'src="{src}"', f'src="{cdn_url}"')
            
        # Extract poster attribute
        poster_match = re.search(r'poster=["\'](.*?)["\']', tag)
        if poster_match:
            poster = poster_match.group(1)
            file_path = Path(poster)
            cdn_url = self._get_media_dir(file_path)
            tag = tag.replace(f'poster="{poster}"', f'poster="{cdn_url}"')
            
        return tag
        
    def _process_audio_tag(self, tag: str) -> str:
        """Process audio tag and update src attribute."""
        src_match = re.search(r'src=["\'](.*?)["\']', tag)
        if src_match:
            src = src_match.group(1)
            file_path = Path(src)
            cdn_url = self._get_media_dir(file_path)
            tag = tag.replace(f'src="{src}"', f'src="{cdn_url}"')
            
        return tag

    def process_markdown_content(self, content: str) -> str:
        """Process markdown content and replace relative media links with absolute URLs."""
        if not hasattr(self, "engine") or not self.engine:
            return content
        
        # Get configuration
        site_url = self.engine.config.get("base_url", "")
        media_dir = self.engine.config.get("media_dir", "media")
        
        if site_url.endswith("/"):
            site_url = site_url[:-1]
        
        # Pattern for markdown image links: ![alt](src)
        markdown_img_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        
        def replace_markdown_image(match):
            alt_text = match.group(1)
            src = match.group(2)
            
            # Skip external images
            if src.startswith(('http://', 'https://', '//')):
                return match.group(0)
            
            # Skip already absolute URLs
            if src.startswith(f'{site_url}/'):
                return match.group(0)
            
            # Remove leading slash if present
            if src.startswith('/'):
                src = src[1:]
            
            # If it's a media file, make it absolute
            if src.startswith(media_dir) or src.startswith(f'{media_dir}/'):
                # Already in media directory
                absolute_src = f"{site_url}/{src}"
            else:
                # Assume it's in media directory
                absolute_src = f"{site_url}/{media_dir}/{src}"
            
            return f"![{alt_text}]({absolute_src})"
        
        # Process markdown image links
        content = markdown_img_pattern.sub(replace_markdown_image, content)
        
        # Pattern for markdown video links: !VIDEO(src)
        markdown_video_pattern = re.compile(r'!VIDEO\(([^)]+)\)')
        
        def replace_markdown_video(match):
            src = match.group(1)
            
            # Skip external videos
            if src.startswith(('http://', 'https://', '//')):
                return match.group(0)
            
            # Skip already absolute URLs
            if src.startswith(f'{site_url}/'):
                return match.group(0)
            
            # Remove leading slash if present
            if src.startswith('/'):
                src = src[1:]
            
            # If it's a media file, make it absolute
            if src.startswith(media_dir) or src.startswith(f'{media_dir}/'):
                # Already in media directory
                absolute_src = f"{site_url}/{src}"
            else:
                # Assume it's in media directory
                absolute_src = f"{site_url}/{media_dir}/{src}"
            
            return f"!VIDEO({absolute_src})"
        
        # Process markdown video links
        content = markdown_video_pattern.sub(replace_markdown_video, content)
        
        # Pattern for markdown audio links: !AUDIO(src)
        markdown_audio_pattern = re.compile(r'!AUDIO\(([^)]+)\)')
        
        def replace_markdown_audio(match):
            src = match.group(1)
            
            # Skip external audio
            if src.startswith(('http://', 'https://', '//')):
                return match.group(0)
            
            # Skip already absolute URLs
            if src.startswith(f'{site_url}/'):
                return match.group(0)
            
            # Remove leading slash if present
            if src.startswith('/'):
                src = src[1:]
            
            # If it's a media file, make it absolute
            if src.startswith(media_dir) or src.startswith(f'{media_dir}/'):
                # Already in media directory
                absolute_src = f"{site_url}/{src}"
            else:
                # Assume it's in media directory
                absolute_src = f"{site_url}/{media_dir}/{src}"
            
            return f"!AUDIO({absolute_src})"
        
        # Process markdown audio links
        content = markdown_audio_pattern.sub(replace_markdown_audio, content)
        
        return content
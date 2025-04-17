"""
GitHub Pages Deployment Module for StaticFlow

This module provides functionality to deploy StaticFlow sites to GitHub Pages.
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
import tempfile
from typing import Dict, Any, Optional, List, Tuple


class GitHubPagesDeployer:
    """
    Deployer class for GitHub Pages integration
    """
    
    def __init__(self, site_path: str = "public"):
        """
        Initialize the GitHub Pages deployer
        
        Args:
            site_path: Path to the built site (defaults to "public")
        """
        self.site_path = Path(site_path)
        self.config_path = Path("deploy/github_pages.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load deployment configuration from file
        
        Returns:
            Dictionary with deployment configuration
        """
        if not self.config_path.exists():
            # Create default config
            default_config = {
                "repo_url": "",
                "branch": "gh-pages",
                "cname": "",
                "username": "",
                "email": "",
                "token": "",
                "last_deployment": None,
                "history": []
            }
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default config
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            return default_config
        
        # Load existing config
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error parsing config file {self.config_path}, using defaults")
            return {
                "repo_url": "",
                "branch": "gh-pages",
                "cname": "",
                "username": "",
                "email": "",
                "token": "",
                "last_deployment": None,
                "history": []
            }
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """
        Save deployment configuration to file
        
        Args:
            config: Configuration to save (uses self.config if None)
        """
        if config is not None:
            self.config = config
            
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_config(self, **kwargs) -> None:
        """
        Update deployment configuration
        
        Args:
            **kwargs: Key-value pairs to update in the configuration
        """
        self.config.update(kwargs)
        self.save_config()
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the deployment configuration
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        if not self.config.get("repo_url"):
            errors.append("Repository URL is required")
            
        if not self.config.get("username"):
            errors.append("GitHub username is required")
            
        if not self.config.get("email"):
            errors.append("Git email is required")
            
        # Validate repository URL format
        repo_url = self.config.get("repo_url", "")
        if repo_url and not (repo_url.startswith("https://github.com/") or
                              repo_url.startswith("git@github.com:")):
            errors.append("Repository URL must be a valid GitHub URL")
            
        return (len(errors) == 0, errors)
    
    def _run_command(self, command: List[str], cwd: Optional[str] = None,
                     env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
        """
        Run a shell command and return results
        
        Args:
            command: Command parts as list
            cwd: Working directory
            env: Environment variables
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    
    def deploy(self) -> Tuple[bool, str]:
        """
        Deploy the site to GitHub Pages
        
        Returns:
            Tuple of (success, message)
        """
        # Validate configuration
        is_valid, errors = self.validate_config()
        if not is_valid:
            return False, f"Invalid configuration: {', '.join(errors)}"
        
        # Check if site exists
        if not self.site_path.exists() or not self.site_path.is_dir():
            return False, f"Site directory not found at {self.site_path}"
        
        # Extract config values
        repo_url = self.config["repo_url"]
        branch = self.config["branch"]
        username = self.config["username"]
        email = self.config["email"]
        cname = self.config.get("cname", "")
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Set up git environment
            git_env = os.environ.copy()
            git_env["GIT_AUTHOR_NAME"] = username
            git_env["GIT_AUTHOR_EMAIL"] = email
            git_env["GIT_COMMITTER_NAME"] = username
            git_env["GIT_COMMITTER_EMAIL"] = email
            
            # If we have a token, use HTTPS with credentials
            if self.config.get("token"):
                token = self.config["token"]
                # Convert SSH URL to HTTPS with token if needed
                if repo_url.startswith("git@github.com:"):
                    repo_path = repo_url.split("git@github.com:")[1]
                    repo_url = f"https://{username}:{token}@github.com/{repo_path}"
                elif repo_url.startswith("https://github.com/"):
                    repo_path = repo_url.split("https://github.com/")[1]
                    repo_url = f"https://{username}:{token}@github.com/{repo_path}"
            
            # Initialize git repo
            code, out, err = self._run_command(
                ["git", "init"],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                return False, f"Failed to initialize git repository: {err}"
            
            # Set remote
            code, out, err = self._run_command(
                ["git", "remote", "add", "origin", repo_url],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                return False, f"Failed to set git remote: {err}"
                
            # Configure git
            self._run_command(
                ["git", "config", "user.name", username],
                cwd=temp_dir,
                env=git_env
            )
            
            self._run_command(
                ["git", "config", "user.email", email],
                cwd=temp_dir,
                env=git_env
            )
            
            # Try to fetch the branch if it exists
            branch_exists = False
            code, out, err = self._run_command(
                ["git", "fetch", "origin", branch],
                cwd=temp_dir,
                env=git_env
            )
            if code == 0:
                # Branch exists, check it out
                code, out, err = self._run_command(
                    ["git", "checkout", "-b", branch, f"origin/{branch}"],
                    cwd=temp_dir,
                    env=git_env
                )
                if code == 0:
                    branch_exists = True
            
            if not branch_exists:
                # Create a new branch
                self._run_command(
                    ["git", "checkout", "--orphan", branch],
                    cwd=temp_dir,
                    env=git_env
                )
            
            # Clean the working directory
            for item in temp_path.iterdir():
                if item.name == ".git":
                    continue
                    
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            
            # Copy site content to the repo
            for item in self.site_path.iterdir():
                if item.is_dir():
                    shutil.copytree(
                        item,
                        temp_path / item.name,
                        dirs_exist_ok=True
                    )
                else:
                    shutil.copy2(item, temp_path / item.name)
            
            # Create CNAME file if specified
            if cname:
                cname_path = temp_path / "CNAME"
                with open(cname_path, "w") as f:
                    f.write(cname)
            
            # Add all files
            code, out, err = self._run_command(
                ["git", "add", "."],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                return False, f"Failed to add files to git: {err}"
            
            # Check if there are changes
            code, out, err = self._run_command(
                ["git", "status", "--porcelain"],
                cwd=temp_dir,
                env=git_env
            )
            
            if not out.strip():
                # No changes to commit
                return True, "No changes to deploy"
            
            # Commit changes
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            code, out, err = self._run_command(
                ["git", "commit", "-m", f"Deployed at {timestamp}"],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                return False, f"Failed to commit changes: {err}"
            
            # Push to remote
            code, out, err = self._run_command(
                ["git", "push", "-u", "origin", branch],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                return False, f"Failed to push to GitHub: {err}"
            
            # Update deployment history
            import datetime
            self.config.setdefault("history", [])
            self.config["history"].insert(0, {
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success"
            })
            
            # Limit history to 10 entries
            if len(self.config["history"]) > 10:
                self.config["history"] = self.config["history"][:10]
                
            self.config["last_deployment"] = datetime.datetime.now().isoformat()
            self.save_config()
            
            return True, "Successfully deployed to GitHub Pages"
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """
        Get the current deployment status
        
        Returns:
            Dictionary with deployment status
        """
        return {
            "configured": bool(self.config.get("repo_url")),
            "last_deployment": self.config.get("last_deployment"),
            "history": self.config.get("history", []),
            "config": {
                "repo_url": self.config.get("repo_url", ""),
                "branch": self.config.get("branch", "gh-pages"),
                "cname": self.config.get("cname", ""),
                "username": self.config.get("username", ""),
                "email": self.config.get("email", ""),
                # Don't expose the token
                "has_token": bool(self.config.get("token"))
            }
        } 
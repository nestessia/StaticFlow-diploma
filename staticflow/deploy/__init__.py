"""
StaticFlow deploy module
Used for deploying StaticFlow sites to various platforms
"""

from .github_pages import GitHubPagesDeployer

__all__ = ['GitHubPagesDeployer'] 
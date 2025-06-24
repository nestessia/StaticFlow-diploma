---
title: Deployment
date: 2025-05-20
author: nestessia
tags: [deployment, hosting, server]
format: markdown
template: en_page.html
language: en
---

## 🌐 Deployment

StaticFlow supports automatic deployment to various platforms:

### 🐙 GitHub Pages

```bash
# Setup via CLI
staticflow deploy setup github-pages

# Run deployment
staticflow deploy github-pages
```

Or use the built-in admin panel for setup and deployment (available at `/admin/deploy`).

**🔐 Secure GitHub Token Storage:**

StaticFlow ensures secure storage of GitHub tokens:
- 🔒 Tokens are encrypted before saving to the configuration file
- 🌍 Environment variable support (`GITHUB_TOKEN`, `STATICFLOW_GITHUB_TOKEN`)
- ⏰ Token expiration checking and warnings
- 📝 Ability to specify custom commit messages during deployment

**📋 Required information for deployment:**
- 🔗 Repository URL (required)
- 👤 GitHub username (required)
- 📧 Git Email (required)
- 🔑 GitHub Token (recommended)
- 🌿 Deployment branch (default: gh-pages)
- 🌐 CNAME for custom domain (optional)
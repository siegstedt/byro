# Contributing to Byro

Thank you for your interest in contributing to Byro! This document provides guidelines and information for contributors.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Testing Requirements](#testing-requirements)
5. [Pull Request Process](#pull-request-process)
6. [Architecture Guidelines](#architecture-guidelines)
7. [Security Considerations](#security-considerations)

## 🚀 Getting Started

Byro is a proprietary legal document management system designed for family office use. Before contributing, please:

1. Read the [README.md](README.md) for project overview and setup instructions
2. Review the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards
3. Understand the [LICENSE.md](LICENSE.md) terms

## 🛠 Development Setup

### Prerequisites
- Docker Desktop
- Git
- OpenAI API Key (for AI features)

### Local Development
```bash
# Clone the repository
git clone https://github.com/siegstedt/byro.git
cd byro

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Start development environment
docker-compose up --build
```

### Accessing the Application
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Database GUI:** http://localhost:5050

## 📝 Code Style Guidelines

### Python Backend (FastAPI)
- **Formatter:** Black (`black .`)
- **Linter:** Ruff (`ruff check .`) or Flake8
- **Type Hints:** Required for all functions
- **Imports:** Standard library → Third-party → Local imports
- **Naming:** snake_case for variables/functions, PascalCase for classes
- **Docstrings:** Use Google-style docstrings for complex functions

### TypeScript Frontend (Next.js)
- **Formatter:** Prettier (configured in package.json)
- **Linter:** ESLint (`npm run lint`)
- **Naming:** camelCase for variables/functions, PascalCase for components
- **Imports:** Use absolute imports with `@/` prefix
- **Types:** Define interfaces for all data structures

### General Guidelines
- **Commits:** Write clear, descriptive commit messages
- **Branches:** Use descriptive branch names (e.g., `feature/add-pdf-viewer`, `fix/dark-mode-sidebar`)
- **Comments:** Write self-documenting code; add comments only for complex logic

## 🧪 Testing Requirements

### Backend Testing
```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_inbox.py

# Run with coverage
docker-compose exec backend pytest --cov=app
```

### Frontend Testing
```bash
# Run tests (when implemented)
cd frontend && npm test

# Run linting
cd frontend && npm run lint
```

### Testing Standards
- **Unit Tests:** Test individual functions and components
- **Integration Tests:** Test API endpoints and workflows
- **Coverage:** Aim for >80% code coverage
- **CI/CD:** All tests must pass before merging

## 🔄 Pull Request Process

### Before Submitting
1. **Update Branch:** Ensure your branch is up-to-date with `main`
2. **Run Tests:** All tests must pass locally
3. **Code Style:** Run formatters and linters
4. **Documentation:** Update docs if needed

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process
1. **Automated Checks:** CI/CD pipeline runs tests and linting
2. **Code Review:** At least one maintainer review required
3. **Approval:** PR approved and merged by maintainer
4. **Cleanup:** Delete branch after merge

## 🏗 Architecture Guidelines

### Backend Architecture
- **API Design:** RESTful endpoints with OpenAPI documentation
- **Database:** Async SQLAlchemy with PostgreSQL
- **File Storage:** Abstract storage service (local/S3)
- **Background Tasks:** Celery for AI processing
- **Error Handling:** Proper HTTP status codes and error messages

### Frontend Architecture
- **State Management:** React Query for server state
- **Component Structure:** Reusable UI components with Shadcn/ui
- **Routing:** Next.js App Router
- **Styling:** Tailwind CSS with CSS variables for theming

### Key Patterns
- **Storage Abstraction:** Never use direct file paths
- **Schema-Driven UI:** Backend defines data shapes
- **Async Processing:** Handle long-running tasks properly
- **Security First:** Input validation and secure defaults

## 🔒 Security Considerations

### General Security
- **Input Validation:** Validate all inputs with Pydantic/FastAPI
- **Secrets Management:** Never commit API keys or sensitive data
- **HTTPS:** Use HTTPS in production
- **Access Control:** Implement proper authentication/authorization

### Family Office Context
- **Data Privacy:** Handle sensitive financial/legal information appropriately
- **Audit Trail:** Log important actions for compliance
- **Data Retention:** Implement appropriate data lifecycle management
- **Backup Security:** Secure backup procedures

### Development Security
- **Dependencies:** Keep dependencies updated and scan for vulnerabilities
- **Code Review:** Security-focused code reviews
- **Testing:** Include security testing in CI/CD pipeline

## 📞 Getting Help

- **Issues:** Use GitHub Issues for bugs and feature requests
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check README.md and inline code documentation

## 🙏 Recognition

Contributors will be recognized in project documentation and release notes. Thank you for helping improve Byro!</content>
<parameter name="filePath">CONTRIBUTING.md
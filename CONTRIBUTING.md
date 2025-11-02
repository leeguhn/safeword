# Contributing to SafeWord

Thank you for your interest in contributing to SafeWord!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Run `./setup.sh` to set up dependencies
4. Create a feature branch: `git checkout -b feature/your-feature`

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where possible
- Document functions with docstrings
- Keep functions focused and small

### JavaScript/React (Frontend)
- Use functional components with hooks
- Use meaningful variable names
- Keep components focused and reusable
- Handle errors gracefully

## Testing

### Backend Tests
```bash
cd backend
source .venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Pull Request Process

1. Update README.md with details of changes if needed
2. Update requirements.txt or package.json if adding dependencies
3. Test your changes thoroughly
4. Write clear commit messages
5. Submit a pull request with a clear description

## Areas for Contribution

- **SMS/Email Integration**: Complete Twilio and SMTP implementations
- **Async Training**: Move training to background workers
- **Mobile Apps**: iOS/Android native apps
- **Testing**: Add unit and integration tests
- **Documentation**: Improve docs and add tutorials
- **UI/UX**: Enhance the React interface
- **Security**: Security audits and improvements
- **Performance**: Optimize detection and training

## Questions?

Open an issue for questions or discussions!

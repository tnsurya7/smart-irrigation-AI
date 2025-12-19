# Contributing to Smart Irrigation AI

Thank you for your interest in contributing to the Smart Irrigation AI project! This document provides guidelines for contributing to this open-source smart agriculture dashboard.

## 🌱 Project Overview

Smart Irrigation AI is a production-ready IoT-based smart agriculture dashboard that combines:
- Real-time ESP32 sensor monitoring
- AI-powered irrigation predictions (ARIMA/ARIMAX models)
- Weather-based irrigation decisions
- Telegram bot automation
- Modern web technologies (React, FastAPI, Supabase)

## 🤝 How to Contribute

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/smart-irrigation-AI.git
cd smart-irrigation-AI
```

### 2. Set Up Development Environment
```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes
- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure your changes don't break existing functionality

### 5. Test Your Changes
```bash
# Run frontend tests
npm test

# Run backend tests
cd backend
python -m pytest

# Test the full system
npm run dev  # Terminal 1
cd backend && python production_backend.py  # Terminal 2
cd backend && python production_websocket.py  # Terminal 3
```

### 6. Commit and Push
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 7. Create Pull Request
- Go to GitHub and create a pull request
- Provide a clear description of your changes
- Reference any related issues

## 📋 Contribution Guidelines

### Code Style
- **Frontend**: Use TypeScript, follow ESLint rules, use Prettier for formatting
- **Backend**: Follow PEP 8 for Python, use type hints
- **Commits**: Use conventional commit messages (feat:, fix:, docs:, etc.)

### Areas for Contribution

#### 🎨 Frontend Improvements
- UI/UX enhancements
- Mobile responsiveness improvements
- New dashboard components
- Performance optimizations
- Accessibility improvements

#### ⚙️ Backend Enhancements
- API endpoint improvements
- Database optimization
- WebSocket performance
- Security enhancements
- Error handling improvements

#### 🤖 AI/ML Improvements
- Model accuracy improvements
- New prediction algorithms
- Data preprocessing enhancements
- Feature engineering
- Model evaluation metrics

#### 📱 Hardware Integration
- ESP32 code improvements
- New sensor integrations
- Hardware compatibility
- Communication protocols
- Power optimization

#### 🔧 DevOps & Infrastructure
- Deployment improvements
- CI/CD pipeline enhancements
- Docker optimizations
- Monitoring and logging
- Performance monitoring

#### 📚 Documentation
- API documentation
- Setup guides
- Troubleshooting guides
- Code comments
- Architecture documentation

### Bug Reports
When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, versions)
- Screenshots or logs if applicable

### Feature Requests
For new features, please:
- Check if the feature already exists or is planned
- Provide a clear use case and rationale
- Consider the impact on existing functionality
- Discuss implementation approach if possible

## 🛡️ Security

If you discover security vulnerabilities, please:
- **DO NOT** create a public issue
- Email the maintainers directly
- Provide detailed information about the vulnerability
- Allow time for the issue to be addressed before disclosure

## 📝 Development Setup Details

### Environment Variables
Copy `.env.example` to `.env.local` and configure:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8080/ws
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_OPENWEATHER_API_KEY=your-openweather-key
```

### Database Setup
1. Create Supabase project
2. Run `database/supabase-schema.sql`
3. Configure Row Level Security

### Testing
- Frontend: Jest + React Testing Library
- Backend: pytest + FastAPI TestClient
- Integration: End-to-end testing with real services

## 🏆 Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes for significant contributions
- Invited to join the core team for outstanding contributions

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For security issues or private matters

## 📄 License

By contributing to Smart Irrigation AI, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Every contribution, no matter how small, helps make Smart Irrigation AI better for everyone. Thank you for being part of this project!

---

**Happy Contributing! 🌱**
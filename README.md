# Biased - News Bias Analysis Platform

## Overview

Biased is a platform for analyzing news articles for political bias, sentiment, and loaded language. It provides a web interface for users to submit articles via URL or file upload, and returns detailed analysis using NLP models.

## Features

- 🔍 **Bias Detection**: Analyze political bias in news articles
- 😊 **Sentiment Analysis**: Determine emotional tone of content
- 🚩 **Loaded Language Detection**: Identify potentially biased language
- 📊 **Visual Results**: Clear, easy-to-understand analysis results
- 📚 **History Tracking**: View your analysis history
- 🌐 **URL Support**: Submit articles by URL or direct text input

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: Flask + SQLAlchemy
- **Database**: PostgreSQL
- **Queue System**: Redis + RQ
- **AI Models**: Transformers (Hugging Face)
- **Deployment**: Docker + Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Biased.git
   cd Biased
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Manual Setup

If you prefer to set up manually:

1. **Copy environment file:**
   ```bash
   cp env.example .env
   ```

2. **Start services:**
   ```bash
   docker-compose up --build
   ```

## Development

### Project Structure

```
Biased/
├── frontend/          # React application
├── backend/           # Flask API server
├── ai/               # NLP models and analysis
├── tests/            # Test suite
├── docs/             # Documentation
├── scripts/          # Setup and deployment scripts
└── docker-compose.yml
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest ../tests/

# Frontend tests
cd frontend
npm test
```

### Development Mode

```bash
# Start only database and Redis
docker-compose up db redis

# Run backend in development mode
cd backend
python app.py

# Run frontend in development mode
cd frontend
npm run dev
```

## API Endpoints

- `POST /api/analyze` - Submit article for analysis
- `GET /api/status/<job_id>` - Check analysis status
- `GET /api/results/<job_id>` - Get analysis results
- `GET /api/history` - Get user's analysis history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
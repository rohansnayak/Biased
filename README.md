# Biased Project

## Overview

Biased is a platform for analyzing news articles for political bias, sentiment, and loaded language. It provides a web interface for users to submit articles via URL or file upload, and returns detailed analysis using NLP models.

## Directory Structure

- `frontend/` – Client-side React application
- `backend/` – API and worker services (Express or Flask)
- `ai/` – NLP pipelines and model code (transformers, spaCy)
- `tests/` – Unit and integration tests
- `docs/` – Design notes and API specifications

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd Biased
   ```
2. **Install dependencies:**
   - Frontend: See `frontend/README.md`
   - Backend: See `backend/README.md`
   - AI: See `ai/README.md`
3. **Run services locally:**
   - Use `docker-compose up` for local development (see `docker-compose.yml`)
4. **Testing:**
   - Run tests in the `tests/` directory
5. **Documentation:**
   - See `docs/` for API specs and design notes
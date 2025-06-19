# Backend

This directory contains the API and worker services for Biased.

## Setup

1. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   # or for Node.js
   npm install
   ```
3. Set environment variables (see `.env.example`)
4. Start the API server:
   ```sh
   python app.py
   # or
   npm start
   ```

## Tech Stack
- [Flask](https://flask.palletsprojects.com/) (Python) or [Express](https://expressjs.com/) (Node.js)
- Database: PostgreSQL or MongoDB
- Message Broker: Redis or RabbitMQ 
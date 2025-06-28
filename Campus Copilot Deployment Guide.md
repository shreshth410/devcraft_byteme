# Campus Copilot Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Telegram Bot Setup](#telegram-bot-setup)
6. [Google API Setup](#google-api-setup)
7. [Database Setup](#database-setup)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Troubleshooting](#troubleshooting)

## Overview

Campus Copilot is an AI-powered Telegram bot designed to assist students with campus life. It provides features including:

- **Calendar Integration**: Google Calendar sync and event management
- **Location Services**: Campus navigation and directions
- **AI Query Processing**: Natural language understanding for student queries
- **Content Generation**: Event poster creation and email summarization
- **Personal Assistant**: Reminders, schedules, and personalized assistance

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: Version 3.11 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: Minimum 5GB free space
- **Network**: Internet connection for API access

### Required Accounts and Services
- **Telegram Bot Token**: From @BotFather on Telegram
- **Google Cloud Project**: For Calendar and Maps API access
- **Domain/Server**: For webhook endpoints (optional for polling mode)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd campus_copilot
```

### 2. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download Required Models
```bash
python -m spacy download en_core_web_sm
```

## Configuration

### 1. Environment Variables
Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google API Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Database Configuration
DATABASE_PATH=data/campus_copilot.db

# Webhook Configuration (for production)
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PORT=8443

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

### 2. Directory Structure
Ensure the following directories exist:
```bash
mkdir -p data logs config
```

## Telegram Bot Setup

### 1. Create Bot with BotFather
1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Save the bot token provided

### 2. Configure Bot Settings
```bash
# Set bot description
/setdescription - Your AI assistant for campus life

# Set bot commands
/setcommands
start - Welcome message and introduction
help - Show all commands and features
schedule - View your class schedule
events - Check upcoming events
connect_calendar - Link your Google Calendar
find - Find campus locations
directions - Get walking directions
generate_poster - Create event posters
summarize_email - Summarize emails
settings - Configure preferences
```

## Google API Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Calendar API
   - Google Maps JavaScript API
   - Google Maps Directions API
   - Google Maps Places API

### 2. Create Credentials
1. Go to "Credentials" in the API & Services section
2. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-domain.com/oauth2callback`
3. Create API Key for Google Maps
4. Download the OAuth client configuration

### 3. Configure OAuth Consent Screen
1. Go to "OAuth consent screen"
2. Configure the consent screen with your app information
3. Add test users if in development mode
4. Add required scopes:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`

## Database Setup

The application uses SQLite by default. The database will be automatically created on first run.

### Database Schema
The following tables will be created:
- `users`: User profiles and preferences
- `college_events`: Campus events and activities
- `reminders`: Personal reminders and notifications
- `user_settings`: User configuration and preferences

### Manual Database Initialization
```bash
python -c "
from src.database.database_manager import DatabaseManager
db = DatabaseManager()
print('Database initialized successfully')
"
```

## Testing

### 1. Run Unit Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m unittest tests.test_email_summarizer -v
python -m unittest tests.test_poster_generator -v
```

### 2. Test Bot Functionality
```bash
# Test bot startup
python src/main.py

# Test NLP processing
python -c "
from src.nlp.nlp_processor import NLPProcessor
nlp = NLPProcessor()
result = nlp.process_query('What is my schedule today?')
print(result)
"
```

### 3. Test API Integrations
```bash
# Test poster generation
python -c "
from src.utils.poster_generator import PosterGenerator
pg = PosterGenerator()
result = pg.generate_event_poster({
    'title': 'Test Event',
    'date': '2024-04-20',
    'time': '6:00 PM'
})
print(f'Generated: {result}')
"

# Test email summarization
python -c "
from src.utils.email_summarizer import EmailSummarizer
es = EmailSummarizer()
result = es.summarize_email('Test email content for summarization.')
print(f'Summary: {result[\"summary\"]}')
"
```

## Deployment

### Option 1: Local Development
```bash
# Start the bot
python src/main.py
```

### Option 2: Production Server

#### Using systemd (Recommended)
1. Create service file:
```bash
sudo nano /etc/systemd/system/campus-copilot.service
```

2. Add service configuration:
```ini
[Unit]
Description=Campus Copilot Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/campus_copilot
Environment=PATH=/path/to/campus_copilot/venv/bin
ExecStart=/path/to/campus_copilot/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable campus-copilot
sudo systemctl start campus-copilot
```

#### Using Docker (Alternative)
1. Create Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
CMD ["python", "src/main.py"]
```

2. Build and run:
```bash
docker build -t campus-copilot .
docker run -d --name campus-copilot --env-file .env campus-copilot
```

### Option 3: Cloud Deployment

#### Heroku
1. Create `Procfile`:
```
worker: python src/main.py
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
```

#### AWS EC2
1. Launch EC2 instance (t3.small or larger)
2. Install dependencies and clone repository
3. Configure security groups for webhook port
4. Set up SSL certificate for webhook endpoint
5. Use systemd service for process management

## Monitoring and Maintenance

### 1. Logging
Logs are written to:
- Console output (development)
- `logs/campus_copilot.log` (production)

Configure log level in `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### 2. Health Checks
```bash
# Check bot status
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Check webhook status (if using webhooks)
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 3. Database Maintenance
```bash
# Backup database
cp data/campus_copilot.db data/backup_$(date +%Y%m%d).db

# Check database integrity
sqlite3 data/campus_copilot.db "PRAGMA integrity_check;"
```

### 4. Performance Monitoring
Monitor the following metrics:
- Response time to user messages
- Memory usage
- Database query performance
- API call success rates

## Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check bot token validity:
```bash
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

2. Check logs for errors:
```bash
tail -f logs/campus_copilot.log
```

3. Verify network connectivity and firewall settings

#### Google API Errors
1. Verify API keys and OAuth credentials
2. Check API quotas and billing
3. Ensure redirect URIs are correctly configured
4. Verify required scopes are granted

#### Database Issues
1. Check file permissions:
```bash
ls -la data/campus_copilot.db
```

2. Test database connection:
```bash
python -c "
from src.database.database_manager import DatabaseManager
db = DatabaseManager()
print('Database connection successful')
"
```

#### NLP Model Issues
1. Reinstall spaCy model:
```bash
python -m spacy download en_core_web_sm --force
```

2. Check model loading:
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Model loaded successfully')"
```

### Performance Optimization

#### Memory Usage
- Monitor memory consumption with `htop` or `ps`
- Consider using smaller NLP models for resource-constrained environments
- Implement connection pooling for database operations

#### Response Time
- Cache frequently accessed data
- Optimize database queries
- Use asynchronous operations where possible

#### Scaling
- Use load balancers for multiple bot instances
- Implement Redis for session storage
- Consider microservices architecture for large deployments

### Security Considerations

1. **Environment Variables**: Never commit sensitive data to version control
2. **API Keys**: Rotate API keys regularly
3. **Database**: Use proper file permissions (600 for database file)
4. **HTTPS**: Always use HTTPS for webhook endpoints
5. **Input Validation**: Sanitize all user inputs
6. **Rate Limiting**: Implement rate limiting for API calls

### Backup and Recovery

#### Automated Backups
Create a backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp data/campus_copilot.db $BACKUP_DIR/db_backup_$DATE.db

# Backup configuration
cp .env $BACKUP_DIR/env_backup_$DATE

# Backup generated content
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz data/

echo "Backup completed: $DATE"
```

#### Recovery Procedure
1. Stop the bot service
2. Restore database from backup
3. Verify configuration files
4. Restart the bot service
5. Test functionality

## Support and Updates

### Getting Help
- Check the troubleshooting section above
- Review logs for error messages
- Test individual components separately
- Verify all prerequisites are met

### Updates and Maintenance
- Regularly update dependencies: `pip install -r requirements.txt --upgrade`
- Monitor for security updates
- Test updates in development environment first
- Backup before applying updates

### Contributing
- Follow the existing code structure
- Add tests for new features
- Update documentation
- Follow Python PEP 8 style guidelines

---

**Note**: This deployment guide assumes a Linux environment. For Windows deployment, adjust paths and commands accordingly. Always test in a development environment before deploying to production.


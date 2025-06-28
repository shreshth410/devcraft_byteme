# Campus Copilot: AI Agent for Student Life

A comprehensive Telegram-based AI chatbot designed to assist students with various college-related queries and tasks.

## Features

- **Query Answering**: Responds to questions about timetables, exams, events, club activities, and deadlines
- **Email/Notice Summarization**: Condenses long notices and emails into concise summaries
- **Content Generation**: Converts raw event information into formatted posters, descriptions, and mail drafts
- **API Integrations**: Connects with Google Calendar, Google Maps, and potentially college LMS/SIS
- **Personalized Reminders**: Sends notifications based on class schedules and personal habits

## Architecture

The system follows a modular architecture with the following components:

- **Telegram Bot Interface**: Handles user communication via Telegram Bot API
- **NLP Module**: Processes natural language queries and identifies intents
- **Knowledge Base & Database**: Stores college information and user data
- **External API Integrations**: Connects to Google services and college systems
- **Utility Modules**: Provides summarization, content generation, and reminder services

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd campus_copilot
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

Before running the bot, you need to configure the following:

1. **Telegram Bot Token**: Create a bot via @BotFather on Telegram
2. **Google API Credentials**: Set up Google Cloud Project and enable Calendar API
3. **Database**: Configure PostgreSQL connection
4. **Pinecone**: Set up vector database for document embeddings
5. **Redis**: Configure for task queue management

## Usage

1. Start the bot:
   ```bash
   python src/main.py
   ```

2. Interact with the bot on Telegram by sending messages or commands

## Development

### Project Structure

```
campus_copilot/
├── src/
│   ├── bot/                 # Telegram bot interface
│   ├── nlp/                 # Natural language processing
│   ├── database/            # Database models and operations
│   ├── api_integrations/    # External API connections
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── config/                  # Configuration files
├── data/                    # Data files
├── logs/                    # Log files
└── requirements.txt         # Python dependencies
```

### Testing

Run tests using pytest:
```bash
pytest tests/
```

### Code Formatting

Format code using black:
```bash
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.


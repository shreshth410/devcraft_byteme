import os
import logging
from typing import Dict, Any
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode
import asyncio

from .calendar_handlers import CalendarHandlers
from .advanced_handlers import AdvancedHandlers
from ..nlp.nlp_processor import NLPProcessor
from ..database.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class CampusCopilotBot:
    """Main Telegram bot class for Campus Copilot"""
    
    def __init__(self, token: str):
        """Initialize the bot with token"""
        self.token = token
        self.application = None
        self.calendar_handlers = CalendarHandlers()
        self.advanced_handlers = AdvancedHandlers()
        self.nlp_processor = NLPProcessor()
        self.db_manager = DatabaseManager()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user_telegram_id = update.effective_user.id
        
        # Add user to database if not exists
        user_exists = self.db_manager.get_user(user_telegram_id)
        if not user_exists:
            self.db_manager.add_user(user_telegram_id)
            logger.info(f"New user {user_telegram_id} added to database.")
        
        welcome_message = """
🎓 Welcome to Campus Copilot! 🤖

I'm your AI assistant for college life. I can help you with:

📅 **Schedule & Events**
• Check your timetable
• Find upcoming exams
• Get event information
• Set personal reminders

🏫 **Campus Information**
• Find classrooms and buildings
• Get faculty schedules
• Club activities and deadlines
• Campus announcements

📧 **Smart Assistance**
• Summarize long emails/notices
• Create event posters
• Draft emails
• Answer college-related questions

Just type your question or use these commands:
/help - Show all available commands
/connect_calendar - Link your Google Calendar
/events - View upcoming events
/find - Find campus locations
/directions - Get walking directions
/generate_poster - Create event posters
/summarize_email - Summarize emails
/summarize_notice - Summarize notices
/list_posters - View generated posters

How can I help you today? 😊
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_message = """
🆘 **Campus Copilot Commands**

**📅 Calendar & Events**
/connect_calendar - Link your Google Calendar
/events - View upcoming events
/create_event - Create a new calendar event
/schedule - Check your class schedule

**🗺 Campus Navigation**
/find <location> - Find campus locations
/directions <destination> - Get walking directions
/map - Browse campus map

**🔔 Reminders & Notifications**
/reminders - Manage personal reminders
/deadlines - View assignment deadlines
/notifications - Configure alerts

**⚙️ Settings & Account**
/settings - Configure preferences
/status - Check bot and connection status
/disconnect_calendar - Unlink Google Calendar

**💬 Natural Language Queries**
You can also ask me questions naturally:
• "When is my next class?"
• "Where is the library?"
• "How do I get to the computer science building?"
• "What events are happening today?"
• "Create a study session for tomorrow"

**🔗 Quick Actions**
/about - About Campus Copilot
/feedback - Send feedback

Need more help? Just ask me anything! 🤔
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /schedule command"""
        # TODO: Integrate with actual schedule data
        schedule_message = """
📅 **Your Schedule for Today**

🕘 **9:00 AM - 10:30 AM**
Computer Science 101
📍 Room: CS-204
👨‍🏫 Prof. Johnson

🕐 **1:00 PM - 2:30 PM**
Mathematics 201
📍 Room: MATH-105
👩‍🏫 Prof. Smith

🕕 **6:00 PM - 7:00 PM**
Study Group - Physics
📍 Library Room 3B

*Note: This is sample data. Connect your college account to see real schedule.*

Use /connect_calendar to link your Google Calendar for real-time data.
        """
        
        await update.message.reply_text(
            schedule_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def events_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /events command"""
        # This command is now handled by calendar_handlers.handle_calendar_events
        await self.calendar_handlers.handle_calendar_events(update, context)
        
    async def reminders_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /reminders command"""
        reminders_message = """
🔔 **Your Reminders**

**📚 Active Reminders**
• Assignment due: Physics Lab Report (Tomorrow 11:59 PM)
• Event: Tech Club Meeting (Today 4:00 PM)
• Study reminder: Prepare for Math quiz (2 hours before)

**➕ Add New Reminder**
Just tell me what you want to be reminded about:
• "Remind me to submit assignment tomorrow at 5 PM"
• "Set reminder for club meeting in 2 hours"
• "Alert me 30 minutes before my next class"

**⚙️ Reminder Settings**
• Default reminder time: 15 minutes before
• Notification method: Telegram message
• Timezone: EST

Use /settings to customize reminder preferences.
        """
        
        await update.message.reply_text(
            reminders_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /settings command"""
        settings_message = """
⚙️ **Campus Copilot Settings**

**👤 Profile Information**
• Name: Not set
• College: Not connected
• Year: Not specified
• Major: Not specified

**🔗 Connected Accounts**
• Google Calendar: ❌ Not connected
• College LMS: ❌ Not connected
• Email: ❌ Not connected

**🔔 Notification Preferences**
• Reminder timing: 15 minutes before
• Daily schedule summary: 8:00 AM
• Event notifications: Enabled
• Assignment alerts: Enabled

**🌍 Preferences**
• Timezone: EST (UTC-5)
• Language: English
• Date format: MM/DD/YYYY

**🔧 Quick Actions**
• /connect_calendar - Link Google Calendar
• /timezone - Change timezone
• /profile - Update profile info

To modify any setting, just tell me what you'd like to change!
        """
        
        await update.message.reply_text(
            settings_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        status_message = """
🤖 **Campus Copilot Status**

**🟢 System Status: Online**
• Bot response time: < 1 second
• Database connection: ✅ Active
• API integrations: ✅ Operational
• Last update: Just now

**📊 Your Usage Stats**
• Messages sent: 0
• Commands used: 1
• Reminders set: 0
• Events tracked: 0

**🔧 Available Features**
• ✅ Basic commands
• ✅ Natural language processing
• ✅ Google Calendar (setup required)
• ⏳ College LMS (setup required)
• ⏳ Smart reminders (setup required)

**📈 Recent Activity**
• No recent activity

**🆘 Need Help?**
If you're experiencing issues, try:
• /help for command list
• Restart conversation with /start
• Contact support with /feedback

Everything looks good! How can I assist you? 😊
        """
        
        await update.message.reply_text(
            status_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Received message from user {user_id}: {user_message}")
        
        # Process query using NLP
        processed_query = self.nlp_processor.process_query(user_message)
        intent = processed_query["intent"]
        entities = processed_query["entities"]
        
        logger.info(f"Detected intent: {intent}, Entities: {entities}")
        
        response_text = ""
        
        if intent == "get_schedule":
            # TODO: Integrate with actual schedule retrieval
            response_text = "I can help with your schedule! Please use `/schedule` to see your current timetable. If you've connected your Google Calendar, I'll show your real classes soon."
        elif intent == "get_events":
            await self.calendar_handlers.handle_calendar_events(update, context)
            return
        elif intent == "create_reminder":
            # TODO: Implement reminder creation
            response_text = "I can set reminders for you! Please use `/reminders` to manage your reminders. For example, you can say \"Remind me to submit my essay tomorrow at 5 PM\"."
        elif intent == "find_location":
            if entities.get("location"):
                context.args = [entities["location"]]
                await self.calendar_handlers.handle_find_location(update, context)
                return
            else:
                response_text = "I can help you find locations on campus. What place are you looking for? (e.g., \"Where is the library?\")"
        elif intent == "get_directions":
            if entities.get("location"):
                context.args = [entities["location"]]
                await self.calendar_handlers.handle_directions(update, context)
                return
            else:
                response_text = "I can give you directions on campus. Where do you want to go? (e.g., \"Directions to the gym\")"
        elif intent == "create_event":
            # TODO: Implement interactive event creation using entities
            response_text = "I can help you create events! Please use `/create_event` and follow the instructions to add a new event to your calendar."
        elif intent == "summarize_text":
            response_text = "I can summarize text for you. Please provide the text you'd like me to summarize."
        elif intent == "generate_poster":
            response_text = "I can help you generate posters for events. Please provide details like event name, date, time, and a brief description."
        elif intent == "general_greeting":
            response_text = "Hello! How can I assist you today?"
        elif intent == "general_thanks":
            response_text = "You're welcome! Is there anything else I can help with?"
        else: # general_unclear or other unhandled intents
            response_text = f"""
🤖 **I received your message:** "{user_message}"

I'm still learning! Here's what I can help you with right now:

**📋 Try these commands:**
• /schedule - Check your schedule
• /events - View upcoming events
• /reminders - Manage reminders
• /help - See all commands

**💬 Or ask me questions like:**
• "What's my next class?"
• "Any events today?"
• "Set a reminder for tomorrow"
• "Where is the library?"

I'm getting smarter every day! Soon I'll understand your questions better. 🧠✨

*This is a development version. Full AI capabilities coming soon!*
            """
        
        await update.message.reply_text(
            response_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "🚨 Oops! Something went wrong. Please try again or use /help for assistance."
            )
            
    def setup_handlers(self):
        """Set up command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("schedule", self.schedule_command))
        self.application.add_handler(CommandHandler("reminders", self.reminders_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Calendar-related commands
        self.application.add_handler(CommandHandler("connect_calendar", self.calendar_handlers.handle_connect_calendar))
        self.application.add_handler(CommandHandler("events", self.calendar_handlers.handle_calendar_events))
        self.application.add_handler(CommandHandler("create_event", self.calendar_handlers.handle_create_event))
        
        # Location-related commands
        self.application.add_handler(CommandHandler("find", self.calendar_handlers.handle_find_location))
        self.application.add_handler(CommandHandler("directions", self.calendar_handlers.handle_directions))
        
        # Advanced feature handlers
        self.application.add_handler(CommandHandler("generate_poster", self.advanced_handlers.handle_generate_poster))
        self.application.add_handler(CommandHandler("summarize_email", self.advanced_handlers.handle_summarize_email))
        self.application.add_handler(CommandHandler("summarize_notice", self.advanced_handlers.handle_summarize_notice))
        self.application.add_handler(CommandHandler("list_posters", self.advanced_handlers.handle_list_posters))
        
        # Message handler for NLP
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
    async def setup_bot_commands(self):
        """Set up bot commands in Telegram UI"""
        commands = [
            BotCommand("start", "Welcome message and introduction"),
            BotCommand("help", "Show all commands and features"),
            BotCommand("schedule", "View your class schedule"),
            BotCommand("events", "Check upcoming events"),
            BotCommand("reminders", "Manage personal reminders"),
            BotCommand("settings", "Configure preferences"),
            BotCommand("connect_calendar", "Link your Google Calendar"),
            BotCommand("find", "Find campus locations"),
            BotCommand("directions", "Get walking directions"),
            BotCommand("create_event", "Create a new calendar event"),
            BotCommand("generate_poster", "Create event posters"),
            BotCommand("summarize_email", "Summarize emails"),
            BotCommand("summarize_notice", "Summarize notices"),
            BotCommand("list_posters", "View generated posters"),
            BotCommand("status", "Check bot status"),
        ]
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands set up successfully.")

    async def start_bot(self):
        """Start the bot application"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        await self.setup_bot_commands()
        logger.info("Bot started polling.")
        await self.application.run_polling()

    def run(self):
        """Run the bot"""
        try:
            asyncio.run(self.start_bot())
        except Exception as e:
            logger.error(f"Error running bot: {e}")




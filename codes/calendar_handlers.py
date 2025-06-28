from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from api_integrations.google_calendar import GoogleCalendarService
from api_integrations.google_maps import GoogleMapsService
from database.database_manager import DatabaseManager
from config.config import get_config

logger = logging.getLogger(__name__)

class CalendarHandlers:
    def __init__(self):
        config = get_config()
        self.db_manager = DatabaseManager()
        self.google_calendar = GoogleCalendarService(
            client_id=config["GOOGLE_CLIENT_ID"],
            client_secret=config["GOOGLE_CLIENT_SECRET"],
            redirect_uri=config["WEBHOOK_URL"] + "/oauth2callback",
            db_manager=self.db_manager
        )
        self.google_maps = GoogleMapsService(api_key=config["GOOGLE_MAPS_API_KEY"])

    async def handle_connect_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        auth_url, state = self.google_calendar.get_authorization_url(user_id)

        keyboard = [
            [InlineKeyboardButton("🔗 Connect Google Calendar", url=auth_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📅 **Connect Your Google Calendar**\n\n"
            "To get personalized event and schedule updates, please connect your Google Calendar.\n\n"
            "Click the button below to securely link your account:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_calendar_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if not self.google_calendar.load_credentials(user_id):
            await self._prompt_calendar_connection(update)
            return

        events = self.google_calendar.get_upcoming_events(user_id)

        if not events:
            await update.message.reply_text("🎉 No upcoming events found for the next 7 days.")
            return

        response = "📅 **Upcoming Events:**\n\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            response += "- {} ({})\n".format(event["summary"], start)
        await update.message.reply_text(response)

    async def handle_create_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # This is a placeholder. Full implementation would involve a multi-step conversation.
        await update.message.reply_text("To create an event, I need more details like summary, start time, and end time. "
                                       "For example: 'Create event: Study session tomorrow 10 AM to 12 PM'")

    async def handle_find_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not context.args:
            await update.message.reply_text("Please provide a location to find. E.g., `/find library`")
            return

        location_query = " ".join(context.args)
        location_data = self.google_maps.search_place(f"campus {location_query}")

        if not location_data:
            await update.message.reply_text(f"Sorry, I couldn't find '{location_query}' on campus.")
            return

        name = location_data.get("name", "")
        address = location_data.get("address", "")
        rating = location_data.get("rating", "N/A")
        map_url = location_data.get("map_url", "")

        message = f"""
📍 **{name}**
Address: {address}
Rating: {rating}
        """
        keyboard = [
            [InlineKeyboardButton("🗺 Open in Google Maps", url=map_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_directions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not context.args:
            await update.message.reply_text("Please provide a destination. E.g., `/directions library`")
            return

        destination = " ".join(context.args)
        origin = "current location" # In a real scenario, this would be user's current location

        try:
            directions = self.google_maps.get_directions(
                origin=origin,
                destination=f"campus {destination}",
                mode="walking"
            )

            if not directions:
                await update.message.reply_text(
                    f"❌ Sorry, I couldn't find directions to '{destination}' .\n\n"
                    "Please try a more specific location name."
                )
                return

            # Generate directions URL
            directions_url = self.google_maps.generate_maps_url(
                origin, f"campus {destination}", "walking"
            )

            # Create response with directions
            keyboard = [
                [InlineKeyboardButton("🗺 Open Directions in Maps", url=directions_url)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = f"""
🧭 **Directions to {destination.title()}**

**From:** {directions["origin"]}
**To:** {directions["destination"]}

**📏 Distance:** {directions["distance"]}
**⏱ Walking Time:** {directions["duration"]}

**📋 Step-by-Step:**
            """

            for i, step in enumerate(directions["steps"][:3], 1):  # Show first 3 steps
                # Remove HTML tags from instructions
                instruction = step["instruction"].replace("<b>", "").replace("</b>", "")
                instruction = instruction.replace("<div>", " ").replace("</div>", "")
                message += "\n{}. {} ({})".format(i, instruction, step["distance"])

            if len(directions["steps"]) > 3:
                message += "\n\n*... and {} more steps*".format(len(directions["steps"]) - 3)

            message += "\n\nTap the button below for detailed turn-by-turn directions!"

            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            logger.error(f"Error handling directions: {e}")
            await update.message.reply_text("Sorry, I couldn't get directions at the moment. Please try again later.")

    async def _prompt_calendar_connection(self, update: Update) -> None:
        """Prompt user to connect their calendar"""
        user_id = str(update.effective_user.id)
        auth_url, state = self.google_calendar.get_authorization_url(int(user_id))

        keyboard = [
            [InlineKeyboardButton("🔗 Connect Google Calendar", url=auth_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📅 **Calendar Not Connected**\n\n"
            "To view your personalized schedule and events, please connect your Google Calendar.\n\n"
            "Click the button below to securely link your account:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )



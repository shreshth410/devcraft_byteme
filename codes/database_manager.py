"""
Database Manager for Campus Copilot.
Handles connection, schema creation, and basic CRUD operations.
"""
import sqlite3
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="data/campus_copilot.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    google_calendar_token TEXT,
                    preferences TEXT
                )
            """)

            # Events table (for college-wide events, not personal calendar events)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS college_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    location TEXT,
                    category TEXT
                )
            """)

            # Timetable table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS timetables (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_name TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    location TEXT,
                    instructor TEXT
                )
            """)

            # Deadlines table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deadlines (
                    deadline_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT NOT NULL,
                    course TEXT
                )
            """)

            # Reminders table (for personal reminders set by users)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    due_time TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            conn.commit()
            logger.info("Database tables created or already exist.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
        finally:
            if conn:
                conn.close()

    def execute_query(self, query, params=()):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def fetch_query(self, query, params=()):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching query: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_user(self, telegram_id, google_calendar_token=None, preferences=None):
        query = "INSERT INTO users (telegram_id, google_calendar_token, preferences) VALUES (?, ?, ?)"
        return self.execute_query(query, (telegram_id, google_calendar_token, preferences))

    def get_user(self, telegram_id):
        query = "SELECT * FROM users WHERE telegram_id = ?"
        return self.fetch_query(query, (telegram_id,))

    def update_user_token(self, telegram_id, google_calendar_token):
        query = "UPDATE users SET google_calendar_token = ? WHERE telegram_id = ?"
        return self.execute_query(query, (google_calendar_token, telegram_id))

    def add_college_event(self, title, description, start_time, end_time, location, category):
        query = "INSERT INTO college_events (title, description, start_time, end_time, location, category) VALUES (?, ?, ?, ?, ?, ?)"
        return self.execute_query(query, (title, description, start_time, end_time, location, category))

    def get_college_events(self, category=None):
        if category:
            query = "SELECT * FROM college_events WHERE category = ? ORDER BY start_time ASC"
            return self.fetch_query(query, (category,))
        else:
            query = "SELECT * FROM college_events ORDER BY start_time ASC"
            return self.fetch_query(query)

    def add_timetable_entry(self, course_name, day_of_week, start_time, end_time, location, instructor):
        query = "INSERT INTO timetables (course_name, day_of_week, start_time, end_time, location, instructor) VALUES (?, ?, ?, ?, ?, ?)"
        return self.execute_query(query, (course_name, day_of_week, start_time, end_time, location, instructor))

    def get_timetable(self, day_of_week=None):
        if day_of_week:
            query = "SELECT * FROM timetables WHERE day_of_week = ? ORDER BY start_time ASC"
            return self.fetch_query(query, (day_of_week,))
        else:
            query = "SELECT * FROM timetables ORDER BY day_of_week, start_time ASC"
            return self.fetch_query(query)

    def add_deadline(self, title, description, due_date, course=None):
        query = "INSERT INTO deadlines (title, description, due_date, course) VALUES (?, ?, ?, ?)"
        return self.execute_query(query, (title, description, due_date, course))

    def get_deadlines(self, course=None):
        if course:
            query = "SELECT * FROM deadlines WHERE course = ? ORDER BY due_date ASC"
            return self.fetch_query(query, (course,))
        else:
            query = "SELECT * FROM deadlines ORDER BY due_date ASC"
            return self.fetch_query(query)

    def add_reminder(self, user_id, text, due_time):
        query = "INSERT INTO reminders (user_id, text, due_time) VALUES (?, ?, ?)"
        return self.execute_query(query, (user_id, text, due_time))

    def get_reminders(self, user_id, completed=0):
        query = "SELECT * FROM reminders WHERE user_id = ? AND is_completed = ? ORDER BY due_time ASC"
        return self.fetch_query(query, (user_id, completed))

    def mark_reminder_completed(self, reminder_id):
        query = "UPDATE reminders SET is_completed = 1 WHERE reminder_id = ?"
        return self.execute_query(query, (reminder_id,))


# Example Usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_manager = DatabaseManager()

    # Add a user
    user_id = db_manager.add_user(telegram_id=123456789, preferences="{}")
    if user_id:
        logger.info(f"Added user with ID: {user_id}")
    else:
        logger.info("User already exists or error adding user.")

    # Get user
    user = db_manager.get_user(telegram_id=123456789)
    logger.info(f"Retrieved user: {user}")

    # Add a college event
    db_manager.add_college_event(
        "Freshers Welcome Party",
        "Annual welcome party for new students",
        "2025-09-01 18:00:00",
        "2025-09-01 22:00:00",
        "University Auditorium",
        "Social"
    )
    logger.info("Added college event.")

    # Get college events
    events = db_manager.get_college_events()
    logger.info(f"College events: {events}")

    # Add a timetable entry
    db_manager.add_timetable_entry(
        "Introduction to AI",
        "Monday",
        "09:00",
        "10:30",
        "Room 101",
        "Dr. A.I. Professor"
    )
    logger.info("Added timetable entry.")

    # Get timetable
    timetable = db_manager.get_timetable(day_of_week="Monday")
    logger.info(f"Monday timetable: {timetable}")

    # Add a deadline
    db_manager.add_deadline(
        "AI Project Proposal",
        "Submit proposal for final AI project",
        "2025-10-15 23:59:59",
        "Introduction to AI"
    )
    logger.info("Added deadline.")

    # Get deadlines
    deadlines = db_manager.get_deadlines()
    logger.info(f"All deadlines: {deadlines}")

    # Add a reminder for the user
    if user:
        db_manager.add_reminder(user_id=user[0][0], text="Buy new textbooks", due_time="2025-08-25 10:00:00")
        logger.info("Added reminder.")

        # Get reminders
        reminders = db_manager.get_reminders(user_id=user[0][0])
        logger.info(f"User reminders: {reminders}")

        # Mark reminder as completed
        if reminders:
            db_manager.mark_reminder_completed(reminders[0][0])
            logger.info(f"Marked reminder {reminders[0][0]} as completed.")

            reminders_after_completion = db_manager.get_reminders(user_id=user[0][0])
            logger.info(f"User reminders after completion: {reminders_after_completion}")




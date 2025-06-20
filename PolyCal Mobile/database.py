import sqlite3
import os
import threading
from contextlib import contextmanager
from datetime import datetime

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_name='polycal.db'):
        if self._initialized:
            return

        try:
            # Get current working directory
            self.cwd = os.getcwd()
            print(f"Current working directory: {self.cwd}")

            # Construct full path to database
            self.db_path = os.path.join(self.cwd, db_name)
            print(f"Attempting to connect to database: {db_name}")
            print(f"Full database path: {self.db_path}")

            # Initialize database tables using context manager
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Create tables if they don't exist
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    program TEXT,
                    bio TEXT,
                    profile_image TEXT,
                    is_admin INTEGER DEFAULT 0
                )
                ''')

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    description TEXT,
                    tagged_ids TEXT,
                    link TEXT,
                    image_path TEXT,
                    privacy TEXT DEFAULT 'public',
                    creator_id TEXT
                )
                ''')

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    event_id INTEGER,
                    title TEXT,
                    message TEXT,
                    is_read INTEGER DEFAULT 0,
                    notification_type TEXT DEFAULT 'notification',
                    invitation_status TEXT DEFAULT NULL,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
                ''')

                # Check if bio and profile_image columns exist, add them if they don't
                try:
                    cursor.execute("SELECT bio FROM users LIMIT 1")
                except sqlite3.OperationalError:
                    # Bio column doesn't exist, add it
                    cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
                    print("Added 'bio' column to users table")

                try:
                    cursor.execute("SELECT profile_image FROM users LIMIT 1")
                except sqlite3.OperationalError:
                    # Profile image column doesn't exist, add it
                    cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
                    print("Added 'profile_image' column to users table")

                # Check if privacy and creator_id columns exist in events table, add them if they don't
                try:
                    cursor.execute("SELECT privacy FROM events LIMIT 1")
                except sqlite3.OperationalError:
                    # Privacy column doesn't exist, add it
                    cursor.execute("ALTER TABLE events ADD COLUMN privacy TEXT DEFAULT 'public'")
                    print("Added 'privacy' column to events table")

                try:
                    cursor.execute("SELECT creator_id FROM events LIMIT 1")
                except sqlite3.OperationalError:
                    # Creator_id column doesn't exist, add it
                    cursor.execute("ALTER TABLE events ADD COLUMN creator_id TEXT")
                    print("Added 'creator_id' column to events table")

                # Check if is_admin column exists in users table, add it if it doesn't
                try:
                    cursor.execute("SELECT is_admin FROM users LIMIT 1")
                except sqlite3.OperationalError:
                    # is_admin column doesn't exist, add it
                    cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
                    print("Added 'is_admin' column to users table")

                # Check if section column exists in users table, add it if it doesn't
                try:
                    cursor.execute("SELECT section FROM users LIMIT 1")
                except sqlite3.OperationalError:
                    # section column doesn't exist, add it
                    cursor.execute("ALTER TABLE users ADD COLUMN section TEXT")
                    print("Added 'section' column to users table")

                # Check if notification_type column exists in notifications table, add it if it doesn't
                try:
                    cursor.execute("SELECT notification_type FROM notifications LIMIT 1")
                except sqlite3.OperationalError:
                    # notification_type column doesn't exist, add it
                    cursor.execute("ALTER TABLE notifications ADD COLUMN notification_type TEXT DEFAULT 'notification'")
                    print("Added 'notification_type' column to notifications table")

                # Check if invitation_status column exists in notifications table, add it if it doesn't
                try:
                    cursor.execute("SELECT invitation_status FROM notifications LIMIT 1")
                except sqlite3.OperationalError:
                    # invitation_status column doesn't exist, add it
                    cursor.execute("ALTER TABLE notifications ADD COLUMN invitation_status TEXT DEFAULT NULL")
                    print("Added 'invitation_status' column to notifications table")

                # Create default admin user if it doesn't exist
                cursor.execute("SELECT * FROM users WHERE id = 'ADMIN'")
                admin_exists = cursor.fetchone()
                if not admin_exists:
                    cursor.execute('''
                    INSERT INTO users (id, name, program, bio, profile_image, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', ('ADMIN', 'System Administrator', 'Administration', 'System admin account', '', 1))
                    print("Created default admin user (ID: ADMIN)")

                conn.commit()
                print("Database initialized successfully")

            self._initialized = True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections to ensure proper closing"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_user(self, user_id, name, program, bio='', profile_image='', is_admin=0, section=''):
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    INSERT OR REPLACE INTO users (id, name, program, bio, profile_image, is_admin, section)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, name, program, bio, profile_image, is_admin, section))
                    conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error adding user: {e}")
                return False
    
    def get_user(self, user_id):
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                    user = cursor.fetchone()
                    if user:
                        return dict(user)
                    return None
            except sqlite3.Error as e:
                print(f"Error getting user: {e}")
                return None

    def get_all_users(self):
        """Get all users from the database"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, name, program, section FROM users ORDER BY name')
                    users = cursor.fetchall()
                    return [dict(user) for user in users]
            except sqlite3.Error as e:
                print(f"Error getting all users: {e}")
                return []
    
    def update_user(self, user_id, name, program, bio='', profile_image='', is_admin=None, section=''):
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if is_admin is not None:
                        cursor.execute('''
                        UPDATE users
                        SET name = ?, program = ?, bio = ?, profile_image = ?, is_admin = ?, section = ?
                        WHERE id = ?
                        ''', (name, program, bio, profile_image, is_admin, section, user_id))
                    else:
                        cursor.execute('''
                        UPDATE users
                        SET name = ?, program = ?, bio = ?, profile_image = ?, section = ?
                        WHERE id = ?
                        ''', (name, program, bio, profile_image, section, user_id))
                    conn.commit()
                    return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error updating user: {e}")
                return False

    def search_users(self, search_term='', program='', section=''):
        """Search users by name, ID, program, and/or section"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()

                    # Build dynamic query based on provided filters
                    query = 'SELECT id, name, program, section FROM users WHERE 1=1'
                    params = []

                    if search_term:
                        query += ' AND (name LIKE ? OR id LIKE ?)'
                        params.extend([f'%{search_term}%', f'%{search_term}%'])

                    if program:
                        query += ' AND program = ?'
                        params.append(program)

                    if section:
                        query += ' AND section = ?'
                        params.append(section)

                    query += ' ORDER BY name'

                    cursor.execute(query, params)
                    users = cursor.fetchall()
                    return [dict(user) for user in users]
            except sqlite3.Error as e:
                print(f"Error searching users: {e}")
                return []

    def get_unique_programs(self):
        """Get list of unique programs from users"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT DISTINCT program FROM users WHERE program IS NOT NULL AND program != "" ORDER BY program')
                    programs = cursor.fetchall()
                    return [row[0] for row in programs]
            except sqlite3.Error as e:
                print(f"Error getting programs: {e}")
                return []

    def get_unique_sections(self, program=''):
        """Get list of unique sections, optionally filtered by program"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if program:
                        cursor.execute('SELECT DISTINCT section FROM users WHERE program = ? AND section IS NOT NULL AND section != "" ORDER BY section', (program,))
                    else:
                        cursor.execute('SELECT DISTINCT section FROM users WHERE section IS NOT NULL AND section != "" ORDER BY section')
                    sections = cursor.fetchall()
                    return [row[0] for row in sections]
            except sqlite3.Error as e:
                print(f"Error getting sections: {e}")
                return []

    def add_event(self, date, description, tagged_ids='', link='', image_path='', privacy='public', creator_id=''):
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    INSERT INTO events (date, description, tagged_ids, link, image_path, privacy, creator_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (date, description, tagged_ids, link, image_path, privacy, creator_id))
                    event_id = cursor.lastrowid

                    # Create notifications for tagged students
                    if tagged_ids and event_id:
                        student_ids = [id.strip() for id in tagged_ids.split(',') if id.strip()]
                        for student_id in student_ids:
                            # Get event title (first part before " - " if exists)
                            event_title = description
                            if " - " in description:
                                event_title = description.split(" - ", 1)[0].strip()

                            notification_title = "Event Invitation"
                            notification_message = f"You have been invited to '{event_title}' on {date}"

                            cursor.execute('''
                            INSERT INTO notifications (user_id, event_id, title, message, notification_type, invitation_status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (student_id, event_id, notification_title, notification_message, 'invitation', 'pending',
                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                    conn.commit()
                    return event_id
            except sqlite3.Error as e:
                print(f"Error adding event: {e}")
                return None
    
    def get_events_by_date(self, date, user_id=None):
        """Get events for a specific date, filtered by privacy and user permissions"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if user_id:
                        # Get public events OR private events where user is creator OR tagged
                        cursor.execute('''
                        SELECT * FROM events
                        WHERE date = ? AND (
                            privacy = 'public' OR
                            creator_id = ? OR
                            tagged_ids LIKE ?
                        )
                        ''', (date, user_id, f"%{user_id}%"))
                    else:
                        # If no user_id provided, only return public events
                        cursor.execute('SELECT * FROM events WHERE date = ? AND privacy = "public"', (date,))
                    events = cursor.fetchall()
                    return [dict(event) for event in events]
            except sqlite3.Error as e:
                print(f"Error getting events by date: {e}")
                return []
    
    def get_events_between_dates(self, start_date, end_date, user_id=None):
        """Get events between dates, filtered by privacy and user permissions"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if user_id:
                        # Get public events OR private events where user is creator OR tagged
                        cursor.execute('''
                        SELECT * FROM events
                        WHERE date BETWEEN ? AND ? AND (
                            privacy = 'public' OR
                            creator_id = ? OR
                            tagged_ids LIKE ?
                        )
                        ''', (start_date, end_date, user_id, f"%{user_id}%"))
                    else:
                        # If no user_id provided, only return public events
                        cursor.execute('''
                        SELECT * FROM events WHERE date BETWEEN ? AND ? AND privacy = "public"
                        ''', (start_date, end_date))
                    events = cursor.fetchall()
                    return [dict(event) for event in events]
            except sqlite3.Error as e:
                print(f"Error getting events between dates: {e}")
                return []

    def get_admin_events_between_dates(self, start_date, end_date):
        """Get only events created by admin users between dates"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    # Get events where creator is an admin user
                    cursor.execute('''
                    SELECT e.* FROM events e
                    INNER JOIN users u ON e.creator_id = u.id
                    WHERE e.date BETWEEN ? AND ? AND u.is_admin = 1
                    ORDER BY e.date ASC
                    ''', (start_date, end_date))
                    events = cursor.fetchall()
                    return [dict(event) for event in events]
            except sqlite3.Error as e:
                print(f"Error getting admin events between dates: {e}")
                return []

    def update_event(self, event_id, title=None, date=None, description=None, tagged_ids=None, link=None, image_path=None, privacy=None, tagged_students=None):
        """Update an event with only the provided parameters"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()

                    # Build dynamic update query based on provided parameters
                    update_fields = []
                    values = []

                    if title is not None:
                        update_fields.append("title = ?")
                        values.append(title)
                    if date is not None:
                        update_fields.append("date = ?")
                        values.append(date)
                    if description is not None:
                        update_fields.append("description = ?")
                        values.append(description)
                    if tagged_ids is not None:
                        update_fields.append("tagged_ids = ?")
                        values.append(tagged_ids)
                    if tagged_students is not None:
                        update_fields.append("tagged_ids = ?")
                        values.append(tagged_students)
                    if link is not None:
                        update_fields.append("link = ?")
                        values.append(link)
                    if image_path is not None:
                        update_fields.append("image_path = ?")
                        values.append(image_path)
                    if privacy is not None:
                        update_fields.append("privacy = ?")
                        values.append(privacy)

                    if not update_fields:
                        return False  # Nothing to update

                    # Add event_id to values for WHERE clause
                    values.append(event_id)

                    query = f"UPDATE events SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error updating event: {e}")
                return False
    
    def delete_event(self, event_id):
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
                    conn.commit()
                    return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error deleting event: {e}")
                return False

    def delete_user_events(self, user_id, include_notes=False):
        """Delete events created by a specific user and their related notifications

        Args:
            user_id: The user ID whose events to delete
            include_notes: If True, also delete personal notes. If False, only delete public events.
        """
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()

                    if include_notes:
                        # Delete ALL events created by this user (including notes)
                        cursor.execute('SELECT id FROM events WHERE creator_id = ?', (user_id,))
                        event_ids = [row[0] for row in cursor.fetchall()]

                        # Delete all events created by this user
                        cursor.execute('DELETE FROM events WHERE creator_id = ?', (user_id,))
                        deleted_count = cursor.rowcount
                    else:
                        # Only delete public events, preserve personal notes
                        cursor.execute('''
                        SELECT id FROM events
                        WHERE creator_id = ? AND (
                            privacy = 'public' OR
                            (privacy = 'private' AND description NOT LIKE 'Note:%')
                        )
                        ''', (user_id,))
                        event_ids = [row[0] for row in cursor.fetchall()]

                        # Delete only non-note events created by this user
                        cursor.execute('''
                        DELETE FROM events
                        WHERE creator_id = ? AND (
                            privacy = 'public' OR
                            (privacy = 'private' AND description NOT LIKE 'Note:%')
                        )
                        ''', (user_id,))
                        deleted_count = cursor.rowcount

                    # Delete notifications related to these events
                    if event_ids:
                        placeholders = ','.join('?' * len(event_ids))
                        cursor.execute(f'DELETE FROM notifications WHERE event_id IN ({placeholders})', event_ids)

                    # Also delete notifications for this user (in case they were tagged in other events)
                    cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))

                    conn.commit()
                    event_type = "events and notes" if include_notes else "events (notes preserved)"
                    print(f"Deleted {deleted_count} {event_type} for user {user_id}")
                    return deleted_count > 0
            except sqlite3.Error as e:
                print(f"Error deleting user events: {e}")
                return False
    
    def get_upcoming_events(self, user_id=None):
        """Get upcoming events for the current user, filtered by privacy"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    # Get current date in YYYY-MM-DD format
                    current_date = datetime.now().strftime('%Y-%m-%d')

                    if user_id:
                        # Get public events OR private events where user is creator OR tagged
                        query = """
                        SELECT id, date, description, image_path, tagged_ids, link, privacy, creator_id
                        FROM events
                        WHERE date >= ? AND (
                            privacy = 'public' OR
                            creator_id = ? OR
                            tagged_ids LIKE ?
                        )
                        ORDER BY date ASC
                        LIMIT 10
                        """
                        cursor.execute(query, (current_date, user_id, f"%{user_id}%"))
                    else:
                        # If no user_id provided, only return public events
                        query = """
                        SELECT id, date, description, image_path, tagged_ids, link, privacy, creator_id
                        FROM events
                        WHERE date >= ? AND privacy = 'public'
                        ORDER BY date ASC
                        LIMIT 10
                        """
                        cursor.execute(query, (current_date,))

                    events = cursor.fetchall()
                    return [dict(event) for event in events]
            except Exception as e:
                print(f"Error getting upcoming events: {e}")
                return []
    
    def get_events_by_tagged_id(self, user_id):
        """Get events where the user is tagged"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    query = """
                    SELECT id, date, description, image_path, tagged_ids, link
                    FROM events
                    WHERE tagged_ids LIKE ?
                    ORDER BY date ASC
                    """

                    # Use LIKE with wildcards to find the user_id in the tagged_ids field
                    # This assumes tagged_ids is stored as a comma-separated string
                    cursor.execute(query, (f"%{user_id}%",))
                    events = cursor.fetchall()
                    return [dict(event) for event in events]
            except Exception as e:
                print(f"Error getting events by tagged ID: {e}")
                return []

    def is_admin_user(self, user_id):
        """Check if a user is an admin"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
                    result = cursor.fetchone()
                    return result and result[0] == 1
            except sqlite3.Error as e:
                print(f"Error checking admin status: {e}")
                return False

    def add_notification(self, user_id, event_id, title, message, notification_type='notification'):
        """Add a notification for a user"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute('''
                    INSERT INTO notifications (user_id, event_id, title, message, notification_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, event_id, title, message, notification_type, created_at))
                    conn.commit()
                    return cursor.lastrowid
            except Exception as e:
                print(f"Error adding notification: {e}")
                return None

    def get_user_notifications(self, user_id, unread_only=False):
        """Get notifications for a user"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if unread_only:
                        query = """
                        SELECT n.*, e.description as event_description, e.date as event_date
                        FROM notifications n
                        LEFT JOIN events e ON n.event_id = e.id
                        WHERE n.user_id = ? AND n.is_read = 0
                        ORDER BY n.created_at DESC
                        """
                    else:
                        query = """
                        SELECT n.*, e.description as event_description, e.date as event_date
                        FROM notifications n
                        LEFT JOIN events e ON n.event_id = e.id
                        WHERE n.user_id = ?
                        ORDER BY n.created_at DESC
                        """
                    cursor.execute(query, (user_id,))
                    notifications = cursor.fetchall()
                    return [dict(notification) for notification in notifications]
            except Exception as e:
                print(f"Error getting notifications: {e}")
                return []

    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    UPDATE notifications SET is_read = 1 WHERE id = ?
                    ''', (notification_id,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                print(f"Error marking notification as read: {e}")
                return False

    def get_unread_notification_count(self, user_id):
        """Get count of unread notifications for a user"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0
                    ''', (user_id,))
                    count = cursor.fetchone()[0]
                    return count
            except Exception as e:
                print(f"Error getting unread notification count: {e}")
                return 0

    def get_event_by_id(self, event_id):
        """Get a specific event by ID"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    SELECT * FROM events WHERE id = ?
                    ''', (event_id,))
                    event = cursor.fetchone()
                    if event:
                        return dict(event)
                    return None
            except Exception as e:
                print(f"Error getting event by ID: {e}")
                return None

    def update_invitation_status(self, notification_id, status):
        """Update the status of an invitation (accept/decline)"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    UPDATE notifications
                    SET invitation_status = ?, is_read = 1
                    WHERE id = ? AND notification_type = 'invitation'
                    ''', (status, notification_id))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                print(f"Error updating invitation status: {e}")
                return False

    def delete_invitation_event(self, notification_id, user_id):
        """Delete an event associated with an invitation notification"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()

                    # First get the event_id from the notification
                    cursor.execute('''
                    SELECT event_id FROM notifications
                    WHERE id = ? AND user_id = ? AND notification_type = 'invitation'
                    ''', (notification_id, user_id))
                    result = cursor.fetchone()

                    if not result:
                        return False

                    event_id = result[0]

                    # Delete the event
                    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))

                    # Delete all notifications related to this event
                    cursor.execute('DELETE FROM notifications WHERE event_id = ?', (event_id,))

                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                print(f"Error deleting invitation event: {e}")
                return False

    def delete_notification(self, notification_id):
        """Delete a specific notification"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                print(f"Error deleting notification: {e}")
                return False

    def delete_multiple_notifications(self, notification_ids):
        """Delete multiple notifications by their IDs"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    placeholders = ','.join('?' * len(notification_ids))
                    cursor.execute(f'DELETE FROM notifications WHERE id IN ({placeholders})', notification_ids)
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                print(f"Error deleting multiple notifications: {e}")
                return 0
    
    def close(self):
        # No persistent connection to close since we use context managers
        pass

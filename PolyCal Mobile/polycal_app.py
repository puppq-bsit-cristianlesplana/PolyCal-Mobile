from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '380')
Config.set('graphics', 'height', '780')

import os
from datetime import datetime, timedelta
from calendar import month_name
import calendar
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty
from kivy.uix.spinner import Spinner
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.metrics import dp
from calendar import monthrange, day_abbr
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from database import DatabaseManager
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget  # Add this import
# Import DatePicker
# Add these imports at the top of the file if they're not already there
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, RoundedRectangle

# Global user data dictionary
user_data = {}

def create_nav_bar(current_screen):
    nav_bar = BoxLayout(size_hint_y=None, height=60, spacing=0, padding=0)

    # Check if current user is admin
    is_admin = user_data.get('is_admin', 0) == 1

    # Base navigation buttons
    btns = [
        ('main', 'Home'),
        ('calendar', 'Calendar'),
        ('profile', 'Profile'),
        ('settings', 'Settings'),
    ]

    # Add admin panel if user is admin
    if is_admin:
        btns.insert(-1, ('admin', 'Admin'))  # Insert before settings

    for target, label in btns:
        is_active = current_screen == target
        btn = Button(text=label, size_hint_x=1, background_normal='', background_color=(0.12, 0.47, 0.95, 1) if is_active else (0.85, 0.15, 0.15, 1), color=(1, 1, 1, 1), font_size='16sp', bold=True)
        btn.bind(on_release=lambda inst, t=target: setattr(App.get_running_app().root, 'current', t))
        nav_bar.add_widget(btn)
    return nav_bar



class LoginScreen(Screen):
    """Login screen for user authentication"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()

    def login(self):
        """Handle user login"""
        try:
            username = self.ids.username.text.strip()

            if not username:
                self.show_error("Please enter your Student ID")
                return

            # Check if user exists in database
            user = self.db.get_user(username)

            if user:
                # User exists, load their data
                global user_data
                user_data.clear()  # Clear existing data first
                user_data.update(user)

                # Ensure profile_image is properly loaded
                if 'profile_image' not in user_data or not user_data['profile_image']:
                    user_data['profile_image'] = ''

                print(f"Login successful. Profile image: {user_data.get('profile_image', 'None')}")  # Debug print
                self.manager.current = 'main'
            else:
                # User doesn't exist, redirect to signup
                self.show_error("Student ID not found. Please sign up first.")
                self.manager.current = 'signup'

        except Exception as e:
            print(f"Login error: {e}")
            self.show_error("Login failed. Please try again.")

    def show_error(self, message):
        """Show error popup"""
        popup = Popup(title='Error', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class SignupScreen(Screen):
    """Signup screen for new user registration"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()

    def create_account(self):
        """Handle account creation"""
        try:
            student_id = self.ids.id_input.text.strip()
            name = self.ids.name_input.text.strip()
            program = self.ids.program_input.text.strip()
            dob = self.ids.dob_input.text.strip()

            # Validate inputs
            if not all([student_id, name, program]):
                self.show_error("Please fill in all required fields")
                return

            # Check if user already exists
            existing_user = self.db.get_user(student_id)
            if existing_user:
                self.show_error("Student ID already exists. Please login instead.")
                return

            # Create new user
            success = self.db.add_user(student_id, name, program)

            if success:
                # Show success message
                popup = Popup(title='Success', content=Label(text='Account created successfully!\nPlease sign in with your Student ID.'), size_hint=(0.8, 0.4))
                popup.open()

                # Navigate to login screen after a delay (don't auto-login)
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.go_to_login(), 1.5)
            else:
                self.show_error("Failed to create account. Please try again.")

        except Exception as e:
            print(f"Signup error: {e}")
            self.show_error("Account creation failed. Please try again.")

    def go_to_login(self):
        """Navigate to login screen"""
        self.manager.current = 'login'

    def show_error(self, message):
        """Show error popup"""
        popup = Popup(title='Error', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class ProfileScreen(Screen):
    """Profile screen for user profile management"""
    profile_image_path = StringProperty("")  # Define as a Kivy property

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.profile_image_path = ''

    def on_enter(self):
        """Called when entering the profile screen"""
        self.load_profile_data()

    def load_profile_data(self):
        """Load user profile data from global user_data"""
        global user_data

        # Update the header name label
        if hasattr(self.ids, 'user_name_label'):
            user_name = user_data.get('name', 'User Name')
            self.ids.user_name_label.text = user_name

        # Update form fields with user data (with null checks)
        if 'id' in user_data and hasattr(self.ids, 'id_input'):
            self.ids.id_input.text = user_data.get('id', '') or ''
        if 'name' in user_data and hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = user_data.get('name', '') or ''
        if 'program' in user_data and hasattr(self.ids, 'program_input'):
            self.ids.program_input.text = user_data.get('program', '') or ''
        if 'bio' in user_data and hasattr(self.ids, 'bio_input'):
            bio_text = user_data.get('bio', '') or ''  # Handle None values
            self.ids.bio_input.text = bio_text

        # Update profile image
        self.profile_image_path = user_data.get('profile_image', '') or ''
        print(f"Loading profile image: {self.profile_image_path}")  # Debug print
        if hasattr(self.ids, 'profile_image'):
            if self.profile_image_path and os.path.exists(self.profile_image_path):
                self.ids.profile_image.source = self.profile_image_path
                print(f"Profile image set to: {self.profile_image_path}")  # Debug print
            else:
                self.ids.profile_image.source = 'ICON/Default Profile.png'
                print("Using default profile image")  # Debug print

    def save_profile(self):
        """Save profile changes"""
        try:
            user_id = self.ids.id_input.text.strip()
            name = self.ids.name_input.text.strip()
            program = self.ids.program_input.text.strip()
            bio = self.ids.bio_input.text.strip()

            if not all([user_id, name, program]):
                self.show_error("Please fill in all required fields")
                return

            # Update database
            success = self.db.update_user(user_id, name, program, bio, self.profile_image_path)

            if success:
                # Update global user data
                global user_data
                user_data.update({
                    'id': user_id,
                    'name': name,
                    'program': program,
                    'bio': bio,
                    'profile_image': self.profile_image_path
                })

                # Update the header name label immediately
                if hasattr(self.ids, 'user_name_label'):
                    self.ids.user_name_label.text = name

                # Show success message
                popup = Popup(
                    title='Success',
                    content=Label(text='Profile updated successfully!'),
                    size_hint=(0.8, 0.4)
                )
                popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
            else:
                self.show_error("Failed to update profile. Please try again.")

        except Exception as e:
            print(f"Profile save error: {e}")
            self.show_error("Failed to save profile. Please try again.")

    def open_file_chooser(self):
        """Open file chooser for profile image"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # File chooser for images
        file_chooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif'],
            path=os.path.expanduser('~')
        )
        content.add_widget(file_chooser)

        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(text="Select", size_hint_x=0.5, background_normal='', background_color=(0.85, 0.15, 0.15, 1))

        def cancel(instance):
            popup.dismiss()

        def select_image(instance):
            if file_chooser.selection:
                selected_path = file_chooser.selection[0]
                self.profile_image_path = selected_path
                print(f"Selected image: {selected_path}")  # Debug print

                # Update the image display immediately
                if hasattr(self.ids, 'profile_image'):
                    self.ids.profile_image.source = selected_path
                    print(f"Updated profile image display to: {selected_path}")  # Debug print

                # Force refresh of the image widget
                if hasattr(self.ids, 'profile_image'):
                    self.ids.profile_image.reload()

                # Automatically save the profile image to database
                self.save_profile_image_to_db(selected_path)

                popup.dismiss()

        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_image)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        popup = Popup(
            title="Select Profile Image",
            content=content,
            size_hint=(0.9, 0.8)
        )
        popup.open()

    def save_profile_image_to_db(self, image_path):
        """Automatically save the profile image to database"""
        try:
            global user_data

            # Get current user data
            user_id = user_data.get('id', '')
            name = user_data.get('name', '')
            program = user_data.get('program', '')
            bio = user_data.get('bio', '') or ''

            if not user_id:
                print("Error: No user ID found, cannot save profile image")
                return False

            # Update database with new profile image
            success = self.db.update_user(user_id, name, program, bio, image_path)

            if success:
                # Update global user data
                user_data['profile_image'] = image_path
                print(f"Profile image saved to database: {image_path}")

                # Show brief success message
                from kivy.clock import Clock
                success_popup = Popup(
                    title='Success',
                    content=Label(text='Profile image updated!'),
                    size_hint=(0.6, 0.3)
                )
                success_popup.open()
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.0)

                return True
            else:
                print("Failed to save profile image to database")
                return False

        except Exception as e:
            print(f"Error saving profile image: {e}")
            return False

    def update_char_count(self, text_input, text):
        """Update character count for bio field"""
        if hasattr(self.ids, 'char_count_label'):
            char_count = len(text)
            self.ids.char_count_label.text = f"{char_count}/120"

            # Limit to 120 characters
            if char_count > 120:
                text_input.text = text[:120]

    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class SettingsScreen(Screen):
    """Settings screen for app configuration"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()

    def clear_data(self):
        """Clear all user data"""
        # Show confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        content.add_widget(Label(text="Are you sure you want to clear all data?\nThis action cannot be undone.", font_size='16sp'))

        # Buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        confirm_btn = Button(text="Clear Data", size_hint_x=0.5, background_normal='', background_color=(0.9, 0.3, 0.3, 1))

        def cancel(instance):
            popup.dismiss()

        def confirm_clear(instance):
            popup.dismiss()
            self.perform_clear_data()

        cancel_btn.bind(on_release=cancel)
        confirm_btn.bind(on_release=confirm_clear)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Confirm Clear Data",
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def perform_clear_data(self):
        """Actually clear the data"""
        try:
            # Clear database (you might want to implement this in DatabaseManager)
            # For now, just clear global user data
            global user_data
            user_data.clear()

            # Show success message
            popup = Popup(
                title='Success',
                content=Label(text='Data cleared successfully!'),
                size_hint=(0.8, 0.4)
            )
            popup.open()

            # Navigate back to login
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.go_to_login(), 1.5)

        except Exception as e:
            print(f"Clear data error: {e}")
            self.show_error("Failed to clear data. Please try again.")

    def go_to_login(self):
        """Navigate to login screen"""
        self.manager.current = 'login'

    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
    
    def on_enter(self):
        # Update welcome message with user's name
        user_name = user_data.get('name', 'Iska')
        self.ids.welcome_label.text = f"Hello, {user_name}!"

        # Update month display
        self.ids.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

        # Load events for the main screen (refresh every time we enter)
        self.load_events()

    def change_month(self, step):
        """Change the displayed month by the given number of steps"""
        self.current_month += step
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        elif self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        
        # Update month display
        self.ids.month_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"
        
        # Reload events for the new month
        self.load_events()
    
    def load_events(self):
        # Clear existing events
        if hasattr(self.ids, 'event_list'):
            self.ids.event_list.clear_widgets()

        # Get ONLY admin-created events for the current month (MainScreen shows only admin events)
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        last_day = monthrange(self.current_year, self.current_month)[1]
        end_date = f"{self.current_year}-{self.current_month:02d}-{last_day:02d}"
        month_events = self.db.get_admin_events_between_dates(start_date, end_date)
        
        # Add spacing at the top
        self.ids.event_list.add_widget(Widget(size_hint_y=None, height=dp(10)))
        
        # Display events for this month
        if month_events:
            for event in month_events:
                # Pass the event directly as dictionary to preserve all fields including creator_id
                self.add_event_to_list(event)
        else:
            # No events message
            no_events_card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(80),
                padding=dp(15),
                spacing=dp(5)
            )
            
            # Add white background with rounded corners
            with no_events_card.canvas.before:
                Color(1, 1, 1, 1)  # White background
                RoundedRectangle(pos=no_events_card.pos, size=no_events_card.size, radius=[15])
            
            no_events_label = Label(text=f"No events for {calendar.month_name[self.current_month]}", color=(0.5, 0.5, 0.5, 1), font_size='16sp', halign='center', valign='middle')
            no_events_card.add_widget(no_events_label)
            self.ids.event_list.add_widget(no_events_card)
        
        # Add spacing at the bottom to ensure content doesn't get hidden by navigation bar
        self.ids.event_list.add_widget(Widget(size_hint_y=None, height=dp(80)))
            
    def add_event_to_list(self, event):
        # Create event card
        event_container = self.create_event_card(event)
        self.ids.event_list.add_widget(event_container)
    
    def create_event_card(self, event):
        # Handle both dictionary and tuple formats
        if isinstance(event, dict):
            event_id = event.get('id')
            date = event.get('date')
            description = event.get('description')
            image_path = event.get('image_path')
            tagged_ids = event.get('tagged_ids')
            link = event.get('link')
            creator_id = event.get('creator_id')
        else:
            # Handle tuple format - check if it includes creator_id
            if len(event) >= 7:
                # Tuple with creator_id: (id, date, description, image_path, tagged_ids, link, creator_id)
                event_id, date, description, image_path, tagged_ids, link, creator_id = event[:7]
            else:
                # Legacy tuple format: (id, date, description, image_path, tagged_ids, link)
                event_id, date, description, image_path, tagged_ids, link = event[:6]
                creator_id = None

        # Parse title from description (no subtitle/details in main screen)
        title = description

        # Handle different event types
        if description.startswith("Note: "):
            # For notes, show "Note: [content]" as title
            title = description
        elif " - " in description:
            # For regular events with title - description format, only show title part
            parts = description.split(" - ", 1)
            title = parts[0].strip()

        # Truncate title if it's too long (show partial title)
        max_title_length = 45  # Adjust this value as needed
        if len(title) > max_title_length:
            title = title[:max_title_length] + "..."

        # Format date to match your design (MM/DD/YYYY)
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%m/%d/%Y')
        except:
            formatted_date = date

        # MainScreen only shows admin events, so all events here are admin-created
        # Use red color for admin events (as requested)
        card_color = (1.0, 0.8, 0.8, 1)  # Light red for admin events

        # Create card with colored background and rounded corners
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),  # Fixed height since we only show title
            padding=[dp(15), dp(12), dp(15), dp(12)],
            spacing=dp(3)
        )

        # Add colored background with rounded corners
        with card.canvas.before:
            Color(*card_color)  # Use determined color
            RoundedRectangle(pos=card.pos, size=card.size, radius=[10])

        # Update background when position/size changes
        card.bind(pos=self.update_card_background, size=self.update_card_background)

        # Header with title and date
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(24)
        )

        # Title (left side)
        title_label = Label(text=title, font_size='15sp', bold=True, halign='left', valign='middle', color=(0.15, 0.15, 0.15, 1), size_hint_x=0.8)
        title_label.bind(size=title_label.setter('text_size'))

        # Date (right side)
        date_label = Label(text=formatted_date, font_size='10sp', halign='right', valign='middle', color=(0.5, 0.5, 0.5, 1), size_hint_x=0.3)
        date_label.bind(size=date_label.setter('text_size'))

        header.add_widget(title_label)
        header.add_widget(date_label)
        card.add_widget(header)

        # No subtitle/details shown in main screen - only visible when viewing details

        # Container for card with spacing
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=card.height + dp(15),  # Card height + spacing
            padding=[0, 0, 0, dp(10)]  # Bottom spacing
        )

        container.add_widget(card)

        # Make the card clickable to show details
        card.bind(on_touch_down=lambda instance, touch:
                self.show_event_details(event) if instance.collide_point(*touch.pos) else None)

        return container

    def update_card_background(self, instance, value):
        """Update card background when position/size changes"""
        try:
            # Find the RoundedRectangle instruction in the canvas
            from kivy.graphics import RoundedRectangle
            for instruction in instance.canvas.before.children:
                if isinstance(instruction, RoundedRectangle):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except Exception as e:
            print(f"Error updating card background: {e}")

    def show_event_details(self, event):
        """Navigate to event details screen"""
        # Navigate to view event screen
        view_screen = self.manager.get_screen('view_event')
        view_screen.set_event(event)
        self.manager.current = 'view_event'

    def edit_event(self, event, parent_popup=None):
        """Open edit event popup"""
        if parent_popup:
            parent_popup.dismiss()
        
        self.show_edit_event_popup(event)

    def confirm_delete_event(self, event_id, parent_popup=None):
        """Show enhanced confirmation dialog before deleting event"""
        if parent_popup:
            parent_popup.dismiss()

        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning icon and title
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)

        # Warning icon (using emoji)
        warning_icon = Label(text="⚠️", font_size='24sp', size_hint_x=None, width=dp(40))

        # Warning title
        warning_title = Label(text="Delete Event", font_size='18sp', bold=True, color=(0.9, 0.3, 0.3, 1), halign='left')
        warning_title.bind(size=warning_title.setter('text_size'))

        title_layout.add_widget(warning_icon)
        title_layout.add_widget(warning_title)
        content.add_widget(title_layout)

        # Warning message
        warning_message = Label(
            text="Are you sure you want to delete this event?\n\nThis action cannot be undone and the event will be permanently removed from your calendar.",
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(15))

        cancel_btn = Button(text="Cancel", size_hint_x=0.5, background_normal='', background_color=(0.7, 0.7, 0.7, 1), color=(1, 1, 1, 1), font_size='16sp')

        confirm_btn = Button(text="Delete Event", size_hint_x=0.5, background_normal='', background_color=(0.9, 0.3, 0.3, 1), color=(1, 1, 1, 1), font_size='16sp', bold=True)

        # Create popup
        confirm_popup = Popup(
            title="⚠️ Confirm Deletion",
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )

        # Bind actions
        def cancel_deletion(instance):
            confirm_popup.dismiss()

        def confirm_deletion(instance):
            confirm_popup.dismiss()
            self.delete_event_and_dismiss(event_id, None)

        cancel_btn.bind(on_release=cancel_deletion)
        confirm_btn.bind(on_release=confirm_deletion)

        # Add buttons to layout
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)

        # Show popup
        confirm_popup.open()

    def delete_event_and_dismiss(self, event_id, popup):
        """Delete event and dismiss popup"""
        popup.dismiss()
        self.delete_event(event_id)

    def show_edit_event_popup(self, event):
        """Show popup to edit event details"""
        # Check if event is a dictionary or tuple and extract values accordingly
        if isinstance(event, dict):
            event_id = event.get('id')
            current_date = event.get('date')
            current_description = event.get('description')
            current_image_path = event.get('image_path')
            current_tagged_ids = event.get('tagged_ids')
            current_link = event.get('link')
        else:  # Assume it's a tuple
            event_id, current_date, current_description, current_image_path, current_tagged_ids, current_link = event

        # Try to split title and description if they exist
        title_text = ""
        desc_text = ""

        if current_description and " - " in current_description:
            parts = current_description.split(" - ", 1)
            title_text = parts[0].replace("Note: ", "")  # Remove "Note: " prefix if it exists
            desc_text = parts[1]
        else:
            title_text = current_description.replace("Note: ", "") if current_description else ""

        # Create main layout with scrollable content
        main_layout = BoxLayout(orientation='vertical', spacing=5, padding=10)

        # Scrollable content area
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=15, padding=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Title input section
        title_label = Label(
            text="Title",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        title_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        layout.add_widget(title_label)

        title_input = TextInput(
            text=title_text,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(title_input)

        # Description input section
        desc_label = Label(
            text="Description",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        desc_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        layout.add_widget(desc_label)

        desc_input = TextInput(
            text=desc_text,
            multiline=True,
            size_hint_y=None,
            height=dp(100)  # Increased height
        )
        layout.add_widget(desc_input)

        # Tagged IDs input section
        tag_label = Label(
            text="Tagged IDs (comma separated)",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        tag_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        layout.add_widget(tag_label)

        tag_input = TextInput(
            text=current_tagged_ids or "",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(tag_input)

        # Link input section
        link_label = Label(
            text="Link",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        link_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        layout.add_widget(link_label)

        link_input = TextInput(
            text=current_link or "",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(link_input)
        
        # Image selection section
        image_label_text = Label(
            text="Image",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        image_label_text.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        layout.add_widget(image_label_text)

        image_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=5)
        image_label = Label(
            text=f"Current image: {current_image_path if current_image_path else 'None'}",
            size_hint_x=0.7,
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        image_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 10, None)))
        image_btn = Button(text="Change Image", size_hint_x=0.3)

        # Container for image path
        image_path = [current_image_path]

        def show_image_picker(instance):
            self.show_image_picker_popup(image_label, image_path, "Select Event Image")

        image_btn.bind(on_release=show_image_picker)
        image_layout.add_widget(image_label)
        image_layout.add_widget(image_btn)
        layout.add_widget(image_layout)

        # Add the scrollable content to the scroll view
        scroll.add_widget(layout)
        main_layout.add_widget(scroll)

        # Buttons (outside scroll area)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)

        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.7, 0.7, 0.7, 1))

        update_btn = Button(text="Update", background_normal='', background_color=(0.85, 0.15, 0.15, 1))

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(update_btn)
        main_layout.add_widget(button_layout)

        # Create popup
        popup = Popup(title="Edit Event/Note", content=main_layout, size_hint=(0.9, 0.8))

        def cancel_edit(instance):
            popup.dismiss()

        def update_event(instance):
            # Get values from inputs
            title = title_input.text.strip()
            description = desc_input.text.strip()

            # Validation: Check if title is provided
            if not title:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text='Please enter a title'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Validation: Check title length (max 50 characters)
            if len(title) > 50:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text='Title must be 50 characters or less'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Validation: Check description length (max 200 characters for events, 300 for notes)
            is_note = current_description and current_description.startswith("Note:")
            max_desc_length = 300 if is_note else 200
            desc_type = "note content" if is_note else "description"

            if description and len(description) > max_desc_length:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text=f'{desc_type.capitalize()} must be {max_desc_length} characters or less'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Combine title and description
            if is_note:
                full_description = f"Note: {title}"
            else:
                full_description = title

            if description:
                full_description += f" - {description}"

            success = self.update_event_in_db(
                event_id,
                current_date,
                full_description,
                image_path[0],
                tag_input.text,
                link_input.text
            )

            if success:
                self.load_events()  # Refresh events on main screen
                popup.dismiss()

                # Show success message
                success_popup = Popup(
                    title='Success',
                    content=Label(text='Updated successfully!'),
                    size_hint=(0.6, 0.3)
                )
                success_popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
            else:
                # Show error message
                error_popup = Popup(
                    title='Error',
                    content=Label(text='Failed to update!'),
                    size_hint=(0.6, 0.3)
                )
                error_popup.open()

        cancel_btn.bind(on_release=cancel_edit)
        update_btn.bind(on_release=update_event)

        popup.open()

    def update_event_in_db(self, event_id, date, description, image_path, tagged_ids, link):
        """Update event in database"""
        try:
            self.db.update_event(event_id, date, description, image_path, tagged_ids, link)
            return True
        except Exception as e:
            print(f"Error updating event: {e}")
            return False



    def delete_event(self, event_id):
        """Delete event from database and refresh the main screen"""
        try:
            self.db.delete_event(event_id)
            self.load_events()  # Refresh the main screen event list

            # Show success message
            success_popup = Popup(
                title='Success',
                content=Label(text='Event deleted successfully!'),
                size_hint=(0.6, 0.3)
            )
            success_popup.open()

            # Auto-dismiss after 1.5 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
        except Exception as e:
            print(f"Error deleting event: {e}")
            # Show error message
            error_popup = Popup(
                title='Error',
                content=Label(text=f'Failed to delete event: {str(e)}'),
                size_hint=(0.6, 0.3)
            )
            error_popup.open()

    def get_events_for_current_month(self):
        # Get all events for the current month
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        end_date = f"{self.current_year}-{self.current_month:02d}-31"
        return self.db.get_events_between_dates(start_date, end_date) # Implement this method in DatabaseManager

    def show_image_picker_popup(self, label_widget, image_path_container, title, details=None):
        """Show a file chooser popup to select an image and update the provided label"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # File chooser for images
        file_chooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif'],
            path=os.path.expanduser('~')  # Start in user's home directory
        )
        content.add_widget(file_chooser)

        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(text="Select", size_hint_x=0.5, background_normal='', background_color=(0.85, 0.15, 0.15, 1))

        def cancel(instance):
            image_popup.dismiss()

        def select_image(instance):
            if file_chooser.selection:
                selected_path = file_chooser.selection[0]
                # Update the label
                if isinstance(image_path_container, dict):
                    # For dictionary containers (like in CalendarScreen)
                    label_widget.text = os.path.basename(selected_path)
                    image_path_container['path'] = selected_path
                else:
                    # For list containers (like in MainScreen)
                    label_widget.text = f"Current image: {os.path.basename(selected_path)}"
                    image_path_container[0] = selected_path
                image_popup.dismiss()

        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_image)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        image_popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.8)
        )
        image_popup.open()



class DatePicker(BoxLayout):
    def __init__(self, year=None, month=None, day=None, **kwargs):
        super(DatePicker, self).__init__(orientation='vertical', **kwargs)
        
        # Set default date to today if not provided
        today = datetime.now()
        self.year = year if year else today.year
        self.month = month if month else today.month
        self.day = day if day else today.day
        
        # Create date object
        self.date = datetime(self.year, self.month, self.day)
        
        # Month and year selection
        header = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
        
        # Previous month button
        prev_btn = Button(text="<", size_hint_x=0.15)
        prev_btn.bind(on_release=self.prev_month)
        
        # Month/Year label
        self.date_label = Label(
            text=f"{calendar.month_name[self.month]} {self.year}",
            size_hint_x=0.7
        )
        
        # Next month button
        next_btn = Button(text=">", size_hint_x=0.15)
        next_btn.bind(on_release=self.next_month)
        
        header.add_widget(prev_btn)
        header.add_widget(self.date_label)
        header.add_widget(next_btn)
        self.add_widget(header)
        
        # Days grid
        self.days_grid = GridLayout(cols=7)
        self.build_days()
        self.add_widget(self.days_grid)
    
    def build_days(self):
        self.days_grid.clear_widgets()
        
        # Add day headers
        for day_abbr in calendar.day_abbr:
            self.days_grid.add_widget(Label(text=day_abbr[:1]))
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.year, self.month)
        
        # Add day buttons
        for week in cal:
            for day in week:
                if day == 0:
                    # Empty day
                    self.days_grid.add_widget(Label(text=""))
                else:
                    day_btn = ToggleButton(text=str(day), group='days')
                    if day == self.day:
                        day_btn.state = 'down'
                    day_btn.bind(on_release=lambda btn: self.select_day(int(btn.text)))
                    self.days_grid.add_widget(day_btn)
    
    def select_day(self, day):
        self.day = day
        self.date = datetime(self.year, self.month, self.day)
    
    def prev_month(self, instance):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.date_label.text = f"{calendar.month_name[self.month]} {self.year}"
        self.day = min(self.day, calendar.monthrange(self.year, self.month)[1])
        self.date = datetime(self.year, self.month, self.day)
        self.build_days()
    
    def next_month(self, instance):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.date_label.text = f"{calendar.month_name[self.month]} {self.year}"
        self.day = min(self.day, calendar.monthrange(self.year, self.month)[1])
        self.date = datetime(self.year, self.month, self.day)
        self.build_days()

class AddEventScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.selected_date = None
        self.selected_students = []
        self.image_path_container = {'path': ''}
        self.build_ui()

    def build_ui(self):
        # Main layout with light gray background - consistent with other screens
        main_layout = BoxLayout(orientation='vertical')

        # Add light gray background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Red header with logo and title - consistent with other screens
        header_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )

        # Add red background to header
        with header_layout.canvas.before:
            Color(0.85, 0.15, 0.15, 1)  # Red color
            Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self.update_header_bg, size=self.update_header_bg)

        # PUP Logo
        logo = Image(
            source='PUPlogo.png',
            size_hint_x=None,
            width=dp(40),
            fit_mode='contain'
        )

        # Title
        title_label = Label(text="PolyCal - Add Event", font_size='24sp', bold=True, color=(1, 1, 1, 1), halign='left', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))

        # Back button
        back_btn = Button(text="← Back", size_hint_x=None, width=dp(80), background_normal='', background_color=(0.3, 0.3, 0.3, 1), color=(1, 1, 1, 1), font_size='14sp')
        back_btn.bind(on_release=self.go_back)

        header_layout.add_widget(logo)
        header_layout.add_widget(title_label)
        header_layout.add_widget(back_btn)
        main_layout.add_widget(header_layout)

        # Content area with padding
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Scroll view for the form
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=[0, dp(10)])
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))

        self.date_label = Label(text="Date: Select a date", size_hint_x=0.7, halign='left', font_size='16sp', bold=True, color=(0.85, 0.15, 0.15, 1))
        self.date_label.bind(size=self.date_label.setter('text_size'))

        # Date picker button
        date_btn = Button(text="Select Date", size_hint_x=0.3, background_normal='', background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1), font_size='14sp')
        date_btn.bind(on_release=self.open_date_picker)

        date_layout.add_widget(self.date_label)
        date_layout.add_widget(date_btn)
        form_layout.add_widget(date_layout)

        # Title input
        title_section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(70))
        title_label = Label(text="Event Title *", size_hint_y=None, height=dp(25), halign='left', font_size='14sp', bold=True, color=(0.66, 0.66, 0.66, 1))
        title_label.bind(size=title_label.setter('text_size'))

        self.title_input = TextInput(hint_text="Enter event title", multiline=False, size_hint_y=None, height=dp(40), font_size='14sp')

        title_section.add_widget(title_label)
        title_section.add_widget(self.title_input)
        form_layout.add_widget(title_section)

        # Description input
        desc_section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        desc_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))

        desc_label = Label(text="Description *", halign='left', font_size='14sp', bold=True, size_hint_x=0.7, color=(0.66, 0.66, 0.66, 1))
        desc_label.bind(size=desc_label.setter('text_size'))

        self.char_counter = Label(text="0/200", halign='right', font_size='12sp', color=(0.6, 0.6, 0.6, 1), size_hint_x=0.3)

        desc_header.add_widget(desc_label)
        desc_header.add_widget(self.char_counter)

        self.desc_input = TextInput(hint_text="Enter event description (max 200 characters)", multiline=True, size_hint_y=None, height=dp(90), font_size='14sp')
        self.desc_input.bind(text=self.update_char_counter)

        desc_section.add_widget(desc_header)
        desc_section.add_widget(self.desc_input)
        form_layout.add_widget(desc_section)

        self.add_student_tagging_section(form_layout)
        self.add_additional_fields_section(form_layout)
        self.add_action_buttons(form_layout)

        scroll.add_widget(form_layout)
        content_layout.add_widget(scroll)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        """Update main background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_header_bg(self, instance, value):
        """Update header background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_nav_bg(self, instance, value):
        """Update navigation background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def add_student_tagging_section(self, parent_layout):
        # Student tagging section
        students_section = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        students_section.bind(minimum_height=students_section.setter('height'))

        # Section header
        students_header = Label(
            text="Tag Students",
            size_hint_y=None,
            height=dp(30),
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        students_header.bind(size=students_header.setter('text_size'))
        students_section.add_widget(students_header)

        # Search input
        self.search_input = TextInput(
            hint_text="🔍 Search by Student ID or Name",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size='14sp'
        )
        self.search_input.bind(on_text_validate=self.search_students)
        students_section.add_widget(self.search_input)

        # Program filter
        filter_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))

        filter_label = Label(
            text="Filter by Program:",
            size_hint_x=0.4,
            halign='left',
            font_size='14sp',
            bold=True,
            color=(0.66, 0.66, 0.66, 1)
        )
        filter_label.bind(size=filter_label.setter('text_size'))

        self.program_spinner = Spinner(
            text='All Programs',
            values=['All Programs'],
            size_hint_x=0.6,
            font_size='12sp'
        )

        filter_layout.add_widget(filter_label)
        filter_layout.add_widget(self.program_spinner)
        students_section.add_widget(filter_layout)

        # Search button
        search_btn = Button(text="🔍 Search Students", size_hint_y=None, height=dp(45), background_normal='', background_color=(0.2, 0.6, 0.9, 1), font_size='14sp', bold=True)
        search_btn.bind(on_release=self.search_students)
        students_section.add_widget(search_btn)

        # Results header
        results_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
        results_label = Label(text="Available Students:",halign='left',font_size='14sp',bold=True,size_hint_x=0.7, color=(0.66, 0.66, 0.66, 1))
        results_label.bind(size=results_label.setter('text_size'))

        clear_btn = Button(text="Clear All", size_hint_x=0.3, size_hint_y=None, height=dp(30), background_normal='', background_color=(0.9, 0.3, 0.3, 1), font_size='12sp')
        clear_btn.bind(on_release=self.clear_all_students)

        results_header.add_widget(results_label)
        results_header.add_widget(clear_btn)
        students_section.add_widget(results_header)

        # Results scroll view
        results_scroll = ScrollView(
            size_hint_y=None,
            height=dp(150)
        )

        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))

        results_scroll.add_widget(self.results_layout)
        students_section.add_widget(results_scroll)

        # Selected students display
        selected_header = Label(
            text="Selected Students:",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            font_size='14sp',
            bold=True,
            color=(0.66, 0.66, 0.66, 1)
        )
        selected_header.bind(size=selected_header.setter('text_size'))
        students_section.add_widget(selected_header)

        self.selected_label = Label(
            text="None selected",
            size_hint_y=None,
            height=dp(60),
            halign='left',
            valign='top',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        self.selected_label.bind(size=self.selected_label.setter('text_size'))
        students_section.add_widget(self.selected_label)

        parent_layout.add_widget(students_section)

        # Load initial data
        self.load_initial_data()

    def add_additional_fields_section(self, parent_layout):
        # Image selection
        image_section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))
        image_label = Label(
            text="Event Image (optional)",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            font_size='14sp',
            bold=True,
            color=(0.66, 0.66, 0.66, 1)
        )
        image_label.bind(size=image_label.setter('text_size'))

        image_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))

        self.image_label = Label(
            text="No image selected",
            halign='left',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=0.7
        )
        self.image_label.bind(size=self.image_label.setter('text_size'))

        image_btn = Button(text="Select Image", size_hint_x=0.3, background_normal='', background_color=(0.4, 0.4, 0.4, 1), font_size='12sp')
        image_btn.bind(on_release=self.show_image_picker)

        image_layout.add_widget(self.image_label)
        image_layout.add_widget(image_btn)

        image_section.add_widget(image_label)
        image_section.add_widget(image_layout)
        parent_layout.add_widget(image_section)

    def add_action_buttons(self, parent_layout):
        # Action buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15),
            padding=[0, dp(20)]
        )

        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.7, 0.7, 0.7, 1), font_size='16sp', bold=True)
        cancel_btn.bind(on_release=self.cancel_add_event)

        add_btn = Button(text="Add Event", background_normal='', background_color=(0.85, 0.15, 0.15, 1), font_size='16sp', bold=True)
        add_btn.bind(on_release=self.add_event)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(add_btn)
        parent_layout.add_widget(button_layout)

    def load_initial_data(self):
        """Load programs and initialize search"""
        programs = self.db.get_unique_programs()
        self.program_spinner.values = ['All Programs'] + programs
        self.search_students()

    def update_char_counter(self, instance, text):
        """Update character counter for description"""
        char_count = len(text)
        self.char_counter.text = f"{char_count}/200"
        if char_count > 200:
            self.char_counter.color = (1, 0, 0, 1)  # Red if over limit
        else:
            self.char_counter.color = (0.6, 0.6, 0.6, 1)  # Gray if within limit

    def update_selected_display(self):
        """Update the selected students display"""
        if self.selected_students:
            student_names = []
            for student_id in self.selected_students:
                student = self.db.get_user(student_id)
                if student:
                    student_names.append(f"• {student['name']} ({student_id})")
            self.selected_label.text = '\n'.join(student_names)
            self.selected_label.color = (0.2, 0.2, 0.2, 1)
        else:
            self.selected_label.text = "None selected"
            self.selected_label.color = (0.6, 0.6, 0.6, 1)

    def clear_all_students(self, instance):
        """Clear all selected students"""
        self.selected_students.clear()
        self.update_selected_display()
        self.search_students()

    def search_students(self, instance=None):
        """Search and display students"""
        self.results_layout.clear_widgets()

        search_term = self.search_input.text.strip()
        program_filter = self.program_spinner.text if self.program_spinner.text != 'All Programs' else ''

        students = self.db.search_users(search_term, program_filter, '')

        if students:
            for student in students:
                student_card = self.create_student_card(student)
                self.results_layout.add_widget(student_card)
        else:
            no_results = Label(
                text="No students found matching your criteria",
                size_hint_y=None,
                height=dp(40),
                halign='center',
                font_size='13sp',
                color=(0.6, 0.6, 0.6, 1)
            )
            self.results_layout.add_widget(no_results)

    def create_student_card(self, student):
        """Create a student card widget"""
        from kivy.graphics import Color, RoundedRectangle

        student_card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10),
            padding=[dp(10), dp(5)]
        )

        # Add background
        with student_card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=student_card.pos, size=student_card.size, radius=[5])

        # Update background when position/size changes
        def update_bg(instance, value):
            try:
                for instruction in instance.canvas.before.children:
                    if isinstance(instruction, RoundedRectangle):
                        instruction.pos = instance.pos
                        instruction.size = instance.size
                        break
            except:
                pass

        student_card.bind(pos=update_bg, size=update_bg)

        # Student info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.75, spacing=dp(2))

        name_label = Label(
            text=f"{student['name']} ({student['id']})",
            halign='left',
            font_size='13sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=0.6
        )
        name_label.bind(size=name_label.setter('text_size'))

        program_text = student.get('program', '')
        program_label = Label(
            text=program_text,
            halign='left',
            font_size='11sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.4
        )
        program_label.bind(size=program_label.setter('text_size'))

        info_layout.add_widget(name_label)
        info_layout.add_widget(program_label)

        # Add/Remove button
        is_selected = student['id'] in self.selected_students
        action_btn = Button(text="✓ Added" if is_selected else "+ Add", size_hint_x=0.25, background_normal='', background_color=(0.9, 0.3, 0.3, 1) if is_selected else (0.2, 0.7, 0.2, 1), font_size='12sp', bold=True)

        def toggle_student(btn, student_id=student['id']):
            if student_id in self.selected_students:
                self.selected_students.remove(student_id)
                btn.text = "+ Add"
                btn.background_color = (0.2, 0.7, 0.2, 1)
            else:
                self.selected_students.append(student_id)
                btn.text = "/ Added"
                btn.background_color = (0.9, 0.3, 0.3, 1)
            self.update_selected_display()
            self.search_students()

        action_btn.bind(on_release=toggle_student)

        student_card.add_widget(info_layout)
        student_card.add_widget(action_btn)

        return student_card

    def show_image_picker(self, instance):
        """Show image picker popup"""
        # For now, just show a placeholder message
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Image Selection',
            content=Label(text='Image selection feature\nwill be implemented here'),
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def set_date(self, date_str):
        """Set the selected date"""
        self.selected_date = date_str
        self.date_label.text = f"Date: {date_str}"

    def go_back(self, instance):
        """Go back to calendar screen"""
        self.manager.current = 'calendar'

    def cancel_add_event(self, instance):
        """Cancel adding event with confirmation if data entered"""
        has_data = (
            self.title_input.text.strip() or
            self.desc_input.text.strip() or
            self.link_input.text.strip() or
            len(self.selected_students) > 0 or
            self.image_path_container['path']
        )

        if has_data:
            self.show_cancel_confirmation()
        else:
            self.go_back(instance)

    def show_cancel_confirmation(self):
        """Show confirmation dialog when canceling with data"""
        from kivy.uix.popup import Popup

        layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))

        message = Label(
            text="Are you sure you want to cancel?\n\nAny unsaved changes will be lost.",
            halign='center',
            font_size='14sp'
        )

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        continue_btn = Button(text="Continue Editing", background_normal='', background_color=(0.2, 0.6, 0.9, 1))

        cancel_btn = Button(text="Discard Changes", background_normal='', background_color=(0.9, 0.3, 0.3, 1))

        popup = Popup(
            title='Confirm Cancel',
            content=layout,
            size_hint=(0.8, 0.4)
        )

        continue_btn.bind(on_release=lambda x: popup.dismiss())
        cancel_btn.bind(on_release=lambda x: (popup.dismiss(), self.go_back(None)))

        button_layout.add_widget(continue_btn)
        button_layout.add_widget(cancel_btn)

        layout.add_widget(message)
        layout.add_widget(button_layout)

        popup.open()

    def add_event(self, instance):
        """Add the event to database"""
        # Validate required fields
        title = self.title_input.text.strip()
        description = self.desc_input.text.strip()

        if not title:
            self.show_error("Please enter an event title")
            return

        if not description:
            self.show_error("Please enter an event description")
            return

        if len(description) > 200:
            self.show_error("Description must be 200 characters or less")
            return

        if not self.selected_date:
            self.show_error("Please select a date")
            return

        # Combine title and description
        full_description = f"{title} - {description}"

        # Get other fields
        link = self.link_input.text.strip()
        image_path = self.image_path_container['path']

        # Automatically determine privacy
        privacy = 'private' if self.selected_students else 'public'

        # Get tagged IDs
        tagged_ids_str = ','.join(self.selected_students) if self.selected_students else ''

        # Get current user ID as creator from global user_data
        global user_data
        creator_id = user_data.get('id', '')

        # Add event to database
        success = self.db.add_event(
            self.selected_date,
            full_description,
            tagged_ids_str,
            link,
            image_path,
            privacy,
            creator_id
        )

        if success:
            self.show_success("Event added successfully!")
            # Clear form
            self.clear_form()
            # Go back to calendar
            self.manager.current = 'calendar'
            # Refresh calendar
            calendar_screen = self.manager.get_screen('calendar')
            calendar_screen.build_calendar()
        else:
            self.show_error("Failed to add event. Please try again.")

    def clear_form(self):
        """Clear all form fields"""
        self.title_input.text = ""
        self.desc_input.text = ""
        self.link_input.text = ""
        self.search_input.text = ""
        self.selected_students.clear()
        self.image_path_container['path'] = ""
        self.image_label.text = "No image selected"
        self.program_spinner.text = "All Programs"
        self.update_selected_display()
        self.search_students()

    def show_error(self, message):
        """Show error popup"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def show_success(self, message):
        """Show success popup"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Success',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

        # Auto-dismiss after 1.5 seconds
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def open_date_picker(self, instance):
        """Open date picker popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout
        from kivy.uix.gridlayout import GridLayout
        from datetime import datetime, timedelta
        import calendar as cal

        content = PopupBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        # Current date for default
        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # Month/Year navigation
        nav_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

        prev_btn = Button(text="<", size_hint_x=None, width=dp(40))
        month_label = Label(text=f"{cal.month_name[current_month]} {current_year}", font_size='16sp')
        next_btn = Button(text=">", size_hint_x=None, width=dp(40))

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(month_label)
        nav_layout.add_widget(next_btn)
        content.add_widget(nav_layout)

        # Calendar grid
        calendar_grid = GridLayout(cols=7, spacing=dp(2))

        # Day headers
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            calendar_grid.add_widget(Label(text=day, font_size='12sp', size_hint_y=None, height=dp(30)))

        # Calendar days
        month_calendar = cal.monthcalendar(current_year, current_month)
        selected_date = None

        def create_day_button(day):
            if day == 0:
                return Label(text="", size_hint_y=None, height=dp(40))

            btn = Button(text=str(day), size_hint_y=None, height=dp(40), background_normal='', background_color=(0.9, 0.9, 0.9, 1), color=(0, 0, 0, 1), font_size='14sp')

            def select_date(instance):
                nonlocal selected_date
                selected_date = f"{current_year}-{current_month:02d}-{day:02d}"
                # Update button appearance
                for child in calendar_grid.children:
                    if hasattr(child, 'background_color'):
                        child.background_color = (0.9, 0.9, 0.9, 1)
                instance.background_color = (0.85, 0.15, 0.15, 1)  # Red for selected

            btn.bind(on_release=select_date)
            return btn

        for week in month_calendar:
            for day in week:
                calendar_grid.add_widget(create_day_button(day))

        content.add_widget(calendar_grid)

        # Buttons
        button_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(text="Select", size_hint_x=0.5, background_normal='', background_color=(0.85, 0.15, 0.15, 1))

        popup = Popup(title='Select Date', content=content, size_hint=(0.9, 0.8))

        def cancel(instance):
            popup.dismiss()

        def select_date_final(instance):
            if selected_date:
                self.set_selected_date(selected_date)
            popup.dismiss()

        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_date_final)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        popup.open()

    def set_selected_date(self, date_str):
        """Set the selected date"""
        self.selected_date = date_str
        # Format date for display
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            self.date_label.text = f"Date: {formatted_date}"
        except:
            self.date_label.text = f"Date: {date_str}"

class AddNoteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.selected_date = None
        self.build_ui()

    def build_ui(self):
        # Main layout with light gray background - consistent with other screens
        main_layout = BoxLayout(orientation='vertical')

        # Add light gray background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Red header with logo and title - consistent with other screens
        header_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )

        # Add red background to header
        with header_layout.canvas.before:
            Color(0.85, 0.15, 0.15, 1)  # Red color
            Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self.update_header_bg, size=self.update_header_bg)

        # PUP Logo
        logo = Image(
            source='PUPlogo.png',
            size_hint_x=None,
            width=dp(40),
            fit_mode='contain'
        )

        # Title
        title_label = Label(
            text="PolyCal - Add Note",
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))

        # Back button
        back_btn = Button(
            text="← Back",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.3, 0.3, 0.3, 1),  # Dark gray
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        back_btn.bind(on_release=self.go_back)

        header_layout.add_widget(logo)
        header_layout.add_widget(title_label)
        header_layout.add_widget(back_btn)
        main_layout.add_widget(header_layout)

        # Content area with padding
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Scroll view for the form
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None, padding=[0, dp(10)])
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))

        self.date_label = Label(
            text="Date: Select a date",
            size_hint_x=0.7,
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))

        # Date picker button
        date_btn = Button(text="Select Date", size_hint_x=0.3, background_normal='', background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1), font_size='14sp')
        date_btn.bind(on_release=self.open_date_picker)

        date_layout.add_widget(self.date_label)
        date_layout.add_widget(date_btn)
        form_layout.add_widget(date_layout)

        # Title input
        title_label = Label(text="Note Title *", size_hint_y=None, height=dp(25), halign='left', font_size='16sp', bold=True, color=(0.85, 0.15, 0.15, 1))
        title_label.bind(size=title_label.setter('text_size'))
        form_layout.add_widget(title_label)

        self.title_input = TextInput(hint_text="Enter note title (max 50 characters)", multiline=False, size_hint_y=None, height=dp(40), background_normal='', background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), cursor_color=(0.85, 0.15, 0.15, 1), font_size='14sp')
        self.title_input.bind(text=self.update_title_char_counter)
        form_layout.add_widget(self.title_input)

        # Title character counter
        self.title_char_counter = Label(text="0/50", size_hint_y=None, height=dp(20), halign='right', font_size='12sp', color=(0.6, 0.6, 0.6, 1))
        self.title_char_counter.bind(size=self.title_char_counter.setter('text_size'))
        form_layout.add_widget(self.title_char_counter)

        # Note content input
        note_section = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(200))

        # Note header with character counter
        note_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))

        note_label = Label(text="Note Content *", halign='left', font_size='16sp', bold=True, color=(0.85, 0.15, 0.15, 1), size_hint_x=0.7)
        note_label.bind(size=note_label.setter('text_size'))

        self.char_counter = Label(text="0/200", halign='right', font_size='12sp', color=(0.6, 0.6, 0.6, 1), size_hint_x=0.3)

        note_header.add_widget(note_label)
        note_header.add_widget(self.char_counter)

        # Note input
        self.note_input = TextInput(hint_text="Enter your note here (max 200 characters)", multiline=True, size_hint_y=None, height=dp(160), font_size='14sp')
        self.note_input.bind(text=self.update_char_counter)

        note_section.add_widget(note_header)
        note_section.add_widget(self.note_input)
        form_layout.add_widget(note_section)

        # Action buttons with consistent styling
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(15), padding=[0, dp(20)])

        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.7, 0.7, 0.7, 1), color=(1, 1, 1, 1), font_size='16sp', bold=True)
        cancel_btn.bind(on_release=self.cancel_add_note)

        add_btn = Button(text="Add Note", background_normal='', background_color=(0.85, 0.15, 0.15, 1), color=(1, 1, 1, 1), font_size='16sp', bold=True)
        add_btn.bind(on_release=self.add_note)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(add_btn)
        form_layout.add_widget(button_layout)

        scroll.add_widget(form_layout)
        content_layout.add_widget(scroll)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        """Update main background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_header_bg(self, instance, value):
        """Update header background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_nav_bg(self, instance, value):
        """Update navigation background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_char_counter(self, instance, text):
        """Update character counter for note content"""
        char_count = len(text)
        self.char_counter.text = f"{char_count}/200"
        if char_count > 200:
            self.char_counter.color = (1, 0, 0, 1)  # Red if over limit
        else:
            self.char_counter.color = (0.6, 0.6, 0.6, 1)  # Gray if within limit

    def update_title_char_counter(self, instance, text):
        """Update character counter for note title"""
        char_count = len(text)
        self.title_char_counter.text = f"{char_count}/50"
        if char_count > 50:
            self.title_char_counter.color = (1, 0, 0, 1)  # Red if over limit
            # Limit to 50 characters
            instance.text = text[:50]
        elif char_count > 45:
            self.title_char_counter.color = (1, 0.5, 0, 1)  # Orange if approaching limit
        else:
            self.title_char_counter.color = (0.6, 0.6, 0.6, 1)  # Gray if within limit

    def set_date(self, date_str):
        """Set the selected date"""
        self.selected_date = date_str
        self.date_label.text = f"Date: {date_str}"

    def go_back(self, instance):
        """Go back to calendar screen"""
        self.manager.current = 'calendar'

    def cancel_add_note(self, instance):
        """Cancel adding note with confirmation if data entered"""
        if self.note_input.text.strip():
            self.show_cancel_confirmation()
        else:
            self.go_back(instance)

    def show_cancel_confirmation(self):
        """Show confirmation dialog when canceling with data"""
        from kivy.uix.popup import Popup

        layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))

        message = Label(text="Are you sure you want to cancel?\n\nAny unsaved changes will be lost.", halign='center', font_size='14sp')

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        continue_btn = Button(text="Continue Editing", background_normal='', background_color=(0.2, 0.6, 0.9, 1))

        cancel_btn = Button(text="Discard Changes", background_normal='', background_color=(0.9, 0.3, 0.3, 1))

        popup = Popup(title='Confirm Cancel', content=layout, size_hint=(0.8, 0.4))

        continue_btn.bind(on_release=lambda x: popup.dismiss())
        cancel_btn.bind(on_release=lambda x: (popup.dismiss(), self.go_back(None)))

        button_layout.add_widget(continue_btn)
        button_layout.add_widget(cancel_btn)

        layout.add_widget(message)
        layout.add_widget(button_layout)

        popup.open()

    def add_note(self, instance):
        """Add the note to database"""
        # Validate required fields
        title = self.title_input.text.strip()
        note_content = self.note_input.text.strip()

        if not title:
            self.show_error("Please enter note title")
            return

        if not note_content:
            self.show_error("Please enter note content")
            return

        if len(title) > 50:
            self.show_error("Note title must be 50 characters or less")
            return

        if len(note_content) > 200:
            self.show_error("Note content must be 200 characters or less")
            return

        if not self.selected_date:
            self.show_error("Please select a date")
            return

        # Format note with title and content
        full_description = f"Note: {title} - {note_content}"

        # Get current user ID as creator from global user_data
        global user_data
        creator_id = user_data.get('id', '')

        # Add note to database (notes are always private to the creator)
        success = self.db.add_event(
            self.selected_date,
            full_description,
            '',  # No tagged IDs for personal notes
            '',  # No link for notes
            '',  # No image for notes
            'private',  # Notes are always private
            creator_id
        )

        if success:
            self.show_success("Note added successfully!")
            # Clear form
            self.clear_form()
            # Go back to calendar
            self.manager.current = 'calendar'
            # Refresh calendar
            calendar_screen = self.manager.get_screen('calendar')
            calendar_screen.build_calendar()
        else:
            self.show_error("Failed to add note. Please try again.")

    def clear_form(self):
        """Clear all form fields"""
        self.title_input.text = ""
        self.note_input.text = ""

    def show_error(self, message):
        """Show error popup with consistent styling"""
        from kivy.uix.popup import Popup
        popup = Popup(title='Error', content=Label(text=message, halign='center'), size_hint=(0.7, 0.3))
        popup.open()

    def show_success(self, message):
        """Show success popup with consistent styling"""
        from kivy.uix.popup import Popup
        popup = Popup(title='Success', content=Label(text=message, halign='center'), size_hint=(0.7, 0.3))
        popup.open()

        # Auto-dismiss after 1.5 seconds
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def open_date_picker(self, instance):
        """Open date picker popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout
        from kivy.uix.gridlayout import GridLayout
        from datetime import datetime, timedelta
        import calendar as cal

        content = PopupBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        # Current date for default
        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # Month/Year navigation
        nav_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

        prev_btn = Button(text="<", size_hint_x=None, width=dp(40))
        month_label = Label(text=f"{cal.month_name[current_month]} {current_year}", font_size='16sp')
        next_btn = Button(text=">", size_hint_x=None, width=dp(40))

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(month_label)
        nav_layout.add_widget(next_btn)
        content.add_widget(nav_layout)

        # Calendar grid
        calendar_grid = GridLayout(cols=7, spacing=dp(2))

        # Day headers
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            calendar_grid.add_widget(Label(text=day, font_size='12sp', size_hint_y=None, height=dp(30)))

        # Calendar days
        month_calendar = cal.monthcalendar(current_year, current_month)
        selected_date = None

        def create_day_button(day):
            if day == 0:
                return Label(text="", size_hint_y=None, height=dp(40))

            btn = Button(
                text=str(day),
                size_hint_y=None,
                height=dp(40),
                background_normal='',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1),
                font_size='14sp'
            )

            def select_date(instance):
                nonlocal selected_date
                selected_date = f"{current_year}-{current_month:02d}-{day:02d}"
                # Update button appearance
                for child in calendar_grid.children:
                    if hasattr(child, 'background_color'):
                        child.background_color = (0.9, 0.9, 0.9, 1)
                instance.background_color = (0.85, 0.15, 0.15, 1)  # Red for selected

            btn.bind(on_release=select_date)
            return btn

        for week in month_calendar:
            for day in week:
                calendar_grid.add_widget(create_day_button(day))

        content.add_widget(calendar_grid)

        # Buttons
        button_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(
            text="Select",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)
        )

        popup = Popup(
            title='Select Date',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def cancel(instance):
            popup.dismiss()

        def select_date_final(instance):
            if selected_date:
                self.set_date(selected_date)
            popup.dismiss()

        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_date_final)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        popup.open()

class ViewEventScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_event = None
        self.build_ui()

    def build_ui(self):
        # Main layout with light gray background - consistent with other screens
        main_layout = BoxLayout(orientation='vertical')

        # Add light gray background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Red header with logo and title - consistent with other screens
        header_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )

        # Add red background to header
        with header_layout.canvas.before:
            Color(0.85, 0.15, 0.15, 1)  # Red color
            Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self.update_header_bg, size=self.update_header_bg)

        # PUP Logo
        logo = Image(
            source='PUPlogo.png',
            size_hint_x=None,
            width=dp(40),
            fit_mode='contain'
        )

        # Title
        self.title_label = Label(
            text="PolyCal - Event Details",
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text
            halign='left',
            valign='middle'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))

        # Back button
        back_btn = Button(
            text="← Back",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.3, 0.3, 0.3, 1),  # Dark gray
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        back_btn.bind(on_release=self.go_back)

        header_layout.add_widget(logo)
        header_layout.add_widget(self.title_label)
        header_layout.add_widget(back_btn)
        main_layout.add_widget(header_layout)

        # Content area with padding
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Scroll view for the content
        scroll = ScrollView()
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None, padding=[0, dp(10)])
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        scroll.add_widget(self.content_layout)
        content_layout.add_widget(scroll)

        # Action buttons layout
        self.action_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15),
            padding=[0, dp(20)]
        )
        content_layout.add_widget(self.action_layout)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        """Update main background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_header_bg(self, instance, value):
        """Update header background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_nav_bg(self, instance, value):
        """Update navigation background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def set_event(self, event_data):
        """Set the event data to display"""
        self.current_event = event_data
        self.populate_content()

    def populate_content(self):
        """Populate the screen with event details"""
        if not self.current_event:
            return

        # Clear existing content
        self.content_layout.clear_widgets()
        self.action_layout.clear_widgets()

        event = self.current_event

        # Determine if it's a note or event
        description = event.get('description', '')
        is_note = description.startswith("Note:")

        # Update title
        self.title_label.text = "Note Details" if is_note else "Event Details"

        # Date section
        date_section = self.create_info_section("Date", event.get('date', 'N/A'))
        self.content_layout.add_widget(date_section)

        # Title and description section
        if is_note:
            # For notes, show content without "Note:" prefix
            note_content = description[5:].strip() if len(description) > 5 else description
            content_section = self.create_info_section("Note Content", note_content)
        else:
            # For events, split title and description
            if " - " in description:
                title, desc = description.split(" - ", 1)
                title_section = self.create_info_section("Title", title)
                self.content_layout.add_widget(title_section)
                content_section = self.create_info_section("Description", desc)
            else:
                content_section = self.create_info_section("Description", description)

        self.content_layout.add_widget(content_section)

        # Tagged students section (only for events)
        if not is_note and event.get('tagged_ids'):
            tagged_ids = event.get('tagged_ids', '').split(',')
            tagged_students = []
            for student_id in tagged_ids:
                if student_id.strip():
                    student = self.db.get_user(student_id.strip())
                    if student:
                        tagged_students.append(f"• {student['name']} ({student_id.strip()})")

            if tagged_students:
                students_text = '\n'.join(tagged_students)
                students_section = self.create_info_section("Tagged Students", students_text)
                self.content_layout.add_widget(students_section)

        # Link section (if available)
        if event.get('link'):
            link_section = self.create_info_section("Event Link", event.get('link'))
            self.content_layout.add_widget(link_section)

        # Privacy section
        privacy = event.get('privacy', 'public')
        privacy_section = self.create_info_section("Visibility", privacy.title())
        self.content_layout.add_widget(privacy_section)

        # Creator section
        creator_id = event.get('creator_id', '')
        if creator_id:
            creator = self.db.get_user(creator_id)
            creator_name = creator['name'] if creator else f"User {creator_id}"
            creator_section = self.create_info_section("Created by", creator_name)
            self.content_layout.add_widget(creator_section)

        # Add action buttons
        self.add_action_buttons(event)

    def create_info_section(self, label, content):
        """Create a styled information section"""
        section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))

        # Label
        label_widget = Label(
            text=label,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            font_size='14sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        label_widget.bind(size=label_widget.setter('text_size'))

        # Content with card background
        content_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(15)
        )
        content_card.bind(minimum_height=content_card.setter('height'))

        # Add background
        from kivy.graphics import Color, RoundedRectangle
        with content_card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background - consistent with app
            RoundedRectangle(pos=content_card.pos, size=content_card.size, radius=[5])

        # Update background when position/size changes
        def update_bg(instance, value):
            try:
                for instruction in instance.canvas.before.children:
                    if isinstance(instruction, RoundedRectangle):
                        instruction.pos = instance.pos
                        instruction.size = instance.size
                        break
            except:
                pass

        content_card.bind(pos=update_bg, size=update_bg)

        content_widget = Label(
            text=content,
            halign='left',
            valign='top',
            font_size='13sp',
            color=(0.3, 0.3, 0.3, 1),
            text_size=(None, None)
        )
        content_widget.bind(size=content_widget.setter('text_size'))

        content_card.add_widget(content_widget)

        section.add_widget(label_widget)
        section.add_widget(content_card)

        return section

    def add_action_buttons(self, event):
        """Add action buttons based on event type and permissions"""
        # Get current user from global user_data
        global user_data
        current_user_id = user_data.get('id', '')
        creator_id = event.get('creator_id', '')

        # Check if current user is the creator
        is_creator = current_user_id == creator_id

        # Back button (always available)
        back_btn = Button(
            text="Back to Calendar",
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray - consistent with app
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        back_btn.bind(on_release=self.go_back)
        self.action_layout.add_widget(back_btn)

        # Edit button (only for creators)
        if is_creator:
            # Check if this is a note to show appropriate button text
            description = event.get('description', '')
            is_note = description.startswith('Note: ')
            button_text = "Edit Note" if is_note else "Edit Event"

            edit_btn = Button(
                text=button_text,
                background_normal='',
                background_color=(0.2, 0.6, 0.9, 1),  # Blue - consistent with app
                color=(1, 1, 1, 1),
                font_size='14sp',
                bold=True
            )
            edit_btn.bind(on_release=self.edit_event)
            self.action_layout.add_widget(edit_btn)

            # Delete button (only for creators)
            delete_btn = Button(
                text="Delete",
                background_normal='',
                background_color=(0.9, 0.3, 0.3, 1),  # Secondary red - consistent with app
                color=(1, 1, 1, 1),
                font_size='14sp',
                bold=True
            )
            delete_btn.bind(on_release=self.delete_event)
            self.action_layout.add_widget(delete_btn)
        else:
            # Show info for non-creators
            info_label = Label(
                text="You can only edit events you created",
                font_size='12sp',
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(30)
            )
            self.action_layout.add_widget(info_label)

    def go_back(self, instance):
        """Go back to calendar screen"""
        self.manager.current = 'calendar'

    def edit_event(self, instance):
        """Navigate to appropriate edit screen (event or note)"""
        if not self.current_event:
            return

        # Check if this is a note (description starts with "Note: ")
        description = self.current_event.get('description', '')
        is_note = description.startswith('Note: ')

        if is_note:
            # Navigate to edit note screen
            edit_screen = self.manager.get_screen('edit_note')
            edit_screen.set_note_data(self.current_event)
            self.manager.current = 'edit_note'
        else:
            # Navigate to edit event screen
            edit_screen = self.manager.get_screen('edit_event')
            edit_screen.set_event_data(self.current_event)
            self.manager.current = 'edit_event'

    def delete_event(self, instance):
        """Show delete confirmation"""
        if not self.current_event:
            return

        from kivy.uix.popup import Popup

        layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))

        # Warning message
        event_title = "this item"
        description = self.current_event.get('description', '')
        if description:
            if description.startswith("Note:"):
                event_title = "this note"
            else:
                if " - " in description:
                    title_part = description.split(" - ", 1)[0]
                    event_title = f'"{title_part}"'
                else:
                    event_title = f'"{description[:30]}..."' if len(description) > 30 else f'"{description}"'

        message = Label(
            text=f"Are you sure you want to delete {event_title}?\n\nThis action cannot be undone.",
            halign='center',
            font_size='14sp'
        )

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(
            text="Cancel",
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1)  # Gray - consistent with app
        )

        delete_btn = Button(
            text="Delete",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1)  # Secondary red - consistent with app
        )

        popup = Popup(
            title='Confirm Delete',
            content=layout,
            size_hint=(0.8, 0.4)
        )

        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        delete_btn.bind(on_release=lambda x: (popup.dismiss(), self.perform_delete()))

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)

        layout.add_widget(message)
        layout.add_widget(button_layout)

        popup.open()

    def perform_delete(self):
        """Actually delete the event"""
        if not self.current_event:
            return

        event_id = self.current_event.get('id')
        if event_id:
            success = self.db.delete_event(event_id)
            if success:
                # Show success message
                from kivy.uix.popup import Popup
                popup = Popup(
                    title='Success',
                    content=Label(text='Item deleted successfully!'),
                    size_hint=(0.6, 0.3)
                )
                popup.open()

                # Auto-dismiss and go back
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: (popup.dismiss(), self.go_back(None)), 1.5)

                # Refresh calendar
                calendar_screen = self.manager.get_screen('calendar')
                calendar_screen.build_calendar()
            else:
                # Show error message
                from kivy.uix.popup import Popup
                popup = Popup(
                    title='Error',
                    content=Label(text='Failed to delete item!'),
                    size_hint=(0.6, 0.3)
                )
                popup.open()

class EditEventScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_event = None
        self.selected_date = None
        self.build_ui()

    def build_ui(self):
        # Main layout with light gray background - consistent with other screens
        main_layout = BoxLayout(orientation='vertical')

        # Add light gray background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Red header with logo and title - consistent with other screens
        header_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )

        # Add red background to header
        with header_layout.canvas.before:
            Color(0.85, 0.15, 0.15, 1)  # Red color
            Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self.update_header_bg, size=self.update_header_bg)

        # PUP Logo
        logo = Image(
            source='PUPlogo.png',
            size_hint_x=None,
            width=dp(40),
            fit_mode='contain'
        )

        # Title
        title_label = Label(
            text="PolyCal - Edit Event",
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))

        # Back button
        back_btn = Button(
            text="← Back",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.3, 0.3, 0.3, 1),  # Dark gray
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        back_btn.bind(on_release=self.go_back)

        header_layout.add_widget(logo)
        header_layout.add_widget(title_label)
        header_layout.add_widget(back_btn)
        main_layout.add_widget(header_layout)

        # Content area with padding
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Scroll view for the form
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=[0, dp(10)])
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Title input
        title_label = Label(
            text="Event Title *",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        title_label.bind(size=title_label.setter('text_size'))
        form_layout.add_widget(title_label)

        self.title_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0.85, 0.15, 0.15, 1),
            font_size='14sp'
        )
        form_layout.add_widget(self.title_input)

        # Description input with character counter
        desc_header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))

        desc_label = Label(
            text="Description *",
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1),  # Red color - consistent with other screens
            size_hint_x=0.7
        )
        desc_label.bind(size=desc_label.setter('text_size'))

        self.char_counter = Label(
            text="0/200",
            halign='right',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=0.3
        )

        desc_header_layout.add_widget(desc_label)
        desc_header_layout.add_widget(self.char_counter)
        form_layout.add_widget(desc_header_layout)

        self.description_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0.85, 0.15, 0.15, 1),
            font_size='14sp'
        )
        self.description_input.bind(text=self.update_char_counter)
        form_layout.add_widget(self.description_input)

        # Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))

        self.date_label = Label(
            text="Date: Not set",
            size_hint_x=0.7,
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))

        # Date picker button
        date_btn = Button(
            text="Change Date",
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),  # Blue - consistent with app
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        date_btn.bind(on_release=self.open_date_picker)

        date_layout.add_widget(self.date_label)
        date_layout.add_widget(date_btn)
        form_layout.add_widget(date_layout)

        # Student tagging section
        self.add_student_tagging_section(form_layout)

        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(15))

        # Cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Light gray - consistent with app
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        cancel_btn.bind(on_release=self.cancel_edit)

        # Save button
        save_btn = Button(
            text="Save Changes",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1),  # Primary red - consistent with app
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        save_btn.bind(on_release=self.save_event)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        form_layout.add_widget(button_layout)

        scroll.add_widget(form_layout)
        content_layout.add_widget(scroll)

        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        """Update main background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_header_bg(self, instance, value):
        """Update header background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def add_student_tagging_section(self, parent_layout):
        """Add student tagging interface"""
        # Section header
        students_header = Label(
            text="Tagged Students",
            size_hint_y=None,
            height=dp(30),
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        students_header.bind(size=students_header.setter('text_size'))
        parent_layout.add_widget(students_header)

        # Search and filter layout
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))

        # Search input
        self.search_input = TextInput(
            hint_text="Search by Student ID or Name",
            size_hint_x=0.5,
            multiline=False,
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            font_size='14sp'
        )
        self.search_input.bind(text=self.on_search_text)

        # Program filter
        self.program_spinner = Spinner(
            text='All Programs',
            values=['All Programs'],
            size_hint_x=0.3,
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            font_size='12sp'
        )
        self.program_spinner.bind(text=self.on_program_filter)

        # Section filter
        self.section_spinner = Spinner(
            text='All Sections',
            values=['All Sections'],
            size_hint_x=0.2,
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            font_size='12sp'
        )
        self.section_spinner.bind(text=self.on_section_filter)

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(self.program_spinner)
        search_layout.add_widget(self.section_spinner)
        parent_layout.add_widget(search_layout)

        # Selected students display
        selected_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))

        self.selected_label = Label(
            text="None selected",
            size_hint_x=0.7,
            halign='left',
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        self.selected_label.bind(size=self.selected_label.setter('text_size'))

        clear_btn = Button(
            text="Clear All",
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(25),
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Secondary red - consistent with app
            font_size='12sp'
        )
        clear_btn.bind(on_release=self.clear_all_students)

        selected_layout.add_widget(self.selected_label)
        selected_layout.add_widget(clear_btn)
        parent_layout.add_widget(selected_layout)

        # Students list scroll view
        students_scroll = ScrollView(size_hint_y=None, height=dp(150))
        self.students_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            padding=[0, dp(5)]
        )
        self.students_layout.bind(minimum_height=self.students_layout.setter('height'))

        students_scroll.add_widget(self.students_layout)
        parent_layout.add_widget(students_scroll)

        # Initialize data
        self.selected_students = set()
        self.all_students = []
        self.load_students_data()

    def update_char_counter(self, instance, text):
        """Update character counter for description"""
        char_count = len(text)
        self.char_counter.text = f"{char_count}/200"

        # Change color based on limit
        if char_count > 200:
            self.char_counter.color = (1, 0, 0, 1)  # Red if over limit
        elif char_count > 180:
            self.char_counter.color = (1, 0.5, 0, 1)  # Orange if near limit
        else:
            self.char_counter.color = (0.6, 0.6, 0.6, 1)  # Gray if normal

    def load_students_data(self):
        """Load students from database"""
        try:
            students = self.db.get_all_students()
            self.all_students = students

            # Get unique programs and sections
            programs = list(set(student.get('program', 'Unknown') for student in students))
            sections = list(set(student.get('section', 'Unknown') for student in students))

            self.program_spinner.values = ['All Programs'] + sorted(programs)
            self.section_spinner.values = ['All Sections'] + sorted(sections)

            self.search_students()
        except Exception as e:
            print(f"Error loading students: {e}")

    def on_search_text(self, instance, text):
        """Handle search text changes"""
        self.search_students()

    def on_program_filter(self, spinner, text):
        """Handle program filter changes"""
        self.search_students()

    def on_section_filter(self, spinner, text):
        """Handle section filter changes"""
        self.search_students()

    def search_students(self):
        """Search and filter students"""
        self.students_layout.clear_widgets()

        search_text = self.search_input.text.lower()
        program_filter = self.program_spinner.text
        section_filter = self.section_spinner.text

        filtered_students = []
        for student in self.all_students:
            # Apply search filter
            if search_text:
                student_id = str(student.get('id', '')).lower()
                name = f"{student.get('first_name', '')} {student.get('last_name', '')}".lower()
                if search_text not in student_id and search_text not in name:
                    continue

            # Apply program filter
            if program_filter != 'All Programs':
                if student.get('program', '') != program_filter:
                    continue

            # Apply section filter
            if section_filter != 'All Sections':
                if student.get('section', '') != section_filter:
                    continue

            filtered_students.append(student)

        # Display filtered students
        for student in filtered_students[:20]:  # Limit to 20 for performance
            self.add_student_button(student)

    def add_student_button(self, student):
        """Add a student button to the list"""
        student_id = str(student.get('id', ''))
        name = f"{student.get('first_name', '')} {student.get('last_name', '')}"
        program = student.get('program', 'Unknown')
        section = student.get('section', 'Unknown')

        is_selected = student_id in self.selected_students

        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))

        # Student info
        info_label = Label(
            text=f"{student_id} - {name} ({program} - {section})",
            halign='left',
            font_size='12sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_x=0.8
        )
        info_label.bind(size=info_label.setter('text_size'))

        # Add/Remove button
        action_btn = Button(
            text="Remove" if is_selected else "Add",
            size_hint_x=0.2,
            size_hint_y=None,
            height=dp(30),
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1) if is_selected else (0.2, 0.7, 0.2, 1),
            font_size='10sp',
            bold=True
        )
        action_btn.bind(on_release=lambda x, s_id=student_id: self.toggle_student_selection(s_id))

        btn_layout.add_widget(info_label)
        btn_layout.add_widget(action_btn)
        self.students_layout.add_widget(btn_layout)

    def toggle_student_selection(self, student_id):
        """Toggle student selection"""
        if student_id in self.selected_students:
            self.selected_students.remove(student_id)
        else:
            self.selected_students.add(student_id)

        self.update_selected_display()
        self.search_students()  # Refresh to update button states

    def update_selected_display(self):
        """Update the selected students display"""
        if self.selected_students:
            count = len(self.selected_students)
            self.selected_label.text = f"{count} student(s) selected"
            self.selected_label.color = (0.2, 0.7, 0.2, 1)  # Green
        else:
            self.selected_label.text = "None selected"
            self.selected_label.color = (0.6, 0.6, 0.6, 1)

    def clear_all_students(self, instance):
        """Clear all selected students"""
        self.selected_students.clear()
        self.update_selected_display()
        self.search_students()  # Refresh to update button states

    def set_event_data(self, event_data):
        """Set the event data to edit"""
        self.current_event = event_data
        if event_data:
            # Populate form fields
            self.title_input.text = event_data.get('title', '')
            self.description_input.text = event_data.get('description', '')

            # Set date
            event_date = event_data.get('date', '')
            self.selected_date = event_date
            # Format date for display
            try:
                from datetime import datetime
                date_obj = datetime.strptime(event_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%B %d, %Y')
                self.date_label.text = f"Date: {formatted_date}"
            except:
                self.date_label.text = f"Date: {event_date}"

            # Set selected students
            tagged_students = event_data.get('tagged_students', [])
            if isinstance(tagged_students, str):
                # Handle comma-separated string
                tagged_students = [s.strip() for s in tagged_students.split(',') if s.strip()]

            self.selected_students = set(str(s) for s in tagged_students)
            self.update_selected_display()

            # Update character counter
            self.update_char_counter(None, self.description_input.text)

    def cancel_edit(self, instance):
        """Cancel editing and go back"""
        # Show confirmation if there are unsaved changes
        if self.has_unsaved_changes():
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout

            content = PopupBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

            message = Label(
                text="You have unsaved changes.\nAre you sure you want to cancel?",
                halign='center',
                font_size='16sp'
            )

            button_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

            cancel_btn = Button(
                text="Keep Editing",
                background_normal='',
                background_color=(0.7, 0.7, 0.7, 1),
                font_size='14sp'
            )

            confirm_btn = Button(
                text="Discard Changes",
                background_normal='',
                background_color=(0.9, 0.3, 0.3, 1),
                font_size='14sp'
            )

            popup = Popup(
                title='Unsaved Changes',
                content=content,
                size_hint=(0.8, 0.4)
            )

            cancel_btn.bind(on_release=lambda x: popup.dismiss())
            confirm_btn.bind(on_release=lambda x: (popup.dismiss(), self.go_back(None)))

            button_layout.add_widget(cancel_btn)
            button_layout.add_widget(confirm_btn)
            content.add_widget(message)
            content.add_widget(button_layout)

            popup.open()
        else:
            self.go_back(None)

    def has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        if not self.current_event:
            return False

        # Check title
        if self.title_input.text != self.current_event.get('title', ''):
            return True

        # Check description
        if self.description_input.text != self.current_event.get('description', ''):
            return True

        # Check tagged students
        original_students = self.current_event.get('tagged_students', [])
        if isinstance(original_students, str):
            original_students = [s.strip() for s in original_students.split(',') if s.strip()]
        original_set = set(str(s) for s in original_students)

        if self.selected_students != original_set:
            return True

        return False

    def save_event(self, instance):
        """Save the edited event"""
        # Validate inputs
        title = self.title_input.text.strip()
        description = self.description_input.text.strip()

        if not title:
            self.show_error("Please enter an event title")
            return

        if not description:
            self.show_error("Please enter an event description")
            return

        if len(description) > 200:
            self.show_error("Description must be 200 characters or less")
            return

        if not self.current_event:
            self.show_error("No event data to update")
            return

        try:
            # Get current user ID as creator from global user_data
            global user_data
            creator_id = user_data.get('id', '')

            # Prepare tagged students
            tagged_students_list = list(self.selected_students)
            tagged_students_str = ','.join(tagged_students_list) if tagged_students_list else ''

            # Update event in database
            event_id = self.current_event.get('id')
            success = self.db.update_event(
                event_id=event_id,
                title=title,
                date=self.selected_date,
                description=description,
                tagged_students=tagged_students_str
            )

            if success:
                # Show success message
                from kivy.uix.popup import Popup
                popup = Popup(
                    title='Success',
                    content=Label(text='Event updated successfully!'),
                    size_hint=(0.6, 0.3)
                )
                popup.open()

                # Auto-dismiss and go back
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: (popup.dismiss(), self.go_back(None)), 1.5)

                # Refresh calendar
                calendar_screen = self.manager.get_screen('calendar')
                if hasattr(calendar_screen, 'refresh_events'):
                    calendar_screen.refresh_events()
            else:
                self.show_error("Failed to update event. Please try again.")

        except Exception as e:
            print(f"Error updating event: {e}")
            self.show_error("An error occurred while updating the event")

    def open_date_picker(self, instance):
        """Open date picker popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout
        from kivy.uix.gridlayout import GridLayout
        from datetime import datetime, timedelta
        import calendar as cal

        content = PopupBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        # Current date for default
        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # Month/Year navigation
        nav_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

        prev_btn = Button(text="<", size_hint_x=None, width=dp(40))
        month_label = Label(text=f"{cal.month_name[current_month]} {current_year}", font_size='16sp')
        next_btn = Button(text=">", size_hint_x=None, width=dp(40))

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(month_label)
        nav_layout.add_widget(next_btn)
        content.add_widget(nav_layout)

        # Calendar grid
        calendar_grid = GridLayout(cols=7, spacing=dp(2))

        # Day headers
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            calendar_grid.add_widget(Label(text=day, font_size='12sp', size_hint_y=None, height=dp(30)))

        # Calendar days
        month_calendar = cal.monthcalendar(current_year, current_month)
        selected_date = None

        def create_day_button(day):
            if day == 0:
                return Label(text="", size_hint_y=None, height=dp(40))

            btn = Button(
                text=str(day),
                size_hint_y=None,
                height=dp(40),
                background_normal='',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1),
                font_size='14sp'
            )

            def select_date(instance):
                nonlocal selected_date
                selected_date = f"{current_year}-{current_month:02d}-{day:02d}"
                # Update button appearance
                for child in calendar_grid.children:
                    if hasattr(child, 'background_color'):
                        child.background_color = (0.9, 0.9, 0.9, 1)
                instance.background_color = (0.85, 0.15, 0.15, 1)  # Red for selected

            btn.bind(on_release=select_date)
            return btn

        for week in month_calendar:
            for day in week:
                calendar_grid.add_widget(create_day_button(day))

        content.add_widget(calendar_grid)

        # Buttons
        button_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(
            text="Select",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)
        )

        popup = Popup(
            title='Select Date',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def cancel(instance):
            popup.dismiss()

        def select_date_final(instance):
            if selected_date:
                self.set_selected_date(selected_date)
            popup.dismiss()

        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_date_final)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        popup.open()

    def set_selected_date(self, date_str):
        """Set the selected date"""
        self.selected_date = date_str
        # Format date for display
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            self.date_label.text = f"Date: {formatted_date}"
        except:
            self.date_label.text = f"Date: {date_str}"

    def show_error(self, message):
        """Show error popup"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def go_back(self, instance):
        """Go back to view event screen"""
        self.manager.current = 'view_event'


class EditNoteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_note = None
        self.selected_date = None
        self.build_ui()

    def build_ui(self):
        # Main layout with light gray background - consistent with other screens
        main_layout = BoxLayout(orientation='vertical')

        # Add light gray background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Red header with logo and title - consistent with other screens
        header_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )

        # Add red background to header
        with header_layout.canvas.before:
            Color(0.85, 0.15, 0.15, 1)  # Red color
            Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self.update_header_bg, size=self.update_header_bg)

        # PUP Logo
        logo = Image(
            source='PUPlogo.png',
            size_hint_x=None,
            width=dp(40),
            fit_mode='contain'
        )

        # Title
        title_label = Label(
            text="PolyCal - Edit Note",
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))

        # Back button
        back_btn = Button(
            text="← Back",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.3, 0.3, 0.3, 1),  # Dark gray
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        back_btn.bind(on_release=self.go_back)

        header_layout.add_widget(logo)
        header_layout.add_widget(title_label)
        header_layout.add_widget(back_btn)
        main_layout.add_widget(header_layout)

        # Content area with padding
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Scroll view for the form
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=[0, dp(10)])
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))

        self.date_label = Label(
            text="Date: Not set",
            size_hint_x=0.7,
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))

        # Date picker button
        date_btn = Button(
            text="Change Date",
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),  # Blue - consistent with app
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        date_btn.bind(on_release=self.open_date_picker)

        date_layout.add_widget(self.date_label)
        date_layout.add_widget(date_btn)
        form_layout.add_widget(date_layout)

        # Note content input with character counter
        note_header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))

        note_label = Label(
            text="Note Content *",
            halign='left',
            font_size='16sp',
            bold=True,
            color=(0.85, 0.15, 0.15, 1),  # Red color - consistent with other screens
            size_hint_x=0.7
        )
        note_label.bind(size=note_label.setter('text_size'))

        self.char_counter = Label(
            text="0/200",
            halign='right',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=0.3
        )

        note_header_layout.add_widget(note_label)
        note_header_layout.add_widget(self.char_counter)
        form_layout.add_widget(note_header_layout)

        self.note_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(120),
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0.85, 0.15, 0.15, 1),
            font_size='14sp'
        )
        self.note_input.bind(text=self.update_char_counter)
        form_layout.add_widget(self.note_input)

        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(15))

        # Cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Light gray - consistent with app
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        cancel_btn.bind(on_release=self.cancel_edit)

        # Save button
        save_btn = Button(
            text="Save Changes",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1),  # Primary red - consistent with app
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        save_btn.bind(on_release=self.save_note)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        form_layout.add_widget(button_layout)

        scroll.add_widget(form_layout)
        content_layout.add_widget(scroll)
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        """Update main background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_header_bg(self, instance, value):
        """Update header background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_char_counter(self, instance, text):
        """Update character counter for note content"""
        char_count = len(text)
        self.char_counter.text = f"{char_count}/200"

        # Change color based on limit
        if char_count > 200:
            self.char_counter.color = (1, 0, 0, 1)  # Red if over limit
        elif char_count > 180:
            self.char_counter.color = (1, 0.5, 0, 1)  # Orange if near limit
        else:
            self.char_counter.color = (0.6, 0.6, 0.6, 1)  # Gray if normal

    def set_note_data(self, note_data):
        """Set the note data to edit"""
        self.current_note = note_data
        if note_data:
            # Extract note content from description (remove "Note: " prefix)
            description = note_data.get('description', '')
            if description.startswith('Note: '):
                note_content = description[6:]  # Remove "Note: " prefix
            else:
                note_content = description

            self.note_input.text = note_content

            # Set date
            note_date = note_data.get('date', '')
            self.selected_date = note_date
            # Format date for display
            try:
                from datetime import datetime
                date_obj = datetime.strptime(note_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%B %d, %Y')
                self.date_label.text = f"Date: {formatted_date}"
            except:
                self.date_label.text = f"Date: {note_date}"

            # Update character counter
            self.update_char_counter(None, self.note_input.text)

    def cancel_edit(self, instance):
        """Cancel editing and go back"""
        # Show confirmation if there are unsaved changes
        if self.has_unsaved_changes():
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout

            content = PopupBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

            message = Label(
                text="You have unsaved changes.\nAre you sure you want to cancel?",
                halign='center',
                font_size='16sp'
            )

            button_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

            cancel_btn = Button(
                text="Keep Editing",
                background_normal='',
                background_color=(0.7, 0.7, 0.7, 1),
                font_size='14sp'
            )

            confirm_btn = Button(
                text="Discard Changes",
                background_normal='',
                background_color=(0.9, 0.3, 0.3, 1),
                font_size='14sp'
            )

            popup = Popup(
                title='Unsaved Changes',
                content=content,
                size_hint=(0.8, 0.4)
            )

            cancel_btn.bind(on_release=lambda x: popup.dismiss())
            confirm_btn.bind(on_release=lambda x: (popup.dismiss(), self.go_back(None)))

            button_layout.add_widget(cancel_btn)
            button_layout.add_widget(confirm_btn)
            content.add_widget(message)
            content.add_widget(button_layout)

            popup.open()
        else:
            self.go_back(None)

    def has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        if not self.current_note:
            return False

        # Get original note content (remove "Note: " prefix)
        original_description = self.current_note.get('description', '')
        if original_description.startswith('Note: '):
            original_content = original_description[6:]
        else:
            original_content = original_description

        # Check if note content changed
        current_content = self.note_input.text.strip()
        return current_content != original_content

    def save_note(self, instance):
        """Save the edited note"""
        # Validate inputs
        note_content = self.note_input.text.strip()

        if not note_content:
            self.show_error("Please enter note content")
            return

        if len(note_content) > 200:
            self.show_error("Note content must be 200 characters or less")
            return

        if not self.current_note:
            self.show_error("No note data to update")
            return

        try:
            # Get current user ID as creator from global user_data
            global user_data
            creator_id = user_data.get('id', '')

            # Prepare description with "Note: " prefix
            description = f"Note: {note_content}"

            # Update note in database
            note_id = self.current_note.get('id')
            success = self.db.update_event(
                event_id=note_id,
                date=self.selected_date,
                description=description
            )

            if success:
                # Show success message
                from kivy.uix.popup import Popup
                popup = Popup(
                    title='Success',
                    content=Label(text='Note updated successfully!'),
                    size_hint=(0.6, 0.3)
                )
                popup.open()

                # Auto-dismiss and go back
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: (popup.dismiss(), self.go_back(None)), 1.5)

                # Refresh calendar
                calendar_screen = self.manager.get_screen('calendar')
                if hasattr(calendar_screen, 'refresh_events'):
                    calendar_screen.refresh_events()
            else:
                self.show_error("Failed to update note. Please try again.")

        except Exception as e:
            print(f"Error updating note: {e}")
            self.show_error("An error occurred while updating the note")

    def open_date_picker(self, instance):
        """Open date picker popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout
        from kivy.uix.gridlayout import GridLayout
        from datetime import datetime, timedelta
        import calendar as cal

        content = PopupBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        # Current date for default
        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # Month/Year navigation
        nav_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

        prev_btn = Button(text="<", size_hint_x=None, width=dp(40))
        month_label = Label(text=f"{cal.month_name[current_month]} {current_year}", font_size='16sp')
        next_btn = Button(text=">", size_hint_x=None, width=dp(40))

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(month_label)
        nav_layout.add_widget(next_btn)
        content.add_widget(nav_layout)

        # Calendar grid
        calendar_grid = GridLayout(cols=7, spacing=dp(2))

        # Day headers
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            calendar_grid.add_widget(Label(text=day, font_size='12sp', size_hint_y=None, height=dp(30)))

        # Calendar days
        month_calendar = cal.monthcalendar(current_year, current_month)
        selected_date = None

        def create_day_button(day):
            if day == 0:
                return Label(text="", size_hint_y=None, height=dp(40))

            btn = Button(
                text=str(day),
                size_hint_y=None,
                height=dp(40),
                background_normal='',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1),
                font_size='14sp'
            )

            def select_date(instance):
                nonlocal selected_date
                selected_date = f"{current_year}-{current_month:02d}-{day:02d}"
                # Update button appearance
                for child in calendar_grid.children:
                    if hasattr(child, 'background_color'):
                        child.background_color = (0.9, 0.9, 0.9, 1)
                instance.background_color = (0.85, 0.15, 0.15, 1)  # Red for selected

            btn.bind(on_release=select_date)
            return btn

        for week in month_calendar:
            for day in week:
                calendar_grid.add_widget(create_day_button(day))

        content.add_widget(calendar_grid)

        # Buttons
        button_layout = PopupBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(
            text="Select",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)
        )

        popup = Popup(
            title='Select Date',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def cancel(instance):
            popup.dismiss()

        def select_date_final(instance):
            if selected_date:
                self.set_selected_date(selected_date)
            popup.dismiss()

        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_date_final)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        popup.open()

    def set_selected_date(self, date_str):
        """Set the selected date"""
        self.selected_date = date_str
        # Format date for display
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            self.date_label.text = f"Date: {formatted_date}"
        except:
            self.date_label.text = f"Date: {date_str}"

    def show_error(self, message):
        """Show error popup"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def go_back(self, instance):
        """Go back to view event screen"""
        self.manager.current = 'view_event'


class InboxScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.build_ui()

    def build_ui(self):
        # Main layout with light gray background - consistent with other screens
        main_layout = BoxLayout(orientation='vertical')

        # Add light gray background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Red header with logo and title - consistent with other screens
        header_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )

        # Add red background to header
        with header_layout.canvas.before:
            Color(0.85, 0.15, 0.15, 1)  # Red color
            Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self.update_header_bg, size=self.update_header_bg)

        # PUP Logo
        logo = Image(
            source='PUPlogo.png',
            size_hint_x=None,
            width=dp(40),
            fit_mode='contain'
        )

        # Title
        title_label = Label(
            text="PolyCal - Inbox",
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))

        # Button layout for refresh and back
        button_layout = BoxLayout(size_hint_x=None, width=dp(140), spacing=dp(10))

        # Refresh button
        refresh_btn = Button(
            text="🔄",
            size_hint_x=None,
            width=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),  # Blue - consistent with app
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        refresh_btn.bind(on_release=self.refresh_notifications)

        # Back button
        back_btn = Button(
            text="← Back",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.3, 0.3, 0.3, 1),  # Dark gray
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        back_btn.bind(on_release=self.go_back)

        button_layout.add_widget(refresh_btn)
        button_layout.add_widget(back_btn)

        header_layout.add_widget(logo)
        header_layout.add_widget(title_label)
        header_layout.add_widget(button_layout)
        main_layout.add_widget(header_layout)

        # Content area with padding
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Notifications count
        self.count_label = Label(
            text="Loading notifications...",
            size_hint_y=None,
            height=dp(30),
            halign='center',
            font_size='14sp',
            color=(0.85, 0.15, 0.15, 1)  # Red color - consistent with other screens
        )
        content_layout.add_widget(self.count_label)

        # Scroll view for notifications
        scroll = ScrollView()
        self.notifications_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(10)]
        )
        self.notifications_layout.bind(minimum_height=self.notifications_layout.setter('height'))

        scroll.add_widget(self.notifications_layout)
        content_layout.add_widget(scroll)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        """Update main background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_header_bg(self, instance, value):
        """Update header background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def update_nav_bg(self, instance, value):
        """Update navigation background"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except:
            pass

    def on_enter(self):
        """Called when the screen is entered"""
        # Load notifications when screen is displayed
        self.refresh_notifications()

    def go_back(self, instance):
        """Go back to calendar screen"""
        self.manager.current = 'calendar'

    def refresh_notifications(self, instance=None):
        """Refresh the notifications list"""
        # Safety check - ensure manager is available
        if not self.manager:
            self.count_label.text = "Loading..."
            return

        # Get current user from global user_data
        try:
            global user_data
            current_user_id = user_data.get('id', '')
            if not current_user_id:
                self.count_label.text = "Please log in first"
                return
        except:
            self.count_label.text = "Please log in first"
            return

        # Get notifications for current user
        notifications = self.db.get_user_notifications(current_user_id)

        # Clear existing notifications
        self.notifications_layout.clear_widgets()

        # Update count
        self.count_label.text = f"You have {len(notifications)} notification(s)"

        if not notifications:
            # Show empty state
            empty_label = Label(
                text="📭\n\nNo notifications yet!\nYou'll see event invitations and updates here.",
                halign='center',
                font_size='14sp',
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(120)
            )
            self.notifications_layout.add_widget(empty_label)
        else:
            # Display notifications
            for notification in notifications:
                notification_card = self.create_notification_card(notification)
                self.notifications_layout.add_widget(notification_card)

    def create_notification_card(self, notification):
        """Create a notification card widget"""
        from kivy.graphics import Color, RoundedRectangle

        # Main card container
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(15),
            spacing=dp(10)
        )
        card.bind(minimum_height=card.setter('height'))

        # Add card background
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background - consistent with app
            RoundedRectangle(pos=card.pos, size=card.size, radius=[8])

        # Update background when position/size changes
        def update_bg(instance, value):
            try:
                for instruction in instance.canvas.before.children:
                    if isinstance(instruction, RoundedRectangle):
                        instruction.pos = instance.pos
                        instruction.size = instance.size
                        break
            except:
                pass

        card.bind(pos=update_bg, size=update_bg)

        # Notification type and date header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))

        type_label = Label(
            text=f"📅 {notification.get('type', 'Event').title()} Invitation",
            halign='left',
            font_size='12sp',
            bold=True,
            color=(0.2, 0.6, 0.9, 1),  # Blue - consistent with app
            size_hint_x=0.7
        )
        type_label.bind(size=type_label.setter('text_size'))

        date_label = Label(
            text=notification.get('event_date', ''),
            halign='right',
            font_size='11sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.3
        )
        date_label.bind(size=date_label.setter('text_size'))

        header_layout.add_widget(type_label)
        header_layout.add_widget(date_label)
        card.add_widget(header_layout)

        # Event title and description
        title_text = notification.get('event_title', 'Event Invitation')
        title_label = Label(
            text=title_text,
            halign='left',
            valign='top',
            font_size='14sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )
        title_label.bind(size=title_label.setter('text_size'))
        card.add_widget(title_label)

        # Event description (if available)
        description = notification.get('event_description', '')
        if description and len(description) > len(title_text):
            desc_label = Label(
                text=description[:100] + "..." if len(description) > 100 else description,
                halign='left',
                valign='top',
                font_size='12sp',
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(40)
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            card.add_widget(desc_label)

        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(8))

        # View details button
        view_btn = Button(
            text="View Details",
            size_hint_x=0.4,
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),  # Blue - consistent with app
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        view_btn.bind(on_release=lambda x, n=notification: self.view_event_details(n))

        # Accept button (for invitations)
        accept_btn = Button(
            text="Accept",
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),  # Green - consistent with app
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        accept_btn.bind(on_release=lambda x, n=notification: self.handle_invitation_response(n, 'accepted'))

        # Decline button (for invitations)
        decline_btn = Button(
            text="Decline",
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Secondary red - consistent with app
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        decline_btn.bind(on_release=lambda x, n=notification: self.handle_invitation_response(n, 'declined'))

        button_layout.add_widget(view_btn)
        button_layout.add_widget(accept_btn)
        button_layout.add_widget(decline_btn)
        card.add_widget(button_layout)

        return card

    def view_event_details(self, notification):
        """View event details in the ViewEventScreen"""
        event_id = notification.get('event_id')
        if event_id:
            event = self.db.get_event_by_id(event_id)
            if event:
                # Navigate to view event screen
                view_screen = self.manager.get_screen('view_event')
                view_screen.set_event(event)
                self.manager.current = 'view_event'

    def handle_invitation_response(self, notification, response):
        """Handle accept/decline invitation"""
        # Update notification status
        notification_id = notification.get('id')
        if notification_id:
            success = self.db.update_invitation_status(notification_id, response)
            if success:
                # Show feedback
                message = f"Invitation {response}!" if response == 'accepted' else "Invitation declined."
                self.show_success(message)

                # If declined, remove from inbox
                if response == 'declined':
                    self.refresh_notifications()
            else:
                self.show_error("Failed to update invitation status")

    def go_back(self, instance):
        """Go back to calendar screen"""
        self.manager.current = 'calendar'

    def show_error(self, message):
        """Show error popup with consistent styling"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Error',
            content=Label(text=message, halign='center'),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def show_success(self, message):
        """Show success popup with consistent styling"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Success',
            content=Label(text=message, halign='center'),
            size_hint=(0.7, 0.3)
        )
        popup.open()

        # Auto-dismiss after 1.5 seconds
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.inbox_visible = False  # Track inbox visibility state
    
    def toggle_inbox(self):
        """Navigate to inbox screen"""
        print("Toggle inbox called")  # Debug print
        self.manager.current = 'inbox'

    def show_inbox(self):
        """Show inbox popup with notifications"""
        try:
            user_id = user_data.get('id')
            if not user_id:
                self.show_error("Please log in to view notifications")
                return

            # Get user notifications
            notifications = self.db.get_user_notifications(user_id)

            # Create inbox layout
            layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

            # Header with title
            header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)

            # Title
            title_label = Label(
                text="Notifications",
                font_size='18sp',
                bold=True,
                size_hint_x=1.0,
                color=(0.85, 0.15, 0.15, 1)  # Red color
            )
            header_layout.add_widget(title_label)
            layout.add_widget(header_layout)

            if notifications:
                # Scrollable notification list
                scroll = ScrollView()
                self.notifications_layout = BoxLayout(
                    orientation='vertical',
                    spacing=15,  # Increased spacing between notifications
                    size_hint_y=None,
                    padding=[10, 15, 10, 15]  # More padding around the list
                )
                self.notifications_layout.bind(minimum_height=self.notifications_layout.setter('height'))

                for notification in notifications:
                    self.create_notification_item(self.notifications_layout, notification)

                scroll.add_widget(self.notifications_layout)
                layout.add_widget(scroll)
            else:
                # No notifications message
                no_notifications_label = Label(
                    text="No notifications",
                    size_hint_y=None,
                    height=60,
                    color=(0.5, 0.5, 0.5, 1)
                )
                layout.add_widget(no_notifications_label)

            # Close button
            close_btn = Button(
                text="Close",
                size_hint_y=None,
                height=40,
                background_normal='',
                background_color=(0.85, 0.15, 0.15, 1)  # Red color
            )

            # Create popup
            inbox_popup = Popup(
                title="Inbox",
                content=layout,
                size_hint=(0.9, 0.7)
            )

            # Store popup reference for dismissing from notification clicks
            self.current_inbox_popup = inbox_popup

            close_btn.bind(on_release=lambda x: inbox_popup.dismiss())
            layout.add_widget(close_btn)

            inbox_popup.open()

        except Exception as e:
            print(f"Error showing inbox: {e}")
            self.show_error("Failed to load notifications")

    def create_notification_item(self, parent_layout, notification):
        """Create a notification item widget"""
        try:
            # Check if this is an invitation
            is_invitation = notification.get('notification_type') == 'invitation'
            invitation_status = notification.get('invitation_status')

            # Notification container - organized layout
            notification_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=150,  # Fixed height for all notifications
                spacing=8,
                padding=[15, 12, 15, 12]
            )

            # Background color and border based on read status and invitation type
            from kivy.graphics import Color, Rectangle, Line
            with notification_box.canvas.before:
                # Background color
                if is_invitation and invitation_status == 'pending':
                    Color(0.9, 0.95, 1, 1)  # Light blue
                elif is_invitation and invitation_status == 'accepted':
                    Color(0.9, 1, 0.9, 1)  # Light green
                elif is_invitation and invitation_status == 'declined':
                    Color(0.95, 0.95, 0.95, 1)  # Light gray
                elif notification['is_read'] == 0:
                    Color(1, 0.9, 0.9, 1)  # Light red for unread
                else:
                    Color(0.98, 0.98, 0.98, 1)  # Very light gray for read

                Rectangle(pos=notification_box.pos, size=notification_box.size)

                # Border
                Color(0.8, 0.8, 0.8, 1)  # Gray border
                Line(rectangle=(notification_box.x, notification_box.y, notification_box.width, notification_box.height), width=1)

            notification_box.bind(pos=self.update_rect, size=self.update_rect)

            # Extract event title from event description if available
            event_title = "Event"
            event_date = notification.get('event_date', '')

            if notification.get('event_description'):
                # Get the full event title (before " - " if exists)
                event_desc = notification['event_description']
                if " - " in event_desc:
                    event_title = event_desc.split(" - ", 1)[0].strip()
                else:
                    event_title = event_desc.strip()

                # Remove "Note: " prefix if it exists
                if event_title.startswith("Note: "):
                    event_title = event_title[6:].strip()

            # Title row with event title and notification date
            title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=5)

            # Show the actual event title with invitation icon if applicable
            title_icon = "💌" if is_invitation else "📅"
            title_label = Label(
                text=f"{title_icon} {event_title}",
                font_size='16sp',
                bold=True,
                halign='left',
                valign='middle',
                size_hint_x=0.75,
                color=(0.85, 0.15, 0.15, 1) if notification['is_read'] == 0 else (0.2, 0.2, 0.2, 1)
            )
            title_label.bind(size=title_label.setter('text_size'))
            title_row.add_widget(title_label)

            # Show notification creation date
            notif_date = notification['created_at'][:16] if notification['created_at'] else ''
            date_label = Label(
                text=notif_date,
                font_size='11sp',
                halign='right',
                valign='middle',
                size_hint_x=0.25,
                color=(0.5, 0.5, 0.5, 1)
            )
            date_label.bind(size=date_label.setter('text_size'))
            title_row.add_widget(date_label)

            # Event date row
            event_date_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)

            event_date_label = Label(
                text=f"📅 Event Date: {event_date}" if event_date else "📅 Event Date: Not specified",
                font_size='13sp',
                halign='left',
                valign='middle',
                color=(0.4, 0.4, 0.4, 1),
                italic=True
            )
            event_date_label.bind(size=event_date_label.setter('text_size'))
            event_date_row.add_widget(event_date_label)

            # Message with better formatting
            message_text = notification['message']
            if is_invitation:
                if invitation_status == 'pending':
                    message_text = "You have been invited to this event."
                elif invitation_status == 'accepted':
                    message_text = "You accepted this invitation."
                elif invitation_status == 'declined':
                    message_text = "You declined this invitation."
            elif notification.get('event_description'):
                message_text = f"You've been tagged in this event. Tap to view details."

            message_label = Label(
                text=message_text,
                font_size='13sp',
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=22,
                color=(0.3, 0.3, 0.3, 1)
            )
            message_label.bind(size=message_label.setter('text_size'))

            notification_box.add_widget(title_row)
            notification_box.add_widget(event_date_row)
            notification_box.add_widget(message_label)

            # Add action buttons
            button_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=8)

            if is_invitation and invitation_status == 'pending':
                # Invitation buttons for pending invitations
                accept_btn = Button(
                    text="✓ Accept",
                    size_hint_x=0.32,
                    background_normal='',
                    background_color=(0.2, 0.7, 0.2, 1),  # Green
                    color=(1, 1, 1, 1),
                    font_size='13sp',
                    bold=True
                )

                decline_btn = Button(
                    text="✗ Decline",
                    size_hint_x=0.32,
                    background_normal='',
                    background_color=(0.9, 0.3, 0.3, 1),  # Secondary red - consistent with app
                    color=(1, 1, 1, 1),
                    font_size='13sp',
                    bold=True
                )

                delete_event_btn = Button(
                    text="🗑 Delete Event",
                    size_hint_x=0.36,
                    background_normal='',
                    background_color=(0.6, 0.6, 0.6, 1),  # Gray
                    color=(1, 1, 1, 1),
                    font_size='12sp',
                    bold=True
                )

                # Bind button actions
                accept_btn.bind(on_release=lambda x, n=notification: self.handle_invitation_response(n, 'accepted'))
                decline_btn.bind(on_release=lambda x, n=notification: self.handle_invitation_response(n, 'declined'))
                delete_event_btn.bind(on_release=lambda x, n=notification: self.handle_invitation_delete(n))

                button_row.add_widget(accept_btn)
                button_row.add_widget(decline_btn)
                button_row.add_widget(delete_event_btn)
            else:
                # For all other notifications (regular notifications, accepted/declined invitations)
                # Add a delete notification button
                delete_notification_btn = Button(
                    text="🗑 Delete Notification",
                    size_hint_x=1.0,
                    background_normal='',
                    background_color=(0.9, 0.3, 0.3, 1),  # Red
                    color=(1, 1, 1, 1),
                    font_size='13sp',
                    bold=True
                )
                delete_notification_btn.bind(on_release=lambda x, n=notification: self.delete_individual_notification(n))
                button_row.add_widget(delete_notification_btn)

            notification_box.add_widget(button_row)

            # Make notification clickable if it has an event_id and no buttons
            if notification['event_id'] and not (is_invitation and invitation_status == 'pending'):
                # Only make clickable if it doesn't have action buttons
                # Create a custom clickable container
                from kivy.uix.relativelayout import RelativeLayout

                clickable_container = RelativeLayout(
                    size_hint_y=None,
                    height=150  # Fixed height matching notification_box
                )

                # Add the notification box to the container
                clickable_container.add_widget(notification_box)

                # Make the entire container clickable
                def on_touch_down(instance, touch, n=notification):
                    if instance.collide_point(*touch.pos):
                        # Handle notification click
                        self.handle_notification_click(n)
                        return True
                    return False

                clickable_container.bind(on_touch_down=on_touch_down)
                parent_layout.add_widget(clickable_container)
            else:
                # For notifications with buttons or without event_id, just add directly
                parent_layout.add_widget(notification_box)

        except Exception as e:
            print(f"Error creating notification item: {e}")

    def handle_invitation_response(self, notification, status):
        """Handle accepting or declining an invitation"""
        try:
            if status == 'declined':
                # For declined invitations, delete the notification entirely
                success = self.db.delete_notification(notification['id'])
                status_text = "declined and removed"
            else:
                # For accepted invitations, update the status
                success = self.db.update_invitation_status(notification['id'], status)
                status_text = "accepted"

            if success:
                # Show success message
                success_popup = Popup(
                    title='✅ Success',
                    content=Label(text=f'Invitation {status_text} successfully!'),
                    size_hint=(0.7, 0.3)
                )
                success_popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)

                # Refresh inbox to show updated status
                self.refresh_inbox()
            else:
                self.show_error("Failed to update invitation status")

        except Exception as e:
            print(f"Error handling invitation response: {e}")
            self.show_error("Failed to process invitation response")

    def handle_invitation_delete(self, notification):
        """Handle deleting an invitation event"""
        try:
            # Show confirmation dialog
            self.show_delete_invitation_confirmation(notification)

        except Exception as e:
            print(f"Error handling invitation delete: {e}")
            self.show_error("Failed to process deletion request")

    def show_delete_invitation_confirmation(self, notification):
        """Show confirmation dialog for deleting invitation event"""
        # Get event title for better confirmation message
        event_title = "this event"
        if notification.get('event_description'):
            event_desc = notification['event_description']
            if " - " in event_desc:
                event_title = f'"{event_desc.split(" - ", 1)[0].strip()}"'
            else:
                event_title = f'"{event_desc[:30]}..."' if len(event_desc) > 30 else f'"{event_desc}"'

        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning message
        warning_message = Label(
            text=f"Are you sure you want to delete {event_title}?\n\nThis will permanently remove the event and all related notifications for all users.",
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(15)
        )

        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        delete_btn = Button(
            text="Delete Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def cancel_delete(instance):
            confirm_popup.dismiss()

        def proceed_delete(instance):
            confirm_popup.dismiss()
            # Delete the invitation event from database
            user_id = user_data.get('id')
            success = self.db.delete_invitation_event(notification['id'], user_id)

            if success:
                # Show success message
                success_popup = Popup(
                    title='✅ Success',
                    content=Label(text='Event deleted successfully!'),
                    size_hint=(0.7, 0.3)
                )
                success_popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)

                # Refresh inbox to remove deleted notification
                self.refresh_inbox()
            else:
                self.show_error("Failed to delete event. Please try again.")

        cancel_btn.bind(on_release=cancel_delete)
        delete_btn.bind(on_release=proceed_delete)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)
        content.add_widget(button_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Deletion",
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()

    def refresh_inbox(self):
        """Refresh the inbox display"""
        try:
            # Close current inbox if open
            if hasattr(self, 'current_inbox_popup') and self.current_inbox_popup:
                self.current_inbox_popup.dismiss()
                self.current_inbox_popup = None

            # Update notification count
            self.update_notification_count()

            # Reopen inbox
            self.show_inbox()

        except Exception as e:
            print(f"Error refreshing inbox: {e}")





    def delete_individual_notification(self, notification):
        """Delete a single notification"""
        try:
            self.show_individual_delete_confirmation(notification)
        except Exception as e:
            print(f"Error deleting individual notification: {e}")



    def show_individual_delete_confirmation(self, notification):
        """Show confirmation dialog for individual notification deletion"""
        # Get notification title for better confirmation message
        event_title = "this notification"
        if notification.get('event_description'):
            event_desc = notification['event_description']
            if " - " in event_desc:
                event_title = f'"{event_desc.split(" - ", 1)[0].strip()}"'
            else:
                event_title = f'"{event_desc[:30]}..."' if len(event_desc) > 30 else f'"{event_desc}"'

        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning message
        warning_message = Label(
            text=f"Are you sure you want to delete the notification for {event_title}?\n\nThis action cannot be undone.",
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(15)
        )

        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        delete_btn = Button(
            text="Delete Notification",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def cancel_delete(instance):
            confirm_popup.dismiss()

        def proceed_delete(instance):
            confirm_popup.dismiss()
            self.perform_individual_delete(notification)

        cancel_btn.bind(on_release=cancel_delete)
        delete_btn.bind(on_release=proceed_delete)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)
        content.add_widget(button_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Deletion",
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()



    def perform_individual_delete(self, notification):
        """Actually perform individual notification deletion"""
        try:
            # Delete from database
            success = self.db.delete_notification(notification['id'])

            if success:
                # Show success message
                success_popup = Popup(
                    title='✅ Success',
                    content=Label(text='Notification deleted successfully!'),
                    size_hint=(0.7, 0.3)
                )
                success_popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)

                # Refresh inbox
                self.refresh_inbox()
            else:
                self.show_error("Failed to delete notification. Please try again.")

        except Exception as e:
            print(f"Error performing individual delete: {e}")
            self.show_error("Failed to delete notification")

    def update_rect(self, instance, value):
        """Update rectangle position and size"""
        try:
            # Find the Rectangle instruction in the canvas
            from kivy.graphics import Rectangle
            for instruction in instance.canvas.before.children:
                if isinstance(instruction, Rectangle):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except Exception as e:
            print(f"Error updating rectangle: {e}")

    def handle_notification_click(self, notification):
        """Handle clicking on a notification"""
        try:
            # Mark notification as read
            if notification['is_read'] == 0:
                self.db.mark_notification_read(notification['id'])
                # Update notification count
                self.update_notification_count()

            # Close the inbox popup first
            if hasattr(self, 'current_inbox_popup') and self.current_inbox_popup:
                self.current_inbox_popup.dismiss()
                self.current_inbox_popup = None

            # Get event details and show them
            if notification['event_id']:
                event = self.db.get_event_by_id(notification['event_id'])
                if event:
                    self.show_event_details_from_notification(event)
                else:
                    self.show_error("Event not found")

        except Exception as e:
            print(f"Error handling notification click: {e}")

    def show_event_details_from_notification(self, event):
        """Show event details popup from notification"""
        try:
            # Create scrollable event details popup with dark background
            main_layout = BoxLayout(orientation='vertical', spacing=5, padding=10)

            # Add dark background to main layout
            from kivy.graphics import Color, Rectangle
            with main_layout.canvas.before:
                Color(0.2, 0.2, 0.2, 1)  # Dark gray background
                Rectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=self.update_rect, size=self.update_rect)

            # Scrollable content area
            scroll = ScrollView()
            layout = BoxLayout(orientation='vertical', spacing=15, padding=5, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))

            # Event title
            title_parts = event['description'].split(' - ', 1)
            title = title_parts[0] if title_parts else event['description']

            # Remove "Note: " prefix if it exists
            if title.startswith("Note: "):
                title = title[6:].strip()
                event_type = "📝 Note"
            else:
                event_type = "📅 Event"

            title_label = Label(
                text=f"{event_type}: {title}",
                font_size='20sp',
                bold=True,
                size_hint_y=None,
                height=dp(50),
                halign='left',
                valign='top',
                color=(1, 0.4, 0.4, 1)  # Light red for dark background
            )
            title_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
            layout.add_widget(title_label)

            # Event date with better formatting
            try:
                from datetime import datetime
                date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
            except:
                formatted_date = event['date']

            date_label = Label(
                text=f"📅 Date: {formatted_date}",
                font_size='16sp',
                size_hint_y=None,
                height=dp(35),
                halign='left',
                valign='top',
                color=(0.9, 0.9, 0.9, 1)  # Light gray for dark background
            )
            date_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
            layout.add_widget(date_label)

            # Event description
            if len(title_parts) > 1:
                desc_label = Label(
                    text=f"📝 Description:\n{title_parts[1]}",
                    font_size='14sp',
                    size_hint_y=None,
                    height=dp(80),
                    halign='left',
                    valign='top',
                    color=(0.8, 0.8, 0.8, 1)  # Light gray for dark background
                )
                desc_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
                layout.add_widget(desc_label)

            # Tagged users if available
            if event.get('tagged_ids'):
                tagged_label = Label(
                    text=f"👥 Tagged Users: {event['tagged_ids']}",
                    font_size='14sp',
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='top',
                    color=(0.7, 0.7, 0.7, 1)  # Light gray for dark background
                )
                tagged_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
                layout.add_widget(tagged_label)

            # Event link if available
            if event.get('link'):
                link_label = Label(
                    text=f"🔗 Link: {event['link']}",
                    font_size='14sp',
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='top',
                    color=(0.4, 0.7, 1, 1)  # Light blue for dark background
                )
                link_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
                layout.add_widget(link_label)

            # Privacy setting
            privacy = event.get('privacy', 'public').title()
            privacy_icon = "🔒" if privacy.lower() == 'private' else "🌐"
            privacy_label = Label(
                text=f"{privacy_icon} Privacy: {privacy}",
                font_size='14sp',
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='top',
                color=(0.6, 0.6, 0.6, 1)  # Light gray for dark background
            )
            privacy_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
            layout.add_widget(privacy_label)

            # Event image if available
            if event.get('image_path') and os.path.exists(event['image_path']):
                try:
                    image_label = Label(
                        text="🖼️ Event Image:",
                        font_size='14sp',
                        size_hint_y=None,
                        height=dp(25),
                        halign='left',
                        valign='top',
                        color=(0.8, 0.8, 0.8, 1)  # Light gray for dark background
                    )
                    image_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
                    layout.add_widget(image_label)

                    event_image = Image(
                        source=event['image_path'],
                        size_hint_y=None,
                        height=dp(200),
                        allow_stretch=True,
                        keep_ratio=True
                    )
                    layout.add_widget(event_image)
                except Exception as img_error:
                    print(f"Error loading image: {img_error}")

            # Add the scrollable content to the scroll view
            scroll.add_widget(layout)
            main_layout.add_widget(scroll)

            # Close button (outside scroll area)
            close_btn = Button(
                text="Close",
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.85, 0.15, 0.15, 1)
            )
            main_layout.add_widget(close_btn)

            # Create popup
            event_popup = Popup(
                title="Event Details",
                content=main_layout,
                size_hint=(0.9, 0.8)
            )

            close_btn.bind(on_release=lambda x: event_popup.dismiss())
            event_popup.open()

        except Exception as e:
            print(f"Error showing event details from notification: {e}")
            self.show_error("Failed to load event details")

    def show_error(self, message):
        """Show error popup"""
        error_popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        error_popup.open()

        # Auto-dismiss after 2 seconds
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: error_popup.dismiss(), 2)

    def search_events(self, search_text):
        """Search for events containing the search text or filter by month/year"""
        if not search_text.strip():
            return

        try:
            # Check if search text is a date pattern
            if self.is_specific_date_search(search_text):
                self.handle_specific_date_search(search_text)
            # Check if search text is a month/year pattern
            elif self.is_month_year_search(search_text):
                self.handle_month_year_search(search_text)
            else:
                # Regular text search
                user_id = user_data.get('id', '')
                all_events = self.db.get_events_between_dates('2020-01-01', '2030-12-31', user_id)
                matching_events = []

                for event in all_events:
                    description = event.get('description', '').lower()
                    if search_text.lower() in description:
                        matching_events.append(event)

                # Show search results
                self.show_search_results(search_text, matching_events)

        except Exception as e:
            print(f"Search error: {e}")

    def is_specific_date_search(self, search_text):
        """Check if search text is a specific date pattern"""
        import re
        from datetime import datetime

        search_text = search_text.strip()

        # Patterns to match:
        # "June 15, 2025", "Jun 15, 2025", "June 15 2025"
        # "15 June 2025", "15 Jun 2025"
        # "2025-06-15", "06-15-2025", "06/15/2025"
        # "15-06-2025", "15/06/2025"

        # Month names (full and abbreviated)
        months = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }

        # Try to parse various date formats
        date_patterns = [
            # Month Day, Year (June 15, 2025)
            r'^([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})$',
            # Day Month Year (15 June 2025)
            r'^(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})$',
            # YYYY-MM-DD
            r'^(\d{4})-(\d{1,2})-(\d{1,2})$',
            # MM-DD-YYYY or DD-MM-YYYY
            r'^(\d{1,2})-(\d{1,2})-(\d{4})$',
            # MM/DD/YYYY or DD/MM/YYYY
            r'^(\d{1,2})/(\d{1,2})/(\d{4})$',
        ]

        for pattern in date_patterns:
            if re.match(pattern, search_text, re.IGNORECASE):
                return True

        return False

    def handle_specific_date_search(self, search_text):
        """Handle specific date search and show events for that date"""
        import re
        from datetime import datetime

        search_text = search_text.strip()
        target_date = None

        # Month names mapping
        months = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }

        try:
            # Try Month Day, Year format (June 15, 2025)
            match = re.match(r'^([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})$', search_text, re.IGNORECASE)
            if match:
                month_name = match.group(1).lower()
                day = int(match.group(2))
                year = int(match.group(3))
                if month_name in months:
                    month = months[month_name]
                    target_date = f"{year}-{month:02d}-{day:02d}"

            # Try Day Month Year format (15 June 2025)
            if not target_date:
                match = re.match(r'^(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})$', search_text, re.IGNORECASE)
                if match:
                    day = int(match.group(1))
                    month_name = match.group(2).lower()
                    year = int(match.group(3))
                    if month_name in months:
                        month = months[month_name]
                        target_date = f"{year}-{month:02d}-{day:02d}"

            # Try YYYY-MM-DD format
            if not target_date:
                match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', search_text)
                if match:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        target_date = f"{year}-{month:02d}-{day:02d}"

            # Try MM-DD-YYYY format (assuming US format)
            if not target_date:
                match = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{4})$', search_text)
                if match:
                    month = int(match.group(1))
                    day = int(match.group(2))
                    year = int(match.group(3))
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        target_date = f"{year}-{month:02d}-{day:02d}"

            # Try MM/DD/YYYY format (assuming US format)
            if not target_date:
                match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', search_text)
                if match:
                    month = int(match.group(1))
                    day = int(match.group(2))
                    year = int(match.group(3))
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        target_date = f"{year}-{month:02d}-{day:02d}"

            # If we successfully parsed a date, show events for that date
            if target_date:
                # Validate the date
                try:
                    datetime.strptime(target_date, '%Y-%m-%d')
                    self.show_date_events(target_date, search_text)
                except ValueError:
                    self.show_error("Invalid date. Please check the date and try again.")
            else:
                self.show_error("Invalid date format. Try 'June 15, 2025', '2025-06-15', or '06/15/2025'")

        except Exception as e:
            print(f"Error parsing date: {e}")
            self.show_error("Invalid date format. Please try again.")

    def show_date_events(self, target_date, original_search):
        """Show all events for a specific date"""
        try:
            # Get events for the specific date
            user_id = user_data.get('id', '')
            date_events = self.db.get_events_between_dates(target_date, target_date, user_id)

            # Format the date nicely for display
            try:
                from datetime import datetime
                date_obj = datetime.strptime(target_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
            except:
                formatted_date = target_date

            # Show events in a popup
            self.show_search_results(f"{formatted_date}", date_events)

        except Exception as e:
            print(f"Error showing date events: {e}")
            self.show_error("Failed to load events for the specified date")

    def is_month_year_search(self, search_text):
        """Check if search text is a month/year pattern"""
        import re
        search_text = search_text.strip().lower()

        # Patterns to match:
        # "january 2025", "jan 2025", "01 2025", "1 2025"
        # "january", "jan", "01", "1" (current year assumed)
        # "2025" (year only)

        # Month names (full and abbreviated)
        months = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }

        # Check for month name + year pattern
        for month_name in months:
            if re.match(rf'^{month_name}\s+\d{{4}}$', search_text):
                return True
            if re.match(rf'^{month_name}$', search_text):
                return True

        # Check for numeric month + year pattern (01 2025, 1 2025)
        if re.match(r'^\d{1,2}\s+\d{4}$', search_text):
            return True

        # Check for month only (01, 1)
        if re.match(r'^\d{1,2}$', search_text):
            month_num = int(search_text)
            return 1 <= month_num <= 12

        # Check for year only (2025)
        if re.match(r'^\d{4}$', search_text):
            year = int(search_text)
            return 2020 <= year <= 2030  # Reasonable year range

        return False

    def handle_month_year_search(self, search_text):
        """Handle month/year search and update calendar display"""
        import re
        from datetime import datetime

        search_text = search_text.strip().lower()
        current_year = datetime.now().year

        # Month names mapping
        months = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }

        target_month = None
        target_year = None

        # Parse different patterns
        # Month name + year (e.g., "january 2025")
        for month_name, month_num in months.items():
            match = re.match(rf'^{month_name}\s+(\d{{4}})$', search_text)
            if match:
                target_month = month_num
                target_year = int(match.group(1))
                break
            # Month name only (e.g., "january")
            elif re.match(rf'^{month_name}$', search_text):
                target_month = month_num
                target_year = current_year
                break

        # Numeric month + year (e.g., "01 2025")
        if target_month is None:
            match = re.match(r'^(\d{1,2})\s+(\d{4})$', search_text)
            if match:
                target_month = int(match.group(1))
                target_year = int(match.group(2))

        # Month only (e.g., "01")
        if target_month is None:
            match = re.match(r'^(\d{1,2})$', search_text)
            if match:
                month_num = int(match.group(1))
                if 1 <= month_num <= 12:
                    target_month = month_num
                    target_year = current_year

        # Year only (e.g., "2025")
        if target_month is None:
            match = re.match(r'^(\d{4})$', search_text)
            if match:
                target_year = int(match.group(1))
                # Show all events for the year
                self.show_year_events(target_year)
                return

        # If we have a valid month/year, show events for that month
        if target_month and target_year:
            self.show_month_events(target_month, target_year)
        else:
            self.show_error("Invalid month/year format. Try 'January 2025', 'Jan 2025', '01 2025', or just '2025'")

    def show_month_events(self, month, year):
        """Show all events for a specific month in a popup"""
        try:
            import calendar
            from calendar import monthrange

            # Get the first and last day of the month
            first_day = f"{year}-{month:02d}-01"
            last_day_num = monthrange(year, month)[1]
            last_day = f"{year}-{month:02d}-{last_day_num:02d}"

            # Get events for the month
            user_id = user_data.get('id', '')
            month_events = self.db.get_events_between_dates(first_day, last_day, user_id)

            # Get month name
            month_name = calendar.month_name[month]

            # Show events in a popup
            self.show_search_results(f"{month_name} {year}", month_events)

        except Exception as e:
            print(f"Error showing month events: {e}")
            self.show_error("Failed to load events for the specified month")

    def navigate_to_month(self, month, year):
        """Navigate calendar to specific month and year"""
        try:
            # Update current month and year
            self.current_month = month
            self.current_year = year

            # Update month/year label
            import calendar
            self.ids.month_year_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

            # Rebuild calendar for the new month
            self.build_calendar()

            # Show success message
            month_name = calendar.month_name[month]
            success_popup = Popup(
                title='✅ Calendar Updated',
                content=Label(text=f'Showing {month_name} {year}'),
                size_hint=(0.6, 0.3)
            )
            success_popup.open()

            # Auto-dismiss after 1.5 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)

        except Exception as e:
            print(f"Error navigating to month: {e}")
            self.show_error("Failed to navigate to the specified month")

    def show_year_events(self, year):
        """Show all events for a specific year"""
        try:
            user_id = user_data.get('id', '')
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            year_events = self.db.get_events_between_dates(start_date, end_date, user_id)

            # Show search results for the year
            self.show_search_results(f"Year {year}", year_events)

        except Exception as e:
            print(f"Error showing year events: {e}")
            self.show_error("Failed to load events for the specified year")

    def show_search_results(self, search_text, events):
        """Show search results in a popup"""
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        title_label = Label(
            text=f"Search results for '{search_text}'",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title_label)

        # Add instruction label
        instruction_label = Label(
            text="Click on any event to view details",
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(instruction_label)

        # Create the popup first
        search_popup = Popup(
            title="Search Results",
            content=layout,
            size_hint=(0.9, 0.7)
        )

        if events:
            # Scrollable event list
            scroll = ScrollView()
            events_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
            events_layout.bind(minimum_height=events_layout.setter('height'))

            for event in events:
                # Truncate long descriptions for better display
                description = event.get('description', 'No description')
                if len(description) > 50:
                    description = description[:47] + "..."

                event_btn = Button(
                    text=f"{event.get('date', '')}: {description}",
                    size_hint_y=None,
                    height=50,  # Increased height for better readability
                    halign='left',
                    background_normal='',
                    background_color=(0.95, 0.95, 0.95, 1),  # Light gray background
                    color=(0.2, 0.2, 0.2, 1)  # Dark text
                )
                # Set text alignment
                event_btn.bind(size=lambda btn, size: setattr(btn, 'text_size', (size[0] - 20, None)))
                event_btn.bind(on_release=lambda x, e=event: self.show_event_details_from_search(e, search_popup))
                events_layout.add_widget(event_btn)

            scroll.add_widget(events_layout)
            layout.add_widget(scroll)
        else:
            no_results_label = Label(
                text="No events found",
                size_hint_y=None,
                height=40
            )
            layout.add_widget(no_results_label)

        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=40
        )
        close_btn.bind(on_release=lambda x: search_popup.dismiss())
        layout.add_widget(close_btn)

        search_popup.open()

    def show_event_details_from_search(self, event, parent_popup):
        """Show event details from search results"""
        try:
            if parent_popup:
                parent_popup.dismiss()
            self.show_event_details(event)
        except Exception as e:
            print(f"Error showing event details from search: {e}")
            self.show_error("Failed to load event details")
    
    def on_enter(self):
        # Update welcome message with user's name
        user_name = user_data.get('name', 'Iska')
        self.ids.welcome_label.text = f"Hello, {user_name}!"

        # Set current month and year in spinners
        self.ids.month_spinner.text = calendar.month_name[self.current_month]
        self.ids.year_spinner.text = str(self.current_year)

        # Update notification count
        self.update_notification_count()

        # Build calendar
        self.build_calendar()

    def update_notification_count(self):
        """Update the notification count in the inbox badge"""
        try:
            user_id = user_data.get('id')
            if user_id:
                unread_count = self.db.get_unread_notification_count(user_id)
                if hasattr(self.ids, 'inbox_badge'):
                    self.ids.inbox_badge.text = str(unread_count)
                    # Show/hide badge based on count
                    self.ids.inbox_badge.opacity = 1 if unread_count > 0 else 0
        except Exception as e:
            print(f"Error updating notification count: {e}")
    
    def on_enter(self):
        """Initialize the calendar screen when entering"""
        # Update month/year label
        self.ids.month_year_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

        # Build the calendar
        self.build_calendar()

        # Update notification count
        self.update_notification_count()
    
    def build_calendar(self):
        # Clear existing calendar
        self.ids.calendar_grid.clear_widgets()
        
        # Get calendar for current month/year
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Get events for this month
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        last_day = monthrange(self.current_year, self.current_month)[1]
        end_date = f"{self.current_year}-{self.current_month:02d}-{last_day:02d}"
        user_id = user_data.get('id', '')
        month_events = self.db.get_events_between_dates(start_date, end_date, user_id)
        
        # Create a set of days with events for quick lookup
        event_days = set()
        for event in month_events:
            try:
                if isinstance(event, dict):
                    date_str = event.get('date', '')
                else:
                    date_str = event[1] if len(event) > 1 else ''
                day = int(date_str.split('-')[2])  # Extract day from date
                event_days.add(day)
            except:
                pass
        
        # Add day buttons to the grid
        for week in cal:
            for day in week:
                if day == 0:
                    # Empty day (padding)
                    self.ids.calendar_grid.add_widget(Label(text=""))
                else:
                    # Create day button
                    day_btn = Button(
                        text=str(day),
                        background_normal='',
                        background_color=(0.95, 0.95, 0.95, 1),  # Light gray
                        color=(0.3, 0.3, 0.3, 1)  # Dark gray text
                    )
                    
                    # Highlight today
                    today = datetime.now()
                    if day == today.day and self.current_month == today.month and self.current_year == today.year:
                        day_btn.background_color = (0.9, 0.7, 0.7, 1)  # Light red
                    
                    # Highlight days with events
                    if day in event_days:
                        day_btn.bold = True
                        day_btn.color = (0.85, 0.15, 0.15, 1)  # Red text
                    
                    # Bind to check events for this day first
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    day_btn.bind(on_release=lambda btn, d=date_str: self.check_events_for_date(d))
                    
                    self.ids.calendar_grid.add_widget(day_btn)

    def check_events_for_date(self, date_str):
        """Check if there are events for the selected date and show them"""
        # Get events for this date
        user_id = user_data.get('id', '')
        events = self.db.get_events_by_date(date_str, user_id)

        if events:
            # If events exist, show them in a popup
            self.show_events_for_date(date_str, None)  # Pass None as parent_popup
        else:
            # If no events, ask if user wants to add one
            self.ask_add_event(date_str)

    def show_events_for_date(self, date_str, parent_popup=None):
        """Show all events for a specific date"""
        # If parent_popup is provided, dismiss it
        if parent_popup:
            parent_popup.dismiss()

        user_id = user_data.get('id', '')
        events = self.db.get_events_by_date(date_str, user_id)

        # Format date for better display
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%m/%d/%Y')
        except:
            formatted_date = date_str

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        title_label = Label(
            text=f"Events for {formatted_date}",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle',
            text_size=(None, None),
            color=(0.85, 0.15, 0.15, 1)  # Red color
        )
        title_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        layout.add_widget(title_label)

        # Scrollable event list
        scroll = ScrollView()
        events_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=[5, 5])
        events_layout.bind(minimum_height=events_layout.setter('height'))

        # Store event buttons to bind them after popup creation
        event_buttons = []

        for event in events:
            # Create better event display
            description_text = event.get('description', 'No description')
            if not description_text or description_text.strip() == '':
                description_text = 'Untitled Event'

            # Determine event color based on creator_id
            # Yellow for user-added events (with creator_id), Red for database events (without creator_id)
            creator_id = event.get('creator_id')
            if creator_id and creator_id.strip():
                # User-added event - Yellow background
                event_color = (1.0, 1.0, 0.7, 1)  # Light yellow
            else:
                # Database event - Red background
                event_color = (1.0, 0.8, 0.8, 1)  # Light red

            event_btn = Button(
                text=description_text,
                size_hint_y=None,
                height=dp(50),  # Increased height
                background_normal='',
                background_color=event_color,  # Use determined color
                color=(0.2, 0.2, 0.2, 1),  # Dark text color for better visibility
                font_size='14sp'  # Set explicit font size
            )
            # Set text alignment after widget is created
            def setup_text_alignment(btn, *args):
                btn.halign = 'left'
                btn.valign = 'middle'
                btn.text_size = (btn.width - 20, None)

            event_btn.bind(size=setup_text_alignment)

            # Store button and event for later binding
            event_buttons.append((event_btn, event))
            events_layout.add_widget(event_btn)

        scroll.add_widget(events_layout)
        layout.add_widget(scroll)

        # Create the popup
        events_popup = Popup(
            title="Events",
            content=layout,
            size_hint=(0.9, 0.7)
        )

        # Now bind the event buttons to show details and dismiss popup
        def show_event_with_popup_dismiss(event, popup):
            """Show event details and dismiss the popup"""
            if popup:
                popup.dismiss()
            self.show_event_details(event)

        for event_btn, event in event_buttons:
            event_btn.bind(on_release=lambda x, e=event: show_event_with_popup_dismiss(e, events_popup))

        # Add new event button
        add_btn = Button(
            text="Add New Event",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)  # Red color
        )
        add_btn.bind(on_release=lambda x: self.add_event_from_popup(date_str, events_popup))
        layout.add_widget(add_btn)

        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=40
        )
        close_btn.bind(on_release=lambda x: events_popup.dismiss())
        layout.add_widget(close_btn)

        events_popup.open()

    def add_event_from_popup(self, date_str, parent_popup):
        """Navigate to add event screen from the events list popup"""
        if parent_popup:
            parent_popup.dismiss()
        self.navigate_to_add_event(date_str)

    def ask_add_event(self, date_str):
        """Ask if user wants to add an event for this date"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Format date for better display
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%m/%d/%Y')
        except:
            formatted_date = date_str

        label = Label(
            text=f"No events for {formatted_date}. Would you like to add one?",
            size_hint_y=None,
            height=dp(80),  # Increased height
            halign='center',
            valign='middle',
            text_size=(None, None),
            font_size='16sp'
        )
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))
        layout.add_widget(label)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)

        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        add_btn = Button(
            text="Add Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)  # Red color
        )

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(add_btn)
        layout.add_widget(button_layout)

        popup = Popup(
            title=f"Date: {formatted_date}",
            content=layout,
            size_hint=(0.85, 0.45)  # Slightly larger
        )

        def cancel(instance):
            popup.dismiss()

        def add_event(instance):
            popup.dismiss()
            self.navigate_to_add_event(date_str)

        cancel_btn.bind(on_release=cancel)
        add_btn.bind(on_release=add_event)

        popup.open()
    def open_add_event_popup(self):
        """Wrapper method for KV file - uses current date"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.navigate_to_add_event(today)

    def navigate_to_add_event(self, date_str):
        """Navigate to the add event screen"""
        # Get the add event screen
        add_event_screen = self.manager.get_screen('add_event')
        # Set the selected date
        add_event_screen.set_date(date_str)
        # Navigate to the screen
        self.manager.current = 'add_event'
    
    def show_add_event_popup(self, selected_date=None):
        """Show popup to add a new event"""
        if selected_date is None:
            # Use today's date as default
            selected_date = datetime.now().strftime("%Y-%m-%d")
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Title input with character limit
        title_input = TextInput(
            hint_text="Event Title (required, max 50 characters)",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(title_input)

        # Character counter for title
        title_char_label = Label(
            text="0/50",
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='right'
        )
        title_char_label.bind(size=title_char_label.setter('text_size'))
        layout.add_widget(title_char_label)

        # Bind text change to update character count for title
        def update_title_char_count(instance, text):
            char_count = len(text)
            title_char_label.text = f"{char_count}/50"
            # Change color if approaching limit
            if char_count > 45:
                title_char_label.color = (1, 0, 0, 1)  # Red
            elif char_count > 40:
                title_char_label.color = (1, 0.5, 0, 1)  # Orange
            else:
                title_char_label.color = (0.5, 0.5, 0.5, 1)  # Gray

            # Limit to 50 characters
            if char_count > 50:
                instance.text = text[:50]

        title_input.bind(text=update_title_char_count)
        
        # Description input with character limit
        desc_input = TextInput(
            hint_text="Description (required, max 200 characters)",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        layout.add_widget(desc_input)

        # Character counter for description
        desc_char_label = Label(
            text="0/200",
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='right'
        )
        desc_char_label.bind(size=desc_char_label.setter('text_size'))
        layout.add_widget(desc_char_label)

        # Bind text change to update character count
        def update_desc_char_count(instance, text):
            char_count = len(text)
            desc_char_label.text = f"{char_count}/200"
            # Change color if approaching limit
            if char_count > 180:
                desc_char_label.color = (1, 0, 0, 1)  # Red
            elif char_count > 150:
                desc_char_label.color = (1, 0.5, 0, 1)  # Orange
            else:
                desc_char_label.color = (0.5, 0.5, 0.5, 1)  # Gray

            # Limit to 200 characters
            if char_count > 200:
                instance.text = text[:200]

        desc_input.bind(text=update_desc_char_count)
        
        # Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        date_label = Label(text=f"Date: {selected_date}", size_hint_x=0.7)
        date_btn = Button(text="Change Date", size_hint_x=0.3)
        
        def show_date_picker(instance):
            self.show_date_picker_popup(date_label, selected_date)
            
        date_btn.bind(on_release=show_date_picker)
        date_layout.add_widget(date_label)
        date_layout.add_widget(date_btn)
        layout.add_widget(date_layout)
        
        # Title input
        title_input = TextInput(
            hint_text="Event Title (required)",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(title_input)

        # Description input
        desc_input = TextInput(
            hint_text="Description (required, max 200 characters)",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        layout.add_widget(desc_input)

        # Character counter for description
        char_counter = Label(
            text="0/200",
            size_hint_y=None,
            height=dp(20),
            halign='right',
            valign='middle',
            font_size='12sp'
        )
        char_counter.bind(size=char_counter.setter('text_size'))
        layout.add_widget(char_counter)

        # Bind description input to update character counter
        def update_char_counter(instance, text):
            char_count = len(text)
            char_counter.text = f"{char_count}/200"
            if char_count > 200:
                char_counter.color = (1, 0, 0, 1)  # Red if over limit
            else:
                char_counter.color = (0.6, 0.6, 0.6, 1)  # Gray if within limit

        desc_input.bind(text=update_char_counter)

        # Student tagging section with better organization
        students_label = Label(
            text="Tag Students:",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            font_size='16sp',
            bold=True
        )
        students_label.bind(size=students_label.setter('text_size'))
        layout.add_widget(students_label)

        # Search input with better styling
        search_input = TextInput(
            hint_text="🔍 Search by Student ID or Name",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size='14sp'
        )
        layout.add_widget(search_input)

        # Program filter only (simplified)
        filter_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))

        # Program filter with label
        program_label = Label(
            text="Filter by Program:",
            size_hint_x=0.4,
            halign='left',
            valign='middle',
            font_size='14sp',
            bold=True,
            color=(0.66, 0.66, 0.66, 1)
        )
        program_label.bind(size=program_label.setter('text_size'))

        program_spinner = Spinner(
            text='All Programs',
            values=['All Programs'],
            size_hint_x=0.6,
            size_hint_y=None,
            height=dp(35),
            font_size='12sp'
        )

        filter_layout.add_widget(program_label)
        filter_layout.add_widget(program_spinner)
        layout.add_widget(filter_layout)

        # Search button with better styling
        search_btn = Button(
            text="🔍 Search Students",
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),
            font_size='14sp',
            bold=True
        )
        layout.add_widget(search_btn)

        # Results section with better organization
        results_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        results_label = Label(
            text="Available Students:",
            halign='left',
            valign='middle',
            font_size='14sp',
            bold=True,
            size_hint_x=0.7
        )
        results_label.bind(size=results_label.setter('text_size'))

        # Clear selection button
        clear_btn = Button(
            text="Clear All",
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(25),
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Secondary red - consistent with app
            font_size='12sp'
        )

        results_header.add_widget(results_label)
        results_header.add_widget(clear_btn)
        layout.add_widget(results_header)

        # Scrollable results area with better styling
        results_scroll = ScrollView(
            size_hint_y=None,
            height=dp(100)
        )

        results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            padding=dp(5)
        )
        results_layout.bind(minimum_height=results_layout.setter('height'))

        results_scroll.add_widget(results_layout)
        layout.add_widget(results_scroll)

        # Selected students display with better styling
        selected_header = Label(
            text="Selected Students:",
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle',
            font_size='14sp',
            bold=True
        )
        selected_header.bind(size=selected_header.setter('text_size'))
        layout.add_widget(selected_header)

        selected_label = Label(
            text="None selected",
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='top',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        selected_label.bind(size=selected_label.setter('text_size'))
        layout.add_widget(selected_label)

        # Store selected students and initialize data
        selected_students = []  # Store selected student IDs

        # Load initial data
        programs = self.db.get_unique_programs()
        program_spinner.values = ['All Programs'] + programs

        # Helper functions for student search and selection
        def update_selected_display():
            """Update the selected students display"""
            if selected_students:
                # Get student names for display
                student_names = []
                for student_id in selected_students:
                    # Find student name from current results or database
                    student = self.db.get_user(student_id)
                    if student:
                        student_names.append(f"• {student['name']} ({student_id})")
                selected_label.text = '\n'.join(student_names)
                selected_label.color = (0.2, 0.2, 0.2, 1)  # Dark text for selected students
            else:
                selected_label.text = "None selected"
                selected_label.color = (0.6, 0.6, 0.6, 1)  # Gray text for empty state

        def clear_all_students(instance):
            """Clear all selected students"""
            selected_students.clear()
            update_selected_display()
            search_students()  # Refresh to update button states

        def search_students(instance=None):
            """Search and display students based on current filters"""
            # Clear current results
            results_layout.clear_widgets()

            # Get search criteria
            search_term = search_input.text.strip()
            program_filter = program_spinner.text if program_spinner.text != 'All Programs' else ''

            # Search students (no section filter)
            students = self.db.search_users(search_term, program_filter, '')

            if students:
                for student in students:
                    # Create student card with better styling
                    student_card = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=dp(50),
                        spacing=dp(10),
                        padding=[dp(10), dp(5)]
                    )

                    # Add background to card
                    with student_card.canvas.before:
                        Color(0.95, 0.95, 0.95, 1)  # Light gray background
                        RoundedRectangle(pos=student_card.pos, size=student_card.size, radius=[5])

                    # Update background when position/size changes
                    student_card.bind(pos=lambda instance, value: update_card_bg(instance),
                                    size=lambda instance, value: update_card_bg(instance))

                    def update_card_bg(card_instance):
                        """Update card background"""
                        try:
                            from kivy.graphics import RoundedRectangle
                            for instruction in card_instance.canvas.before.children:
                                if isinstance(instruction, RoundedRectangle):
                                    instruction.pos = card_instance.pos
                                    instruction.size = card_instance.size
                                    break
                        except:
                            pass

                    # Student info section
                    info_layout = BoxLayout(orientation='vertical', size_hint_x=0.75, spacing=dp(2))

                    # Student name and ID
                    name_label = Label(
                        text=f"{student['name']} ({student['id']})",
                        halign='left',
                        valign='middle',
                        font_size='13sp',
                        bold=True,
                        color=(0.2, 0.2, 0.2, 1),
                        size_hint_y=0.6
                    )
                    name_label.bind(size=name_label.setter('text_size'))

                    # Program and section info
                    program_text = ""
                    if student.get('program'):
                        program_text = student['program']
                        if student.get('section'):
                            program_text += f" - Section {student['section']}"

                    program_label = Label(
                        text=program_text,
                        halign='left',
                        valign='middle',
                        font_size='11sp',
                        color=(0.5, 0.5, 0.5, 1),
                        size_hint_y=0.4
                    )
                    program_label.bind(size=program_label.setter('text_size'))

                    info_layout.add_widget(name_label)
                    info_layout.add_widget(program_label)

                    # Add/Remove button with better styling
                    is_selected = student['id'] in selected_students
                    action_btn = Button(
                        text="✓ Added" if is_selected else "+ Add",
                        size_hint_x=0.25,
                        size_hint_y=None,
                        height=dp(35),
                        background_normal='',
                        background_color=(0.9, 0.3, 0.3, 1) if is_selected else (0.2, 0.7, 0.2, 1),
                        font_size='12sp',
                        bold=True
                    )

                    # Bind button action
                    def toggle_student(btn, student_id=student['id']):
                        if student_id in selected_students:
                            selected_students.remove(student_id)
                            btn.text = "+ Add"
                            btn.background_color = (0.2, 0.7, 0.2, 1)
                        else:
                            selected_students.append(student_id)
                            btn.text = "✓ Added"
                            btn.background_color = (0.9, 0.3, 0.3, 1)
                        update_selected_display()
                        # Refresh search results to update button states
                        search_students()

                    action_btn.bind(on_release=toggle_student)

                    student_card.add_widget(info_layout)
                    student_card.add_widget(action_btn)
                    results_layout.add_widget(student_card)
            else:
                no_results_label = Label(
                    text="No students found matching your criteria",
                    size_hint_y=None,
                    height=dp(40),
                    halign='center',
                    font_size='13sp',
                    color=(0.6, 0.6, 0.6, 1)
                )
                results_layout.add_widget(no_results_label)

        # Bind events
        search_btn.bind(on_release=search_students)
        search_input.bind(on_text_validate=search_students)
        clear_btn.bind(on_release=clear_all_students)

        # Initial search to show all students
        search_students()
        
        # Link input
        link_input = TextInput(
            hint_text="Event Link (optional)",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(link_input)
        
        # Image selection
        image_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        image_label = Label(text="No image selected", size_hint_x=0.7)
        image_btn = Button(text="Select Image", size_hint_x=0.3)
        
        # Container for image path
        image_path_container = {'path': ''}
        
        def show_image_picker(instance):
            self.show_image_picker_popup(image_label, image_path_container, "Select Event Image")
            
        image_btn.bind(on_release=show_image_picker)
        image_layout.add_widget(image_label)
        image_layout.add_widget(image_btn)
        layout.add_widget(image_layout)

        # Privacy is now automatically determined based on student tagging
        # No manual privacy selection needed

        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        add_btn = Button(
            text="Add Event", 
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)  # Red color
        )
        
        def cancel(instance):
            # Check if any data has been entered
            has_data = (
                title_input.text.strip() or
                desc_input.text.strip() or
                link_input.text.strip() or
                len(selected_students) > 0 or
                image_path_container['path'] or
                date_label.text != f"Date: {selected_date}"
            )

            if has_data:
                # Show confirmation dialog
                self.show_cancel_confirmation(popup)
            else:
                # No data entered, close directly
                popup.dismiss()
            
        def add_event(instance):
            # Get values from inputs
            title = title_input.text.strip()
            description = desc_input.text.strip()

            # Validation: Check if title is provided
            if not title:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text='Please enter an event title'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Validation: Check if description is provided
            if not description:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text='Please enter an event description'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Validation: Check title length (max 50 characters)
            if len(title) > 50:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text='Event title must be 50 characters or less'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Validation: Check description length (max 200 characters)
            if len(description) > 200:
                error_popup = Popup(
                    title='Validation Error',
                    content=Label(text='Event description must be 200 characters or less'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()
                return

            # Format description with title
            full_description = f"{title} - {description}"
                
            # Get date from label
            date_str = date_label.text.replace("Date: ", "")

            # Get tagged IDs from selected students
            tagged_ids_str = ','.join(selected_students) if selected_students else ''

            # Get link
            link = link_input.text.strip()

            # Get image path
            image_path = image_path_container['path']

            # Automatically determine privacy based on student tagging
            # If students are tagged, make it private; otherwise, make it public
            privacy = 'private' if selected_students else 'public'

            # Get current user ID as creator
            creator_id = user_data.get('id', '')

            # Add event to database
            self.db.add_event(date_str, full_description, tagged_ids_str, link, image_path, privacy, creator_id)
            
            # Refresh calendar
            self.build_calendar()
            
            # Close popup
            popup.dismiss()
            
            # Show success message
            success_popup = Popup(
                title='Success',
                content=Label(text='Event added successfully!'),
                size_hint=(0.7, 0.3)
            )
            success_popup.open()
            
            # Auto-dismiss after 1.5 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
            
        cancel_btn.bind(on_release=cancel)
        add_btn.bind(on_release=add_event)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(add_btn)
        layout.add_widget(button_layout)
        
        popup = Popup(
            title="Add New Event",
            content=layout,
            size_hint=(0.9, 0.8)
        )
        popup.open()

    def show_cancel_confirmation(self, parent_popup):
        """Show confirmation dialog when canceling event creation with unsaved data"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning message
        warning_message = Label(
            text="Are you sure you want to cancel?\n\nAny entered information will be lost and no event will be saved.",
            font_size='16sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(15)
        )

        continue_btn = Button(
            text="Continue Editing",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),  # Green
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        cancel_btn = Button(
            text="Yes, Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def continue_editing(instance):
            confirm_popup.dismiss()

        def confirm_cancel(instance):
            confirm_popup.dismiss()
            parent_popup.dismiss()
            # Show cancellation message
            cancel_popup = Popup(
                title='Cancelled',
                content=Label(text='Event creation cancelled. No event was saved.'),
                size_hint=(0.7, 0.3)
            )
            cancel_popup.open()

            # Auto-dismiss after 2 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: cancel_popup.dismiss(), 2)

        continue_btn.bind(on_release=continue_editing)
        cancel_btn.bind(on_release=confirm_cancel)

        button_layout.add_widget(continue_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Cancellation",
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()
    
    def show_date_picker_popup(self, label_widget, current_date=None):
        """Show a date picker popup and update the provided label"""
        if current_date is None:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
        try:
            year, month, day = map(int, current_date.split('-'))
        except:
            # Default to today if date parsing fails
            today = datetime.now()
            year, month, day = today.year, today.month, today.day
            
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Date picker
        date_picker = DatePicker(
            year=year,
            month=month,
            day=day
        )
        content.add_widget(date_picker)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(
            text="Select", 
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)  # Red color
        )
        
        def cancel(instance):
            date_popup.dismiss()
            
        def select_date(instance):
            selected = date_picker.date
            formatted_date = f"{selected.year}-{selected.month:02d}-{selected.day:02d}"
            label_widget.text = f"Date: {formatted_date}"
            date_popup.dismiss()
            
        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_date)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)
        
        date_popup = Popup(
            title="Select Date",
            content=content,
            size_hint=(0.9, 0.7)
        )
        date_popup.open()
    
    def show_image_picker_popup(self, label_widget, image_path_container, title, details=None):
        """Show a file chooser popup to select an image and update the provided label"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # File chooser for images
        file_chooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif'],
            path=os.path.expanduser('~')  # Start in user's home directory
        )
        content.add_widget(file_chooser)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(
            text="Select", 
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)  # Red color
        )
        
        def cancel(instance):
            image_popup.dismiss()
            
        def select_image(instance):
            if file_chooser.selection:
                selected_path = file_chooser.selection[0]
                # Update the label
                label_widget.text = os.path.basename(selected_path)
                # Store the full path in the container
                image_path_container['path'] = selected_path
                image_popup.dismiss()
            
        cancel_btn.bind(on_release=cancel)
        select_btn.bind(on_release=select_image)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)
        
        image_popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.8)
        )
        image_popup.open()
    
    def show_add_note_popup(self, selected_date=None):
        """Navigate to add note screen"""
        if selected_date is None:
            # Use today's date as default
            selected_date = datetime.now().strftime("%Y-%m-%d")

        # Navigate to add note screen
        add_note_screen = self.manager.get_screen('add_note')
        add_note_screen.set_date(selected_date)
        self.manager.current = 'add_note'


    def show_cancel_note_confirmation(self, parent_popup):
        """Show confirmation dialog when canceling note creation with unsaved data"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning message
        warning_message = Label(
            text="Are you sure you want to cancel?\n\nAny entered information will be lost and no note will be saved.",
            font_size='16sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(15)
        )

        continue_btn = Button(
            text="Continue Editing",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),  # Green
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        cancel_btn = Button(
            text="Yes, Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def continue_editing(instance):
            confirm_popup.dismiss()

        def confirm_cancel(instance):
            confirm_popup.dismiss()
            parent_popup.dismiss()
            # Show cancellation message
            cancel_popup = Popup(
                title='Cancelled',
                content=Label(text='Note creation cancelled. No note was saved.'),
                size_hint=(0.7, 0.3)
            )
            cancel_popup.open()

            # Auto-dismiss after 2 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: cancel_popup.dismiss(), 2)

        continue_btn.bind(on_release=continue_editing)
        cancel_btn.bind(on_release=confirm_cancel)

        button_layout.add_widget(continue_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Cancellation",
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()

    def change_month(self, step):
        """Change the displayed month by the given number of steps"""
        self.current_month += step
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        elif self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

        # Update month/year label
        self.ids.month_year_label.text = f"{calendar.month_name[self.current_month]} {self.current_year}"

        # Rebuild calendar for the new month
        self.build_calendar()

    def update_calendar(self):
        """Refresh the calendar display"""
        self.build_calendar()

    def update_rect(self, instance, value):
        """Update rectangle position and size for canvas backgrounds"""
        try:
            for instruction in instance.canvas.before.children:
                if hasattr(instruction, 'pos'):
                    instruction.pos = instance.pos
                if hasattr(instruction, 'size'):
                    instruction.size = instance.size
                    break
        except Exception as e:
            print(f"Error updating background: {e}")

    def show_event_details(self, event):
        """Navigate to event details screen"""
        # Navigate to view event screen
        view_screen = self.manager.get_screen('view_event')
        view_screen.set_event(event)
        self.manager.current = 'view_event'

    def confirm_delete_event(self, event_id):
        """Show enhanced confirmation dialog before deleting event"""
        # Get event details for better confirmation message
        event = self.db.get_event_by_id(event_id)
        event_title = "this event"

        if event:
            description = event.get('description', '')
            if description:
                # Extract title from description
                if " - " in description:
                    event_title = f'"{description.split(" - ", 1)[0].strip()}"'
                else:
                    event_title = f'"{description[:30]}..."' if len(description) > 30 else f'"{description}"'

        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning icon and title
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)

        # Warning icon (using emoji)
        warning_icon = Label(
            text="⚠️",
            font_size='24sp',
            size_hint_x=None,
            width=dp(40)
        )

        # Warning title
        warning_title = Label(
            text="Delete Event",
            font_size='18sp',
            bold=True,
            color=(0.9, 0.3, 0.3, 1),
            halign='left'
        )
        warning_title.bind(size=warning_title.setter('text_size'))

        title_layout.add_widget(warning_icon)
        title_layout.add_widget(warning_title)
        content.add_widget(title_layout)

        # Warning message with event title
        warning_message = Label(
            text=f"Are you sure you want to delete {event_title}?\n\nThis action cannot be undone and the event will be permanently removed from your calendar.",
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(15)
        )

        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        delete_btn = Button(
            text="Delete Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def cancel_delete(instance):
            confirm_popup.dismiss()

        def proceed_delete(instance):
            confirm_popup.dismiss()
            # Delete the event from database
            success = self.db.delete_event(event_id)

            if success:
                # Refresh calendar
                self.build_calendar()

                # Show success message
                success_popup = Popup(
                    title='✅ Success',
                    content=Label(text='Event deleted successfully!'),
                    size_hint=(0.7, 0.3)
                )
                success_popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
            else:
                # Show error message
                error_popup = Popup(
                    title='❌ Error',
                    content=Label(text='Failed to delete event. Please try again.'),
                    size_hint=(0.7, 0.3)
                )
                error_popup.open()

        cancel_btn.bind(on_release=cancel_delete)
        delete_btn.bind(on_release=proceed_delete)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)
        content.add_widget(button_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Deletion",
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()

    def show_edit_event_popup(self, event):
        """Show popup to edit event details"""
        # Check if event is a dictionary or tuple and extract values accordingly
        if isinstance(event, dict):
            event_id = event.get('id')
            current_date = event.get('date')
            current_description = event.get('description')
            current_image_path = event.get('image_path')
            current_tagged_ids = event.get('tagged_ids')
            current_link = event.get('link')
        else:  # Assume it's a tuple
            event_id, current_date, current_description, current_image_path, current_tagged_ids, current_link = event
        
        # Try to split title and description if they exist
        title_text = ""
        desc_text = ""
        
        if current_description and " - " in current_description:
            parts = current_description.split(" - ", 1)
            title_text = parts[0].replace("Note: ", "")  # Remove "Note: " prefix if it exists
            desc_text = parts[1]
        else:
            title_text = current_description.replace("Note: ", "") if current_description else ""
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Title input
        title_label = Label(
            text="Title",
            size_hint_y=None,
            height=20,
            halign='left'
        )
        layout.add_widget(title_label)
        
        title_input = TextInput(
            text=title_text,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title_input)
        
        # Description input
        desc_label = Label(
            text="Description",
            size_hint_y=None,
            height=20,
            halign='left'
        )
        layout.add_widget(desc_label)
        
        desc_input = TextInput(
            text=desc_text,
            multiline=True,
            size_hint_y=None,
            height=80
        )
        layout.add_widget(desc_input)
        
        # Student tagging section with better organization (for editing)
        students_label = Label(
            text="Tag Students:",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            font_size='16sp',
            bold=True
        )
        students_label.bind(size=students_label.setter('text_size'))
        layout.add_widget(students_label)

        # Search input with better styling
        search_input = TextInput(
            hint_text="🔍 Search by Student ID or Name",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size='14sp'
        )
        layout.add_widget(search_input)

        # Filter section with labels
        filter_section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))

        # Filter label
        filter_label = Label(
            text="Filters:",
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle',
            font_size='14sp'
        )
        filter_label.bind(size=filter_label.setter('text_size'))
        filter_section.add_widget(filter_label)

        # Filter dropdowns layout
        filter_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))

        # Program filter with label
        program_layout = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_x=0.5)
        program_label = Label(
            text="Program:",
            size_hint_y=None,
            height=dp(15),
            halign='left',
            font_size='12sp'
        )
        program_label.bind(size=program_label.setter('text_size'))
        program_layout.add_widget(program_label)

        program_spinner = Spinner(
            text='All Programs',
            values=['All Programs'],
            size_hint_y=None,
            height=dp(35),
            font_size='12sp'
        )
        program_layout.add_widget(program_spinner)
        filter_layout.add_widget(program_layout)

        # Section filter with label
        section_layout = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_x=0.5)
        section_label = Label(
            text="Section:",
            size_hint_y=None,
            height=dp(15),
            halign='left',
            font_size='12sp'
        )
        section_label.bind(size=section_label.setter('text_size'))
        section_layout.add_widget(section_label)

        section_spinner = Spinner(
            text='All Sections',
            values=['All Sections'],
            size_hint_y=None,
            height=dp(35),
            font_size='12sp'
        )
        section_layout.add_widget(section_spinner)
        filter_layout.add_widget(section_layout)

        filter_section.add_widget(filter_layout)
        layout.add_widget(filter_section)

        # Search button with better styling
        search_btn = Button(
            text="🔍 Search Students",
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),
            font_size='14sp',
            bold=True
        )
        layout.add_widget(search_btn)

        # Results section with better organization
        results_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        results_label = Label(
            text="Available Students:",
            halign='left',
            valign='middle',
            font_size='14sp',
            bold=True,
            size_hint_x=0.7
        )
        results_label.bind(size=results_label.setter('text_size'))

        # Clear selection button
        clear_btn = Button(
            text="Clear All",
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(25),
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Secondary red - consistent with app
            font_size='12sp'
        )

        results_header.add_widget(results_label)
        results_header.add_widget(clear_btn)
        layout.add_widget(results_header)

        # Scrollable results area with better styling
        results_scroll = ScrollView(
            size_hint_y=None,
            height=dp(100)
        )

        results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            padding=dp(5)
        )
        results_layout.bind(minimum_height=results_layout.setter('height'))

        results_scroll.add_widget(results_layout)
        layout.add_widget(results_scroll)

        # Selected students display with better styling
        selected_header = Label(
            text="Selected Students:",
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle',
            font_size='14sp',
            bold=True
        )
        selected_header.bind(size=selected_header.setter('text_size'))
        layout.add_widget(selected_header)

        selected_label = Label(
            text="None selected",
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='top',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        selected_label.bind(size=selected_label.setter('text_size'))
        layout.add_widget(selected_label)

        # Initialize selected students with current tagged IDs
        selected_students = []
        if current_tagged_ids:
            selected_students = [id.strip() for id in current_tagged_ids.split(',') if id.strip()]

        # Load initial data
        programs = self.db.get_unique_programs()
        program_spinner.values = ['All Programs'] + programs

        sections = self.db.get_unique_sections()
        section_spinner.values = ['All Sections'] + sections

        # Helper functions for student search and selection (same as add event)
        def update_selected_display():
            """Update the selected students display"""
            if selected_students:
                # Get student names for display
                student_names = []
                for student_id in selected_students:
                    # Find student name from current results or database
                    student = self.db.get_user(student_id)
                    if student:
                        student_names.append(f"{student['name']} ({student_id})")
                selected_label.text = f"Selected Students: {', '.join(student_names)}"
            else:
                selected_label.text = "Selected Students: None"

        def search_students(instance=None):
            """Search and display students based on current filters"""
            # Clear current results
            results_layout.clear_widgets()

            # Get search criteria
            search_term = search_input.text.strip()
            program_filter = program_spinner.text if program_spinner.text != 'All Programs' else ''
            section_filter = section_spinner.text if section_spinner.text != 'All Sections' else ''

            # Search students
            students = self.db.search_users(search_term, program_filter, section_filter)

            if students:
                for student in students:
                    student_row = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=dp(35),
                        spacing=dp(10)
                    )

                    # Student info label
                    info_text = f"{student['name']} - {student['id']}"
                    if student.get('program'):
                        info_text += f" ({student['program']}"
                        if student.get('section'):
                            info_text += f" - {student['section']}"
                        info_text += ")"

                    student_label = Label(
                        text=info_text,
                        halign='left',
                        valign='middle',
                        size_hint_x=0.8
                    )
                    student_label.bind(size=student_label.setter('text_size'))

                    # Add/Remove button
                    is_selected = student['id'] in selected_students
                    action_btn = Button(
                        text="Remove" if is_selected else "Add",
                        size_hint_x=0.2,
                        size_hint_y=None,
                        height=dp(30),
                        background_normal='',
                        background_color=(0.9, 0.3, 0.3, 1) if is_selected else (0.2, 0.7, 0.2, 1)
                    )

                    # Bind button action
                    def toggle_student(btn, student_id=student['id']):
                        if student_id in selected_students:
                            selected_students.remove(student_id)
                            btn.text = "Add"
                            btn.background_color = (0.2, 0.7, 0.2, 1)
                        else:
                            selected_students.append(student_id)
                            btn.text = "Remove"
                            btn.background_color = (0.9, 0.3, 0.3, 1)
                        update_selected_display()
                        # Refresh search results to update button states
                        search_students()

                    action_btn.bind(on_release=toggle_student)

                    student_row.add_widget(student_label)
                    student_row.add_widget(action_btn)
                    results_layout.add_widget(student_row)
            else:
                no_results_label = Label(
                    text="No students found",
                    size_hint_y=None,
                    height=dp(30),
                    halign='center'
                )
                results_layout.add_widget(no_results_label)

        def update_sections_for_program(instance, program):
            """Update section dropdown when program changes"""
            if program == 'All Programs':
                sections = self.db.get_unique_sections()
            else:
                sections = self.db.get_unique_sections(program)
            section_spinner.values = ['All Sections'] + sections
            section_spinner.text = 'All Sections'

        # Bind events
        search_btn.bind(on_release=search_students)
        search_input.bind(on_text_validate=search_students)
        program_spinner.bind(text=update_sections_for_program)

        # Initial search to show all students and update display
        search_students()
        update_selected_display()
        
        # Link input
        link_label = Label(
            text="Link",
            size_hint_y=None,
            height=20,
            halign='left'
        )
        layout.add_widget(link_label)
        
        link_input = TextInput(
            text=current_link,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(link_input)
        
        # Image selection
        image_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        image_label = Label(
            text=f"Current image: {current_image_path if current_image_path else 'None'}",
            size_hint_x=0.7
        )
        image_btn = Button(text="Change Image", size_hint_x=0.3)
        
        # Container for image path
        image_path = [current_image_path]
        
        def show_image_picker(instance):
            # You'll need to implement this method if it doesn't exist
            self.show_image_picker_popup(image_label, image_path, "Select Event Image")
        
        image_btn.bind(on_release=show_image_picker)
        image_layout.add_widget(image_label)
        image_layout.add_widget(image_btn)
        layout.add_widget(image_layout)

        # Privacy is now automatically determined based on student tagging
        # No manual privacy selection needed

        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(
            text="Cancel",
            background_color=(0.7, 0.7, 0.7, 1)
        )
        
        update_btn = Button(
            text="Update",
            background_color=(0.85, 0.15, 0.15, 1)
        )
        
        def cancel_edit(instance):
            popup.dismiss()
        
        def update_event(instance):
            # Combine title and description
            is_note = current_description.startswith("Note:")
            if is_note:
                full_description = f"Note: {title_input.text}"
            else:
                full_description = title_input.text
            
            if desc_input.text.strip():
                full_description += f" - {desc_input.text}"
    
            # Get tagged IDs from selected students
            tagged_ids_str = ','.join(selected_students) if selected_students else ''

            # Automatically determine privacy based on student tagging
            # If students are tagged, make it private; otherwise, make it public
            privacy = 'private' if selected_students else 'public'

            success = self.update_event_in_db(
                event_id,
                current_date,
                full_description,
                image_path[0],
                tagged_ids_str,
                link_input.text,
                privacy
            )
    
            if success:
                self.build_calendar()  # Refresh calendar
                popup.dismiss()
        
                # Show success message
                success_popup = Popup(
                    title='Success',
                    content=Label(text='Updated successfully!'),
                    size_hint=(0.6, 0.3)
                )
                success_popup.open()
        
                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
            else:
                # Show error message
                error_popup = Popup(
                    title='Error',
                    content=Label(text='Failed to update!'),
                    size_hint=(0.6, 0.3)
                )
                error_popup.open()
        
        cancel_btn.bind(on_release=cancel_edit)
        update_btn.bind(on_release=update_event)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(update_btn)
        layout.add_widget(button_layout)
        
        popup = Popup(title="Edit Event/Note", content=layout, size_hint=(0.9, 0.8))
        popup.open()

    def update_event_in_db(self, event_id, date, description, image_path, tagged_ids, link, privacy='public'):
        """Update event in database"""
        try:
            self.db.update_event(event_id, date, description, tagged_ids, link, image_path, privacy)
            return True
        except Exception as e:
            print(f"Error updating event: {e}")
            return False

    def confirm_delete_event(self, event_id):
        """Show enhanced confirmation dialog before deleting event"""
        # Get event details for better confirmation message
        event = self.db.get_event_by_id(event_id)
        event_title = "this event"

        if event:
            description = event.get('description', '')
            if description:
                # Extract title from description
                if " - " in description:
                    event_title = f'"{description.split(" - ", 1)[0].strip()}"'
                else:
                    event_title = f'"{description[:30]}..."' if len(description) > 30 else f'"{description}"'

        layout = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning icon and title
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)

        # Warning icon (using emoji)
        warning_icon = Label(
            text="⚠️",
            font_size='24sp',
            size_hint_x=None,
            width=dp(40)
        )

        # Warning title
        warning_title = Label(
            text="Delete Event",
            font_size='18sp',
            bold=True,
            color=(0.9, 0.3, 0.3, 1),
            halign='left'
        )
        warning_title.bind(size=warning_title.setter('text_size'))

        title_layout.add_widget(warning_icon)
        title_layout.add_widget(warning_title)
        layout.add_widget(title_layout)

        # Warning message with event title
        warning_label = Label(
            text=f"Are you sure you want to delete {event_title}?\n\nThis action cannot be undone and the event will be permanently removed from your calendar.",
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_label.bind(size=warning_label.setter('text_size'))
        layout.add_widget(warning_label)

        # Buttons layout
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(15))

        # Cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        # Delete button
        delete_btn = Button(
            text="Delete Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def cancel_delete(instance):
            confirm_popup.dismiss()

        def proceed_delete(instance):
            confirm_popup.dismiss()
            self.delete_event(event_id)

        cancel_btn.bind(on_release=cancel_delete)
        delete_btn.bind(on_release=proceed_delete)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        layout.add_widget(btn_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Deletion",
            content=layout,
            size_hint=(0.85, 0.5),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()

    def delete_event(self, event_id):
        """Delete event from database and refresh the calendar"""
        try:
            self.db.delete_event(event_id)
            self.update_calendar()  # Refresh the calendar
            
            # Show success message
            success_popup = Popup(
                title='Success',
                content=Label(text='Event deleted successfully!'),
                size_hint=(0.6, 0.3)
            )
            success_popup.open()
            
            # Auto-dismiss after 1.5 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
        except Exception as e:
            print(f"Error deleting event: {e}")
            # Show error message
            error_popup = Popup(
                title='Error',
                content=Label(text=f'Failed to delete event: {str(e)}'),
                size_hint=(0.6, 0.3)
            )
            error_popup.open()

    def get_events_for_current_month(self):
        # Get all events for the current month
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        end_date = f"{self.current_year}-{self.current_month:02d}-31"
        return self.db.get_events_between_dates(start_date, end_date) # Implement this method in DatabaseManager



class AdminScreen(Screen):
    """Admin panel for managing events and users"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year

    def on_enter(self):
        """Check admin access and load admin interface"""
        user_id = user_data.get('id', '')
        if not self.db.is_admin_user(user_id):
            # Not an admin, redirect to main screen
            self.show_error("Access denied. Admin privileges required.")
            self.manager.current = 'main'
            return

        # Update welcome message
        user_name = user_data.get('name', 'Admin')
        if hasattr(self.ids, 'admin_welcome_label'):
            self.ids.admin_welcome_label.text = f"Welcome, {user_name}!"

        # Load admin events
        self.load_admin_events()

    def load_admin_events(self):
        """Load events created by admin for management"""
        if not hasattr(self.ids, 'admin_event_list'):
            return

        # Clear existing events
        self.ids.admin_event_list.clear_widgets()

        # Get admin events for current month
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        from calendar import monthrange
        last_day = monthrange(self.current_year, self.current_month)[1]
        end_date = f"{self.current_year}-{self.current_month:02d}-{last_day:02d}"

        admin_events = self.db.get_admin_events_between_dates(start_date, end_date)

        # Add spacing at the top
        self.ids.admin_event_list.add_widget(Widget(size_hint_y=None, height=dp(10)))

        if admin_events:
            for event in admin_events:
                self.add_admin_event_to_list(event)
        else:
            # No events message
            import calendar
            no_events_label = Label(
                text=f"No admin events for {calendar.month_name[self.current_month]}",
                color=(0.5, 0.5, 0.5, 1),
                font_size='16sp',
                size_hint_y=None,
                height=dp(60)
            )
            self.ids.admin_event_list.add_widget(no_events_label)

        # Add spacing at the bottom
        self.ids.admin_event_list.add_widget(Widget(size_hint_y=None, height=dp(80)))

    def add_admin_event_to_list(self, event):
        """Add admin event to the list"""
        # Create simple event card for admin view
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=[dp(15), dp(10)],
            spacing=dp(5)
        )

        # Add background
        with card.canvas.before:
            Color(0.9, 0.9, 1.0, 1)  # Light blue for admin events
            RoundedRectangle(pos=card.pos, size=card.size, radius=[10])

        # Update background when position/size changes
        card.bind(pos=self.update_card_background, size=self.update_card_background)

        # Event title
        title = event.get('description', 'Untitled Event')
        if " - " in title:
            title = title.split(" - ", 1)[0].strip()

        title_label = Label(
            text=title,
            font_size='16sp',
            bold=True,
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(25)
        )
        title_label.bind(size=title_label.setter('text_size'))

        # Event date
        date_label = Label(
            text=f"Date: {event.get('date', '')}",
            font_size='14sp',
            halign='left',
            valign='middle',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(20)
        )
        date_label.bind(size=date_label.setter('text_size'))

        card.add_widget(title_label)
        card.add_widget(date_label)

        # Make clickable for editing
        card.bind(on_touch_down=lambda instance, touch:
                self.edit_admin_event(event) if instance.collide_point(*touch.pos) else None)

        # Container with spacing
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=card.height + dp(10),
            padding=[0, 0, 0, dp(10)]
        )
        container.add_widget(card)
        self.ids.admin_event_list.add_widget(container)

    def update_card_background(self, instance, value):
        """Update card background when position/size changes"""
        try:
            from kivy.graphics import RoundedRectangle
            for instruction in instance.canvas.before.children:
                if isinstance(instruction, RoundedRectangle):
                    instruction.pos = instance.pos
                    instruction.size = instance.size
                    break
        except Exception as e:
            print(f"Error updating card background: {e}")

    def edit_admin_event(self, event):
        """Edit admin event"""
        # For now, just show event details with delete option
        self.show_admin_event_details(event)

    def show_admin_event_details(self, event):
        """Show admin event details with management options"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Event title
        title = event.get('description', 'Untitled Event')
        if " - " in title:
            title = title.split(" - ", 1)[0].strip()

        content.add_widget(Label(
            text=f"Event: {title}",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.85, 0.15, 0.15, 1)
        ))

        # Event description
        description = event.get('description', '')
        if " - " in description:
            desc_part = description.split(" - ", 1)[1].strip()
            content.add_widget(Label(
                text=f"Description: {desc_part}",
                font_size='14sp',
                size_hint_y=None,
                height=dp(60),
                halign='left',
                valign='top'
            ))

        # Event date
        content.add_widget(Label(
            text=f"Date: {event.get('date', '')}",
            font_size='14sp',
            size_hint_y=None,
            height=dp(30)
        ))

        # Action buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        # Delete button
        delete_btn = Button(
            text="Delete Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        # Close button
        close_btn = Button(
            text="Close",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Admin Event Details",
            content=content,
            size_hint=(0.85, 0.6)
        )

        def delete_admin_event(instance):
            popup.dismiss()
            self.confirm_delete_admin_event(event.get('id'))

        delete_btn.bind(on_release=delete_admin_event)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_delete_admin_event(self, event_id):
        """Show confirmation dialog before deleting admin event"""
        # Get event details for better confirmation message
        event = self.db.get_event_by_id(event_id)
        event_title = "this admin event"

        if event:
            description = event.get('description', '')
            if description:
                # Extract title from description
                if " - " in description:
                    event_title = f'"{description.split(" - ", 1)[0].strip()}"'
                else:
                    event_title = f'"{description[:30]}..."' if len(description) > 30 else f'"{description}"'

        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning icon and title
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)

        # Warning icon (using emoji)
        warning_icon = Label(
            text="⚠️",
            font_size='24sp',
            size_hint_x=None,
            width=dp(40)
        )

        # Warning title
        warning_title = Label(
            text="Delete Admin Event",
            font_size='18sp',
            bold=True,
            color=(0.9, 0.3, 0.3, 1),
            halign='left'
        )
        warning_title.bind(size=warning_title.setter('text_size'))

        title_layout.add_widget(warning_icon)
        title_layout.add_widget(warning_title)
        content.add_widget(title_layout)

        # Warning message with event title
        warning_message = Label(
            text=f"Are you sure you want to delete {event_title}?\n\nThis is an admin event that will be removed for ALL users. This action cannot be undone.",
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(100),
            color=(0.3, 0.3, 0.3, 1)
        )
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(15)
        )

        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),  # Gray
            color=(1, 1, 1, 1),
            font_size='16sp'
        )

        delete_btn = Button(
            text="Delete Admin Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),  # Red
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )

        def cancel_delete(instance):
            confirm_popup.dismiss()

        def proceed_delete(instance):
            confirm_popup.dismiss()
            # Delete the admin event from database
            success = self.db.delete_event(event_id)

            if success:
                # Refresh admin events list
                self.load_admin_events()

                # Show success message
                success_popup = Popup(
                    title='✅ Success',
                    content=Label(text='Admin event deleted successfully!'),
                    size_hint=(0.7, 0.3)
                )
                success_popup.open()

                # Auto-dismiss after 1.5 seconds
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
            else:
                # Show error message
                self.show_error("Failed to delete admin event. Please try again.")

        cancel_btn.bind(on_release=cancel_delete)
        delete_btn.bind(on_release=proceed_delete)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)

        confirm_popup = Popup(
            title="⚠️ Confirm Admin Event Deletion",
            content=content,
            size_hint=(0.9, 0.6),
            auto_dismiss=False  # Prevent accidental dismissal
        )
        confirm_popup.open()

    def show_add_admin_event_popup(self):
        """Show popup to add new admin event"""
        # Simple add event popup for admin
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Title input with character limit
        title_input = TextInput(
            hint_text="Event Title (required, max 50 characters)",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title_input)

        # Character counter for title
        title_char_label = Label(
            text="0/50",
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='right'
        )
        title_char_label.bind(size=title_char_label.setter('text_size'))
        content.add_widget(title_char_label)

        # Bind text change to update character count for title
        def update_title_char_count(instance, text):
            char_count = len(text)
            title_char_label.text = f"{char_count}/50"
            # Change color if approaching limit
            if char_count > 45:
                title_char_label.color = (1, 0, 0, 1)  # Red
            elif char_count > 40:
                title_char_label.color = (1, 0.5, 0, 1)  # Orange
            else:
                title_char_label.color = (0.5, 0.5, 0.5, 1)  # Gray

            # Limit to 50 characters
            if char_count > 50:
                instance.text = text[:50]

        title_input.bind(text=update_title_char_count)

        # Description input with character limit
        desc_input = TextInput(
            hint_text="Event Description (required, max 200 characters)",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(desc_input)

        # Character counter for description
        desc_char_label = Label(
            text="0/200",
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='right'
        )
        desc_char_label.bind(size=desc_char_label.setter('text_size'))
        content.add_widget(desc_char_label)

        # Bind text change to update character count for description
        def update_desc_char_count(instance, text):
            char_count = len(text)
            desc_char_label.text = f"{char_count}/200"
            # Change color if approaching limit
            if char_count > 180:
                desc_char_label.color = (1, 0, 0, 1)  # Red
            elif char_count > 150:
                desc_char_label.color = (1, 0.5, 0, 1)  # Orange
            else:
                desc_char_label.color = (0.5, 0.5, 0.5, 1)  # Gray

            # Limit to 200 characters
            if char_count > 200:
                instance.text = text[:200]

        desc_input.bind(text=update_desc_char_count)

        # Date input
        date_input = TextInput(
            hint_text="Date (YYYY-MM-DD)",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(date_input)

        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)

        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        add_btn = Button(
            text="Add Event",
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.85, 0.15, 0.15, 1)
        )

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(add_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Add Admin Event",
            content=content,
            size_hint=(0.9, 0.7)
        )

        def cancel(instance):
            popup.dismiss()

        def add_event(instance):
            title = title_input.text.strip()
            description = desc_input.text.strip()
            date = date_input.text.strip()

            # Validation: Check if title is provided
            if not title:
                self.show_error("Please enter an event title")
                return

            # Validation: Check if description is provided
            if not description:
                self.show_error("Please enter an event description")
                return

            # Validation: Check if date is provided
            if not date:
                self.show_error("Please enter an event date")
                return

            # Validation: Check title length (max 50 characters)
            if len(title) > 50:
                self.show_error("Event title must be 50 characters or less")
                return

            # Validation: Check description length (max 200 characters)
            if len(description) > 200:
                self.show_error("Event description must be 200 characters or less")
                return

            # Validation: Check date format (basic validation)
            try:
                from datetime import datetime
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                self.show_error("Please enter date in YYYY-MM-DD format")
                return

            # Format description
            full_description = f"{title} - {description}"

            # Add event as admin
            admin_id = user_data.get('id', '')
            success = self.db.add_event(
                date=date,
                description=full_description,
                tagged_ids='',
                link='',
                image_path='',
                privacy='public',
                creator_id=admin_id
            )

            if success:
                popup.dismiss()
                self.load_admin_events()  # Refresh admin events

                # Show success message
                success_popup = Popup(
                    title='Success',
                    content=Label(text='Admin event added successfully!'),
                    size_hint=(0.6, 0.3)
                )
                success_popup.open()

                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 1.5)
            else:
                self.show_error("Failed to add event")

        cancel_btn.bind(on_release=cancel)
        add_btn.bind(on_release=add_event)

        popup.open()

    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()

    def logout(self):
        # Clear user data
        user_data.clear()
        # Return to login screen
        self.manager.current = 'login'
    
    def clear_data(self):
        # Show options popup for what to clear
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text="What would you like to clear?",
            font_size='18sp',
            size_hint_y=None,
            height=40
        ))

        # Options
        options_layout = BoxLayout(orientation='vertical', spacing=5)

        # Option 1: Clear events only (preserve notes)
        events_btn = Button(
            text="Clear Events Only\n(Keep personal notes)",
            size_hint_y=None,
            height=60,
            background_color=(0.3, 0.6, 0.9, 1)
        )

        # Option 2: Clear everything
        all_btn = Button(
            text="Clear Everything\n(Events + Notes)",
            size_hint_y=None,
            height=60,
            background_color=(0.9, 0.3, 0.3, 1)
        )

        # Cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_y=None,
            height=40,
            background_color=(0.7, 0.7, 0.7, 1)
        )

        options_layout.add_widget(events_btn)
        options_layout.add_widget(all_btn)
        options_layout.add_widget(cancel_btn)
        content.add_widget(options_layout)

        popup = Popup(title="Clear Data Options", content=content, size_hint=(0.8, 0.6))

        # Bind buttons
        cancel_btn.bind(on_release=popup.dismiss)
        events_btn.bind(on_release=lambda x: self.confirm_clear_data(popup, include_notes=False))
        all_btn.bind(on_release=lambda x: self.confirm_clear_data(popup, include_notes=True))

        popup.open()

    def confirm_clear_data(self, options_popup, include_notes=False):
        # Close options popup
        options_popup.dismiss()

        # Show enhanced confirmation popup
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # Warning icon and title
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)

        # Warning icon (using emoji)
        warning_icon = Label(text="⚠️", font_size='24sp', size_hint_x=None, width=dp(40))

        # Warning title
        warning_title = Label(text="Clear Data", font_size='18sp', bold=True, color=(0.9, 0.3, 0.3, 1), halign='left')
        warning_title.bind(size=warning_title.setter('text_size'))

        title_layout.add_widget(warning_icon)
        title_layout.add_widget(warning_title)
        content.add_widget(title_layout)

        # Warning message
        if include_notes:
            warning_text = "Are you sure you want to clear ALL your data?\n(Events AND personal notes)\n\nThis action cannot be undone and all your information will be permanently lost."
            confirm_text = "Clear Everything"
        else:
            warning_text = "Are you sure you want to clear your events?\n(Personal notes will be preserved)\n\nThis action cannot be undone and all events will be permanently removed."
            confirm_text = "Clear Events"

        warning_message = Label(text=warning_text, font_size='14sp', halign='center', valign='middle', size_hint_y=None, height=dp(100), color=(0.3, 0.3, 0.3, 1))
        warning_message.bind(size=warning_message.setter('text_size'))
        content.add_widget(warning_message)

        # Buttons
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(15))

        cancel_btn = Button(text="Cancel", size_hint_x=0.5, background_normal='', background_color=(0.7, 0.7, 0.7, 1), color=(1, 1, 1, 1), font_size='16sp')

        confirm_btn = Button(text=confirm_text, size_hint_x=0.5, background_normal='', background_color=(0.9, 0.3, 0.3, 1), color=(1, 1, 1, 1), font_size='16sp', bold=True)

        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)

        popup = Popup(
            title="⚠️ Confirm Data Clearing",
            content=content,
            size_hint=(0.85, 0.6),
            auto_dismiss=False  # Prevent accidental dismissal
        )

        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda x: self.perform_clear_data(popup, include_notes))

        popup.open()
    
    def perform_clear_data(self, popup, include_notes=False):
        # Close the confirmation popup
        popup.dismiss()

        # Clear user's events from database
        if 'id' in user_data:
            self.db.delete_user_events(user_data['id'], include_notes=include_notes)

        # Show success message based on what was cleared
        if include_notes:
            message = 'All data has been cleared!\n(Events and notes removed)'
        else:
            message = 'Events have been cleared!\n(Personal notes preserved)'

        success_popup = Popup(
            title='Success',
            content=Label(text=message, text_size=(None, None), halign='center'),
            size_hint=(0.7, 0.4)
        )
        success_popup.open()

        # Auto-dismiss after 2 seconds
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: success_popup.dismiss(), 2.0)


class MainAppLayout(ScreenManager):
    def __init__(self, **kwargs):
        super(MainAppLayout, self).__init__(**kwargs)
        self.transition = FadeTransition()
        self.add_widget(LoginScreen(name='login'))
        self.add_widget(SignupScreen(name='signup'))
        self.add_widget(MainScreen(name='main'))
        self.add_widget(CalendarScreen(name='calendar'))
        self.add_widget(AddEventScreen(name='add_event'))
        self.add_widget(AddNoteScreen(name='add_note'))
        self.add_widget(ViewEventScreen(name='view_event'))
        self.add_widget(EditEventScreen(name='edit_event'))
        self.add_widget(EditNoteScreen(name='edit_note'))
        self.add_widget(InboxScreen(name='inbox'))
        self.add_widget(ProfileScreen(name='profile'))
        self.add_widget(AdminScreen(name='admin'))
        self.add_widget(SettingsScreen(name='settings'))


# Load KV file after widgets are registered
Builder.load_file('polycal_app.kv')


class PolyCalApp(App):
    def build(self):
        return MainAppLayout()


if __name__ == '__main__':
    PolyCalApp().run()

# Application Configuration

# Window settings
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 780
WINDOW_RESIZABLE = False

# Colors
COLORS = {
    'primary': (0.85, 0.15, 0.15, 1),  # Red
    'secondary': (0.12, 0.47, 0.95, 1),  # Blue
    'success': (0.2, 0.7, 0.2, 1),  # Green
    'warning': (1, 0.5, 0, 1),  # Orange
    'danger': (0.9, 0.3, 0.3, 1),  # Red
    'light_gray': (0.95, 0.95, 0.95, 1),
    'dark_gray': (0.3, 0.3, 0.3, 1),
    'background': (0.2, 0.2, 0.2, 1),
}

# Text limits
TEXT_LIMITS = {
    'event_title': 50,
    'event_description': 200,
    'note_title': 50,
    'note_content': 300,
    'bio': 120,
}

# Date settings
DATE_RANGE = {
    'min_year': 2020,
    'max_year': 2030,
}

# File paths
PATHS = {
    'default_profile': 'ICON/Default Profile.png',
    'database': 'polycal.db',
}

# UI Settings
UI_SETTINGS = {
    'popup_auto_dismiss_time': 1.5,
    'success_message_time': 2.0,
    'nav_bar_height': 60,
    'button_height': 50,
}

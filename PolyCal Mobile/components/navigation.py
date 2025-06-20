from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

def create_nav_bar(current_screen, user_data):
    """Create navigation bar with proper styling"""
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
        btn = Button(
            text=label,
            size_hint_x=1,
            background_normal='',
            background_color=(0.12, 0.47, 0.95, 1) if is_active else (0.85, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        btn.bind(on_release=lambda inst, t=target: setattr(App.get_running_app().root, 'current', t))
        nav_bar.add_widget(btn)
    return nav_bar

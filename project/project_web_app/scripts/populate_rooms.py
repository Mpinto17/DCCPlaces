import os
import sys

# Set up the project environment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Load Django configuration
import django
django.setup()

from project_web_app.models import Room

def populate_rooms():
    """
    Script to populate the database with rooms.
    """
    # List of room names
    room_names = [
        "Ada Lovelace", "Philippe Flajolet", "Grace Hopper", "Ramon Picarte", "Efrain Friedmann"
    ]

    # Create the rooms
    for i, name in enumerate(room_names, start=1):
        room_number = i  # Use index as room number
        room_name = name

        # Create or update the room
        room, created = Room.objects.get_or_create(
            room_number=room_number,
            defaults={'name': room_name}
        )

        if created:
            print(f"Room created: {room_number} - {room_name}")
        else:
            print(f"Room already exists: {room_number} - {room_name}")

if __name__ == "__main__":
    populate_rooms()

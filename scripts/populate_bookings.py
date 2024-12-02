import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware
from django.utils import timezone

# Set up the project environment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from project_web_app.models import Student, Room, Booking

def create_bookings_for_students():
    """
    Creates at least one booking for each student within the next 7 days.
    Bookings will be evenly distributed among available time slots and rooms.
    """
    students = Student.objects.all()
    rooms = list(Room.objects.all())  # Convert to a list to rotate between rooms

    if not rooms:
        print("No rooms available.")
        return

    if not students:
        print("No students available.")
        return

    # Define time slots
    TIME_SLOTS = [f'{h:02d}:{m:02d}' for h in range(8, 18) for m in [0, 30]]
    TIME_SLOTS.append('18:00')  # Add 6:00 PM as an option

    random.shuffle(TIME_SLOTS)  # Shuffle time slots for variety

    for student in students:
        success = False
        booking_date = now().date() + timedelta(days=random.randint(0, 6))
        random.shuffle(rooms)  # Randomize rooms for each student

        # Attempt to create a booking for the student
        for duration in [90, 75, 60, 45, 30, 15]:  # Try blocks of 2 hours, 1 hour, 30 minutes
            for room in rooms:
                for i in range(len(TIME_SLOTS) - 1):
                    start_time_str = TIME_SLOTS[i]
                    end_time_str = TIME_SLOTS[i + 1]

                    # Calculate the actual duration in minutes
                    start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = (datetime.combine(booking_date, start_time) + timedelta(minutes=duration)).time()

                    # Ensure the schedule does not exceed the last slot
                    if end_time_str < end_time.strftime('%H:%M'):
                        continue

                    # Create datetime objects with timezone
                    check_in = make_aware(datetime.combine(booking_date, start_time), timezone.get_current_timezone())
                    check_out = make_aware(datetime.combine(booking_date, end_time), timezone.get_current_timezone())

                    # Check for conflicts
                    existing_bookings = Booking.objects.filter(
                        room=room,
                        check_in__lt=check_out,
                        check_out__gt=check_in
                    )

                    if not existing_bookings.exists():
                        # Create the booking if no conflict exists
                        Booking.objects.create(
                            user=student,
                            room=room,
                            check_in=check_in,
                            check_out=check_out
                        )
                        print(f"Booking created: {student.email} - {room.name} - {booking_date} {start_time} to {end_time}")
                        success = True
                        break  # Exit loop if booking was created
                if success:
                    break  # Exit room loop if booking was created
            if success:
                break  # Exit duration loop if booking was created

        if not success:
            print(f"Could not schedule a booking for {student.email}.")

# Run the script
if __name__ == "__main__":
    create_bookings_for_students()

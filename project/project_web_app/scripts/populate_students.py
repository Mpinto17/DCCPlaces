import os
import sys
import random
from django.utils.crypto import get_random_string

# Set up the project environment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Load Django configuration
import django
django.setup()

from project_web_app.models import Student

# List of student names and surnames
students_list = [
    "Valentina Torres C.",
    "Sebastián Rojas M.",
    "Martín Pérez L.",
    "Camila Fuentes S.",
    "Catalina Reyes O.",
    "Matías Vargas A.",
    "Antonia Muñoz E.",
    "Francisco González",
    "Gabriela Morales ",
    "Nicolás Castro P.",
    "Isidora Romero Q.",
    "Javier Fernández H.",
    "Fernanda Soto Z.",
    "Tomás Navarro K.",
    "Emilia Araya J.",
    "Pedro Saavedra G.",
    "Francisca Espinoza B.",
    "Juan Pablo Valdés D.",
    "Ana María Contreras F.",
    "Ignacio Peña ",
    "María José Cifuentes Y.",
    "Agustín Ramírez N.",
    "Sofía Lagos",
    "Pablo Vega U.",
    "Daniela Medina W.",
    "Vicente Sepúlveda C."
]

# Function to generate fictitious emails
def generate_email(name, lastname1):
    username = f"{name.lower()}.{lastname1.lower()}"
    return f"{username}@mail.com"

# Function to generate fictitious phone numbers
def generate_phone():
    return f"+56 9 {random.randint(10000000, 99999999)}"

def populate_students():
    for full_name in students_list:
        # Split the name and surnames
        name_parts = full_name.split()
        name = name_parts[0]
        lastname1 = name_parts[1] if len(name_parts) > 1 else ""
        lastname2 = name_parts[2] if len(name_parts) > 2 else ""  # Assign None if no second surname

        # Generate student details
        email = generate_email(name, lastname1)
        phone = generate_phone()
        password = get_random_string(8)  # Generate a random password

        # Create the student
        student = Student.objects.create_user(
            email=email,
            password=password,
            name=name,
            lastname1=lastname1,
            lastname2=lastname2,
            phone=phone,
        )
        print(f"Student created: {student.email} - {student.name} {student.lastname1} {student.lastname2 or ''} - {student.phone}")

# Call the main function
if __name__ == "__main__":
    populate_students()

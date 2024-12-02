from django import forms
from .models import Booking, Student, Room
from datetime import date, datetime  
from django.db.models import Q
from django.utils.timezone import now

"""
    Tuples with hours and minutes, the left side of the tuple is the value stored, 
    and the right side is the one displayed to the user in the form, filled from 8:00 to 18:45
"""
TIME_SLOTS = [(f'{h:02d}:{m:02d}', f'{h:02d}:{m:02d}')
              for h in range(8, 18) for m in [0, 15, 30, 45]]
TIME_SLOTS.append(('18:00', '18:00')) 

class BookingForm(forms.ModelForm):
    """
    Form for room booking, selecting start and end time
    """
    start_time = forms.ChoiceField(
        choices=[('', '')] + TIME_SLOTS, 
        label="Hora de inicio",
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )
    end_time = forms.ChoiceField(
        choices=[('', '')] + TIME_SLOTS, 
        label="Hora de fin",
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),  
        label="Sala",
        empty_label="Selecciona una sala",  
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )

    class Meta:
        """
        Connects the form with the Booking model
        """
        model = Booking
        fields = ['room', 'start_time', 'end_time'] 
        labels = {
            'room': 'Sala',
            'start_time': 'Hora de inicio',
            'end_time': 'Hora de fin',
        }

    def clean(self):
        """
        Validation to ensure start time is before end time
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time:
            # Convert string to time objects
            start_time_obj = datetime.strptime(start_time, '%H:%M')
            end_time_obj = datetime.strptime(end_time, '%H:%M')
            if start_time_obj >= end_time_obj:
                self.add_error(None, "La hora de término debe ser posterior a la hora de inicio.")
        return cleaned_data
    

class SearchRoomForm(forms.Form):
    """
    Form for searching available rooms by date
    """ 
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center',
            'style': 'text-align: center;',
            'onclick': "this.showPicker()",
            'min': date.today().isoformat()
            }), label='Fecha'
    )

class ScheduleRoomForm(forms.Form):
    """
    Form for searching available rooms by date and time in the search-room-by-name page
    """
    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-200 text-gray-900 text-center rounded-lg py-2 px-2 border-none w-full',
            'onclick': "this.showPicker()",
            'min': date.today().isoformat()
        })
    )
    start_time = forms.ChoiceField(
        choices=[('', '')] + TIME_SLOTS, 
        label="Hora de inicio",
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )
    end_time = forms.ChoiceField(
        choices=[('', '')] + TIME_SLOTS,
        label="Hora de fin",
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )

    def clean(self):
        """
        Validation to ensure start time is before end time
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        actual_time = datetime.now().time()
        selected_date = cleaned_data.get("date")
        if selected_date and selected_date < date.today():
            self.add_error("date", "No puedes seleccionar una fecha anterior a la fecha actual.")
        if selected_date and selected_date == date.today():
            if start_time and start_time < actual_time.strftime('%H:%M'):
                self.add_error("start_time", "La hora de inicio no puede ser anterior a la hora actual.")
        if start_time and end_time:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            if start_time_obj >= end_time_obj:
                self.add_error("end_time", "La hora de término debe ser posterior a la hora de inicio.")
        if not selected_date:
            self.add_error("date", "Debes seleccionar una fecha antes de elegir horarios.")
        elif not start_time or not end_time:
            self.add_error(None, "Debes seleccionar tanto el horario de inicio como el de fin.")

        return cleaned_data

class SignupForm(forms.ModelForm):
    """
    Form for creating a new student
    """
    class Meta:
        model = Student
        fields = ['name', 'email', 'lastname1', 'lastname2', 'phone', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        
class SearchRoomForm(forms.Form):
    """
    Form for searching available rooms by date
    """
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center',
            'style': 'text-align: center;',
            'onclick': "this.showPicker()",
            'min': date.today().isoformat()
        }),
        label='Fecha'
    )


class ScheduleRoomForm(forms.Form):
    """
    Form for searching available rooms by date and time in the search-room-by-name page
    """
    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'bg-gray-200 text-gray-900 text-center rounded-lg py-2 px-2 border-none w-full',
            'onclick': "this.showPicker()",
            'min': date.today().isoformat()
        })
    )
    start_time = forms.ChoiceField(
        choices=[('', '')] + TIME_SLOTS,
        label="Hora de inicio",
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )
    end_time = forms.ChoiceField(
        choices=[('', '')] + TIME_SLOTS,
        label="Hora de fin",
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 text-gray-900 text-sm rounded-lg border-none pl-3 pr-10 py-2 w-full text-center'
        })
    )

    def clean(self):
        """
        Validation to ensure start time is before end time
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        actual_time = datetime.now().time()
        selected_date = cleaned_data.get("date")

        if selected_date and selected_date < date.today():
            self.add_error("date", "No puedes seleccionar una fecha anterior a la fecha actual.")

        if selected_date and selected_date == date.today():
            if start_time and start_time < actual_time.strftime('%H:%M'):
                self.add_error("start_time", "La hora de inicio no puede ser anterior a la hora actual.")

        if start_time and end_time:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            if start_time_obj >= end_time_obj:
                self.add_error("end_time", "La hora de término debe ser posterior a la hora de inicio.")

        if not selected_date:
            self.add_error("date", "Debes seleccionar una fecha antes de elegir horarios.")
        elif not start_time or not end_time:
            self.add_error(None, "Debes seleccionar tanto el horario de inicio como el de fin.")

        return cleaned_data

class SearchRoomNameForm(forms.Form):
    """
    Form for searching available rooms by date
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        label="Buscar sala",
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-200 text-gray-900 text-m rounded-lg border-none w-full text-center h-10 px-4',
            'placeholder': 'Ejemplo: "Grace" encontrará a la sala Grace Hopper 303'
        })
    )

class RoomForm(forms.ModelForm):
    """
    Form for creating or editing rooms.

    This form is used to add or update room details, such as the room number
    and the room name. It is based on the `Room` model.
    """
    class Meta:
        model = Room  # The model associated with this form
        fields = ['room_number', 'name']  # Fields to include in the form
        labels = {
            'room_number': 'Número',  
            'name': 'Nombre'  
        }


class RoomFormDesing(forms.ModelForm):
    """
    Form for managing room creation or editing.

    This form is used by staff to create or edit rooms, 
    providing an intuitive user interface with styled inputs.
    """
    class Meta:
        model = Room 
        fields = ['room_number', 'name']  
        labels = {
            'room_number': 'Número',  
            'name': 'Nombre' 
        }
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'bg-gray-200 rounded-lg px-4 py-2 text-center w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número de sala', 
            }),
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-200 rounded-lg px-4 py-2 text-center w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre de sala', 
            })
        }

class EditBookingForm(forms.ModelForm):
    """
    Form for editing existing bookings.

    This form allows administrators or staff to update an existing booking's
    details, including date, start and end time, and room selection.
    """
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': now().strftime('%Y-%m-%d'),  # Prevent selecting past dates
                'class': 'bg-gray-200 rounded-lg px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-center',
            },
            format='%Y-%m-%d'  # Date format to be used
        ),
        label="Fecha"
    )

    start_time = forms.ChoiceField(
        choices=TIME_SLOTS,  # Predefined time slots for start time
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 rounded-lg px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-center',
        }),
        label="Hora de inicio"
    )

    end_time = forms.ChoiceField(
        choices=TIME_SLOTS,  # Predefined time slots for end time
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 rounded-lg px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-center',
        }),
        label="Hora de fin"
    )

    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),  # Fetch all rooms from the database
        widget=forms.Select(attrs={
            'class': 'bg-gray-200 rounded-lg px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-center',
        }),
        label="Sala",
        empty_label="Selecciona una sala",  # Placeholder for room selection
    )

    class Meta:
        model = Booking  # The model associated with this form
        fields = ['room']  # Only the room field is explicitly required

    def clean(self):
        """
        Custom validation for the form.

        Ensures that the booking:
        - Has a valid date range (start time is before end time).
        - Does not overlap with existing bookings for the same room.
        """
        cleaned_data = super().clean()
        selected_date = cleaned_data.get('date')
        selected_start_time = cleaned_data.get('start_time')
        selected_end_time = cleaned_data.get('end_time')
        selected_room = cleaned_data.get('room')

        if selected_date and selected_start_time and selected_end_time:
            # Convert times to datetime objects for comparison
            start_datetime = datetime.combine(
                selected_date, datetime.strptime(selected_start_time, '%H:%M').time()
            )
            end_datetime = datetime.combine(
                selected_date, datetime.strptime(selected_end_time, '%H:%M').time()
            )

            # Validate that end time is after start time
            if end_datetime <= start_datetime:
                raise forms.ValidationError('La hora de término debe ser posterior a la hora de inicio.')

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=selected_room,
                check_in__lt=end_datetime,  # Existing bookings that end after the start time
                check_out__gt=start_datetime  # Existing bookings that start before the end time
            ).exclude(id=self.instance.id if self.instance else None)  # Exclude the current booking being edited

            if overlapping_bookings.exists():
                raise forms.ValidationError('La sala ya está reservada para este horario.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with pre-filled values for an existing booking instance.

        If an instance of the `Booking` model is provided, it sets initial values
        for the date, start time, end time, and room fields.
        """
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance:
            self.fields['date'].initial = instance.check_in.strftime('%Y-%m-%d')  # Pre-fill date
            self.fields['start_time'].initial = instance.check_in.strftime('%H:%M')  # Pre-fill start time
            self.fields['end_time'].initial = instance.check_out.strftime('%H:%M')  # Pre-fill end time
            self.fields['room'].initial = instance.room  # Pre-fill room

"""
    Form for updating user information on profile
"""
class EditProfile(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "lastname1", "email", "phone"]


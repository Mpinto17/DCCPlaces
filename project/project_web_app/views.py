from django.shortcuts import render, redirect, get_object_or_404
from project_web_app.models import Student, Booking, Room
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import SignupForm, SearchRoomForm, BookingForm, RoomForm, EditBookingForm, RoomFormDesing, EditProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Room
from datetime import timedelta
from django.utils import timezone
from .forms import SearchRoomNameForm, ScheduleRoomForm
from datetime import datetime, timedelta
from .models import Room, Booking

def login(request):
    """
    Login method for processing email and password to log in the user.

    GET: Render login.html
    POST: Try to log in the user

    Args:
        request (HttpRequest): The request.

    Returns:
        HttpResponse: The response.
        Login page if the log in fails
        Profile page if the log in is successful
    """
    # If the page is loading, render login.html
    if request.method == 'GET':
        return render(request, 'project_web_app/login.html')
    # Elif the form is submitted, try to log in the user
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = Student.objects.filter(email=email).first()
        # If the user is not found, return an error message
        if user is None:
            messages.error(request, 'Usuario no encontrado. Si aún no crea una cuenta, regístrese.')
            return render(request, 'project_web_app/login.html', {'error_message': 'Usuario no encontrado.'})
        # If the password matches then log in the user redirecting to profile
        if user.check_password(password):
            auth_login(request, user)
            messages.success(request, 'Has iniciado sesión correctamente.')
            return redirect('profile')
        # If the password does not match, return an error message
        else:
            messages.error(request, 'Contraseña incorrecta.')
            return render(request, 'project_web_app/login.html', {'error_message': 'Contraseña incorrecta.'})
    return render(request, 'project_web_app/login.html')

def signup(request):
    """
    Signup method for creating a new user.

    GET: Render signup.html
    POST: Create a new user and inserts into the database

    Args:
        request (HttpRequest): The request.

    Returns:
        HttpResponse: The response.
        Signup page if the user is not created
        Profile page if the user is sucessfully created
    """
    # If the page is loading, render signup.html
    if request.method == 'GET':
        return render(request, "project_web_app/signup.html")
    # Elif the form is submitted, create a new user
    elif request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)
            messages.success(request, 'Usuario creado')
            return redirect('profile')
        else:
            pass
    return render(request, "project_web_app/signup.html", {'form': form})

@login_required
def logout(request):
    """
    Logout page for logging out the user.

    Args:
        request (HttpRequest): The request.

    Returns:
        HttpResponse: The response.
        Redirect to the login page
    """
    # If the user is logged in, log out and redirect to the login page
    if request.method == 'GET' or 'POST':
        auth_logout(request)
        return redirect('login')


@login_required
def profile(request):
    """
    Profile page for the user.

    Args: 
        request (HttpRequest): The request

    Returns:
        HttpResponse: The response
        Profile page with the user's information (Name, Email, phone)
        Plus the users can see all theirs active reservations
        Plus the users can see how many hours he has available to make reservations
    """
    # Constants to calculate the logic of the available hours
    user = request.user
    now = timezone.now()
    active_reservations = Booking.objects.filter(user=user, check_out__gte=now).order_by('check_in')
    start_of_week, end_of_week = get_week_start_end()
    bookings = Booking.objects.filter(user=user).filter(check_in__gte=start_of_week).filter(check_out__lte=end_of_week)
    available_hours = user.available_hours
    
    for booking in bookings:
        # Calculate the duration of the booking
        duration = booking.check_out - booking.check_in
    
        # Calculate the number of hours in the duration
        hours = duration.total_seconds() / 3600
        available_hours -= hours
  
    # Form to update user information
    if request.method == "POST" :
        form = EditProfile(request.POST, instance=user)

        # To deal with uncomplete form submissions
        d = {"name": user.name, "lastname1": user.lastname1, "email" : user.email, "phone": user.phone}

        for field in form.fields:
            form.fields[field].required = False

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                if value in [None, '', []]: 
                    setattr(form.instance, field, d[field])

            form.save()
            return redirect("profile")
        
        else:
            pass


    # Render the profile page with the user information, the active reservations and the available hours left for the week
    return render(request, 'project_web_app/profile.html', {
        'user': user,
        'active_reservations': active_reservations,
        'available_hours': available_hours,
    })
    
    

    
    


def get_week_start_end():
    """Returns the start of the week (monday) and the end of the week (saturday)."""
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

@login_required
def search_room_by_name(request):
    """
    Search for a room and allow booking for specific time slots only in the current week.

    Args:
        request (HttpRequest): The request.

    Returns
        HttpResponse: The response.
        Search-room-by-name page with the search form and the schedule form.
        In any other case shows the errors in the form.
    """
    form_search = SearchRoomNameForm(request.GET or None)
    form_schedule = None 
    room = None
    availability = []

    start_of_week, end_of_week = get_week_start_end()
    start_of_week = start_of_week.date()
    end_of_week = end_of_week.date()
    today = timezone.now().date()  

    # Search Query
    if form_search.is_valid():
        query = form_search.cleaned_data.get('query')
        room = Room.objects.filter(name__icontains=query).first()

        if room:
            current_date = today
            while current_date <= end_of_week:
                available_slots = calculate_daily_availability(room, current_date)
                availability.append({
                    'date': current_date,
                    'slots': available_slots
                })
                current_date += timedelta(days=1)
            form_schedule = ScheduleRoomForm(request.POST or None)
            
    # If the request is POST, validate and create the reservation
    if request.method == 'POST' and form_schedule and form_schedule.is_valid():
        user = request.user
        available_hours = request.user.available_hours
        bookings = Booking.objects.filter(user=user).filter(check_in__gte=start_of_week).filter(check_out__lte=end_of_week)
        for booking in bookings:
            # Calculate the duration of the booking
            duration = booking.check_out - booking.check_in
        
            # Calculate the number of hours in the duration
            hours = duration.total_seconds() / 3600
            available_hours -= hours

        selected_date = form_schedule.cleaned_data['date']
        selected_start_time = form_schedule.cleaned_data['start_time']
        selected_end_time = form_schedule.cleaned_data['end_time']
        start_time = datetime.strptime(selected_start_time, '%H:%M').time()
        end_time = datetime.strptime(selected_end_time, '%H:%M').time()
        check_in = timezone.make_aware(datetime.combine(selected_date, start_time),timezone=timezone.get_current_timezone())
        check_out = timezone.make_aware(datetime.combine(selected_date, end_time),timezone=timezone.get_current_timezone())

        # Check if the user has enough hours to reservate the room 
        if (((check_out - check_in).total_seconds()) / 3600) > available_hours:
            form_schedule.add_error(None, "No tienes suficientes horas disponibles para reservar este horario.")
        else :
            # Check for overlaps
            overlapping_bookings = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in)
            today = timezone.now().date()
            if selected_date < today:
                form_schedule.add_error(None, "No puedes reservar para fechas anteriores a la fecha actual.")
            elif selected_date > end_of_week:
                form_schedule.add_error(None, "Solo puedes reservar para esta semana.")
            elif overlapping_bookings.exists():
                form_schedule.add_error(None, "La sala ya está reservada en ese horario.")
            else:
                # If everything is ok, create the booking
                Booking.objects.create(
                    user=request.user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out
                )
                messages.success(request, 'Reserva creada exitosamente. Usadas ' + str(((check_out - check_in).total_seconds()) / 3600) + ' horas. Te quedan ' + str(available_hours - ((check_out - check_in).total_seconds()) / 3600) + ' horas disponibles.')
                return redirect('search_room_by_name') 

    return render(
        request,
        'project_web_app/search-room-by-name.html',
        {'form_search': form_search,'form_schedule': form_schedule,'room': room,'availability': availability})

def calculate_daily_availability(room, date):
    """
    Auxiliary Function
    Calculate available time slots for a specific room and date.

    Args: 
        room (Room): The room object.
        date (datetime.date): The date with date format.
    
    Returns:
        List: List of dictionaries with the available time slots.
    """
    start_time = timezone.make_aware(datetime.combine(date, datetime.min.time()) + timedelta(hours=8),timezone=timezone.get_current_timezone())
    end_time = timezone.make_aware(datetime.combine(date, datetime.min.time()) + timedelta(hours=18),timezone=timezone.get_current_timezone())
    available_slots = [(start_time, end_time)]
    bookings = Booking.objects.filter(room=room, check_in__date=date)

    for booking in bookings:
        new_available_slots = []
        for slot_start, slot_end in available_slots:
            booking_start = booking.check_in.astimezone(timezone.get_current_timezone())
            booking_end = booking.check_out.astimezone(timezone.get_current_timezone())
            if booking_end <= slot_start or booking_start >= slot_end:
                new_available_slots.append((slot_start, slot_end))
            else:
                if slot_start < booking_start:
                    new_available_slots.append((slot_start, booking_start))
                if slot_end > booking_end:
                    new_available_slots.append((booking_end, slot_end))
        available_slots = new_available_slots

    return [{'start_time': slot_start.time(), 'end_time': slot_end.time()}for slot_start, slot_end in available_slots]

@login_required
def search_and_book_room_by_date(request):
    """
    Search and book room by date, now considering hours available for the user.

    GET: Render search-by-date.html with available rooms.
    POST: Create a new booking if no overlapping bookings are found and user has enough hours.

    Args:
        request (HttpRequest): The request.

    Returns:
        HttpResponse: The response.
        Search-by-date page with available rooms and error messages if any.
    """
    # Initialize the search form and booking form
    form_search = SearchRoomForm(request.GET or None)
    form_booking = BookingForm(request.POST or None)
    available_rooms = {}
    error_message = ""

    # Calculate the user's available hours before proceeding
    user = request.user
    available_hours = user.available_hours

    start_of_week, end_of_week = get_week_start_end()
    bookings = Booking.objects.filter(user=user, check_in__gte=start_of_week, check_out__lte=end_of_week)
    for booking in bookings:
        # Calculate the duration of the booking
        duration = booking.check_out - booking.check_in
        hours = duration.total_seconds() / 3600
        available_hours -= hours

    # If the search form is valid, retrieve the selected date and search for available rooms
    if form_search.is_valid():
        selected_date = form_search.cleaned_data['date']
        if selected_date > end_of_week.date():
            error_message = "No puedes reservar para fechas posteriores al fin de la semana actual (domingo)."
        else:
            start_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=8)
            end_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=18)
            rooms = Room.objects.all()

            # Iterate over each room and check for existing bookings
            for room in rooms:
                bookings = Booking.objects.filter(
                    room=room,
                    check_in__date=selected_date
                ).order_by('check_in')

                current_time = start_time
                block_start = current_time
                room_slots = []

                # Process existing bookings to find available time blocks
                for booking in bookings:
                    if booking.check_in.replace(tzinfo=None) > current_time.replace(tzinfo=None):
                        block_end = booking.check_in
                        room_slots.append({
                            'start_time': block_start.time(),
                            'end_time': block_end.time()
                        })
                    current_time = booking.check_out
                    block_start = current_time

                # If there's remaining time after the last booking, add the available block
                if current_time.replace(tzinfo=None) < end_time.replace(tzinfo=None):
                    room_slots.append({
                        'start_time': current_time.time(),
                        'end_time': end_time.time()
                    })

                # Add the available slots for the current room to the dictionary
                if room_slots:
                    available_rooms[room.name] = room_slots

    # If the booking form is valid, attempt to create a new booking
    if request.method == 'POST' and form_booking.is_valid():
        user = request.user
        selected_start_time = form_booking.cleaned_data['start_time']
        selected_end_time = form_booking.cleaned_data['end_time']
        check_in = datetime.combine(selected_date, datetime.strptime(selected_start_time, '%H:%M').time())
        check_out = datetime.combine(selected_date, datetime.strptime(selected_end_time, '%H:%M').time())

        # Calculate the duration of the requested booking
        requested_hours = (check_out - check_in).total_seconds() / 3600

        # Check if the selected date is within the current week
        if selected_date > end_of_week.date():
            error_message = "No puedes reservar para fechas posteriores al fin de la semana actual (domingo)."
        # Check if the user has enough hours to reserve the room
        elif requested_hours > available_hours:
            error_message = "No tienes suficientes horas disponibles para reservar este horario."
        else:
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=form_booking.cleaned_data['room'],
                check_in__lt=check_out,
                check_out__gt=check_in
            )

            # If no overlaps are found, save the booking
            if not overlapping_bookings.exists():
                booking = form_booking.save(commit=False)
                booking.user = user
                booking.check_in = check_in
                booking.check_out = check_out
                booking.save()

                # Update available hours after booking is made
                available_hours -= requested_hours
                messages.success(request, f'Reserva creada exitosamente. Usadas {requested_hours} horas. Te quedan {available_hours} horas disponibles.')
                return redirect('profile')
            else:
                error_message = 'La sala ya está reservada para ese horario.'

    # Render the page with forms and available rooms
    return render(request, 'project_web_app/search-by-date.html', {
        'form_search': form_search,
        'form_booking': form_booking,
        'available_rooms': available_rooms,
        'error_message': error_message
    })

@login_required
def delete_reservation(request, id):
    """
    URL for deleting a reservation (booking that a user has).

    POST: 
        Receives the booking id and deletes the booking from the database.
        Redirects to the profile page. The booking will not be shown anymore.

    Args: 
        Request (HttpRequest): The request.
        id: Booking id.
    
    Returns:
        Redirect to the profile page.
    """
    if request.method == 'POST':
        booking = Booking.objects.get(id=id)
        # Only the user logged in can delete their own bookings
        if booking.user == request.user:
            booking.delete()
            messages.success(request, 'La reserva se ha eliminado correctamente.')
            return redirect('profile')
        else:
            messages.error(request, 'No tienes permiso para eliminar esta reserva.')
            return redirect('profile')
    else:
        return redirect('profile')

#staff_member_required = user_passes_test(lambda u: u.is_staff)

@login_required
def room_list(request):
    """
    View to list all rooms available in the system. 

    GET: 
        Retrieves all rooms and renders a template to display them.
        Only staff users are allowed to access this view.

    Args:
        request (HttpRequest): The request.

    Returns:
        HttpResponse: Renders the 'staff-room-list' template with all rooms.
    """
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('profile')

    # Retrieve all rooms from the database
    rooms = Room.objects.all()

    return render(request, 'project_web_app/staff-room-list.html', {'rooms': rooms})

def staff_add_room(request):
    """
    View to add a new room to the system.

    GET:
        Renders a form to add a new room.
    POST:
        Processes the submitted form and saves the new room to the database.

    Args:
        request (HttpRequest): The request.

    Returns:
        HttpResponse: Renders the 'staff-add-room' template with the form.
        Redirects to 'room_list' upon successful addition of the room.
    """
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('profile')

    if request.method == 'POST':
        # Process the submitted form
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La sala se añadió exitosamente.')
            return redirect('room_list')
    else:
        # Render an empty form for adding a new room
        form = RoomForm()

    return render(request, 'project_web_app/staff-add-room.html', {'form': form})

@login_required
def staff_edit_room(request, room_id):
    """
    View to edit or delete an existing room.

    GET:
        Retrieves the room data and renders a form to edit it.
    POST:
        - Updates the room details if 'save' is submitted.
        - Deletes the room if 'delete' is submitted.

    Args:
        request (HttpRequest): The request.
        room_id (int): The ID of the room to edit or delete.

    Returns:
        HttpResponse: Renders the 'staff-edit-room' template with the form.
        Redirects to 'room_list' upon successful edit or deletion.
    """
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('profile')

    # Retrieve the room or return 404 if it doesn't exist
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete the room if 'delete' button is pressed
            room.delete()
            messages.success(request, 'La sala ha sido eliminada exitosamente.')
            return redirect('room_list')
        
        # Process the form to edit the room
        form = RoomFormDesing(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'La sala ha sido editada exitosamente.')
            return redirect('room_list')
    else:
        # Render the form with the current room data
        form = RoomFormDesing(instance=room)

    return render(request, 'project_web_app/staff-edit-room.html', {'form': form, 'room': room})

def staff_view_reservations(request):
    """
        View for staff members to see room reservations.

        Parameters:
            request: HttpRequest object containing data about the current web request,
                     including the authenticated user and GET parameters.

        Functionality:
        - Checks if the user is a staff member (`is_staff`). If not, an error message is displayed,
          and the user is redirected to the profile view.
        - Processes a search form (`SearchRoomNameForm`) based on the room name.
        - If a GET request is received and the form is valid:
            - Gets the current date (`today`) and calculates a range for the next seven days.
            - Filters the `Booking` model for reservations where:
                - The room name contains the search term,
                - Check-in and check-out dates fall within the defined range.
            - Renders the `staff-view-reservations.html` template with the search results.
        - If the form is invalid or no search is performed, it renders the template with an empty form.

        Returns:
            An HTTP response rendering the `staff-view-reservations.html` template with:
            - `form_search`: the search form.
            - `booked_rooms` (optional): a list of filtered reservations, only if the search is valid.

        Notes:
        - Currently, the search functionality is limited to reservations within the next seven days.
          This could be improved by allowing users to select specific dates or broader time ranges.
        - Ensure the `Booking` model and `SearchRoomNameForm` are properly defined and available.
        """
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('profile')

    form_search = SearchRoomNameForm(request.GET or None)

    # If the search form is valid
    if request.method == 'GET' and form_search.is_valid():
        today = timezone.now().date()
        # Improvement option: put an option to see bookings on specific
        # dates or time frame instead of only the next seven days
        seven_days = today + timedelta(days=7)
        query = form_search.cleaned_data.get('query')
        bookings_list = Booking.objects.filter(room__name__icontains=query,
                                               check_in__gte=today,
                                               check_out__lte=seven_days).order_by('check_in',
                                                                                   'check_out',
                                                                                   'room__name')

        return render(request, 'project_web_app/staff-view-reservations.html',
                      {'form_search': form_search,
                       'booked_rooms': bookings_list})

    return render(request, 'project_web_app/staff-view-reservations.html',
                      {'form_search': form_search})


@login_required
def staff_edit_booking(request, booking_id):
    """
    View for staff members to edit or delete an existing booking.

    GET:
        Retrieves the booking data and renders a form to edit it.
    POST:
        - Updates the booking details if 'save' is submitted.
        - Deletes the booking if 'delete' is submitted.

    Args:
        request (HttpRequest): The request.
        booking_id (int): The ID of the booking to edit or delete.

    Returns:
        HttpResponse: Renders the 'staff-edit-booking' template with the form.
        Redirects to 'staff_view_reservations' upon successful edit or deletion.
    """
    # Retrieve the booking or return 404 if it doesn't exist

    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('profile')

    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete the booking if 'delete' button is pressed
            booking.delete()
            messages.success(request, 'La reserva ha sido eliminada correctamente.')
            return redirect('staff_view_reservations')

        # Process the form to edit the booking
        form = EditBookingForm(request.POST, instance=booking)
        if form.is_valid():
            # Extract cleaned data from the form
            selected_date = form.cleaned_data['date']
            selected_start_time = form.cleaned_data['start_time']
            selected_end_time = form.cleaned_data['end_time']
            selected_room = form.cleaned_data['room']

            # Combine the selected date and time into aware datetime objects
            check_in = timezone.make_aware(
                datetime.combine(selected_date, datetime.strptime(selected_start_time, '%H:%M').time())
            )
            check_out = timezone.make_aware(
                datetime.combine(selected_date, datetime.strptime(selected_end_time, '%H:%M').time())
            )

            # Check for overlapping bookings in the same room, excluding the current booking
            overlapping_bookings = Booking.objects.filter(
                room=selected_room,
                check_in__lt=check_out,  # Check-in time is before the new check-out time
                check_out__gt=check_in  # Check-out time is after the new check-in time
            ).exclude(id=booking.id)

            if not overlapping_bookings.exists():
                # Update the booking details if no conflicts exist
                booking.check_in = check_in
                booking.check_out = check_out
                booking.room = selected_room
                booking.save()
                messages.success(request, 'La reserva ha sido modificada correctamente.')
                return redirect('staff_view_reservations')
            else:
                # If there's a conflict, notify the user
                messages.error(request, 'La sala ya está reservada para ese horario.')
        else:
            # Notify the user if the form has errors
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # Render the form pre-filled with the current booking details
        form = EditBookingForm(instance=booking)

    return render(request, 'project_web_app/staff-edit-booking.html', {
        'form': form,
        'booking': booking
    })

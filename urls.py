from django.urls import path
from project_web_app import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('profile', views.profile, name='profile'),
    path('logout', views.logout, name='logout'),
    path('search-room-by-name', views.search_room_by_name, name='search_room_by_name'),
    path('search-room-by-date', views.search_and_book_room_by_date, name='search_by_date'),
    path('rooms', views.room_list, name='room_list'),
    path('staff-add-room', views.staff_add_room, name='staff_add_room'),
    path('staff-edit-room/<int:room_id>', views.staff_edit_room, name='staff_edit_room'),
    path('staff-view-reservations', views.staff_view_reservations, name='staff_view_reservations'),
    path('delete-reservation/<int:id>', views.delete_reservation, name='delete_reservation'),
    path('staff-edit-booking/<int:booking_id>/', views.staff_edit_booking, name='staff_edit_booking'),
]

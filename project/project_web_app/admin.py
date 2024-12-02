from django.contrib import admin
from .models import Student, Room, Booking

admin.site.site_header = "DCCPlaces - Panel de Administración"
admin.site.site_title = "DCCPlaces"
admin.site.index_title = "Panel de Administración"

admin.site.register(Student)
admin.site.register(Room)
admin.site.register(Booking)

from django.contrib import admin

from .models import Competence, Trajectory, User
# Register your models here.

admin.site.register(Competence)
admin.site.register(Trajectory)
admin.site.register(User)

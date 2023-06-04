from django.contrib import admin
from .models import *

admin.site.register(Classroom)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Announcement)
admin.site.register(Attendance)

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User

from .models import Contact, CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email','is_student', 'is_teacher')
    list_filter = ('email','is_student', 'is_teacher')

    fieldsets = (
    (None, {'fields' : ('first_name','last_name' ,'email','password','profile_img','mobile','is_student', 'is_teacher')}),
    ('Permissions', {'fields' : ('is_staff', 'is_active')})
    )

    add_fieldsets =  (
    (None, {'classes' : ('wide',),
            'fields' : ('first_name','last_name' ,'email','mobile', 'password1', 'password2','is_staff', 'is_active','is_student', 'is_teacher')
    }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.unregister(Group)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Contact)


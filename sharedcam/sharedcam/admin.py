from django.contrib import admin
from .models import *


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(HashPhoto)
class HashPhotoAdmin(admin.ModelAdmin):
    ordering = ('-date_uploaded',)

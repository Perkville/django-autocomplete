from django.contrib import admin
from django.contrib.auth.models import Message
from ac_example import forms

class MessageAdmin(admin.ModelAdmin):
    form = forms.InsertMessage
    fields = ('user', 'message')

admin.site.register(Message, MessageAdmin)

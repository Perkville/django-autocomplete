from django.contrib import admin
from django.contrib.auth.models import Message
from actest.acapp import forms

class MessageAdmin(admin.ModelAdmin):
    form = forms.InsertMessage
    fields = ('user', 'message')

admin.site.register(Message, MessageAdmin)

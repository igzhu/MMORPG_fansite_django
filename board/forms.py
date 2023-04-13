from django.forms import ModelForm
from .models import Message


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['messageTitle', 'messageText', 'messageImage', 'messageVideo', 'messageCategory']
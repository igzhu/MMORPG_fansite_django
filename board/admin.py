from django.contrib import admin
from .models import Message, Post



class PostAdmin(admin.ModelAdmin):
    list_display = ('postAuthor', 'postToMessage', 'postText', 'postAccepted', 'postDateTime')
    list_filter = ('postAuthor', 'postToMessage', 'postText', 'postAccepted', 'postDateTime')
    # search_fields = ["postAuthor__authorName__username", 'postType', 'category__name', 'head', 'postRate']  # advanced filters
    search_fields = ('postAuthor', 'postToMessage__author__username', 'postText', 'postAccepted', 'postDateTime')  # advanced filters

class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'messageDateTime', 'messageTitle', 'messageCategory')
    list_filter = ('author', 'messageDateTime', 'messageTitle', 'messageCategory')  # simple filters
    search_fields = ('name', "subscribers__username")  # advanced filters


admin.site.register(Post, PostAdmin)
admin.site.register(Message, MessageAdmin)



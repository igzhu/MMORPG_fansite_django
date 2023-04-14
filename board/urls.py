from django.urls import path
from .views import MessageList,MessageEdit, MessageDetails, MessageAdd,MessageDelete, PostList, PostDetails, PostDelete, approve_post, respond_to_message
# from .views import upgrade_me_to_author, subscribe_to_category

#app_name = 'news'

urlpatterns = [
    path('', MessageList.as_view(),  name='messages'),
    path('<int:pk>/', MessageDetails.as_view(), name='message_details'),
    path('add/', MessageAdd.as_view(), name='message_add'),
    path('<int:pk>/delete/', MessageDelete.as_view(), name='message_delete'),
    path('<int:pk>/edit/', MessageEdit.as_view(), name='message_edit'),
    path('posts/', PostList.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetails.as_view(), name='post_details'),
    path('posts/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('posts/<int:pk>/approve/', approve_post, name='post_approve'),
    path('<int:pk>/respond/', respond_to_message, name='respond'),
]

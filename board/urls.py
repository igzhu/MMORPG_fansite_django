from django.urls import path
from .views import MessageList, MessageDetails, MessageAdd, PostAdd, ResponcesList
# from .views import upgrade_me_to_author, subscribe_to_category

#app_name = 'news'

urlpatterns = [
    path('', MessageList.as_view()),
    path('<int:pk>/', MessageDetails.as_view(), name='message_details'),
    path('add/', MessageAdd.as_view(), name='message_add'),
    path('<int:pk>/delete/', MessageDelete.as_view(), name='message_delete'),
    path('<int:pk>/edit/', MessageEdit.as_view(), name='message_edit'),
    path('posts/', PostList.as_view(), name='post_list'),
    path('posts/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('posts/<int:pk>/approve/', PostApprove.as_view(), name='post_approve'),
    #path('upgrade/', upgrade_me_to_author, name='upgrade'),
    #path('category/<int:pk>/subscribe/', subscribe_to_category, name='subscribe'),
    #path('category/<int:pk>/', PostCategoryView.as_view(), name='category'),
]
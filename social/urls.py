from django.urls import path, include

from social import views, viewsets, api

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('profiles', viewsets.ProfileViewSet)

app_name = 'social'

urlpatterns = [
    # messages page
    path('', views.messages_vue, name='messages'),
    # signup page
    path('signup/', views.signup, name='signup'),
    # login page
    path('login/', views.login, name='login'),
    # logout page
    path('logout/', views.logout, name='logout'),
    # changed to documents page
    path('documents/', views.documents, name='documents'),
    # changed to editor page
    path('editor/', views.editor, name='editor'),
    # user profile edit page
    path('profile/', views.profile, name='profile'),

    # Ajax: upload new profile image
    path('uploadimage/', views.upload_image, name='uploadimage'),

    # Ajax: post a new message
    path('api/messages/', api.messages_api, name='messages api'),
    # Ajax: delete a message
    path('api/messages/<int:message_id>/', api.message_api, name='message api'),

    # Django-REST-API
    path('rest-api/', include(router.urls)),
    
    # Legal Dictionary
    path('Dictionary/', views.legal_dictionary, name="legal-dict"),
]

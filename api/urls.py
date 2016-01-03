__author__ = 'austin'

from django.conf.urls import url, include
from rest_framework.authtoken import views as auth_views
import views



urlpatterns = [
    #url(r'^login/', auth_views.obtain_auth_token),
    #url(r'^users/', views.UserList.as_view(), name="user-list"),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^persons/(?P<pk>[0-9]+)/suggestions/', views.SuggestionList.as_view(), name="suggestion-list"),
    url(r'^persons/(?P<pk>[0-9]+)/likes/', views.LikeList.as_view(), name="like-list"),
    url(r'^persons/(?P<pk>[0-9]+)/skips/', views.SkipCreateView.as_view(), name="skip-create"),
    url(r'^persons/(?P<pk>[0-9]+)/shares/', views.SharePersonListView.as_view(), name="share-create"),
    url(r'^persons/(?P<pk>[0-9]+)/', views.PersonDetailView.as_view(), name="person-detail"),
    url(r'^persons/', views.PersonList.as_view(), name="person-list"),
    url(r'^shares/(?P<pk>[0-9]+)/', views.ShareDeleteView.as_view(), name="share-delete"),
    url(r'^users/current/shares/', views.ShareUserListView.as_view(), name="share-list"),
    url(r'^users/current/', views.CurrentUserDetailView.as_view(), name="user-detail"),
    url(r'^users/', views.UserList.as_view(), name="user-list"),



]
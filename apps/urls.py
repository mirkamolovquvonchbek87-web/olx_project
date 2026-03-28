from django.urls import path

from apps.views import AnnouncementListView, MainView, CustomLoginView, GoogleLoginView, GoogleCallbackView, \
    RegisterCreateView, \
    AnnouncementSearchView, ProfileUpdateView, CustomLogoutView, AnnouncementCreateView, category_attributes, \
    ChatPageView, UserChatsView, FavouriteToggleView, FavouriteListView, AnnouncementDetailView

urlpatterns = [
    path('', MainView.as_view(), name='main_page'),
    path('category/<slug:slug>/', AnnouncementListView.as_view(), name='announcement_list_page'),
    path('announcement/<slug:slug>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('adding/', AnnouncementCreateView.as_view(), name='add_announcement_page'),
    path("categories/<slug:slug>/attributes/", category_attributes, name="category_attributes"),
    path("search/", AnnouncementSearchView.as_view(), name="announcement_search_page"),

    path('auth/login/', CustomLoginView.as_view(), name='login_page'),
    path("auth/google-login", GoogleLoginView.as_view(), name='google_login_page'),
    path("auth/oauth2/callback", GoogleCallbackView.as_view(), name='google_callback_page'),
    path('auth/logout', CustomLogoutView.as_view(), name='logout_page'),
    path('auth/register', RegisterCreateView.as_view(), name='register_page'),
    path('auth/profile', ProfileUpdateView.as_view(), name='profile_page'),

    path("chat/<int:chat_id>/", ChatPageView.as_view(), name="chat_page"),
    path("chats/", UserChatsView.as_view(), name="user_chats_page"),

    path('favorites/', FavouriteListView.as_view(), name='favourites_page'),
    path('favorites/toggle/<int:pk>/', FavouriteToggleView.as_view(), name='favourite_toggle'),

]

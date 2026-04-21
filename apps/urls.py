from django.urls import path
from apps.views import AnnouncementListView, MainView, CustomLoginView, GoogleLoginView, GoogleCallbackView, \
    RegisterCreateView, AnnouncementSearchView, ProfileUpdateView, CustomLogoutView, AnnouncementCreateView, \
    category_attributes, ChatPageView, UserChatsView, FavouriteToggleView, FavouriteListView, AnnouncementDetailView, \
    UserProfileView, StartChatView, UserSettingsView

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
    path('auth/profile/settings', UserSettingsView.as_view(), name='settings_page'),

    path("chat/<int:chat_id>/", ChatPageView.as_view(), name="chat_page"),
    path("chat/start/<int:user_id>/", StartChatView.as_view(), name="start_chat"),
    path("chats/", UserChatsView.as_view(), name="user_chats_page"),

    path('favorites/', FavouriteListView.as_view(), name='favourites_page'),
    path('favorites/toggle/<int:pk>/', FavouriteToggleView.as_view(), name='favourite_toggle'),
    path('user/<int:pk>/', UserProfileView.as_view(), name='user_profile'),

#     path("api/categories/roots/", api_categories_roots, name="api_categories_roots"),
#     path("api/categories/<int:parent_id>/children/", api_categories_children, name="api_categories_children"),
#     path("api/categories/<int:category_id>/attributes/", api_category_attributes, name="api_category_attributes"),

]

import urllib.parse
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
import requests
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from apps.filters import AnnouncementFilterSet, AnnouncementOrderFilterSet
from apps.models import Announcement, Category, User, Chat, Region, District
from apps.forms import AnnouncementModelForm, RegisterModelForm, EmailLoginForm
from django.views.generic import ListView
from apps.models.announcements import AnnouncementImage, FavouriteAnnouncement
from root import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


class MainView(ListView):
    template_name = 'apps/main.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        announcements = Announcement.objects.filter(
            product_type=Announcement.AnnouncementType.VIP
        ).select_related('district__region').prefetch_related('images')

        q = self.request.GET.get("q")
        if q:
            announcements = announcements.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            ).distinct()

        region_id = self.request.GET.get("region")
        if region_id:
            announcements = announcements.filter(region_id=region_id)

        district_id = self.request.GET.get("district")
        if district_id:
            announcements = announcements.filter(district_id=district_id)

        fav_ids = []
        if self.request.user.is_authenticated:
            fav_ids = FavouriteAnnouncement.objects.filter(
                user=self.request.user
            ).values_list('announcement_id', flat=True)

        context['announcements'] = announcements
        context['search_value'] = q or ""
        context['fav_ids'] = list(fav_ids)
        return context


class AnnouncementSearchView(ListView):
    template_name = "apps/announcement-list.html"
    context_object_name = "announcements"
    paginate_by = 40

    def get_queryset(self):
        queryset = Announcement.objects.all().select_related('district__region').prefetch_related('images')
        
        region_id = self.request.GET.get("region")
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        district_id = self.request.GET.get("district")
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        self.filterset = AnnouncementFilterSet(self.request.GET, queryset=queryset, category=None)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        fav_ids = []
        if self.request.user.is_authenticated:
            fav_ids = FavouriteAnnouncement.objects.filter(
                user=self.request.user
            ).values_list('announcement_id', flat=True)

        context["filter"] = self.filterset
        context["dynamic_fields"] = self.filterset.dynamic_fields
        context["top_categories"] = Category.objects.filter(parent=None)
        context["current_category"] = None
        context["search_value"] = self.request.GET.get("q", "")
        context['fav_ids'] = list(fav_ids)
        return context




class AnnouncementListView(ListView):
    template_name = "apps/announcement-list.html"
    context_object_name = "announcements"
    paginate_by = 40
    def get_queryset(self):
        slug = self.kwargs.get("slug")
        self.category = get_object_or_404(Category, slug=slug)
        categories = self.category.get_descendants(include_self=True)

        queryset = Announcement.objects.filter(category__in=categories)
        
        region_id = self.request.GET.get("region")
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        district_id = self.request.GET.get("district")
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        self.filterset = AnnouncementFilterSet(
            self.request.GET,
            queryset=queryset,
            category=self.category
        )
        queryset = self.filterset.qs


        self.order_filter = AnnouncementOrderFilterSet(
            self.request.GET,
            queryset=queryset
        )
        return self.order_filter.qs



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        fav_ids = []
        if self.request.user.is_authenticated:
            fav_ids = FavouriteAnnouncement.objects.filter(
                user=self.request.user
            ).values_list('announcement_id', flat=True)

        context["filter"] = self.filterset
        context["dynamic_fields"] = self.filterset.dynamic_fields
        context["top_categories"] = Category.objects.filter(parent=None)
        context["current_category"] = self.category
        context["search_value"] = self.request.GET.get("q", "")
        context['fav_ids'] = list(fav_ids)
        return context


class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = "apps/announcement_details.html"
    context_object_name = "announcement"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['similar_announcements'] = Announcement.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id).select_related('district__region').prefetch_related('images')[:10]
        
        context['user_announcements'] = Announcement.objects.filter(
            user=self.object.user
        ).exclude(id=self.object.id).select_related('district__region').prefetch_related('images')[:10]

        fav_ids = []
        if self.request.user.is_authenticated:
            fav_ids = FavouriteAnnouncement.objects.filter(
                user=self.request.user
            ).values_list('announcement_id', flat=True)
        context['fav_ids'] = list(fav_ids)

        return context

class CustomLoginView(LoginView):
    template_name = 'apps/auth/login.html'
    authentication_form = EmailLoginForm
    success_url = reverse_lazy('profile_page')
    redirect_authenticated_user = True

class RegisterCreateView(CreateView):
    template_name = 'apps/auth/register.html'
    form_class = RegisterModelForm
    success_url = reverse_lazy('login_page')


class GoogleLoginView(View):
    def get(self, request):
        scope = "email profile"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={urllib.parse.quote(settings.GOOGLE_REDIRECT_URI)}"
            f"&scope={urllib.parse.quote(scope)}"
        )
        return redirect(auth_url)


class GoogleCallbackView(View):
    def get(self, request):
        code = request.GET.get("code")

        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_res = requests.post("https://oauth2.googleapis.com/token", data=token_data).json()
        access_token = token_res.get("access_token")

        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 200:
            info = response.json()
            email = info["email"]
            name = info["name"]

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"first_name": name}
            )
            if not user.is_valid_password or created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
            login(request, user)

            return redirect('profile_page')
        return redirect('login_page')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    template_name = 'apps/auth/profile.html'
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('profile_page')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status', Announcement.Status.ACTIVE)
        sort = self.request.GET.get('sort', 'newest')
        
        announcements = Announcement.objects.filter(
            user=self.request.user,
            status=status
        ).select_related('category', 'district__region').prefetch_related('images')

        if sort == 'price_asc':
            announcements = announcements.order_by('price')
        elif sort == 'price_desc':
            announcements = announcements.order_by('-price')
        else:
            announcements = announcements.order_by('-created_at')
        
        context['announcements'] = announcements
        context['current_status'] = status
        context['current_sort'] = sort
        context['Status'] = Announcement.Status
        return context


class UserSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'apps/auth/settings.html'
    fields = ['first_name', 'last_name', 'phone', 'avatar']
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('main_page')


class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    model = Announcement
    template_name = 'apps/add_announcement.html'
    form_class = AnnouncementModelForm
    success_url = reverse_lazy('profile_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_categories'] = Category.objects.filter(parent=None)
        context['regions'] = Region.objects.prefetch_related('districts').all()
        return context

    def form_valid(self, form):

        form.instance.user = self.request.user

        response = super().form_valid(form)

        images = self.request.FILES.getlist("images")
        for img in images:
            AnnouncementImage.objects.create(
                product=self.object,
                image=img
            )

        return response


def category_attributes(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return JsonResponse(cat.attribute or [], safe=False)




#
# class ChatPageView(LoginRequiredMixin, DetailView):
#     model = Chat
#     template_name = 'apps/chat.html'
#     context_object_name = "chat"
#     pk_url_kwarg = "chat_id"
#
#     message.is_image = message.file.name.lower().endswith(
#         (".jpg", ".png", ".jpeg", ".gif", ".webp")
#     )
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Fetch chats for the sidebar
#         context['chats'] = Chat.objects.filter(
#             Q(user1=self.request.user) | Q(user2=self.request.user)
#         ).distinct().order_by("-created_at")
#
#         # Identify the other user in the current chat
#         chat = self.object
#         if chat.user1 == self.request.user:
#             context['other_user'] = chat.user2
#         else:
#             context['other_user'] = chat.user1
#
#         return context

class ChatPageView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = 'apps/chat.html'
    context_object_name = "chat"
    pk_url_kwarg = "chat_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # sidebar chats
        context['chats'] = Chat.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).distinct().order_by("-created_at")

        chat = self.object

        # other user
        if chat.user1 == self.request.user:
            context['other_user'] = chat.user2
        else:
            context['other_user'] = chat.user1


        messages = chat.messages.all()

        for m in messages:
            if m.file:
                m.is_image = m.file.name.lower().endswith(
                    (".jpg", ".png", ".jpeg", ".gif", ".webp")
                )
            else:
                m.is_image = False

        context['messages'] = messages
        context['has_messages'] = messages.exists()

        return context

class UserChatsView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'apps/chats.html'
    context_object_name = 'chats'

    def get_queryset(self):
        return Chat.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).distinct().order_by("-created_at")


class FavouriteListView(LoginRequiredMixin, ListView):
    template_name = 'apps/favourites.html'
    context_object_name = 'favourites'
    login_url = 'login_page'

    def get_queryset(self):
        return FavouriteAnnouncement.objects.filter(
            user=self.request.user
        ).select_related('announcement__user').prefetch_related('announcement__images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.get_queryset().count()
        context['limit'] = 150
        fav_ids = FavouriteAnnouncement.objects.filter(
            user=self.request.user
        ).values_list('announcement_id', flat=True)
        context['fav_ids'] = list(fav_ids)
        return context


class FavouriteToggleView(LoginRequiredMixin, View):
    login_url = 'login_page'

    def post(self, request, pk, *args, **kwargs):
        announcement = get_object_or_404(Announcement, pk=pk)
        fav = FavouriteAnnouncement.objects.filter(
            user=request.user, announcement=announcement
        ).first()

        if fav:
            fav.delete()
            status = 'removed'
        else:
            count = FavouriteAnnouncement.objects.filter(user=request.user).count()
            if count >= 150:
                return JsonResponse({
                    'status': 'error',
                    'message': "Siz maksimal 150 ta sevimli e'longa ega bo'la olasiz."
                }, status=400)
            FavouriteAnnouncement.objects.create(
                user=request.user,
                announcement=announcement
            )
            status = 'added'

        total = FavouriteAnnouncement.objects.filter(user=request.user).count()
        return JsonResponse({'status': status, 'count': total})

class UserProfileView(DetailView):
    model = User
    template_name = 'apps/user.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User announcements
        announcements = Announcement.objects.filter(
            user=self.object
        ).select_related('district__region').prefetch_related('images')
        context['announcements'] = announcements
        
        fav_ids = []
        if self.request.user.is_authenticated:
            fav_ids = FavouriteAnnouncement.objects.filter(
                user=self.request.user
            ).values_list('announcement_id', flat=True)
        context['fav_ids'] = list(fav_ids)
        
        return context

class StartChatView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)

        # Agar user o‘ziga o‘zi chat boshlamoqchi bo‘lsa profilga yubor
        if request.user == other_user:
            return redirect('user_profile', pk=user_id)

        # Chatni tekshirish: agar mavjud bo‘lsa olish, yo‘q bo‘lsa yaratish
        chat, created = Chat.get_or_create_chat(request.user, other_user)

        return redirect('chat_page', chat_id=chat.id)



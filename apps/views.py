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
from apps.models import Announcement, Category, User ,Chat
from apps.forms import AnnouncementModelForm, RegisterModelForm, EmailLoginForm
from apps.models import Announcement, Category, User
from django.views.generic import ListView
from apps.models.announcements import AnnouncementImage
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
        )

        q = self.request.GET.get("q")
        if q:
            announcements = announcements.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            ).distinct()

        context['announcements'] = announcements
        context['search_value'] = q or ""
        return context


class AnnouncementSearchView(ListView):
    template_name = "apps/announcement-list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        queryset = Announcement.objects.all()
        self.filterset = AnnouncementFilterSet(self.request.GET, queryset=queryset, category=None)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["dynamic_fields"] = self.filterset.dynamic_fields
        context["top_categories"] = Category.objects.filter(parent=None)
        context["current_category"] = None
        context["search_value"] = self.request.GET.get("q", "")
        return context




class AnnouncementListView(ListView):
    template_name = "apps/announcement-list.html"
    context_object_name = "announcements"


    def get_queryset(self):
        slug = self.kwargs.get("slug")
        self.category = get_object_or_404(Category, slug=slug)
        categories = self.category.get_descendants(include_self=True)

        queryset = Announcement.objects.filter(category__in=categories)

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
        context["filter"] = self.filterset
        context["dynamic_fields"] = self.filterset.dynamic_fields
        context["top_categories"] = Category.objects.filter(parent=None)
        context["current_category"] = self.category
        context["search_value"] = self.request.GET.get("q", "")
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
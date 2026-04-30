import urllib.parse
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
import requests
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, TemplateView
from apps.filters import AnnouncementFilterSet, AnnouncementOrderFilterSet
from apps.models import Announcement, Category, User, Chat, Region, District, Transaction
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
            product_type=Announcement.AnnouncementType.VIP,
            status=Announcement.Status.ACTIVE
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
        
        # Recently viewed
        recent_ids = self.request.session.get('recently_viewed', [])
        if recent_ids:
            # Preserve the order given by the session list via Case/When or just sorting in Python
            recent_objects = Announcement.objects.filter(id__in=recent_ids).select_related('district__region').prefetch_related('images')
            recent_objects_dict = {obj.id: obj for obj in recent_objects}
            context['recently_viewed_announcements'] = [recent_objects_dict[id] for id in recent_ids if id in recent_objects_dict]
        else:
            context['recently_viewed_announcements'] = []
            
        context['search_value'] = q or ""
        context['fav_ids'] = list(fav_ids)
        return context


class AnnouncementSearchView(ListView):
    template_name = "apps/announcement-list.html"
    context_object_name = "announcements"
    paginate_by = 40

    def get_queryset(self):
        queryset = Announcement.objects.filter(
            status=Announcement.Status.ACTIVE
        ).select_related('district__region').prefetch_related('images')
        
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

        queryset = Announcement.objects.filter(
            category__in=categories,
            status=Announcement.Status.ACTIVE
        )
        
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
        
        # Add to recently viewed session
        recent = self.request.session.get('recently_viewed', [])
        if obj.id in recent:
            recent.remove(obj.id)
        recent.insert(0, obj.id)
        self.request.session['recently_viewed'] = recent[:12]
        
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
        
        user_announcements = Announcement.objects.filter(user=self.request.user)
        
        context['announcements'] = user_announcements.filter(
            status=status
        ).select_related('category', 'district__region').prefetch_related('images')
        
        if sort == 'price_asc':
            context['announcements'] = context['announcements'].order_by('price')
        elif sort == 'price_desc':
            context['announcements'] = context['announcements'].order_by('-price')
        else:
            context['announcements'] = context['announcements'].order_by('-created_at')
        
        # Status counts
        from django.db.models import Count
        counts = user_announcements.values('status').annotate(total=Count('id'))
        counts_dict = {item['status']: item['total'] for item in counts}
        
        context['counts'] = counts_dict
        context['current_status'] = status
        context['current_sort'] = sort
        context['Status'] = Announcement.Status
        return context


class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'apps/auth/history.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        period = self.request.GET.get('period', '30')
        
        if period != 'all':
            from django.utils import timezone
            from datetime import timedelta
            days = int(period)
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=start_date)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_period'] = self.request.GET.get('period', '30')
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

class UserChatsView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'apps/chats.html'
    context_object_name = "chats"

    def get_queryset(self):
        queryset = Chat.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).distinct().order_by("-created_at")
        
        chat_type = self.request.GET.get('type') # 'buying' or 'selling'
        unread = self.request.GET.get('unread') # '1' for unread only

        if chat_type == 'buying':
            queryset = queryset.exclude(announcement__user=self.request.user)
        elif chat_type == 'selling':
            queryset = queryset.filter(announcement__user=self.request.user)
            
        if unread == '1':
            queryset = queryset.filter(messages__is_read=False).exclude(messages__from_user=self.request.user)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_type'] = self.request.GET.get('type', 'all')
        context['current_unread'] = self.request.GET.get('unread', '0')
        return context


class ChatPageView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = 'apps/chat.html'
    context_object_name = "chat"
    pk_url_kwarg = "chat_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # sidebar chats with the same filtering logic
        queryset = Chat.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).distinct().order_by("-created_at")
        
        chat_type = self.request.GET.get('type')
        unread = self.request.GET.get('unread')

        if chat_type == 'buying':
            queryset = queryset.exclude(announcement__user=self.request.user)
        elif chat_type == 'selling':
            queryset = queryset.filter(announcement__user=self.request.user)
            
        if unread == '1':
            queryset = queryset.filter(messages__is_read=False).exclude(messages__from_user=self.request.user)
            
        context['chats'] = queryset
        context['current_type'] = chat_type or 'all'
        context['current_unread'] = unread or '0'

        chat = self.object
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
        context['active_chat_id'] = chat.id
        return context


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
        # Check if chat already exists
        chat = Chat.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).first()

        if not chat:
            chat = Chat.objects.create(user1=request.user, user2=other_user)

        return redirect('chat_page', chat_id=chat.id)

class AnnouncementDeactivateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        announcement = get_object_or_404(Announcement, pk=pk, user=request.user)
        if announcement.status == Announcement.Status.ACTIVE:
            announcement.status = Announcement.Status.UNACTIVE
        else:
            announcement.status = Announcement.Status.WAITING
        announcement.save()
        return redirect('profile_page')

class PromoteSelectionView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'apps/promote.html'
    context_object_name = 'announcement'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class PushUpPaymentView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'apps/pushup_payment.html'
    context_object_name = 'announcement'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class PromotionCheckoutView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'apps/promotion_checkout.html'
    context_object_name = 'announcement'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['package'] = self.request.GET.get('package', 'optimum').capitalize()
        context['price'] = self.request.GET.get('price', '45 000')
        return context

class WalletTopupView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/wallet_topup.html'

class WalletCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/wallet_checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount'] = self.request.GET.get('amount', '6 000')
        return context


class HelpView(ListView):
    template_name = 'apps/help.html'
    queryset = Category.objects.filter(parent=None)
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adding some mock popular articles for the help page
        context['popular_articles'] = [
            {'title': 'Как подать объявление?', 'id': 1},
            {'title': 'Как изменить или удалить объявление?', 'id': 2},
            {'title': 'Правила публикации', 'id': 3},
            {'title': 'Безопасность на OLX', 'id': 4},
        ]
        return context

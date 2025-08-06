from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import House, UserProfile, Comment, Review, ContactMessage, HouseImage
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import HouseForm, RegisterForm, UserProfileForm, CommentForm, ReviewForm, ContactForm
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Avg, Count

# Create your views here.

class HouseListView(ListView):
    model = House
    template_name = 'listings/house_list.html'
    context_object_name = 'houses'
    paginate_by = 8

    def get_queryset(self):
        queryset = House.objects.all()
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        price_min = self.request.GET.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        price_max = self.request.GET.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        bedrooms = self.request.GET.get('bedrooms')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        bathrooms = self.request.GET.get('bathrooms')
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)
        
        # Sorting
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')  # Default sorting
        
        return queryset

class HouseDetailView(DetailView):
    model = House
    template_name = 'listings/house_detail.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author').order_by('-created_at')
        context['comment_form'] = CommentForm()
        # Reviews
        context['reviews'] = self.object.reviews.select_related('author').order_by('-created_at')
        context['review_form'] = ReviewForm()
        # Average rating
        reviews = self.object.reviews.all()
        if reviews:
            context['average_rating'] = sum(r.rating for r in reviews) / reviews.count()
        else:
            context['average_rating'] = None
        # Has user reviewed?
        user = self.request.user
        context['has_reviewed'] = user.is_authenticated and self.object.reviews.filter(author=user).exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'text' in request.POST and 'rating' not in request.POST:
            # Comment form
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to comment.')
                return redirect('login')
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.house = self.object
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added!')
                return redirect('house-detail', pk=self.object.pk)
            context = self.get_context_data(object=self.object)
            context['comment_form'] = form
            return self.render_to_response(context)
        elif 'rating' in request.POST:
            # Review form
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to review.')
                return redirect('login')
            if self.object.reviews.filter(author=request.user).exists():
                messages.error(request, 'You have already reviewed this house.')
                return redirect('house-detail', pk=self.object.pk)
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.house = self.object
                review.author = request.user
                review.save()
                messages.success(request, 'Review added!')
                return redirect('house-detail', pk=self.object.pk)
            context = self.get_context_data(object=self.object)
            context['review_form'] = form
            return self.render_to_response(context)
        else:
            return super().post(request, *args, **kwargs)

class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    template_name = 'listings/house_form.html'

    def form_valid(self, form):
        house = form.save(commit=False)
        house.author = self.request.user
        house.save()
        self.object = house  # <-- Add this line!
        images = self.request.FILES.getlist('images')
        for img in images[:10]:
            HouseImage.objects.create(house=house, image=img)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('house-detail', kwargs={'pk': self.object.pk})

# User Registration View
class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Save profile fields
            profile = user.userprofile
            profile.profile_image = form.cleaned_data.get('profile_image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
        return render(request, 'registration/register.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        user = request.user
        # Ensure profile exists for all users
        profile, created = UserProfile.objects.get_or_create(user=user)
        form = UserProfileForm(instance=profile)
        return render(request, 'profile.html', {'form': form, 'profile': profile})

    def post(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        return render(request, 'profile.html', {'form': form, 'profile': profile})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = 'house-list'

@login_required
def house_like_view(request, pk):
    house = get_object_or_404(House, pk=pk)
    user = request.user
    if user in house.likes.all():
        house.likes.remove(user)
    else:
        house.likes.add(user)
    return redirect('house-detail', pk=pk)

# About and Contact Views
class AboutView(View):
    def get(self, request):
        return render(request, 'listings/about.html')

class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'listings/contact.html', {'form': form})
    
    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
        return render(request, 'listings/contact.html', {'form': form})

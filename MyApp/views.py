# D:\TaskLink\TaskLink\MyApp\views.py
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, WorkerReviewForm
from django.core.mail import send_mail
import random
from .models import CustomUser, WorkerReview  # Correct import
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import razorpay
from django.db.models import Avg

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def services(request):
    worker_types = CustomUser.objects.filter(is_worker=True).values_list('worker_type', flat=True).distinct()
    selected_type = request.GET.get('worker_type', '')
    
    if selected_type:
        workers = CustomUser.objects.filter(is_worker=True, worker_type=selected_type)
    else:
        workers = CustomUser.objects.filter(is_worker=True).order_by('?')[:3]  # Random 3 workers
    
    worker_ratings = {
        worker.id: worker.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        for worker in workers
    }

    context = {
        'worker_types': worker_types,
        'selected_type': selected_type,
        'workers': workers,
        'worker_ratings': worker_ratings,
        'is_subscribed': request.user.is_subscribed,
        'is_worker': request.user.is_worker,
    }
    return render(request, 'services.html', context)

def worker_profile(request, worker_id):
    # Use CustomUser instead of Worker, ensure it's a worker
    worker = get_object_or_404(CustomUser, id=worker_id, is_worker=True)
    reviews = WorkerReview.objects.filter(worker=worker)
    rating_avg = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = WorkerReview.objects.filter(
            worker=worker,
            reviewer=request.user
        ).exists()


    is_subscribed = request.user.is_authenticated and request.user.is_subscribed
    is_worker = request.user == worker 
    review_form = None
    if is_subscribed and not is_worker and request.method == "POST":
        review_form = WorkerReviewForm(request.POST)
        if review_form.is_valid() and not has_reviewed:
            review = review_form.save(commit=False)
            review.worker = worker
            review.reviewer = request.user
            review.save()
            return redirect('worker_profile', worker_id=worker.id)
    else:
        review_form = WorkerReviewForm()

    context = {
        'worker': worker,
        'reviews': reviews,
        'rating_avg': rating_avg,
        'is_subscribed': is_subscribed,
        'is_worker': is_worker,
        'review_form': review_form,
        'has_reviewed': has_reviewed,
    }
    return render(request, 'worker_profile.html', context)

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            request.session['form_data'] = form.cleaned_data
            request.session['otp'] = otp
            try:
                send_mail(
                    'TaskLink Registration OTP',
                    f'Your OTP for registration is: {otp}',
                    'adityabhosale5877@gmail.com',
                    [form.cleaned_data['email']],
                    fail_silently=False,
                )
                messages.success(request, "OTP sent to your email!")
            except Exception as e:
                messages.error(request, f"Failed to send OTP: {str(e)}")
                return render(request, 'register.html', {'form': form})
            return redirect('verify_otp')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        form_data = request.session.get('form_data')
        if not form_data or not stored_otp:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')
        if entered_otp == stored_otp:
            form = CustomUserCreationForm(form_data)
            if form.is_valid():
                user = form.save(commit=False)
                user.otp = stored_otp
                user.is_otp_verified = True
                user.save()
                messages.success(request, f"Welcome, {user.username}! Please log in.")
                del request.session['form_data']
                del request.session['otp']
                return redirect('login')
            else:
                messages.error(request, "Something went wrong. Please register again.")
                return redirect('register')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'verify_otp.html')

def user_logout(request):
    logout(request)
    return redirect('home')



@login_required
def subscribe(request):
    if request.user.is_subscribed:
        messages.info(request, "You are already subscribed!")
        return redirect('home')
    return render(request, 'subscribe.html')

@csrf_exempt
def subscribe_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        amount = data.get('amount')

        try:
            client = razorpay.Client(auth=("rzp_test_UseuEM9CE5roTD", "uprgx1wXs3arurLMNqMbJ60K"))
            payment = client.payment.fetch(payment_id)

            if payment['status'] == 'authorized':
                client.payment.capture(payment_id, int(amount))
                payment = client.payment.fetch(payment_id)

            if payment['amount'] == int(amount) and payment['status'] == 'captured':
                request.user.is_subscribed = True
                request.user.subscription_date = timezone.now()
                request.user.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failure', 'error': 'Payment verification failed'})
        except Exception as e:
            return JsonResponse({'status': 'failure', 'error': str(e)})
    
    return JsonResponse({'status': 'failure', 'error': 'Invalid request'})

@login_required
def profile(request):
    if request.method == 'POST':
        new_location = request.POST.get('location')
        if new_location:
            request.user.location = new_location
            request.user.save()
            messages.success(request, "Address updated successfully!")
        else:
            messages.error(request, "Please provide a valid address.")
        return redirect('profile')

    subscription_date = request.user.subscription_date if request.user.is_subscribed else None
    context = {
        'subscription_date': subscription_date,
    }
    return render(request, 'profile.html', context)




























































def test_email(request):
    try:
        send_mail(
            'Test Email',
            'This is a test email from Django.',
            'adityabhosale5877@gmail.com',
            ['your_test_email@example.com'],
            fail_silently=False,
        )
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {str(e)}")
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import AuctionItem, Bid
from .forms import AuctionForm, CustomUserCreationForm
from django.contrib import messages
import random
import string
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import stripe
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

# ✅ Homepage (INDEX)
def index(request):
    return render(request, "index.html")

# ✅ Browse Auctions
def browse(request):
    auctions = AuctionItem.objects.all()
    return render(request, 'browse.html', {'auctions': auctions})

@login_required
def place_bid(request, item_id):
    item = get_object_or_404(AuctionItem, id=item_id)
    
     # Prevent bidding if auction is closed
    if item.is_closed:
       return render(request, 'auction_closed.html', {'auction': item})
    
    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        if not bid_amount:
            messages.error(request, "Please enter a bid amount.")
            return redirect("place_bid", item_id=item.id)
        
        try:
            bid_amount = Decimal(bid_amount)
        except Exception:
            messages.error(request, "Invalid bid amount.")
            return redirect("place_bid", item_id=item.id)
        
        # Determine the minimum acceptable bid:
        highest_bid = item.bids.order_by("-amount").first()
        min_bid = highest_bid.amount if highest_bid else item.starting_bid
        
        if bid_amount <= min_bid:
            messages.error(request, f"Your bid must be greater than ${min_bid}.")
            return redirect("place_bid", item_id=item.id)
        
        # Save the new bid
        Bid.objects.create(auction=item, bidder=request.user, amount=bid_amount)
        messages.success(request, f"Your bid of ${bid_amount} has been placed.")
        return redirect("browse")  # or redirect to a detailed auction page
    
    # For GET request, display a bid form
    return render(request, "place_bid.html", {"item": item})

@login_required
def bids(request):
    bids = Bid.objects.filter(bidder=request.user).select_related("auction")
    return render(request, "bids.html", {"bids": bids})

# ✅ Register (Signup)
def register(request):
    """User registers with email; an OTP is sent to verify and activate the account."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user with is_active=False
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Generate OTP and store in session
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['user_id'] = user.id

            # Send OTP via email
            send_otp_email(user.email, otp)

            messages.success(request, "An OTP has been sent to your email. Please verify to activate your account.")
            return redirect("verify_otp")  # We'll create this URL
        else:
            messages.error(request, "Error during registration. Please fix the issues below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "registration/register.html", {"form": form})

def verify_otp(request):
    """Verify the OTP sent to the user's email. Activate and log in the user if correct."""
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        user_id = request.session.get("user_id")

        if input_otp == session_otp and user_id:
            # Activate the user
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            # Log the user in
            login(request, user)

            # Clear OTP session data
            del request.session['otp']
            del request.session['user_id']

            messages.success(request, "Your account has been activated successfully!")
            return redirect("home")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "registration/verify_otp.html")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect("home")  # ✅ Redirect to homepage correctly
        else:
            messages.error(request, "Error during registration. Try again.")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

# ✅ Login (with authentication check)
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            
            # ✅ Redirect to 'next' page if exists, otherwise go to home
            next_url = request.GET.get("next", "home")
            return redirect(next_url)  
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

# ✅ Logout (Redirects to login)
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")  # ✅ Correctly redirect to login page

# ✅ Protected Pages (Require Login)
@login_required
def account(request):
    return render(request, "account.html")



@login_required
def my_listings(request):
     if not request.user.is_authenticated:
        return redirect('login')  # Redirect if user is not logged in

     auctions = AuctionItem.objects.filter(seller=request.user)  # Filter auctions by logged-in user
     return render(request, 'my_listings.html', {'auctions': auctions})

@login_required
def profile(request):
    return render(request, "profile.html")

# ✅ Public Help Page
def help_page(request):
    return render(request, "help.html")



def index(request):
    auctions = AuctionItem.objects.all()
    form = AuctionForm()

    if request.method == "POST":
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user  # Assign logged-in user
            auction.save()
            return redirect('home')

    return render(request, 'index.html', {'form': form, 'auctions': auctions})

@login_required
def delete_auction(request, auction_id):
    auction = AuctionItem.objects.get(id=auction_id)
    if request.user == auction.seller:
        auction.delete()
    return redirect('home')

def generate_otp(length=6):
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)
    
@login_required
def auction_detail(request, auction_id):
    """
    Display auction details. If the auction is closed and no winner is set,
    determine the winner based on the highest bid.
    """
    auction = get_object_or_404(AuctionItem, id=auction_id)
    
     # Convert times to local timezone
    local_now = timezone.localtime(timezone.now())
    local_end_time = timezone.localtime(auction.end_time) if auction.end_time else None
    
   # Check if auction is closed based on local time
    if local_end_time and local_now >= local_end_time and auction.winner is None:
        highest_bid = auction.bids.order_by("-amount").first()
        if highest_bid:
            auction.winner = highest_bid.bidder
            auction.save()
    
    return render(request, "auction_detail.html", {"auction": auction})
def category_auctions(request, category):
    auctions = AuctionItem.objects.filter(category=category)
    return render(request, "category_auctions.html", {"category": category, "auctions": auctions})


@login_required
def make_payment(request, auction_id):
    # Get the auction object. Ensure the user is the winner.
    auction = get_object_or_404(AuctionItem, id=auction_id)
    
    # Optional: Check if request.user is the winner
    if auction.winner != request.user:
        return redirect('auction_detail', auction_id=auction.id)
    
    # Create a Stripe Checkout session
    # For demonstration, we use a fixed currency and amount based on the winning bid or a fixed amount.
    # In production, calculate the amount correctly (in cents, and integer only).
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(auction.bids.order_by("-amount").first().amount * 100),  # Amount in cents
                    'product_data': {
                        'name': auction.title,
                        'description': auction.description,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )
    except Exception as e:
        return render(request, "payment_error.html", {"error": str(e)})
    
    # Redirect the user to Stripe Checkout
    return redirect(checkout_session.url)

def payment_success(request):
    # Optionally, verify the session here with stripe.checkout.Session.retrieve(...)
    return render(request, "payment_success.html")

def payment_cancel(request):
    return render(request, "payment_cancel.html")
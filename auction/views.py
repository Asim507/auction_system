from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import AuctionItem
from .forms import AuctionForm


# ✅ Homepage (INDEX)
def index(request):
    return render(request, "index.html")

# ✅ Browse Auctions
def browse(request):
    return render(request, "browse.html")

# ✅ Register (Signup)
def register(request):
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
def bids(request):
    return render(request, "bids.html")

@login_required
def my_listings(request):
    return render(request, "my_listings.html")

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


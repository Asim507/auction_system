from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="home"),  # ✅ Ensure the homepage name is "home"
    path("browse/", views.browse, name="browse"),  # Browse Auctions
    path("register/", views.register, name="register"),  # Signup
    path("login/", views.user_login, name="login"),  # Login
    path("logout/", views.user_logout, name="logout"),  # Logout
    path("account/", views.account, name="account"),  # Protected Account Page
    path("bids/", views.bids, name="bids"),  # Protected Bids Page
    path("listings/", views.my_listings, name="listings"),  # Protected Listings
    path("profile/", views.profile, name="profile"),  # Protected Profile Page
    path("help/", views.help_page, name="help"),  # Public Help Page
  path('delete_auction/<int:auction_id>/', views.delete_auction, name='delete_auction'),
]

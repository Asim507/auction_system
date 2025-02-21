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
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('place-bid/<int:item_id>/', views.place_bid, name='place_bid'),
     path('category/<str:category>/', views.category_auctions, name='category_auctions'),
    path('auction/<int:auction_id>/', views.auction_detail, name='auction_detail'),
    #stripe
    path('make-payment/<int:auction_id>/', views.make_payment, name='make_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),

]

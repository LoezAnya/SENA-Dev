from django.urls import path

from users.views import MeView, RateLimitedTokenObtainPairView, RegisterView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", RateLimitedTokenObtainPairView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
]

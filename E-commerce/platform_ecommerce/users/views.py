from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import RegisterSerializer, UserSerializer


def ratelimited_error(request, exception):
    """Custom handler wired via settings.RATELIMIT_VIEW.

    django-ratelimit calls this for non-DRF views; our DRF views instead
    catch Ratelimited explicitly (see dispatch overrides below) so both
    paths return a consistent JSON 429 response.
    """
    return Response(
        {"detail": "Too many requests. Please try again later."},
        status=status.HTTP_429_TOO_MANY_REQUESTS,
    )


class RateLimitedAPIView(APIView):
    """Base class that turns a Ratelimited exception into a clean 429 JSON
    response instead of the default HTML/500 behaviour, acting as the
    lightweight "API Gateway" rate-limiting layer for Sprint 1.
    """

    def handle_exception(self, exc):
        if isinstance(exc, Ratelimited):
            return Response(
                {"detail": "Too many requests. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return super().handle_exception(exc)


class RegisterView(RateLimitedAPIView, generics.CreateAPIView):
    """POST /api/v1/auth/register/

    Registers a buyer or seller. Rate-limited to 10 requests/minute per
    IP to slow down automated account-creation abuse.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
        )


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/auth/me/

    Returns (or partially updates) the profile of the currently
    authenticated user, including their seller_profile if present.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RateLimitedTokenObtainPairView(RateLimitedAPIView, TokenObtainPairView):
    """POST /api/v1/auth/login/

    Wraps SimpleJWT's login endpoint with a 20 requests/minute per-IP
    limit to mitigate credential-stuffing / brute force attempts.
    """

    @method_decorator(ratelimit(key="ip", rate="20/m", method="POST", block=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

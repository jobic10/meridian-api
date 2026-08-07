from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsAdmin

from .serializers import StaffCreateSerializer, UserSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = str(request.data.get("username", "")).strip().lower()
        password = request.data.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active:
            return Response(
                {"detail": "Those credentials don't match an active account."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh", ""))
            token.blacklist()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        return StaffCreateSerializer if self.request.method == "POST" else UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = User.objects.order_by("-is_active", "name")
        role = self.request.query_params.get("role")
        active = self.request.query_params.get("status")
        if role:
            qs = qs.filter(role=role)
        if active:
            qs = qs.filter(is_active=(active == "ACTIVE"))
        return qs


class UserToggleStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        if str(request.user.pk) == str(pk):
            return Response(
                {"detail": "You can't deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            target = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        target.is_active = not target.is_active
        target.save(update_fields=["is_active"])
        return Response(UserSerializer(target).data)

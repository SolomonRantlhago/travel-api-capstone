from rest_framework import generics, permissions
from rest_framework.response import Response

from django.contrib.auth import (
    get_user_model,
    password_validation,
)
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    AdminUserSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/accounts/register/ - create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT/PATCH /api/accounts/profile/ - view or update
    the logged-in user's own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    """
    POST /api/accounts/password/change/ - change the logged-in
    user's password.
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = request.user
        new_password = serializer.validated_data['new_password']

        password_validation.validate_password(
            new_password,
            user
        )

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response(
            {
                "detail": "Password changed successfully."
            },
            status=200
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """
    POST /api/accounts/password/reset/ - request a password reset.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(
                email__iexact=email,
                is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "If an account with that email exists, "
                        "a password reset email has been sent."
                    )
                },
                status=200
            )

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(user)

        reset_link = (
            f"http://localhost:8000/api/v1/accounts/"
            f"password/reset/confirm/"
            f"?uid={uid}&token={token}"
        )

        send_mail(
            subject='Travel API Password Reset',
            message=(
                "You requested a password reset.\n\n"
                f"Use the following link to reset your password:\n"
                f"{reset_link}\n\n"
                "If you did not request this, you can ignore this email."
            ),
            from_email=None,
            recipient_list=[user.email],
        )

        return Response(
            {
                "detail": (
                    "If an account with that email exists, "
                    "a password reset email has been sent."
                )
            },
            status=200
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    POST /api/accounts/password/reset/confirm/ - confirm a
    password reset using the uid and token.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(
                urlsafe_base64_decode(uid)
            )
            user = User.objects.get(
                pk=user_id,
                is_active=True
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist
        ):
            return Response(
                {
                    "detail": "Invalid password reset link."
                },
                status=400
            )

        if not default_token_generator.check_token(
            user,
            token
        ):
            return Response(
                {
                    "detail": "Invalid or expired password reset token."
                },
                status=400
            )

        password_validation.validate_password(
            new_password,
            user
        )

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response(
            {
                "detail": "Password has been reset successfully."
            },
            status=200
        )


class UserListView(generics.ListAPIView):
    """
    GET /api/accounts/users/ - list all users (admin only)
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/accounts/users/<id>/ - manage
    any user (admin only)
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]
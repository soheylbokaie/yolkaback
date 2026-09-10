from django.shortcuts import render

# Create your views here.
from django.utils.crypto import get_random_string

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import User

from api.serializers import UserSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def user_list(request):

    users = User.objects.all().order_by("-created_at")

    paginator = PageNumberPagination()
    paginator.page_size = 20

    result_page = paginator.paginate_queryset(
        users,
        request,
    )

    serializer = UserSerializer(
        result_page,
        many=True,
        context={"request": request},
    )

    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def customer_list(request):

    customers = User.objects.filter(role=User.Role.CUSTOMER).order_by("-created_at")

    paginator = PageNumberPagination()
    paginator.page_size = 10

    result_page = paginator.paginate_queryset(
        customers,
        request,
    )

    serializer = UserSerializer(
        result_page,
        many=True,
        context={"request": request},
    )

    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def filter_customers_by_date(request):
    """
    Filter customers by created_at date range.

    Query params:
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
    """

    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    if not start_date or not end_date:
        return Response(
            {"detail": "start_date and end_date are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from datetime import datetime

        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

    except ValueError:
        return Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if start > end:
        return Response(
            {"detail": "start_date cannot be greater than end_date."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    customers = User.objects.filter(
        role=User.Role.CUSTOMER,
        created_at__date__gte=start,
        created_at__date__lte=end,
    ).order_by("-created_at")

    serializer = UserSerializer(
        customers,
        many=True,
        context={"request": request},
    )

    return Response(
        {
            "count": customers.count(),
            "results": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_by_id(
    request,
    user_id,
):

    try:
        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response(
            {"detail": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UserSerializer(
        user,
        context={"request": request},
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def toggle_active_user(
    request,
    user_id,
):

    try:
        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response(
            {"detail": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.is_active = not user.is_active
    user.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    return Response(
        {
            "detail": "User active status updated.",
            "user_id": user.id,
            "is_active": user.is_active,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):

    data = request.data.copy()

    data["role"] = User.Role.CUSTOMER

    serializer = UserSerializer(
        data=data,
        context={"request": request},
    )

    if serializer.is_valid():

        user = serializer.save()

        return Response(
            UserSerializer(
                user,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_by_email(
    request,
    email,
):

    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:

        return Response(
            {"detail": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UserSerializer(
        user,
        context={"request": request},
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )

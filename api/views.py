from decimal import Decimal

from django.db import transaction
from django.utils.crypto import get_random_string

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from users.models import User, Address
from catalog.models import Product, ProductVariant

from orders.models import Order, OrderItem
from .serializers.user import AddressSerializer, UserSerializer

# ============================================================
# HELPERS
# ============================================================


def generate_order_number():
    """
    Generate a unique order number.
    Example:
        ORD-A8K29FJ31P
    """

    while True:
        order_number = f"ORD-{get_random_string(10).upper()}"

        if not Order.objects.filter(order_number=order_number).exists():
            return order_number


def get_product_price(product, variant=None):
    """
    Get price and SKU from product/variant.

    Assumes:
        Product.price
        Product.sku
        ProductVariant.price
        ProductVariant.sku
    """

    if variant is not None:
        return (
            Decimal(str(variant.price)),
            variant.sku,
        )

    return (
        Decimal(str(product.price)),
        product.sku,
    )


def recalculate_order(order):
    """
    Recalculate subtotal and total from OrderItems.
    """

    subtotal = sum(
        (item.total_price for item in order.items.all()),
        Decimal("0"),
    )

    discount = Decimal(str(order.discount or 0))

    shipping_cost = Decimal(str(order.shipping_cost or 0))

    total = subtotal - discount + shipping_cost

    if total < 0:
        total = Decimal("0")

    order.subtotal = subtotal
    order.total = total

    order.save(
        update_fields=[
            "subtotal",
            "total",
            "updated_at",
        ]
    )


def serialize_address(address):
    if not address:
        return None

    return {
        "id": address.id,
        "title": address.title,
        "address_type": address.address_type,
        "recipient_name": address.recipient_name,
        "recipient_phone": address.recipient_phone,
        "province": address.province,
        "city": address.city,
        "address": address.address,
        "postal_code": address.postal_code,
        "latitude": (str(address.latitude) if address.latitude is not None else None),
        "longitude": (
            str(address.longitude) if address.longitude is not None else None
        ),
        "is_default": address.is_default,
    }


def serialize_order(order):
    """
    Serialize an Order for API responses.
    """

    return {
        "id": order.id,
        "order_number": order.order_number,
        "user": {
            "id": order.user.id,
            "email": order.user.email,
            "first_name": order.user.first_name,
            "last_name": order.user.last_name,
            "phone_number": order.user.phone_number,
        },
        "address": serialize_address(order.address),
        "status": order.status,
        "subtotal": str(order.subtotal),
        "discount": str(order.discount),
        "shipping_cost": str(order.shipping_cost),
        "total": str(order.total),
        "coupon_code": order.coupon_code,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "product_name": item.product_name,
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "total_price": str(item.total_price),
                "created_at": item.created_at,
            }
            for item in order.items.all()
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


# ============================================================
# USERS
# ============================================================


# ============================================================
# CREATE ORDER
# ============================================================


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def create_order(request):

    data = request.data

    user_id = data.get("user_id")

    address_id = data.get("address_id")

    items = data.get("items")

    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    if not user_id:

        return Response(
            {"detail": "user_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response(
            {"detail": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # Items
    # --------------------------------------------------------

    if not items:

        return Response(
            {"detail": "items is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(items, list):

        return Response(
            {"detail": "items must be an array."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Address
    # --------------------------------------------------------

    address = None

    if address_id:

        try:

            address = Address.objects.get(
                id=address_id,
                user=user,
            )

        except Address.DoesNotExist:

            return Response(
                {"detail": ("Address not found " "for this user.")},
                status=status.HTTP_404_NOT_FOUND,
            )

    # --------------------------------------------------------
    # Discount / shipping
    # --------------------------------------------------------

    try:

        discount = Decimal(
            str(
                data.get(
                    "discount",
                    "0",
                )
            )
        )

        shipping_cost = Decimal(
            str(
                data.get(
                    "shipping_cost",
                    "0",
                )
            )
        )

    except Exception:

        return Response(
            {"detail": ("discount and shipping_cost " "must be valid numbers.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if discount < 0:

        return Response(
            {"detail": "discount cannot be negative."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if shipping_cost < 0:

        return Response(
            {"detail": ("shipping_cost cannot be negative.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Create order
    # --------------------------------------------------------

    order = Order.objects.create(
        user=user,
        address=address,
        order_number=generate_order_number(),
        status=Order.Status.PENDING,
        discount=discount,
        shipping_cost=shipping_cost,
        coupon_code=data.get(
            "coupon_code",
            "",
        ),
        notes=data.get(
            "notes",
            "",
        ),
    )

    # --------------------------------------------------------
    # Create order items
    # --------------------------------------------------------

    for item in items:

        product_id = item.get("product_id")

        variant_id = item.get("variant_id")

        quantity = item.get(
            "quantity",
            1,
        )

        if not product_id:

            return Response(
                {"detail": ("product_id is required " "for every item.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            quantity = int(quantity)

        except (
            TypeError,
            ValueError,
        ):

            return Response(
                {"detail": ("quantity must be an integer.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:

            return Response(
                {"detail": ("quantity must be greater than 0.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Product
        # ----------------------------------------------------

        try:

            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:

            return Response(
                {"detail": (f"Product {product_id} " "not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # Variant
        # ----------------------------------------------------

        variant = None

        if variant_id:

            try:

                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                )

            except ProductVariant.DoesNotExist:

                return Response(
                    {
                        "detail": (
                            f"Variant {variant_id} " "not found for this product."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        unit_price, sku = get_product_price(
            product,
            variant,
        )

        total_price = unit_price * quantity

        # ----------------------------------------------------
        # Create item
        # ----------------------------------------------------

        OrderItem.objects.create(
            order=order,
            product=product,
            variant=variant,
            product_name=product.name,
            sku=sku,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
        )

    # --------------------------------------------------------
    # Calculate totals
    # --------------------------------------------------------

    recalculate_order(order)

    order.refresh_from_db()

    return Response(
        {
            "detail": "Order created successfully.",
            "order": serialize_order(order),
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# ADD PRODUCT TO ORDER
# ============================================================


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def add_product_to_order(
    request,
    order_id,
    product_id,
):

    # --------------------------------------------------------
    # Order
    # --------------------------------------------------------

    try:

        order = Order.objects.get(id=order_id)

    except Order.DoesNotExist:

        return Response(
            {"detail": "Order not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # Only pending orders can change
    # --------------------------------------------------------

    if order.status != Order.Status.PENDING:

        return Response(
            {"detail": ("Products can only be added " "to pending orders.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    quantity = request.data.get(
        "quantity",
        1,
    )

    try:

        quantity = int(quantity)

    except (
        TypeError,
        ValueError,
    ):

        return Response(
            {"detail": ("quantity must be an integer.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity <= 0:

        return Response(
            {"detail": ("quantity must be greater than 0.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    try:

        product = Product.objects.get(id=product_id)

    except Product.DoesNotExist:

        return Response(
            {"detail": "Product not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # Variant
    # --------------------------------------------------------

    variant_id = request.data.get("variant_id")

    variant = None

    if variant_id:

        try:

            variant = ProductVariant.objects.get(
                id=variant_id,
                product=product,
            )

        except ProductVariant.DoesNotExist:

            return Response(
                {"detail": "Variant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    unit_price, sku = get_product_price(
        product,
        variant,
    )

    # --------------------------------------------------------
    # Find existing item
    # --------------------------------------------------------

    order_item = OrderItem.objects.filter(
        order=order,
        product=product,
        variant=variant,
    ).first()

    if order_item:

        order_item.quantity += quantity

    else:

        order_item = OrderItem(
            order=order,
            product=product,
            variant=variant,
            product_name=product.name,
            sku=sku,
            quantity=quantity,
            unit_price=unit_price,
            total_price=(unit_price * quantity),
        )

    order_item.unit_price = unit_price

    order_item.total_price = unit_price * order_item.quantity

    order_item.save()

    # --------------------------------------------------------
    # Recalculate
    # --------------------------------------------------------

    recalculate_order(order)

    order.refresh_from_db()

    return Response(
        {
            "detail": "Product added to order.",
            "order": serialize_order(order),
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# REMOVE PRODUCT FROM ORDER
# ============================================================


@api_view(["DELETE"])
@permission_classes([AllowAny])
@transaction.atomic
def remove_product_from_order(
    request,
    order_id,
    product_id,
):

    # --------------------------------------------------------
    # Order
    # --------------------------------------------------------

    try:

        order = Order.objects.get(id=order_id)

    except Order.DoesNotExist:

        return Response(
            {"detail": "Order not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if order.status != Order.Status.PENDING:

        return Response(
            {"detail": ("Products can only be removed " "from pending orders.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Variant
    # --------------------------------------------------------

    variant_id = request.query_params.get("variant_id")

    queryset = OrderItem.objects.filter(
        order=order,
        product_id=product_id,
    )

    if variant_id:

        queryset = queryset.filter(variant_id=variant_id)

    else:

        queryset = queryset.filter(variant__isnull=True)

    order_item = queryset.first()

    if not order_item:

        return Response(
            {"detail": ("Product is not in this order.")},
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    order_item.delete()

    # --------------------------------------------------------
    # Recalculate
    # --------------------------------------------------------

    recalculate_order(order)

    order.refresh_from_db()

    return Response(
        {
            "detail": "Product removed from order.",
            "order": serialize_order(order),
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# UPDATE ORDER STATUS
# ============================================================


@api_view(["PUT", "PATCH"])
@permission_classes([AllowAny])
def update_order_status(
    request,
    order_id,
):

    new_status = request.data.get("status")

    if not new_status:

        return Response(
            {"detail": "status is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    valid_statuses = [value for value, label in Order.Status.choices]

    if new_status not in valid_statuses:

        return Response(
            {
                "detail": "Invalid order status.",
                "allowed_statuses": valid_statuses,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Order
    # --------------------------------------------------------

    try:

        order = Order.objects.get(id=order_id)

    except Order.DoesNotExist:

        return Response(
            {"detail": "Order not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    order.status = new_status

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return Response(
        {
            "detail": "Order status updated.",
            "order": serialize_order(order),
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# GET ORDER DETAILS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def get_order_details(
    request,
    order_id,
):

    try:

        order = (
            Order.objects.select_related(
                "user",
                "address",
            )
            .prefetch_related("items")
            .get(id=order_id)
        )

    except Order.DoesNotExist:

        return Response(
            {"detail": "Order not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        serialize_order(order),
        status=status.HTTP_200_OK,
    )


# ============================================================
# LIST ORDERS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def list_orders(request):

    orders = (
        Order.objects.select_related(
            "user",
            "address",
        )
        .prefetch_related("items")
        .order_by("-created_at")
    )

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    user_id = request.query_params.get("user_id")

    order_status = request.query_params.get("status")

    order_number = request.query_params.get("order_number")

    if user_id:

        orders = orders.filter(user_id=user_id)

    if order_status:

        orders = orders.filter(status=order_status)

    if order_number:

        orders = orders.filter(order_number__icontains=order_number)

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    paginator = PageNumberPagination()

    paginator.page_size = 10

    result_page = paginator.paginate_queryset(
        orders,
        request,
    )

    data = [serialize_order(order) for order in result_page]

    return paginator.get_paginated_response(data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def address_list(request):

    # GET /api/addresses/
    if request.method == "GET":

        user_id = request.query_params.get("user_id")

        addresses = Address.objects.select_related("user").all()

        if user_id:
            addresses = addresses.filter(user_id=user_id)

        serializer = AddressSerializer(
            addresses,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # POST /api/addresses/

    user_id = request.data.get("user_id")

    if not user_id:
        return Response(
            {"user_id": ["This field is required."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"user_id": ["User not found."]},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AddressSerializer(
        data=request.data,
        context={"request": request},
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():

        # If this address should be default,
        # remove default from existing addresses.
        if serializer.validated_data.get("is_default", False):

            Address.objects.filter(
                user=user,
                is_default=True,
            ).update(is_default=False)

        address = serializer.save(user=user)

    return Response(
        AddressSerializer(
            address,
            context={"request": request},
        ).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def address_detail(request, address_id):

    try:
        address = Address.objects.select_related("user").get(id=address_id)
    except Address.DoesNotExist:
        return Response(
            {"detail": "Address not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # GET
    if request.method == "GET":

        serializer = AddressSerializer(
            address,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # PUT / PATCH
    if request.method in ["PUT", "PATCH"]:

        serializer = AddressSerializer(
            address,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():

            if serializer.validated_data.get("is_default", False):
                Address.objects.filter(
                    user=address.user,
                    is_default=True,
                ).exclude(
                    id=address.id
                ).update(is_default=False)

            address = serializer.save()

        return Response(
            AddressSerializer(
                address,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    # DELETE
    if request.method == "DELETE":

        address.delete()

        return Response(
            {"detail": "Address deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

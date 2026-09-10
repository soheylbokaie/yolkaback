from django.urls import path

from .views import *
from users.views import *

urlpatterns = [
    # ========================================================
    # USERS
    # ========================================================
    path(
        "users/",
        user_list,
        name="user-list",
    ),
    path(
        "customers/",
        customer_list,
        name="customer-list",
    ),
    path(
        "create-user/",
        create_user,
        name="create-user",
    ),
    path(
        "users/<int:user_id>/",
        get_user_by_id,
        name="get-user-by-id",
    ),
    path(
        "users/<int:user_id>/toggle-active/",
        toggle_active_user,
        name="toggle-active-user",
    ),
    path(
        "users/email/<str:email>/",
        get_user_by_email,
        name="get-user-by-email",
    ),
    # ========================================================
    # ORDERS
    # ========================================================
    path(
        "orders/",
        list_orders,
        name="order-list",
    ),
    path(
        "orders/create/",
        create_order,
        name="order-create",
    ),
    path(
        "orders/<int:order_id>/",
        get_order_details,
        name="order-details",
    ),
    path(
        "orders/<int:order_id>/status/",
        update_order_status,
        name="order-status",
    ),
    path(
        "orders/<int:order_id>/products/<int:product_id>/add/",
        add_product_to_order,
        name="order-add-product",
    ),
    path(
        "orders/<int:order_id>/products/<int:product_id>/remove/",
        remove_product_from_order,
        name="order-remove-product",
    ),
    path(
        "addresses/",
        address_list,
        name="address-list",
    ),
    path(
        "addresses/<int:address_id>/",
        address_detail,
        name="address-detail",
    ),
    path(
        "customers/filter-by-date/",
        filter_customers_by_date,
        name="filter-customers-by-date",
    ),
]

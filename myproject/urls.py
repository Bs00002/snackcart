from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from myapp1 import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Public Pages ──
    path('', views.index),
    path('about', views.about),
    path('contact', views.contact),
    path('menu', views.menu),
    path('sellers', views.sellers_list),
    path('seller-detail/<int:sid>', views.seller_detail),
    path('product-detail/<int:pid>', views.product_detail),

    # ── Auth ──
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('forgot-password', views.forgot_password),
    path('change-password', views.change_password),

    # ── Customer ──
    path('customer/dashboard', views.customer_dashboard),
    path('customer/profile', views.customer_profile),
    path('customer/add-address', views.add_address),
    path('customer/orders', views.customer_orders),
    path('customer/order-detail/<int:oid>', views.order_detail),
    path('customer/cancel-order/<int:oid>', views.cancel_order),
    path('customer/review/<int:oid>', views.submit_review),
    path('customer/complaint/<int:oid>', views.submit_complaint),
    path('customer/complaints', views.customer_complaints),

    # ── Order & Payment ──
    path('place-order/<int:pid>', views.place_order),
    path('confirm-order', views.confirm_order),
    path('payment-success', views.payment_success),

    # ── Inquiry ──
    path('inquiry', views.general_inquiry),

    # ── Seller ──
    path('seller/complete-profile', views.seller_complete_profile),
    path('seller/dashboard', views.seller_dashboard),
    path('seller/add-product', views.seller_add_product),
    path('seller/products', views.seller_products),
    path('seller/edit-product/<int:pid>', views.seller_edit_product),
    path('seller/delete-product/<int:pid>', views.seller_delete_product),
    path('seller/orders', views.seller_orders),
    path('seller/update-order/<int:oid>', views.seller_update_order_status),
    path('seller/earnings', views.seller_earnings),
    path('seller/subscription', views.seller_subscription),
    path('seller/subscription-success', views.subscription_success),

    # ── Admin ──
    path('admin-dashboard', views.admin_dashboard),
    path('admin/sellers', views.admin_sellers),
    path('admin/approve-seller/<int:sid>', views.admin_approve_seller),
    path('admin/reject-seller/<int:sid>', views.admin_reject_seller),
    path('admin/users', views.admin_users),
    path('admin/approve-user/<int:uid>', views.admin_approve_user),
    path('admin/reject-user/<int:uid>', views.admin_reject_user),
    path('admin/orders', views.admin_orders),
    path('admin/complaints', views.admin_complaints),
    path('admin/resolve-complaint/<int:cid>', views.admin_resolve_complaint),
    path('admin/categories', views.admin_categories),
    path('admin/delete-category/<int:cid>', views.admin_delete_category),
    path('admin/inquiries', views.admin_inquiries),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import mark_safe
from .models import (
    User, SellerProfile, Subscription, Category, Product,
    CustomerAddress, Order, Review, Complaint, Inquiry, Contact,
)
from .reports import generate_order_report_pdf, generate_payment_report_pdf


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: build a coloured badge safely (no format_html + em-dash issues)
# ─────────────────────────────────────────────────────────────────────────────
def badge(label, color):
    return mark_safe(
        f'<span style="background:{color};color:#fff;padding:2px 10px;'
        f'border-radius:10px;font-size:11px;font-weight:600;">'
        f'{label}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT ACTIONS
# ─────────────────────────────────────────────────────────────────────────────
def export_order_pdf(modeladmin, request, queryset):
    orders = queryset.select_related('customer', 'seller', 'product')
    buf = generate_order_report_pdf(orders, date_range='Selected Orders')
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_report.pdf"'
    return response
export_order_pdf.short_description = 'Export Order Report (PDF)'


def export_payment_pdf(modeladmin, request, queryset):
    orders = queryset.select_related('customer', 'seller', 'product')
    buf = generate_payment_report_pdf(orders, date_range='Selected Period')
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payment_report.pdf"'
    return response
export_payment_pdf.short_description = 'Export Payment Report (PDF)'


# ─────────────────────────────────────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'email', 'phone', 'role', 'status_badge', 'created_at')
    list_filter   = ('role', 'status')
    search_fields = ('name', 'email', 'phone')
    ordering      = ('-created_at',)
    list_per_page = 20

    def status_badge(self, obj):
        MAP = {'0': ('#F39C12', 'Unapproved'), '1': ('#27AE60', 'Approved'), '2': ('#E74C3C', 'Rejected')}
        color, label = MAP.get(str(obj.status), ('#888888', str(obj.status)))
        return badge(label, color)
    status_badge.short_description = 'Status'


# ─────────────────────────────────────────────────────────────────────────────
# SELLER PROFILE
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display  = ('id', 'kitchen_name', 'user', 'kitchen_city',
                     'verified_badge', 'rating', 'total_orders', 'subscription_badge', 'created_at')
    list_filter   = ('is_verified', 'kitchen_city')
    search_fields = ('kitchen_name', 'user__name', 'user__email', 'kitchen_city', 'mobile_number')
    ordering      = ('-created_at',)
    list_per_page = 20

    def verified_badge(self, obj):
        if obj.is_verified:
            return badge('Verified', '#27AE60')
        return badge('Pending', '#E74C3C')
    verified_badge.short_description = 'Verified'

    def subscription_badge(self, obj):
        if obj.free_orders_used < 11:
            rem = 11 - obj.free_orders_used
            return badge(f'Free ({rem} left)', '#F39C12')
        try:
            if obj.is_subscription_active():
                return badge('Active', '#2980B9')
        except Exception:
            pass
        return badge('Expired', '#888888')
    subscription_badge.short_description = 'Subscription'


# ─────────────────────────────────────────────────────────────────────────────
# SUBSCRIPTION
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('id', 'seller', 'amount', 'start_date', 'end_date', 'active_badge', 'razorpay_payment_id')
    list_filter   = ('is_active',)
    search_fields = ('seller__kitchen_name', 'razorpay_payment_id')
    ordering      = ('-start_date',)
    list_per_page = 20

    def active_badge(self, obj):
        return badge('Active', '#27AE60') if obj.is_active else badge('Inactive', '#888888')
    active_badge.short_description = 'Status'


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('id', 'category_name', 'product_count')
    search_fields = ('category_name',)
    ordering      = ('category_name',)
    list_per_page = 20

    def product_count(self, obj):
        count = Product.objects.filter(category=obj).count()
        return mark_safe(f'<b style="color:#FF6B35;">{count}</b> products')
    product_count.short_description = 'Products'


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('id', 'product_name', 'seller', 'category', 'price',
                     'stock_qty', 'status_badge', 'ordered_count', 'customizable_badge')
    list_filter   = ('status', 'category', 'is_customizable', 'quantity_unit')
    search_fields = ('product_name', 'seller__name', 'ingredients', 'description')
    ordering      = ('-id',)
    list_per_page = 20

    def status_badge(self, obj):
        MAP = {'Available': '#27AE60', 'Unavailable': '#E74C3C'}
        color = MAP.get(obj.status, '#888888')
        return badge(obj.status, color)
    status_badge.short_description = 'Status'

    def customizable_badge(self, obj):
        if obj.is_customizable:
            return mark_safe('<span style="color:#2980B9;font-weight:bold;">Yes</span>')
        return mark_safe('<span style="color:#aaaaaa;">No</span>')
    customizable_badge.short_description = 'Custom'


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER ADDRESS
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'receiver_name', 'contact_number', 'address_preview', 'default_badge')
    list_filter   = ('is_default',)
    search_fields = ('user__name', 'receiver_name', 'contact_number', 'full_address')
    ordering      = ('-id',)
    list_per_page = 20

    def address_preview(self, obj):
        txt = obj.full_address or ''
        return (txt[:45] + '...') if len(txt) > 45 else txt
    address_preview.short_description = 'Address'

    def default_badge(self, obj):
        if obj.is_default:
            return mark_safe('<span style="color:#27AE60;font-weight:bold;">Default</span>')
        return '-'
    default_badge.short_description = 'Default'


# ─────────────────────────────────────────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'customer', 'seller', 'product_short', 'quantity',
                     'total_amount', 'mode_badge', 'payment_badge', 'order_badge', 'created_at')
    list_filter   = ('order_status', 'payment_status', 'payment_mode')
    search_fields = ('customer__name', 'seller__name', 'product__product_name',
                     'delivery_address', 'razorpay_order_id')
    ordering      = ('-created_at',)
    list_per_page = 20
    actions       = [export_order_pdf, export_payment_pdf]

    def product_short(self, obj):
        name = obj.product.product_name if obj.product else '-'
        return name[:22] if len(name) > 22 else name
    product_short.short_description = 'Product'

    def mode_badge(self, obj):
        if obj.payment_mode == 'online':
            return badge('Online', '#2980B9')
        return badge('COD', '#7F8C8D')
    mode_badge.short_description = 'Mode'

    def payment_badge(self, obj):
        MAP = {'Paid': '#27AE60', 'Pending': '#F39C12', 'Failed': '#E74C3C', 'Refunded': '#8E44AD'}
        color = MAP.get(obj.payment_status, '#888888')
        label = obj.payment_status if obj.payment_status else 'Unknown'
        return badge(label, color)
    payment_badge.short_description = 'Payment'

    def order_badge(self, obj):
        MAP = {
            'Pending':          '#F39C12',
            'Accepted':         '#2980B9',
            'Preparing':        '#8E44AD',
            'Ready for Pickup': '#16A085',
            'Out for Delivery': '#2471A3',
            'Delivered':        '#27AE60',
            'Completed':        '#1E8449',
            'Cancelled':        '#E74C3C',
        }
        color = MAP.get(obj.order_status, '#888888')
        label = obj.order_status if obj.order_status else 'Unknown'
        return badge(label, color)
    order_badge.short_description = 'Order Status'


# ─────────────────────────────────────────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('id', 'customer', 'seller', 'order', 'star_rating', 'created_at')
    list_filter   = ('rating',)
    search_fields = ('customer__name', 'seller__kitchen_name', 'comment')
    ordering      = ('-created_at',)
    list_per_page = 20

    def star_rating(self, obj):
        r = int(obj.rating or 0)
        stars = ('&#9733;' * r) + ('&#9734;' * (5 - r))
        color = '#F39C12' if r >= 3 else '#E74C3C'
        return mark_safe(f'<span style="color:{color};font-size:14px;">{stars}</span> ({obj.rating})')
    star_rating.short_description = 'Rating'


# ─────────────────────────────────────────────────────────────────────────────
# COMPLAINT
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ('id', 'customer', 'order', 'issue_type', 'status_badge', 'refund_badge', 'created_at')
    list_filter   = ('status', 'issue_type', 'refund_processed')
    search_fields = ('customer__name', 'description', 'admin_note')
    ordering      = ('-created_at',)
    list_per_page = 20

    def status_badge(self, obj):
        MAP = {'Pending': '#F39C12', 'Under Review': '#2980B9', 'Resolved': '#27AE60', 'Rejected': '#E74C3C'}
        color = MAP.get(obj.status, '#888888')
        label = obj.status if obj.status else 'Unknown'
        return badge(label, color)
    status_badge.short_description = 'Status'

    def refund_badge(self, obj):
        if obj.refund_processed:
            return mark_safe('<span style="color:#8E44AD;font-weight:bold;">Refunded</span>')
        return '-'
    refund_badge.short_description = 'Refund'


# ─────────────────────────────────────────────────────────────────────────────
# INQUIRY
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'subject', 'status_badge', 'created_at')
    list_filter   = ('status',)
    search_fields = ('user__name', 'user__email', 'subject', 'message')
    ordering      = ('-created_at',)
    list_per_page = 20

    def status_badge(self, obj):
        color = '#27AE60' if obj.status == 'Resolved' else '#F39C12'
        label = obj.status if obj.status else 'Pending'
        return badge(label, color)
    status_badge.short_description = 'Status'


# ─────────────────────────────────────────────────────────────────────────────
# CONTACT
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering      = ('-created_at',)
    list_per_page = 20

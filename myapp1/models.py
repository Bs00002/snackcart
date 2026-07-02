from django.db import models
from django.utils import timezone


class User(models.Model):
    ROLE = (
        ('Customer', 'Customer'),
        ('Seller', 'Seller'),
        ('Admin', 'Admin'),
    )
    STATUS = (
        ("0", "Unapproved"),
        ("1", "Approved"),
        ("2", "Rejected"),
    )
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE, default='Customer')
    status = models.CharField(max_length=10, choices=STATUS, default='1')  # customers auto-approved
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kitchen_name = models.CharField(max_length=200)
    contact_email = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=15)
    kitchen_address = models.TextField()
    kitchen_city = models.CharField(max_length=100)
    kitchen_pincode = models.CharField(max_length=10)
    pan_card = models.FileField(upload_to='seller_docs/', blank=True, null=True)
    aadhaar_card = models.FileField(upload_to='seller_docs/', blank=True, null=True)
    fssai_certificate = models.FileField(upload_to='seller_docs/')
    bank_account = models.CharField(max_length=100, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='seller_images/', blank=True, null=True)
    kitchen_image = models.ImageField(upload_to='seller_images/', blank=True, null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    available_days = models.CharField(max_length=100, default='Mon,Tue,Wed,Thu,Fri,Sat,Sun')
    is_verified = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    total_orders = models.PositiveIntegerField(default=0)
    free_orders_used = models.PositiveIntegerField(default=0)   # track trial usage
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.kitchen_name

    def is_subscription_active(self):
        if self.free_orders_used < 11:
            return True
        active_sub = Subscription.objects.filter(seller=self, is_active=True, end_date__gte=timezone.now().date()).first()
        return active_sub is not None


class Subscription(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    amount = models.FloatField(default=199.0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription - {self.seller.kitchen_name}"


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_photo = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    QUANTITY_UNIT = (
        ('Per Piece', 'Per Piece'),
        ('Per Plate', 'Per Plate'),
        ('250g', '250g'),
        ('500g', '500g'),
        ('1 KG', '1 KG'),
        ('Custom', 'Custom'),
    )
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=150)
    description = models.TextField()
    ingredients = models.TextField()
    expiry_time = models.CharField(max_length=100)
    preparation_time = models.CharField(max_length=100)
    estimated_delivery_time = models.CharField(max_length=100, blank=True, null=True)
    quantity_unit = models.CharField(max_length=30, choices=QUANTITY_UNIT, default='Per Piece')
    custom_unit = models.CharField(max_length=50, blank=True, null=True)
    price = models.FloatField()
    stock_qty = models.PositiveIntegerField(default=0)
    max_orders_per_day = models.PositiveIntegerField(default=10)
    is_customizable = models.BooleanField(default=False)
    product_photo = models.ImageField(upload_to='product_images/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    ordered_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name


class CustomerAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=15)
    full_address = models.TextField()
    landmark = models.CharField(max_length=200, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.receiver_name} - {self.full_address[:40]}"


class Order(models.Model):
    PAYMENT_MODE = (
        ('online', 'Online Payment'),
        ('cod', 'Cash on Delivery'),
    )
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    )
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Preparing', 'Preparing'),
        ('Ready for Pickup', 'Ready for Pickup'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    food_price = models.FloatField()
    platform_fee = models.FloatField(default=10.0)
    delivery_charge = models.FloatField(default=40.0)
    total_amount = models.FloatField()
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    order_status = models.CharField(max_length=30, choices=ORDER_STATUS, default='Pending')
    delivery_address = models.TextField()
    customization_note = models.TextField(blank=True, null=True)
    customization_image = models.ImageField(upload_to='customization/', blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    commission_percent = models.FloatField(default=10.0)
    seller_earning = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product.product_name}"


class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review #{self.id} - {self.rating} stars"


class Complaint(models.Model):
    ISSUE_TYPES = (
        ('Wrong item delivered', 'Wrong item delivered'),
        ('Food quality issue', 'Food quality issue'),
        ('Late delivery', 'Late delivery'),
        ('Missing item', 'Missing item'),
        ('Other', 'Other'),
    )
    STATUS = (
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS, default='Pending')
    admin_note = models.TextField(blank=True, null=True)
    refund_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.id} - {self.issue_type}"


class Inquiry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

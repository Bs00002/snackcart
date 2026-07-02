from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import *
import razorpay


# ─────────────────────────────────────────────
# SESSION HELPER
# ─────────────────────────────────────────────

def checksession(request):
    uid = request.session.get('log_id')
    categories = Category.objects.all()
    sellers = SellerProfile.objects.filter(is_verified=True)

    context = {
        "userdata": None,
        "is_seller": False,
        "is_admin": False,
        "is_customer": False,
        "categories": categories,
        "sellers": sellers,
    }

    if uid:
        try:
            userdata = User.objects.get(id=uid)
            context["userdata"] = userdata
            context["is_seller"] = (userdata.role == "Seller")
            context["is_admin"] = (userdata.role == "Admin")
            context["is_customer"] = (userdata.role == "Customer")
        except User.DoesNotExist:
            pass

    return context


def login_required_redirect(request):
    if not request.session.get('log_id'):
        messages.error(request, "Please login to continue.")
        return True
    return False


# ─────────────────────────────────────────────
# PUBLIC / HOME
# ─────────────────────────────────────────────

def index(request):
    context = checksession(request)
    products = Product.objects.filter(status='Available')
    sellers = SellerProfile.objects.filter(is_verified=True)
    categories = Category.objects.all()

    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    seller_id = request.GET.get('seller', '')

    if search:
        products = products.filter(product_name__icontains=search)
    if category_id:
        products = products.filter(category_id=category_id)
    if seller_id:
        products = products.filter(seller_id=seller_id)

    context.update({
        'products': products,
        'all_sellers': sellers,
        'search': search,
        'selected_category': category_id,
        'selected_seller': seller_id,
    })
    return render(request, 'home.html', context)


def about(request):
    context = checksession(request)
    return render(request, 'about.html', context)


def contact(request):
    context = checksession(request)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('/contact')
    return render(request, 'contact.html', context)


def sellers_list(request):
    context = checksession(request)
    sellers = SellerProfile.objects.filter(is_verified=True)
    context.update({'sellers': sellers})
    return render(request, 'sellers_list.html', context)


def seller_detail(request, sid):
    context = checksession(request)
    try:
        seller = SellerProfile.objects.get(id=sid, is_verified=True)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Seller not found.")
        return redirect('/sellers')

    products = Product.objects.filter(seller=seller.user, status='Available')
    reviews = Review.objects.filter(seller=seller).order_by('-created_at')
    context.update({'seller': seller, 'products': products, 'reviews': reviews})
    return render(request, 'seller_detail.html', context)


def product_detail(request, pid):
    context = checksession(request)
    try:
        product = Product.objects.get(id=pid, status='Available')
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('/menu')

    seller_profile = None
    try:
        seller_profile = SellerProfile.objects.get(user=product.seller)
    except SellerProfile.DoesNotExist:
        pass

    context.update({'product': product, 'seller_profile': seller_profile})
    return render(request, 'product_detail.html', context)


def menu(request):
    context = checksession(request)
    products = Product.objects.filter(status='Available')
    categories = Category.objects.all()

    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    if search:
        products = products.filter(product_name__icontains=search)
    if category_id:
        products = products.filter(category_id=category_id)

    context.update({
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
    })
    return render(request, 'menu.html', context)


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'Customer')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('/register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('/register')

        if phone and User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already registered!")
            return redirect('/register')

        # Customers auto-approved, Sellers need admin approval
        status = '1' if role == 'Customer' else '0'

        user = User.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role,
            status=status
        )

        if role == 'Customer':
            request.session['log_id'] = user.id
            messages.success(request, f"Welcome {name}! Your account has been created.")
            return redirect('/')
        else:
            messages.success(request, "Seller account created! Please complete your profile and wait for admin approval.")
            request.session['log_id'] = user.id
            return redirect('/seller/complete-profile')

    return render(request, 'register.html', {})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('/login')

        if user.status == '0':
            messages.error(request, "Your account is under review. Please wait for admin approval.")
            return redirect('/login')
        if user.status == '2':
            messages.error(request, "Your account has been rejected. Contact support.")
            return redirect('/login')

        request.session['log_id'] = user.id
        messages.success(request, f"Welcome back, {user.name}!")

        if user.role == 'Admin':
            return redirect('/admin-dashboard')
        elif user.role == 'Seller':
            return redirect('/seller/dashboard')
        else:
            return redirect('/')

    return render(request, 'login.html', {})


def logout(request):
    try:
        del request.session['log_id']
    except KeyError:
        pass
    messages.success(request, "Logged out successfully.")
    return redirect('/')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect('/forgot-password')

        import random, string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        user.password = new_password
        user.save()

        from django.core.mail import send_mail
        try:
            send_mail(
                'SnackCart - Password Reset',
                f'Your new password is: {new_password}',
                'snackcart@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, "New password sent to your email.")
        except Exception:
            messages.error(request, "Could not send email. Please try again.")

        return redirect('/login')

    return render(request, 'forgot_password.html', {})


# ─────────────────────────────────────────────
# CUSTOMER MODULE
# ─────────────────────────────────────────────

def customer_dashboard(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_customer']:
        messages.error(request, "Access denied.")
        return redirect('/')

    uid = request.session['log_id']
    active_orders = Order.objects.filter(customer_id=uid).exclude(order_status__in=['Delivered', 'Completed', 'Cancelled']).order_by('-created_at')
    order_history = Order.objects.filter(customer_id=uid, order_status__in=['Delivered', 'Completed', 'Cancelled']).order_by('-created_at')

    context.update({
        'active_orders': active_orders,
        'order_history': order_history,
    })
    return render(request, 'customer_dashboard.html', context)


def customer_profile(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']
    user = User.objects.get(id=uid)
    addresses = CustomerAddress.objects.filter(user_id=uid)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('/customer/profile')

    context.update({'user': user, 'addresses': addresses})
    return render(request, 'customer_profile.html', context)


def add_address(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if request.method == 'POST':
        receiver_name = request.POST.get('receiver_name')
        contact_number = request.POST.get('contact_number')
        full_address = request.POST.get('full_address')
        landmark = request.POST.get('landmark', '')
        is_default = request.POST.get('is_default') == 'on'

        if is_default:
            CustomerAddress.objects.filter(user_id=uid).update(is_default=False)

        CustomerAddress.objects.create(
            user_id=uid,
            receiver_name=receiver_name,
            contact_number=contact_number,
            full_address=full_address,
            landmark=landmark,
            is_default=is_default
        )
        messages.success(request, "Address added successfully!")
        return redirect('/customer/profile')

    return render(request, 'add_address.html', context)


def place_order(request, pid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)

    if not context['is_customer']:
        messages.error(request, "Only customers can place orders.")
        return redirect('/')

    uid = request.session['log_id']

    try:
        product = Product.objects.get(id=pid, status='Available')
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('/menu')

    # Check address
    addresses = CustomerAddress.objects.filter(user_id=uid)
    if not addresses.exists():
        messages.error(request, "Please add a delivery address before ordering.")
        return redirect('/customer/add-address')

    seller_profile = None
    try:
        seller_profile = SellerProfile.objects.get(user=product.seller)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Seller profile not found.")
        return redirect('/menu')

    if not seller_profile.is_subscription_active():
        messages.error(request, "This seller is currently unavailable.")
        return redirect('/menu')

    quantity = int(request.GET.get('qty', 1))
    food_price = product.price * quantity
    platform_fee = 10.0
    delivery_charge = 40.0
    total = food_price + platform_fee + delivery_charge

    context.update({
        'product': product,
        'seller_profile': seller_profile,
        'addresses': addresses,
        'quantity': quantity,
        'food_price': food_price,
        'platform_fee': platform_fee,
        'delivery_charge': delivery_charge,
        'total': total,
    })
    return render(request, 'place_order.html', context)


def confirm_order(request):
    if login_required_redirect(request):
        return redirect('/login')

    if request.method != 'POST':
        return redirect('/menu')

    uid = request.session['log_id']
    pid = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    address_id = request.POST.get('address_id')
    payment_mode = request.POST.get('payment_mode')
    customization_note = request.POST.get('customization_note', '')
    customization_image = request.FILES.get('customization_image')

    try:
        product = Product.objects.get(id=pid)
        address_obj = CustomerAddress.objects.get(id=address_id, user_id=uid)
    except (Product.DoesNotExist, CustomerAddress.DoesNotExist):
        messages.error(request, "Invalid product or address.")
        return redirect('/menu')

    seller_profile = SellerProfile.objects.get(user=product.seller)

    food_price = product.price * quantity
    platform_fee = 10.0
    delivery_charge = 40.0
    total = food_price + platform_fee + delivery_charge

    commission_percent = 10.0
    seller_earning = food_price - (food_price * commission_percent / 100)

    delivery_address = f"{address_obj.receiver_name}, {address_obj.full_address}"
    if address_obj.landmark:
        delivery_address += f", Near {address_obj.landmark}"
    delivery_address += f" - {address_obj.contact_number}"

    if payment_mode == 'cod':
        order = Order.objects.create(
            customer_id=uid,
            seller_id=product.seller_id,
            product=product,
            quantity=quantity,
            food_price=food_price,
            platform_fee=platform_fee,
            delivery_charge=delivery_charge,
            total_amount=total,
            payment_mode='cod',
            payment_status='Pending',
            order_status='Pending',
            delivery_address=delivery_address,
            customization_note=customization_note,
            customization_image=customization_image,
            commission_percent=commission_percent,
            seller_earning=seller_earning,
        )
        product.ordered_count += 1
        product.save()
        seller_profile.free_orders_used += 1
        seller_profile.total_orders += 1
        seller_profile.save()
        messages.success(request, "Order placed successfully!")
        return redirect('/customer/orders')

    elif payment_mode == 'online':
        client = razorpay.Client(auth=('rzp_test_VQhEfe2NCXbbwI', '2ibreCYL78DA3kjOhobCvz0f'))
        amount = int(total * 100)
        data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"snackcart_order_{uid}",
            "payment_capture": 1
        }
        try:
            rz_order = client.order.create(data=data)
            order = Order.objects.create(
                customer_id=uid,
                seller_id=product.seller_id,
                product=product,
                quantity=quantity,
                food_price=food_price,
                platform_fee=platform_fee,
                delivery_charge=delivery_charge,
                total_amount=total,
                payment_mode='online',
                payment_status='Pending',
                order_status='Pending',
                delivery_address=delivery_address,
                customization_note=customization_note,
                customization_image=customization_image,
                razorpay_order_id=rz_order['id'],
                commission_percent=commission_percent,
                seller_earning=seller_earning,
            )
            product.ordered_count += 1
            product.save()
            seller_profile.free_orders_used += 1
            seller_profile.total_orders += 1
            seller_profile.save()

            return render(request, 'payment_page.html', {
                'order': order,
                'razorpay_order_id': rz_order['id'],
                'razorpay_key': 'rzp_test_VQhEfe2NCXbbwI',
                'amount': amount,
                'total': total,
            })
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('/menu')

    messages.error(request, "Invalid payment mode.")
    return redirect('/menu')


def payment_success(request):
    if request.method == 'POST':
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=('rzp_test_VQhEfe2NCXbbwI', '2ibreCYL78DA3kjOhobCvz0f'))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = 'Paid'
            order.save()
            messages.success(request, "Payment successful! Order confirmed.")
            return render(request, 'payment_success.html', {'order': order, 'success': True})
        except Exception as e:
            return render(request, 'payment_success.html', {'success': False})

    return redirect('/')


def customer_orders(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']
    orders = Order.objects.filter(customer_id=uid).order_by('-created_at')
    context.update({'orders': orders})
    return render(request, 'customer_orders.html', context)


def order_detail(request, oid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']
    try:
        order = Order.objects.get(id=oid, customer_id=uid)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('/customer/orders')
    context.update({'order': order, "status" : ["Pending","Accepted","Preparing","Ready for Pickup","Out for Delivery","Delivered"]})
    return render(request, 'order_detail.html', context)


def cancel_order(request, oid):
    if login_required_redirect(request):
        return redirect('/login')
    uid = request.session['log_id']
    try:
        order = Order.objects.get(id=oid, customer_id=uid)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('/customer/orders')

    if order.order_status in ['Pending', 'Accepted']:
        order.order_status = 'Cancelled'
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "Order cannot be cancelled at this stage.")

    return redirect('/customer/orders')


def submit_review(request, oid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    try:
        order = Order.objects.get(id=oid, customer_id=uid, order_status__in=['Delivered', 'Completed'])
    except Order.DoesNotExist:
        messages.error(request, "Order not found or not yet delivered.")
        return redirect('/customer/orders')

    seller_profile = None
    try:
        seller_profile = SellerProfile.objects.get(user=order.seller)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Seller not found.")
        return redirect('/customer/orders')

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')

        if Review.objects.filter(order=order).exists():
            messages.error(request, "You have already reviewed this order.")
            return redirect('/customer/orders')

        Review.objects.create(
            customer_id=uid,
            seller=seller_profile,
            order=order,
            rating=rating,
            comment=comment
        )

        # Update seller average rating
        reviews = Review.objects.filter(seller=seller_profile)
        avg = sum([r.rating for r in reviews]) / reviews.count()
        seller_profile.rating = round(avg, 1)
        seller_profile.save()

        messages.success(request, "Review submitted successfully!")
        return redirect('/customer/orders')

    context.update({'order': order, 'seller_profile': seller_profile})
    return render(request, 'submit_review.html', context)


def submit_complaint(request, oid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    try:
        order = Order.objects.get(id=oid, customer_id=uid)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('/customer/orders')

    if request.method == 'POST':
        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description')
        Complaint.objects.create(
            customer_id=uid,
            order=order,
            issue_type=issue_type,
            description=description
        )
        messages.success(request, "Complaint submitted. Admin will review it.")
        return redirect('/customer/orders')

    context.update({'order': order})
    return render(request, 'submit_complaint.html', context)


def customer_complaints(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']
    complaints = Complaint.objects.filter(customer_id=uid).order_by('-created_at')
    context.update({'complaints': complaints})
    return render(request, 'customer_complaints.html', context)


def general_inquiry(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']
    inquiries = Inquiry.objects.filter(user_id=uid).order_by('-created_at')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        Inquiry.objects.create(user_id=uid, subject=subject, message=message)
        messages.success(request, "Inquiry submitted successfully.")
        return redirect('/inquiry')

    context.update({'inquiries': inquiries})
    return render(request, 'general_inquiry.html', context)


def change_password(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.get(id=uid)
        if user.password != old_password:
            messages.error(request, "Current password is incorrect.")
            return redirect('/change-password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('/change-password')

        user.password = new_password
        user.save()
        messages.success(request, "Password changed successfully.")
        return redirect('/')

    return render(request, 'change_password.html', context)


# ─────────────────────────────────────────────
# SELLER MODULE
# ─────────────────────────────────────────────

def seller_complete_profile(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    existing = None
    try:
        existing = SellerProfile.objects.get(user_id=uid)
    except SellerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        kitchen_name = request.POST.get('kitchen_name')
        contact_email = request.POST.get('contact_email')
        mobile_number = request.POST.get('mobile_number')
        kitchen_address = request.POST.get('kitchen_address')
        kitchen_city = request.POST.get('kitchen_city')
        kitchen_pincode = request.POST.get('kitchen_pincode')
        bank_account = request.POST.get('bank_account', '')
        upi_id = request.POST.get('upi_id', '')
        opening_time = request.POST.get('opening_time')
        closing_time = request.POST.get('closing_time')
        available_days = ','.join(request.POST.getlist('available_days'))

        fssai_certificate = request.FILES.get('fssai_certificate')
        pan_card = request.FILES.get('pan_card')
        aadhaar_card = request.FILES.get('aadhaar_card')
        profile_photo = request.FILES.get('profile_photo')
        kitchen_image = request.FILES.get('kitchen_image')

        if existing:
            existing.kitchen_name = kitchen_name
            existing.contact_email = contact_email
            existing.mobile_number = mobile_number
            existing.kitchen_address = kitchen_address
            existing.kitchen_city = kitchen_city
            existing.kitchen_pincode = kitchen_pincode
            existing.bank_account = bank_account
            existing.upi_id = upi_id
            existing.opening_time = opening_time
            existing.closing_time = closing_time
            existing.available_days = available_days
            if fssai_certificate:
                existing.fssai_certificate = fssai_certificate
            if pan_card:
                existing.pan_card = pan_card
            if aadhaar_card:
                existing.aadhaar_card = aadhaar_card
            if profile_photo:
                existing.profile_photo = profile_photo
            if kitchen_image:
                existing.kitchen_image = kitchen_image
            existing.is_verified = False
            existing.save()
        else:
            if not fssai_certificate:
                messages.error(request, "FSSAI Certificate is mandatory.")
                return redirect('/seller/complete-profile')

            SellerProfile.objects.create(
                user_id=uid,
                kitchen_name=kitchen_name,
                contact_email=contact_email,
                mobile_number=mobile_number,
                kitchen_address=kitchen_address,
                kitchen_city=kitchen_city,
                kitchen_pincode=kitchen_pincode,
                bank_account=bank_account,
                upi_id=upi_id,
                opening_time=opening_time,
                closing_time=closing_time,
                available_days=available_days,
                fssai_certificate=fssai_certificate,
                pan_card=pan_card,
                aadhaar_card=aadhaar_card,
                profile_photo=profile_photo,
                kitchen_image=kitchen_image,
            )

        # Set user status to pending
        user = User.objects.get(id=uid)
        user.status = '0'
        user.save()

        messages.success(request, "Profile submitted for admin approval!")
        return redirect('/seller/dashboard')

    context.update({'existing': existing, 'days':["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]})
    return render(request, 'seller_complete_profile.html', context)


def seller_dashboard(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    seller_profile = None
    try:
        seller_profile = SellerProfile.objects.get(user_id=uid)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('/seller/complete-profile')

    pending_orders = Order.objects.filter(seller_id=uid, order_status='Pending').order_by('-created_at')
    active_orders = Order.objects.filter(seller_id=uid, order_status__in=['Accepted', 'Preparing', 'Ready for Pickup', 'Out for Delivery']).order_by('-created_at')
    completed_orders = Order.objects.filter(seller_id=uid, order_status__in=['Delivered', 'Completed']).order_by('-created_at')

    total_earnings = sum([o.seller_earning for o in completed_orders])
    subscription_active = seller_profile.is_subscription_active()

    context.update({
        'seller_profile': seller_profile,
        'pending_orders': pending_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'total_earnings': total_earnings,
        'subscription_active': subscription_active,
        "quick_links" : ["products","orders","earnings","subscription","inquiry","password"]
    })
    return render(request, 'seller_dashboard.html', context)


def seller_add_product(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    try:
        seller_profile = SellerProfile.objects.get(user_id=uid, is_verified=True)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Your profile is not verified yet.")
        return redirect('/seller/dashboard')

    categories = Category.objects.all()

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        ingredients = request.POST.get('ingredients')
        expiry_time = request.POST.get('expiry_time')
        preparation_time = request.POST.get('preparation_time')
        estimated_delivery_time = request.POST.get('estimated_delivery_time')
        quantity_unit = request.POST.get('quantity_unit')
        custom_unit = request.POST.get('custom_unit', '')
        price = request.POST.get('price')
        stock_qty = request.POST.get('stock_qty')
        max_orders_per_day = request.POST.get('max_orders_per_day', 10)
        is_customizable = request.POST.get('is_customizable') == 'on'
        product_photo = request.FILES.get('product_photo')

        if not product_photo:
            messages.error(request, "Product photo is required.")
            return redirect('/seller/add-product')

        Product.objects.create(
            seller_id=uid,
            category_id=category_id,
            product_name=product_name,
            description=description,
            ingredients=ingredients,
            expiry_time=expiry_time,
            preparation_time=preparation_time,
            estimated_delivery_time=estimated_delivery_time,
            quantity_unit=quantity_unit,
            custom_unit=custom_unit,
            price=price,
            stock_qty=stock_qty,
            max_orders_per_day=max_orders_per_day,
            is_customizable=is_customizable,
            product_photo=product_photo,
        )
        messages.success(request, "Product added successfully!")
        return redirect('/seller/products')

    context.update({'categories': categories})
    return render(request, 'seller_add_product.html', context)


def seller_products(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    products = Product.objects.filter(seller_id=uid)
    context.update({'products': products})
    return render(request, 'seller_products.html', context)


def seller_edit_product(request, pid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    try:
        product = Product.objects.get(id=pid, seller_id=uid)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('/seller/products')

    categories = Category.objects.all()

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.ingredients = request.POST.get('ingredients')
        product.expiry_time = request.POST.get('expiry_time')
        product.preparation_time = request.POST.get('preparation_time')
        product.estimated_delivery_time = request.POST.get('estimated_delivery_time')
        product.quantity_unit = request.POST.get('quantity_unit')
        product.custom_unit = request.POST.get('custom_unit', '')
        product.price = request.POST.get('price')
        product.stock_qty = request.POST.get('stock_qty')
        product.max_orders_per_day = request.POST.get('max_orders_per_day', 10)
        product.is_customizable = request.POST.get('is_customizable') == 'on'
        product.status = request.POST.get('status', 'Available')
        if request.FILES.get('product_photo'):
            product.product_photo = request.FILES.get('product_photo')
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('/seller/products')

    context.update({'product': product, 'categories': categories, "unitsperplat":["Per Piece","Per Plate","250g","500g","1 KG","Custom"]})
    return render(request, 'seller_edit_product.html', context)


def seller_delete_product(request, pid):
    if login_required_redirect(request):
        return redirect('/login')
    uid = request.session['log_id']
    try:
        product = Product.objects.get(id=pid, seller_id=uid)
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
    return redirect('/seller/products')


def seller_orders(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    orders = Order.objects.filter(seller_id=uid).order_by('-created_at')
    context.update({'orders': orders})
    return render(request, 'seller_orders.html', context)


def seller_update_order_status(request, oid):
    if login_required_redirect(request):
        return redirect('/login')
    uid = request.session['log_id']

    try:
        order = Order.objects.get(id=oid, seller_id=uid)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('/seller/orders')

    new_status = request.POST.get('status')
    valid_statuses = ['Accepted', 'Preparing', 'Ready for Pickup', 'Out for Delivery', 'Delivered', 'Completed', 'Cancelled']

    if new_status in valid_statuses:
        order.order_status = new_status
        order.save()
        messages.success(request, f"Order status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status.")

    return redirect('/seller/orders')


def seller_earnings(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    try:
        seller_profile = SellerProfile.objects.get(user_id=uid)
    except SellerProfile.DoesNotExist:
        return redirect('/seller/complete-profile')

    completed_orders = Order.objects.filter(seller_id=uid, order_status__in=['Delivered', 'Completed'])
    total_earnings = sum([o.seller_earning for o in completed_orders])
    total_commission = sum([(o.food_price * o.commission_percent / 100) for o in completed_orders])

    context.update({
        'seller_profile': seller_profile,
        'completed_orders': completed_orders,
        'total_earnings': total_earnings,
        'total_commission': total_commission,
        'subscription_active': seller_profile.is_subscription_active(),
    })
    return render(request, 'seller_earnings.html', context)


def seller_subscription(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    uid = request.session['log_id']

    if not context['is_seller']:
        messages.error(request, "Access denied.")
        return redirect('/')

    try:
        seller_profile = SellerProfile.objects.get(user_id=uid)
    except SellerProfile.DoesNotExist:
        return redirect('/seller/complete-profile')

    active_subscription = Subscription.objects.filter(
        seller=seller_profile,
        is_active=True,
        end_date__gte=timezone.now().date()
    ).first()

    if request.method == 'POST':
        client = razorpay.Client(auth=('rzp_test_VQhEfe2NCXbbwI', '2ibreCYL78DA3kjOhobCvz0f'))
        amount = int(199 * 100)
        data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"sub_{uid}",
            "payment_capture": 1
        }
        try:
            rz_order = client.order.create(data=data)
            return render(request, 'subscription_payment.html', {
                'razorpay_order_id': rz_order['id'],
                'razorpay_key': 'rzp_test_VQhEfe2NCXbbwI',
                'amount': amount,
                'seller_profile': seller_profile,
            })
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")

    context.update({
        'seller_profile': seller_profile,
        'active_subscription': active_subscription,
        'subscription_active': seller_profile.is_subscription_active(),
    })
    return render(request, 'seller_subscription.html', context)


def subscription_success(request):
    if request.method == 'POST':
        uid = request.session.get('log_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=('rzp_test_VQhEfe2NCXbbwI', '2ibreCYL78DA3kjOhobCvz0f'))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            seller_profile = SellerProfile.objects.get(user_id=uid)
            today = timezone.now().date()
            from datetime import timedelta
            Subscription.objects.create(
                seller=seller_profile,
                start_date=today,
                end_date=today + timedelta(days=30),
                razorpay_payment_id=razorpay_payment_id,
                is_active=True
            )
            messages.success(request, "Subscription activated for 30 days!")
            return redirect('/seller/subscription')
        except Exception as e:
            messages.error(request, "Subscription payment failed.")
            return redirect('/seller/subscription')

    return redirect('/')


# ─────────────────────────────────────────────
# ADMIN MODULE
# ─────────────────────────────────────────────

def admin_dashboard(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)

    if not context['is_admin']:
        messages.error(request, "Admin access only.")
        return redirect('/')

    total_users = User.objects.filter(role='Customer').count()
    total_sellers = User.objects.filter(role='Seller').count()
    pending_sellers = SellerProfile.objects.filter(is_verified=False, user__status='0').count()
    total_orders = Order.objects.count()
    total_revenue = sum([o.platform_fee for o in Order.objects.filter(payment_status='Paid')])
    pending_complaints = Complaint.objects.filter(status='Pending').count()

    context.update({
        'total_users': total_users,
        'total_sellers': total_sellers,
        'pending_sellers': pending_sellers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_complaints': pending_complaints,
    })
    return render(request, 'admin_dashboard.html', context)


def admin_sellers(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    sellers = SellerProfile.objects.all().order_by('-created_at')
    context.update({'sellers': sellers})
    return render(request, 'admin_sellers.html', context)


def admin_approve_seller(request, sid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    try:
        seller_profile = SellerProfile.objects.get(id=sid)
        seller_profile.is_verified = True
        seller_profile.rejection_reason = None
        seller_profile.save()
        seller_profile.user.status = '1'
        seller_profile.user.save()
        messages.success(request, f"Seller '{seller_profile.kitchen_name}' has been approved.")
    except SellerProfile.DoesNotExist:
        messages.error(request, "Seller not found.")

    return redirect('/admin/sellers')


def admin_reject_seller(request, sid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Profile does not meet requirements.')
        try:
            seller_profile = SellerProfile.objects.get(id=sid)
            seller_profile.is_verified = False
            seller_profile.rejection_reason = reason
            seller_profile.save()
            seller_profile.user.status = '2'
            seller_profile.user.save()
            messages.success(request, "Seller rejected.")
        except SellerProfile.DoesNotExist:
            messages.error(request, "Seller not found.")

    return redirect('/admin/sellers')


def admin_approve_user(request, uid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    try:
        user = User.objects.get(id=uid, role='Customer')
        user.status = '1'
        user.save()
        messages.success(request, f"Customer '{user.name}' has been approved.")
    except User.DoesNotExist:
        messages.error(request, "Customer not found.")

    return redirect('/admin/users')


def admin_reject_user(request, uid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    try:
        user = User.objects.get(id=uid, role='Customer')
        user.status = '2'
        user.save()
        messages.success(request, f"Customer '{user.name}' has been rejected.")
    except User.DoesNotExist:
        messages.error(request, "Customer not found.")

    return redirect('/admin/users')


def admin_users(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    users = User.objects.filter(role='Customer').order_by('-created_at')
    context.update({'users': users})
    return render(request, 'admin_users.html', context)


def admin_orders(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    orders = Order.objects.all().order_by('-created_at')
    context.update({'orders': orders})
    return render(request, 'admin_orders.html', context)


def admin_complaints(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    complaints = Complaint.objects.all().order_by('-created_at')
    context.update({'complaints': complaints})
    return render(request, 'admin_complaints.html', context)


def admin_resolve_complaint(request, cid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    try:
        complaint = Complaint.objects.get(id=cid)
    except Complaint.DoesNotExist:
        messages.error(request, "Complaint not found.")
        return redirect('/admin/complaints')

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '')
        complaint.admin_note = admin_note

        if action == 'resolve':
            complaint.status = 'Resolved'
            refund = request.POST.get('refund') == 'on'
            if refund:
                complaint.refund_processed = True
                complaint.order.payment_status = 'Refunded'
                complaint.order.save()
        elif action == 'reject':
            complaint.status = 'Rejected'

        complaint.save()
        messages.success(request, "Complaint updated.")
        return redirect('/admin/complaints')

    return redirect('/admin/complaints')


def admin_categories(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    categories = Category.objects.all()

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_photo = request.FILES.get('category_photo')
        Category.objects.create(category_name=category_name, category_photo=category_photo)
        messages.success(request, "Category added.")
        return redirect('/admin/categories')

    context.update({'categories': categories})
    return render(request, 'admin_categories.html', context)


def admin_delete_category(request, cid):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    try:
        cat = Category.objects.get(id=cid)
        cat.delete()
        messages.success(request, "Category deleted.")
    except Category.DoesNotExist:
        messages.error(request, "Category not found.")

    return redirect('/admin/categories')


def admin_inquiries(request):
    if login_required_redirect(request):
        return redirect('/login')
    context = checksession(request)
    if not context['is_admin']:
        return redirect('/')

    inquiries = Inquiry.objects.all().order_by('-created_at')
    context.update({'inquiries': inquiries})
    return render(request, 'admin_inquiries.html', context)

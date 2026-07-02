# SnackCart - Home Made Food Marketplace

A Django-based platform connecting customers with verified home chefs (sellers) for ordering home-cooked food.

---

## 🚀 Quick Setup

### 1. Install Requirements
```bash
pip install django pillow razorpay
```

### 2. Run Migrations
```bash
cd snackcart_project
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (for Admin access)
```bash
python manage.py createsuperuser
```
Then in the admin panel or via shell, create an Admin user in the custom `User` model:
```bash
python manage.py shell
>>> from myapp1.models import User
>>> User.objects.create(name='Admin', email='admin@snackcart.com', password='admin123', role='Admin', status='1')
```

### 4. Collect Static Files (optional for production)
```bash
python manage.py collectstatic
```

### 5. Run Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
snackcart_project/
├── manage.py
├── db.sqlite3 (auto-created after migrate)
├── media/ (user uploads)
│
├── myproject/
│   ├── settings.py
│   ├── urls.py         ← All URL patterns here
│   └── wsgi.py
│
└── myapp1/
    ├── models.py       ← All database models
    ├── views.py        ← All view logic
    ├── admin.py
    ├── static/         ← CSS, JS, images
    └── templates/      ← All HTML templates
```

---

## 👥 User Roles

### Customer
- Register → Auto-approved
- Browse products and sellers
- Place orders (COD or Online via Razorpay)
- Track order status
- Submit reviews and complaints

### Seller (Home Chef)
- Register → Complete profile with FSSAI certificate → Admin approval
- Add and manage products
- Accept/reject orders and update status
- View earnings and commission breakdown
- Subscription: First 11 orders free, then ₹199/month

### Admin
- Approve/reject sellers after reviewing documents
- View all orders, users, complaints
- Manage categories
- Handle complaints and refunds

---

## 💰 Business Logic

### Pricing Per Order
| Item | Amount |
|------|--------|
| Food Price | Product price × Quantity |
| Platform Fee | ₹10 (fixed) |
| Delivery Charge | ₹40 (fixed) |
| **Total** | Food + ₹50 |

### Commission
- Platform takes **10%** of food price
- Seller earns **90%** of food price

### Subscription
- **Free Trial**: First 11 orders
- **After Trial**: ₹199/month via Razorpay
- Products hidden and orders blocked if subscription expired

---

## 📦 Order Status Flow

```
Pending → Accepted → Preparing → Ready for Pickup → Out for Delivery → Delivered → Completed
                                                                    ↓
                                                               Cancelled (only Pending/Accepted)
```

---

## 💳 Payment (Razorpay)

Current credentials (test mode):
- **Key**: `rzp_test_VQhEfe2NCXbbwI`
- **Secret**: `2ibreCYL78DA3kjOhobCvz0f`

To use your own Razorpay account, update in:
- `myapp1/views.py` → search for `rzp_test_VQhEfe2NCXbbwI`

---

## ✉️ Email Configuration

Update in `myproject/settings.py`:
```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🌐 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage |
| `/menu` | Browse all products |
| `/sellers` | Browse sellers |
| `/register` | Register as Customer or Seller |
| `/login` | Login |
| `/seller/dashboard` | Seller panel |
| `/admin-dashboard` | Admin panel |
| `/customer/dashboard` | Customer panel |

---

## 🛠 Tech Stack

- **Backend**: Django (Python)
- **Database**: SQLite (switchable to PostgreSQL)
- **Frontend**: BSL Theme + Bootstrap 5
- **Payments**: Razorpay
- **File Storage**: Local media folder

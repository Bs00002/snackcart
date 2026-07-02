import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.files.base import ContentFile
from myapp1.models import User, SellerProfile, Category, Product

# Clear existing demo data optionally (uncomment if needed)
# User.objects.filter(email__in=[...]).delete()

# Demo customers (15)
customer_names = [
    "Aarav Sharma", "Anaya Mehta", "Rohan Desai", "Sanya Kapoor", "Vivaan Singh",
    "Diya Reddy", "Arjun Patel", "Isha Verma", "Kartik Jain", "Meera Gupta",
    "Riya Nair", "Siddharth Rao", "Tara Khanna", "Viraj Mahajan", "Yashika Bose"
]

customers = []
for i, name in enumerate(customer_names, start=1):
    email = f"{name.lower().replace(' ', '.')}@example.com"
    phone = f"9000000{100 + i}"
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'name': name,
            'password': 'Example@123',
            'phone': phone,
            'role': 'Customer',
            'status': '1',
        }
    )
    customers.append(user)
    if created:
        print('Created customer', email)

# Demo sellers (10)
seller_names = [
    "Spice Village", "Golden Flavors", "Tradition Kitchen", "Homely Eats", "Crystal Bakery",
    "Urban Bites", "Royal Sweets", "Tasty Treats", "Saffron Zone", "Farmhouse Feasts"
]

sellers = []
for i, name in enumerate(seller_names, start=1):
    email = f"{name.lower().replace(' ', '')}@example.com"
    phone = f"9100000{100 + i}"
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'name': name,
            'password': 'Example@123',
            'phone': phone,
            'role': 'Seller',
            'status': '1',
        }
    )
    sellers.append(user)
    if created:
        print('Created seller', email)

# Create minimal SellerProfile for each seller
for idx, seller in enumerate(sellers, start=1):
    profile, created = SellerProfile.objects.get_or_create(
        user=seller,
        defaults={
            'kitchen_name': f"{seller.name} Kitchen",
            'contact_email': seller.email,
            'mobile_number': seller.phone,
            'kitchen_address': f"123 Seller Street {idx}",
            'kitchen_city': 'Ahmedabad',
            'kitchen_pincode': '380001',
            'pan_card': ContentFile(b"fake-pan", name=f"pan_{idx}.txt"),
            'aadhaar_card': ContentFile(b"fake-aadhaar", name=f"aadhaar_{idx}.txt"),
            'fssai_certificate': ContentFile(b"fake-fssai", name=f"fssai_{idx}.txt"),
            'bank_account': f"1234567890{idx}",
            'upi_id': f"seller{idx}@upi",
            'opening_time': '08:00',
            'closing_time': '22:00',
            'is_verified': True,
        }
    )
    if created:
        print('Created seller profile for', seller.email)

# Create categories
image_dir = os.path.join(os.path.dirname(__file__), 'imagesprouct')

category_images = {
    'Snacks': 'Dry Kachori.png',
    'Cakes': 'cake.png',
    'Chocolates': 'choclate.png',
    'Homemade Food': 'homemade.png',
}

category_names = ['Snacks', 'Cakes', 'Chocolates', 'Homemade Food']
categories = {}
for name in category_names:
    cat, created = Category.objects.get_or_create(
        category_name=name,
        defaults={
            'category_photo': ContentFile(open(os.path.join(image_dir, category_images.get(name, 'homemade.png')), 'rb').read(), name=category_images.get(name, 'homemade.png'))
        }
    )
    # Update image if already exists but empty
    if not cat.category_photo and name in category_images:
        img_path = os.path.join(image_dir, category_images[name])
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                cat.category_photo.save(category_images[name], ContentFile(f.read()), save=True)
    categories[name] = cat
    if created:
        print('Created category', name)

# Add products
product_data = {
    'Snacks': ['Dry Kachori', 'Khakhra', 'Methi Puri', 'Farsi Puri', 'Sakarpada', 'Methi Mathri'],
    'Cakes': ['Dry Fruit Cake', 'Paan Cake', 'Gulkand Cake', 'Chocolate Cake', 'Butterscotch Cake', 'Vanilla Cake', 'Cupcakes'],
    'Chocolates': ['Coconut Chocolate', 'Rajwadi Chocolate', 'Roasted Almond Chocolate', 'Kaju Chocolate', 'Jaggery Chocolate'],
    'Homemade Food': ['Thepla', 'Homemade Bakery', 'Homemade Sweets'],
}

product_price = {
    'Snacks': 50.0,
    'Cakes': 250.0,
    'Chocolates': 150.0,
    'Homemade Food': 120.0,
}

# In case no image is required, use dummy file package
image_dir = os.path.join(os.path.dirname(__file__), 'imagesprouct')

image_map = {
    'Dry Kachori': 'Dry Kachori.png',
    'Khakhra': 'Khakhra.png',
    'Methi Puri': 'Methi Puri –.png',
    'Farsi Puri': 'Farsi Puri.png',
    'Sakarpada': 'Sakarpada.png',
    'Methi Mathri': 'Methi Mathri.png',
    'Dry Fruit Cake': 'Dry Fruit Cake.png',
    'Paan Cake': 'Paan Cake.png',
    'Gulkand Cake': 'Gulkand Cake.png',
    'Chocolate Cake': 'Chocolate Cake.png',
    'Butterscotch Cake': 'Butterscotch Cake.png',
    'Vanilla Cake': 'Vanilla Cake.png',
    'Cupcakes': 'Cupcakes.png',
    'Coconut Chocolate': 'Coconut Chocolate.png',
    'Rajwadi Chocolate': 'choclate.png',
    'Roasted Almond Chocolate': 'Roasted Almond Chocolate.png',
    'Kaju Chocolate': 'Kaju Chocolate.png',
    'Jaggery Chocolate': 'Jaggery Chocolate.png',
    'Thepla': 'Thepla.png',
    'Homemade Bakery': 'homemade.png',
    'Homemade Sweets': 'homemade.png',
}

for category_name, names in product_data.items():
    cat = categories[category_name]
    for idx, product_name in enumerate(names, start=1):
        seller = sellers[(idx - 1) % len(sellers)]

        image_file_name = image_map.get(product_name)
        image_content = None
        if image_file_name:
            image_path = os.path.join(image_dir, image_file_name)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_content = ContentFile(f.read(), name=os.path.basename(image_path))

        if image_content is None:
            image_content = ContentFile(b"fake-image", name=f"{product_name.replace(' ', '_').lower()}.jpg")

        product, created = Product.objects.get_or_create(
            seller=seller,
            category=cat,
            product_name=product_name,
            defaults={
                'description': f"Delicious {product_name} from {seller.name}",
                'ingredients': 'Flour, Salt, Spices',
                'expiry_time': '24 hours',
                'preparation_time': '30 mins',
                'estimated_delivery_time': '45 mins',
                'quantity_unit': 'Per Piece',
                'price': product_price[category_name],
                'stock_qty': 100,
                'max_orders_per_day': 50,
                'is_customizable': False,
                'product_photo': image_content,
                'status': 'Available',
            }
        )
        if created:
            print('Created product', product_name, 'in', category_name)

print('Seeding complete!')

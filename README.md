# ShopHub - Modern E-commerce Platform

A full-featured e-commerce application built with Django 5.1, MongoDB Atlas, and Razorpay payment integration. Features include product catalog, shopping cart, checkout, user profiles, order management, AI chatbot assistant, and a comprehensive admin dashboard.

## ✨ Features

### Customer Features
- **Product Catalog**: Browse products with search and category filters
- **Product Details**: Detailed product pages with images, descriptions, and pricing
- **Shopping Cart**: Session-based cart with quantity management
- **Checkout**: Multiple payment options (Cash on Delivery & Razorpay)
- **User Authentication**: Register, login, and profile management
- **Order Management**: View order history and track orders
- **AI Chatbot**: Interactive assistant for product recommendations and order placement
- **Responsive Design**: Modern UI that works on all devices

### Admin Features
- **Product Management**: Add, edit, delete products with image uploads
- **User Management**: Manage customer accounts and permissions
- **Order Management**: View and update order status
- **Category Management**: Organize products by categories
- **Image Preview**: See product images directly in admin list
- **Quick Edit**: Edit prices and availability without opening products
- **Auto-Sync**: All changes automatically sync to MongoDB Atlas

## 🗄️ Database Architecture

**Hybrid Database System**:
- **SQLite**: Primary database for relational data (users, orders, products)
- **MongoDB Atlas**: Cloud database for fast reads and search (synced automatically)

**Collections**:
- `users` - User accounts and profiles
- `products` - Product catalog with images
- `orders` - Order history and details

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- MongoDB Atlas account (or local MongoDB)
- Razorpay account (optional, for online payments)

### Installation

1. **Clone and setup virtual environment**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
MONGO_URI=your-mongodb-atlas-uri
MONGO_DB_NAME=myecommerce_db
RAZOR_KEY_ID=your-razorpay-key-id
RAZOR_KEY_SECRET=your-razorpay-secret
```

4. **Run migrations**
```powershell
python manage.py migrate
```

5. **Create admin account**
```powershell
python manage.py createsuperuser
```

6. **Sync data to MongoDB**
```powershell
python manage.py sync_to_mongo
```

7. **Add product images**
```powershell
python manage.py add_product_images
```

8. **Start the server**
```powershell
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 🔐 Admin Dashboard

### Access
- **URL**: http://127.0.0.1:8000/admin/
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123` (change after first login!)

### Admin Capabilities

#### 1. **Product Management** 📦
- Add new products with images
- Edit product details (title, price, description, category)
- Delete products (removes from both databases)
- Quick edit prices and availability from list view
- Image preview thumbnails
- Search by name or description
- Filter by category, availability, date

#### 2. **User Management** 👥
- View all registered users
- Edit user details and permissions
- Manage staff and superuser status
- Activate/deactivate accounts
- View user profiles (phone, avatar)
- Search by username, email, name
- Filter by role and status

#### 3. **Order Management** 🛒
- View all customer orders
- See order items and quantities inline
- Update payment status
- View shipping addresses
- Search by customer or order ID
- Filter by payment method and status

#### 4. **Category Management** 🏷️
- Create and edit categories
- View product count per category
- Auto-generate slugs

### Common Admin Tasks

**Adding a Product:**
1. Admin Dashboard → Products → Add Product
2. Fill in title, description, price, category
3. Upload product image
4. Check "Available" if in stock
5. Save (auto-syncs to MongoDB)

**Quick Price Update:**
1. Admin Dashboard → Products
2. Edit price directly in the list
3. Click "Save" at bottom

**Managing Users:**
1. Admin Dashboard → Users
2. Click username to edit
3. Update details, permissions, or profile
4. Save changes

## 🤖 AI Chatbot

The chatbot assistant helps customers find products and place orders.

### Features
- Product search by name or category
- Show cheapest/best products
- Category browsing
- Guided checkout process
- Help and information

### Commands
- `hi` - Welcome message
- `show electronics` - Browse by category
- `search phone` - Find specific products
- `cheapest` - See affordable options
- `best products` - View premium items
- `place order` - Guided checkout
- `help` - See all commands

## 💳 Payment Integration

### Razorpay Setup
1. Get API keys from [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Add keys to `.env` file
3. Test with test keys (prefix: `rzp_test_`)
4. Switch to live keys for production

### Payment Flow
1. Customer adds items to cart
2. Proceeds to checkout
3. Chooses payment method:
   - **Cash on Delivery** (COD)
   - **Razorpay** (Online payment)
4. For Razorpay: Secure payment modal opens
5. Payment verified and order created
6. Confirmation sent to customer

## 📁 Project Structure

```
ShopHub/
├── myecommerce/          # Django project settings
│   ├── settings.py       # Configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI config
├── store/               # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # App URLs
│   ├── admin.py         # Admin configuration
│   ├── mongo.py         # MongoDB helpers
│   ├── cart.py          # Shopping cart logic
│   ├── forms.py         # Django forms
│   ├── signals.py       # Auto-sync signals
│   └── management/      # Custom commands
│       └── commands/
│           ├── sync_to_mongo.py
│           └── add_product_images.py
├── templates/           # HTML templates
│   └── store/
│       ├── base.html
│       ├── home.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       ├── profile.html
│       └── razorpay_payment.html
├── static/              # CSS, JS, images
│   └── store/
│       └── styles.css
├── media/               # User uploads
│   └── products/        # Product images
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── manage.py           # Django management
```

## 🛠️ Management Commands

### Sync to MongoDB
```powershell
python manage.py sync_to_mongo
```
Syncs users, products, and orders from SQLite to MongoDB Atlas.

### Add Product Images
```powershell
python manage.py add_product_images
```
Downloads and assigns images to products.

### Create Superuser
```powershell
python manage.py createsuperuser
```
Creates an admin account.

### Test MongoDB Connection
```powershell
python test_mongo.py
```
Verifies MongoDB Atlas connection and shows collection stats.

## 🔧 Troubleshooting

### MongoDB Connection Issues
1. Check if password in `MONGO_URI` is correct
2. Verify IP whitelist in MongoDB Atlas (allow 0.0.0.0/0 for testing)
3. Test connection: `python test_mongo.py`

### Static Files Not Loading
1. Ensure `DEBUG=True` in `.env`
2. Check `STATIC_URL` and `STATICFILES_DIRS` in settings
3. Hard refresh browser (Ctrl+F5)

### Razorpay Payment Fails
1. Verify API keys in `.env`
2. Use test keys for development
3. Check Razorpay dashboard for errors

### Admin Login Issues
Reset admin password:
```powershell
python manage.py changepassword admin
```

## 📊 Features Overview

| Feature | Status | Description |
|---------|--------|-------------|
| Product Catalog | ✅ | Browse and search products |
| Shopping Cart | ✅ | Add/remove items, update quantities |
| User Auth | ✅ | Register, login, profile management |
| Checkout | ✅ | COD and Razorpay payments |
| Order Management | ✅ | View and track orders |
| Admin Dashboard | ✅ | Full CRUD for products, users, orders |
| AI Chatbot | ✅ | Product recommendations and assistance |
| MongoDB Sync | ✅ | Auto-sync to cloud database |
| Image Upload | ✅ | Product images with preview |
| Responsive Design | ✅ | Mobile-friendly UI |

## 🔒 Security Features

- ✅ Password hashing (Django default)
- ✅ CSRF protection
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Secure payment gateway (Razorpay)
- ✅ Environment variables for secrets
- ✅ Admin permission system

## 🚀 Deployment

### Environment Variables for Production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
SECRET_KEY=generate-a-new-secure-key
```

### Deployment Checklist
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Generate new `SECRET_KEY`
- [ ] Use production Razorpay keys
- [ ] Configure static files serving
- [ ] Set up HTTPS
- [ ] Whitelist production IP in MongoDB Atlas

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django and MongoDB documentation
3. Check Razorpay integration docs

## 🎉 Credits

Built with:
- Django 5.1
- MongoDB Atlas
- Razorpay
- Python 3.13
- Modern CSS

---

**Happy Selling! 🛒✨** 

# ShopHub (Django + Mongo)

A minimal e‑commerce app built with Django 3.2 and MongoDB (via djongo). It includes product browsing with search/category filters, a session cart, checkout with address capture, profile management, orders, and a lightweight in‑site chatbot.

## Features
- **Catalog**: Products loaded from MongoDB with optional search (`q`) and category filters. Home shows all available products.
- **Product details**: Dedicated page with images, enriched specs (brand/maker/distributor/category/availability) and highlights, plus Add to Cart and Buy Now.
- **Cart**: Session-based with quantity update, clear, and remove.
- **Checkout**: Address form creates an order (COD). Razorpay endpoint stub included.
- **Auth**: Login/Register/Logout. `LOGIN_URL` points to `/login/`.
- **Profile**: Update username, name, email, phone, avatar and a default address. See your orders; edit your own unpaid orders.
- **Orders**: Order detail page; edit page supports address updates and item quantity changes.
- **Chatbot**: Floating widget that can show cheapest/best products, basic site info, and guide order placement by collecting address fields and placing an order from the current cart.
- **UI polish**: Modern header, product grid, improved buttons, and cart styling.

## Prerequisites
- Windows 10/11
- Python 3.11+
- MongoDB running locally (default `mongodb://localhost:27017`)

## Setup (Windows PowerShell)
1) Create and activate a virtual environment

```powershell
python -m venv .venv311
.\.venv311\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Configure environment (optional)

- Mongo: update `MONGO_URI`/`MONGO_DB_NAME` in `myecommerce/settings.py` if needed.
- Razorpay (optional): set `RAZOR_KEY_ID` and `RAZOR_KEY_SECRET` as env vars or in settings.

4) Run migrations and create a superuser

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5) Start the dev server

```powershell
python manage.py runserver 0.0.0.0:8001
```

Visit: http://127.0.0.1:8001/

## Usage Guide
- **Home**: Browse products, search by keyword, or filter with `?category=<Name>`.
- **Product page**: Click any product card to view details and purchase options.
- **Cart**: Modify quantities with +/−, remove items, clear cart, or proceed to checkout.
- **Checkout**: Fill address; an order is created (COD). Razorpay stub exists at `/razorpay/`.
- **Profile** (`/profile/`):
  - Update account (username, first/last name, email)
  - Update profile (phone, avatar)
  - Update default address
  - View orders; edit your unpaid orders (address + item quantities)
- **Chatbot** (bottom-right): Ask "cheapest", "best", "about", or "place order".
  - Guided order flow collects address fields like `full name:`, `city:`, etc.

## Project Structure (key parts)
- `store/views.py`: All views, including `home`, `product_detail`, cart, checkout, profile, orders, and `chatbot_message`.
- `store/mongo.py`: MongoDB helpers used by views.
- `store/models.py`: Django models for relational features (orders, address, profile) and admin.
- `templates/store/`: `base.html`, `home.html`, `product_detail.html`, `cart.html`, `profile.html`, `order_detail.html`, `order_edit.html`.
- `static/store/styles.css`: Global styles and chatbot styles.

## Media & Static
- Static served from `/static/` in dev; CSS is in `static/store/styles.css`.
- Media (avatars, product images) served from `/media/`. Configure `MEDIA_ROOT`/`MEDIA_URL` in settings.

## Admin
```powershell
python manage.py createsuperuser
# then: http://127.0.0.1:8001/admin/
```

## Troubleshooting
- **Login redirects to /accounts/login/**: Ensure `LOGIN_URL = '/login/'` in `myecommerce/settings.py`.
- **Only few products show**: Home now requests all products. Verify your Mongo collection `products` has `available: true` and proper fields.
- **Product page error on missing fields**: `product_detail` normalizes optional fields; refresh after pulling latest changes.
- **Cart buttons look like links**: Hard-refresh (Ctrl+F5) to invalidate cached CSS.
- **Razorpay**: The endpoint is a stub; add your frontend integration and webhooks.

## Notes
- This app mixes Mongo reads (catalog) with relational writes (orders, auth, addresses). Orders are mirrored to Mongo via helper calls for read experiences.
- The chatbot is intentionally simple and rule-based with server-side session state; it does not call external LLMs.

## License
MIT (for demo purposes).

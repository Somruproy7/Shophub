# My E-commerce Django App

This is a minimal full-stack e-commerce Django app scaffold using MongoDB (via djongo) and a placeholder for Razorpay integration.

Setup (Windows PowerShell):

1. Create a virtual environment and activate it:

   python -m venv .venv; .\.venv\Scripts\Activate.ps1

2. Install dependencies:

   pip install -r requirements.txt

3. Configure MongoDB:

   - Ensure MongoDB is running locally (default: mongodb://localhost:27017)
   - The project uses djongo. If your MongoDB requires credentials or a different host, update `DATABASES` in `myecommerce/settings.py`.

4. Set Razorpay keys (optional) in environment or settings:

   - RAZOR_KEY_ID and RAZOR_KEY_SECRET (used in views)

5. Run migrations and create superuser:

   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser

6. Run the development server:

   python manage.py runserver

Notes & Next steps:

- This scaffold uses a session-based cart in `store/cart.py`.
- Razorpay integration is a placeholder — you'll need to add frontend checkout JS and webhook handling.
- Quantity increase/decrease controls are template placeholders; you can wire them with views/AJAX.
- Admin can manage products, categories, and orders via Django admin.

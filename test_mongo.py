import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv('.env')

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')

print(f"Connecting to MongoDB...")
print(f"Database: {MONGO_DB_NAME}")

try:
    # Create client with timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✓ Successfully connected to MongoDB Atlas!")
    
    # Get database
    db = client[MONGO_DB_NAME]
    
    # List collections
    collections = db.list_collection_names()
    print(f"\nCollections in database: {collections}")
    
    # Count documents
    if 'users' in collections:
        count = db.users.count_documents({})
        print(f"\n📊 Users in MongoDB: {count}")
        # Show sample user
        sample = db.users.find_one()
        if sample:
            print(f"   Sample: {sample.get('username')} ({sample.get('email')})")
    
    if 'products' in collections:
        count = db.products.count_documents({})
        print(f"\n📦 Products in MongoDB: {count}")
        # Show sample product
        sample = db.products.find_one()
        if sample:
            print(f"   Sample: {sample.get('title')} - ₹{sample.get('price')}")
    
    if 'orders' in collections:
        count = db.orders.count_documents({})
        print(f"\n🛒 Orders in MongoDB: {count}")
        # Show sample order
        sample = db.orders.find_one()
        if sample:
            print(f"   Sample: Order #{sample.get('_id')} - ₹{sample.get('total')}")
    
    print("\n" + "="*50)
    print("✓ MongoDB Atlas is working perfectly!")
    print("="*50)
    
    client.close()
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nPlease check:")
    print("1. MongoDB URI is correct")
    print("2. Password is correct (replace YOUR_NEW_PASSWORD)")
    print("3. IP address is whitelisted in MongoDB Atlas")
    print("4. Network connection is working")

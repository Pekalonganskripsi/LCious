"""
Script untuk menambahkan 10 customer dummy dengan data lengkap dan rating
Lokasi sekitar: -7.042657273334495, 109.5725707494307
"""
import sys
import os
import random
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base, engine
from app.models import user, menu, rating

# Setup database connection
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Base location coordinates
BASE_LAT = -7.042657273334495
BASE_LON = 109.5725707494307

# Sample Indonesian names and data
CUSTOMER_DATA = [
    {
        "username": "wibowosantoso",
        "email": "wibowo.santoso@gmail.com",
        "full_name": "Wibowo Santoso",
        "phone": "081234567890",
        "address": "Jl. Merapi No. 15, Ungaran",
        "dob": "1990-05-12",
        "food_preference": "tradisional_jawa",
        "budget_range": "medium",
        "spice_tolerance": 2,
    },
    {
        "username": "srimulyani",
        "email": "sri.mulyani@gmail.com",
        "full_name": "Sri Mulyani",
        "phone": "081234567891",
        "address": "Jl. Dieng No. 23, Wonosobo",
        "dob": "1988-08-20",
        "food_preference": "vegetarian",
        "budget_range": "cheap",
        "spice_tolerance": 0,
    },
    {
        "username": "budiyuwono",
        "email": "budi.yuwono@yahoo.com",
        "full_name": "Budi Yuwono",
        "phone": "081234567892",
        "address": "Jl. Borobudur No. 45, Magelang",
        "dob": "1992-03-15",
        "food_preference": "spicy_food",
        "budget_range": "medium",
        "spice_tolerance": 4,
    },
    {
        "username": "dewikartika",
        "email": "dewi.kartika@gmail.com",
        "full_name": "Dewi Kartika",
        "phone": "081234567893",
        "address": "Jl. Lawu No. 67, Karanganyar",
        "dob": "1995-11-28",
        "food_preference": "sweet_dessert",
        "budget_range": "expensive",
        "spice_tolerance": 1,
    },
    {
        "username": "agussetiawan",
        "email": "agus.setiawan@hotmail.com",
        "full_name": "Agus Setiawan",
        "phone": "081234567894",
        "address": "Jl. Telomoyo No. 89, Boyolali",
        "dob": "1987-07-08",
        "food_preference": "meat_lover",
        "budget_range": "medium",
        "spice_tolerance": 3,
    },
    {
        "username": "fitrihandayani",
        "email": "fitri.handayani@gmail.com",
        "full_name": "Fitri Handayani",
        "phone": "081234567895",
        "address": "Jl. Sindoro No. 34, Salatiga",
        "dob": "1993-12-17",
        "food_preference": "healthy_food",
        "budget_range": "cheap",
        "spice_tolerance": 0,
    },
    {
        "username": "irfanpratama",
        "email": "irfan.pratama@yahoo.com",
        "full_name": "Irfan Pratama",
        "phone": "081234567896",
        "address": "Jl. Muria No. 12, Kudus",
        "dob": "1991-06-22",
        "food_preference": "seafood",
        "budget_range": "expensive",
        "spice_tolerance": 2,
    },
    {
        "username": "ratnawati",
        "email": "ratna.wati@gmail.com",
        "full_name": "Ratna Wati",
        "phone": "081234567897",
        "address": "Jl. Ungaran No. 56, Ambarawa",
        "dob": "1989-09-30",
        "food_preference": "traditional_indonesian",
        "budget_range": "medium",
        "spice_tolerance": 2,
    },
    {
        "username": "henrykurniawan",
        "email": "henry.kurniawan@hotmail.com",
        "full_name": "Henry Kurniawan",
        "phone": "081234567898",
        "address": "Jl. Slamet No. 78, Temanggung",
        "dob": "1994-04-05",
        "food_preference": "western_food",
        "budget_range": "expensive",
        "spice_tolerance": 1,
    },
    {
        "username": "lindawati",
        "email": "linda.wati@gmail.com",
        "full_name": "Linda Wati",
        "phone": "081234567899",
        "address": "Jl. Prau No. 23, Kendal",
        "dob": "1996-01-14",
        "food_preference": "snack_street_food",
        "budget_range": "cheap",
        "spice_tolerance": 3,
    },
]

def generate_location_around_base(base_lat, base_lon, radius_km=5):
    """Generate random coordinates around base location"""
    # Random offset in degrees (approximately 1 degree = 111 km)
    lat_offset = random.uniform(-radius_km/111, radius_km/111)
    lon_offset = random.uniform(-radius_km/111, radius_km/111)

    return str(base_lat + lat_offset), str(base_lon + lon_offset)

def create_customer_with_ratings(customer_data):
    """Create customer with complete profile and ratings"""
    try:
        # Generate unique IDs
        user_id = f"u_{uuid.uuid4().hex[:12]}"
        customer_id = f"c_{uuid.uuid4().hex[:12]}"

        # Generate location around base coordinates
        latitude, longitude = generate_location_around_base(BASE_LAT, BASE_LON)

        # Parse date of birth
        dob = datetime.strptime(customer_data["dob"], "%Y-%m-%d")

        # Create User
        new_user = user.User(
            id=user_id,
            username=customer_data["username"],
            email=customer_data["email"],
            password_hash=pwd_context.hash("Password123!"),  # Default password
            role="customer",
            is_active=True,
            is_verified=True,
            last_login=datetime.utcnow()
        )

        # Create Customer profile
        new_customer = user.Customer(
            id=customer_id,
            user_id=user_id,
            full_name=customer_data["full_name"],
            phone=customer_data["phone"],
            address=customer_data["address"],
            latitude=latitude,
            longitude=longitude,
            date_of_birth=dob
        )

        db.add(new_user)
        db.add(new_customer)
        db.commit()

        print(f"✅ Customer created: {customer_data['full_name']} ({customer_data['username']})")
        print(f"   Location: {latitude}, {longitude}")

        # Create ratings for this customer
        create_customer_ratings(customer_id, customer_data)

        return customer_id

    except Exception as e:
        print(f"❌ Error creating customer {customer_data['username']}: {str(e)}")
        db.rollback()
        return None

def create_customer_ratings(customer_id, customer_data):
    """Create realistic ratings for customer based on preferences"""
    try:
        # Get available menus from nearby merchants
        available_menus = db.query(menu.Menu).join(user.Merchant).filter(
            menu.Menu.is_available == True
        ).all()

        if not available_menus:
            print(f"   ⚠️  No available menus found for ratings")
            return

        # Select 15-25 random menus to rate (diverse selection)
        num_ratings = random.randint(15, 25)
        menus_to_rate = random.sample(available_menus, min(num_ratings, len(available_menus)))

        rated_count = 0
        for menu_item in menus_to_rate:
            try:
                # Calculate realistic rating based on preferences and menu characteristics
                rating_score = calculate_realistic_rating(customer_data, menu_item)

                # Add some randomness to make it more natural
                rating_score = max(1, min(5, rating_score + random.uniform(-0.5, 0.5)))

                # Round to nearest whole number (1, 2, 3, 4, 5)
                rating_score = int(round(rating_score))

                # Create rating
                new_rating = rating.Rating(
                    id=f"r_{uuid.uuid4().hex[:12]}",
                    customer_id=customer_id,
                    menu_id=menu_item.id,
                    score=rating_score,
                    is_verified_purchase=True,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )

                db.add(new_rating)
                rated_count += 1

            except Exception as e:
                print(f"   ⚠️  Error creating rating: {str(e)}")
                continue

        db.commit()
        print(f"   ✅ Created {rated_count} ratings for {customer_data['full_name']}")

    except Exception as e:
        print(f"❌ Error creating ratings: {str(e)}")
        db.rollback()

def calculate_realistic_rating(customer_pref, menu_item):
    """Calculate realistic rating based on customer preferences and menu characteristics"""
    base_rating = 3.5  # Start with neutral positive rating

    # Get merchant info
    merchant = db.query(user.Merchant).filter(user.Merchant.id == menu_item.merchant_id).first()

    # Food preference matching
    pref = customer_pref.get("food_preference", "")
    spice_tol = customer_pref.get("spice_tolerance", 2)

    # Menu characteristics
    menu_spice = menu_item.spice_level or 0
    menu_price = menu_item.price

    # Adjust based on spice tolerance
    if abs(menu_spice - spice_tol) <= 1:
        base_rating += 0.5  # Good spice match
    elif abs(menu_spice - spice_tol) > 2:
        base_rating -= 0.3  # Poor spice match

    # Adjust based on budget
    budget = customer_pref.get("budget_range", "medium")
    if budget == "cheap" and menu_price > 20000:
        base_rating -= 0.5
    elif budget == "expensive" and menu_price < 10000:
        base_rating -= 0.3
    elif budget == "medium" and 10000 <= menu_price <= 30000:
        base_rating += 0.3

    # Food preference matching with cuisine
    if pref == "traditional_jawa" and merchant and "soto" in merchant.shop_name.lower():
        base_rating += 0.8
    elif pref == "spicy_food" and menu_spice >= 3:
        base_rating += 0.6
    elif pref == "vegetarian" and "vegetable" in menu_item.item_name.lower():
        base_rating += 0.7
    elif pref == "sweet_dessert" and menu_item.category == "dessert":
        base_rating += 0.8
    elif pref == "meat_lover" and ("ayam" in menu_item.item_name.lower() or "sapi" in menu_item.item_name.lower()):
        base_rating += 0.6
    elif pref == "seafood" and ("ikan" in menu_item.item_name.lower() or "sea" in menu_item.item_name.lower()):
        base_rating += 0.7
    elif pref == "western_food" and ("burger" in menu_item.item_name.lower() or "steak" in menu_item.item_name.lower()):
        base_rating += 0.6

    # Add some randomness
    base_rating += random.uniform(-0.3, 0.3)

    return max(1.0, min(5.0, base_rating))

def main():
    """Main function to add dummy customers"""
    print("=" * 60)
    print("🔄 Menambahkan 10 Customer Dummy ke LCicious")
    print("=" * 60)
    print(f"📍 Base Location: {BASE_LAT}, {BASE_LON}")
    print(f"📍 Area: Sekitar Universitas Jenderal Soedio")
    print(f"🎯 Target: 18 customers → 28 customers")
    print("=" * 60)

    # Check current customer count
    current_count = db.query(user.User).filter(user.User.role == "customer").count()
    print(f"📊 Current customers: {current_count}")

    if current_count >= 28:
        print("⚠️  Sudah ada 28 atau lebih customers!")
        return

    # Add customers one by one
    added_count = 0
    for customer_data in CUSTOMER_DATA:
        customer_id = create_customer_with_ratings(customer_data)
        if customer_id:
            added_count += 1

    print("=" * 60)
    print(f"✅ Successfully added {added_count} new customers!")

    # Final statistics
    final_count = db.query(user.User).filter(user.User.role == "customer").count()
    total_ratings = db.query(rating.Rating).count()

    print(f"📊 Final customer count: {final_count}")
    print(f"📊 Total ratings: {total_ratings}")
    print(f"📊 New ratings added: ~{added_count * 20} (estimated)")
    print("=" * 60)

    # Calculate estimated sparsity reduction
    total_users = final_count
    total_items = db.query(menu.Menu).count()
    total_possible_ratings = total_users * total_items
    current_sparsity = 1 - (total_ratings / total_possible_ratings)

    print(f"📈 Estimated sparsity: {current_sparsity:.2%}")
    print(f"📉 Previous sparsity: 86.50%")
    print(f"📉 Improvement: {(0.865 - current_sparsity):.2%}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
        print("🎉 Script completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
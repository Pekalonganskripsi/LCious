"""
Script untuk memperbaiki distribusi rating customer baru
Menambah variasi rating natural dan mengurangi sparsity
"""
import sys
import os
import random
import uuid
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.models import user, menu, rating

# Setup database connection
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get the new customers we just added
NEW_CUSTOMER_USERNAMES = [
    'wibowosantoso', 'srimulyani', 'budiyuwono', 'dewikartika', 'agussetiawan',
    'fitrihandayani', 'irfanpratama', 'ratnawati', 'henrykurniawan', 'lindawati'
]

# Customer preferences for realistic rating generation
CUSTOMER_PREFERENCES = {
    'wibowosantoso': {
        'food_preference': 'traditional_jawa',
        'base_rating_range': (3.5, 4.8),  # High preference for traditional food
        'spice_tolerance': 2,
        'preferred_merchants': ['soto', 'gudeg', 'pecel'],
    },
    'srimulyani': {
        'food_preference': 'vegetarian',
        'base_rating_range': (2.8, 4.2),  # Moderate ratings
        'spice_tolerance': 0,
        'preferred_merchants': ['salad', 'vegetable', 'vegan'],
    },
    'budiyuwono': {
        'food_preference': 'spicy_food',
        'base_rating_range': (3.2, 4.9),  # Loves spicy food
        'spice_tolerance': 4,
        'preferred_merchants': ['sate', 'gule', 'spicy'],
    },
    'dewikartika': {
        'food_preference': 'sweet_dessert',
        'base_rating_range': (3.8, 5.0),  # Loves desserts
        'spice_tolerance': 1,
        'preferred_merchants': ['bakery', 'dessert', 'sweet'],
    },
    'agussetiawan': {
        'food_preference': 'meat_lover',
        'base_rating_range': (3.5, 4.7),  # Meat lover
        'spice_tolerance': 3,
        'preferred_merchants': ['steak', 'grill', 'meat'],
    },
    'fitrihandayani': {
        'food_preference': 'healthy_food',
        'base_rating_range': (2.5, 4.0),  # Health conscious
        'spice_tolerance': 0,
        'preferred_merchants': ['salad', 'juice', 'healthy'],
    },
    'irfanpratama': {
        'food_preference': 'seafood',
        'base_rating_range': (3.8, 5.0),  # Seafood lover
        'spice_tolerance': 2,
        'preferred_merchants': ['seafood', 'fish', 'crab'],
    },
    'ratnawati': {
        'food_preference': 'traditional_indonesian',
        'base_rating_range': (3.2, 4.5),  # Traditional food
        'spice_tolerance': 2,
        'preferred_merchants': ['nasi', 'soto', 'tradisional'],
    },
    'henrykurniawan': {
        'food_preference': 'western_food',
        'base_rating_range': (2.8, 4.8),  # Western food
        'spice_tolerance': 1,
        'preferred_merchants': ['burger', 'pizza', 'western'],
    },
    'lindawati': {
        'food_preference': 'snack_street_food',
        'base_rating_range': (3.0, 4.6),  # Street food
        'spice_tolerance': 3,
        'preferred_merchants': ['street', 'snack', 'cheap'],
    },
}

def generate_realistic_rating(customer_pref, menu_item, customer_avg):
    """Generate realistic rating with better distribution"""

    # Get merchant info
    merchant = db.query(user.Merchant).filter(user.Merchant.id == menu_item.merchant_id).first()
    if not merchant:
        return random.uniform(2.5, 4.0)

    merchant_name = merchant.shop_name.lower()
    menu_name = menu_item.item_name.lower()

    # Base rating from customer preference
    base_range = customer_pref['base_rating_range']
    base_rating = random.uniform(*base_range)

    # Adjustments based on preferences
    adjustment = 0

    # Merchant preference match
    for pref_merchant in customer_pref['preferred_merchants']:
        if pref_merchant in merchant_name:
            adjustment += random.uniform(0.3, 0.8)
            break
        elif pref_merchant in menu_name:
            adjustment += random.uniform(0.2, 0.6)
            break

    # Cuisine type matching
    if customer_pref['food_preference'] == 'vegetarian':
        if any(word in menu_name for word in ['sayur', 'vegetable', 'salad', 'gado']):
            adjustment += 0.5
        elif any(word in menu_name for word in ['ayam', 'sapi', 'daging']):
            adjustment -= 0.8

    elif customer_pref['food_preference'] == 'spicy_food':
        if menu_item.spice_level >= 3:
            adjustment += 0.4
        elif menu_item.spice_level <= 1:
            adjustment -= 0.3

    elif customer_pref['food_preference'] == 'sweet_dessert':
        if menu_item.category == 'dessert':
            adjustment += 0.6
        elif menu_item.category == 'food':
            adjustment -= 0.2

    elif customer_pref['food_preference'] == 'meat_lover':
        if any(word in menu_name for word in ['ayam', 'sapi', 'daging', 'meat']):
            adjustment += 0.4
        elif menu_item.category == 'dessert':
            adjustment -= 0.5

    elif customer_pref['food_preference'] == 'seafood':
        if any(word in menu_name for word in ['ikan', 'fish', 'seafood', 'udang', 'crab']):
            adjustment += 0.6
        elif any(word in menu_name for word in ['sate', 'bakso']):
            adjustment -= 0.3

    # Price consideration
    budget_map = {'cheap': 15000, 'medium': 30000, 'expensive': 100000}
    # Get customer budget from preference (approximate)
    customer_budget = budget_map.get('medium', 30000)

    if menu_item.price > customer_budget * 1.5:
        adjustment -= random.uniform(0.3, 0.7)
    elif menu_item.price < customer_budget * 0.3:
        adjustment += random.uniform(0.1, 0.3)

    # Add some natural randomness
    noise = random.uniform(-0.4, 0.4)

    final_rating = base_rating + adjustment + noise

    # Round to 1 decimal place for more variety
    final_rating = round(final_rating, 1)

    # Ensure within valid range
    return max(1.0, min(5.0, final_rating))

def delete_existing_ratings():
    """Delete all existing ratings from the 10 new customers"""
    try:
        # Get customer IDs for the new customers
        customer_ids = db.query(user.Customer.id).join(user.User).filter(
            user.User.username.in_(NEW_CUSTOMER_USERNAMES)
        ).all()

        customer_id_list = [c[0] for c in customer_ids]

        # Delete their ratings
        deleted = db.query(rating.Rating).filter(
            rating.Rating.customer_id.in_(customer_id_list)
        ).delete()

        db.commit()
        print(f"🗑️  Deleted {deleted} existing ratings")
        return customer_id_list

    except Exception as e:
        print(f"❌ Error deleting existing ratings: {str(e)}")
        db.rollback()
        return []

def create_improved_ratings(customer_id_list):
    """Create improved ratings with better distribution"""

    total_new_ratings = 0

    for customer_id in customer_id_list:
        try:
            # Get customer info with user
            customer = db.query(user.Customer).filter(user.Customer.id == customer_id).first()
            if not customer:
                continue

            # Get user associated with customer
            user_obj = db.query(user.User).filter(user.User.id == customer.user_id).first()
            if not user_obj:
                continue

            customer_pref = CUSTOMER_PREFERENCES.get(user_obj.username, {})

            # Get available menus
            available_menus = db.query(menu.Menu).join(user.Merchant).filter(
                menu.Menu.is_available == True
            ).all()

            # Determine how many ratings to give (25-35 for better coverage)
            num_ratings = random.randint(25, 35)
            menus_to_rate = random.sample(available_menus, min(num_ratings, len(available_menus)))

            # Generate ratings with better distribution
            for menu_item in menus_to_rate:
                try:
                    # Generate realistic rating
                    rating_score = generate_realistic_rating(customer_pref, menu_item, None)

                    # Add timestamp with some randomness
                    created_at = datetime.utcnow() - timedelta(days=random.randint(1, 90))

                    # Create rating
                    new_rating = rating.Rating(
                        id=f"r_{uuid.uuid4().hex[:12]}",
                        customer_id=customer_id,
                        menu_id=menu_item.id,
                        score=rating_score,
                        is_verified_purchase=True,
                        created_at=created_at
                    )

                    db.add(new_rating)
                    total_new_ratings += 1

                except Exception as e:
                    print(f"   ⚠️  Error creating rating: {str(e)}")
                    continue

            db.commit()
            print(f"✅ Created {num_ratings} ratings for {customer.full_name}")

        except Exception as e:
            print(f"❌ Error processing customer {customer_id}: {str(e)}")
            continue

    return total_new_ratings

def analyze_rating_distribution():
    """Analyze the improved rating distribution"""
    try:
        # Get rating distribution from new customers
        customer_ids = db.query(user.Customer.id).join(user.User).filter(
            user.User.username.in_(NEW_CUSTOMER_USERNAMES)
        ).all()

        customer_id_list = [c[0] for c in customer_ids]

        # Get distribution using raw SQL for SQLite compatibility
        query = """
            SELECT score, COUNT(*) as count
            FROM ratings
            WHERE customer_id IN ({})
            GROUP BY score
            ORDER BY score ASC
        """.format(','.join(['"' + cid + '"' for cid in customer_id_list]))

        result = db.execute(text(query))
        distribution = [(float(row[0]), row[1]) for row in result]

        print("\n📊 Distribusi Rating Baru:")
        print("-" * 40)
        for score, count in distribution:
            bar_length = int(count * 2)
            bar = "█" * bar_length
            print(f"Rating {score}: {bar} {count}")
        print("-" * 40)

        # Calculate statistics
        total = sum(count for _, count in distribution)
        avg_score = sum(score * count for score, count in distribution) / total if total > 0 else 0

        # Count extreme ratings
        low_ratings = sum(count for score, count in distribution if score <= 2.0)
        high_ratings = sum(count for score, count in distribution if score >= 4.5)

        print(f"\n📈 Statistik Distribusi:")
        print(f"Total ratings: {total}")
        print(f"Average score: {avg_score:.2f}")
        print(f"Low ratings (≤2.0): {low_ratings} ({low_ratings/total*100:.1f}%)")
        print(f"High ratings (≥4.5): {high_ratings} ({high_ratings/total*100:.1f}%)")

        return distribution, total

    except Exception as e:
        print(f"❌ Error analyzing distribution: {str(e)}")
        return [], 0

def main():
    """Main function to improve rating distribution"""
    print("=" * 60)
    print("🔄 Memperbaiki Distribusi Rating Customer Baru")
    print("=" * 60)
    print(f"🎯 Target: Memperbaiki sebaran rating untuk mengurangi sparsity")
    print("=" * 60)

    # Step 1: Delete existing ratings
    print("\n📍 Step 1: Menghapus rating yang ada...")
    customer_id_list = delete_existing_ratings()

    if not customer_id_list:
        print("❌ Tidak bisa mendapatkan customer ID list")
        return

    # Step 2: Create improved ratings
    print("\n📍 Step 2: Membuat rating dengan distribusi lebih baik...")
    total_new_ratings = create_improved_ratings(customer_id_list)

    # Step 3: Analyze new distribution
    print("\n📍 Step 3: Menganalisis distribusi rating baru...")
    distribution, total = analyze_rating_distribution()

    # Final statistics
    print("\n" + "=" * 60)
    print("✅ Hasil Perbaikan Rating Distribution")
    print("=" * 60)
    print(f"📊 Total ratings baru: {total_new_ratings}")
    print(f"📊 Rata-rata per customer: {total_new_ratings/10:.0f} ratings/customer")
    print(f"🎯 Variasi rating: Dari {min(distribution)[0] if distribution else 0} sampai {max(distribution)[0] if distribution else 0}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
        print("\n🎉 Distribusi rating berhasil diperbaiki!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
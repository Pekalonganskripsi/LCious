#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.algorithms import HybridRecommender
from app.models.user import Customer, User

db = SessionLocal()

# Get customer haki
customer = db.query(Customer).join(User).filter(User.username == 'haki').first()

if not customer:
    print("ERROR: Customer 'haki' not found!")
    db.close()
    sys.exit(1)

print(f"Testing for customer: {customer.id}")
print(f"Username: haki")
print(f"Location: {customer.latitude}, {customer.longitude}")

# Get preferences (from recommendations.py logic)
from app.models.fuzzy import CustomerPreference
preference = db.query(CustomerPreference).filter(CustomerPreference.customer_id == customer.id).first()

if preference:
    customer_pref = {
        'pref_price_importance': float(preference.pref_price_importance or 0.5),
        'pref_price_sensitivity': preference.pref_price_sensitivity or 'medium',
        'pref_distance_importance': float(preference.pref_distance_importance or 0.3),
        'pref_max_distance_km': int(preference.pref_max_distance_km or 10),
        'pref_popularity_importance': float(preference.pref_popularity_importance or 0.2),
        'pref_spice_level': int(preference.pref_spice_level or 0),
        'pref_sweetness_level': int(preference.pref_sweetness_level or 0),
        'pref_savory_level': int(preference.pref_savory_level or 0),
        'pref_cuisines': (preference.pref_cuisines.split(',') if preference.pref_cuisines and isinstance(preference.pref_cuisines, str) else preference.pref_cuisines or []),
        'pref_dietary_restrictions': (preference.pref_dietary_restrictions.split(',') if preference.pref_dietary_restrictions and isinstance(preference.pref_dietary_restrictions, str) else preference.pref_dietary_restrictions or [])
    }
else:
    # Use defaults
    customer_pref = {
        'pref_price_importance': 0.5,
        'pref_price_sensitivity': 'medium',
        'pref_distance_importance': 0.3,
        'pref_max_distance_km': 10,
        'pref_popularity_importance': 0.2,
        'pref_spice_level': 0,
        'pref_sweetness_level': 0,
        'pref_savory_level': 0,
        'pref_cuisines': [],
        'pref_dietary_restrictions': []
    }

print(f"\nCustomer Preferences:")
for k, v in customer_pref.items():
    if k != 'pref_cuisines' and k != 'pref_dietary_restrictions':
        print(f"  {k}: {v}")

# Generate recommendations
recommender = HybridRecommender(db, alpha=0.5)
customer_location = (float(customer.latitude), float(customer.longitude))

print(f"\nCustomer Location (float): {customer_location}")

# Get geprekjuara info
from app.models.user import Merchant
geprek_merchant = db.query(Merchant).join(User).filter(User.username == 'geprekjuara').first()

if geprek_merchant:
    print(f"\n=== GEPREKJUARA MERCHANT ===")
    print(f"ID: {geprek_merchant.id}")
    print(f"Shop Name: {geprek_merchant.shop_name}")
    print(f"Location: {geprek_merchant.latitude}, {geprek_merchant.longitude}")
    print(f"Is Active: {geprek_merchant.is_active}")

    # Calculate distance
    from math import radians, cos, sin, asin, sqrt

    def calculate_distance(loc1, loc2):
        lat1, lon1 = float(loc1[0]), float(loc1[1])
        lat2, lon2 = float(loc2[0]), float(loc2[1])

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r

    geprek_location = (float(geprek_merchant.latitude), float(geprek_merchant.longitude))
    distance = calculate_distance(customer_location, geprek_location)
    print(f"Distance from haki: {distance:.6f} km")

    # Get geprekjuara menus
    from app.models.menu import Menu
    geprek_menus = db.query(Menu).filter(Menu.merchant_id == geprek_merchant.id).all()
    print(f"Total menus: {len(geprek_menus)}")
    for menu in geprek_menus:
        print(f"  - {menu.item_name} (available: {menu.is_available})")

recommendations = recommender.generate_recommendations(
    customer_id=str(customer.id),
    customer_pref=customer_pref,
    customer_location=customer_location,
    n_recommendations=20,
    alpha=0.5,
    k_neighbors=20
)

print(f"\n=== TOP 20 RECOMMENDATIONS ===")
geprek_found = False
for rec in recommendations:
    menu = rec['menu']
    scores = rec['scores']
    distance = rec['distance_km']

    is_geprek = 'geprek' in menu.get('shop_name', '').lower() or 'geprek' in menu['item_name'].lower()
    marker = "🏪 GEPREK" if is_geprek else ""

    print(f"\n#{rec['rank']} - {menu['item_name']} ({menu.get('shop_name', 'N/A')}) {marker}")
    print(f"  Distance: {distance:.4f} km")
    print(f"  Fuzzy Score: {scores['fuzzy_score']:.4f}")
    print(f"  CF Score: {scores['cf_score']:.4f}")
    print(f"  Hybrid Score: {scores['hybrid_score']:.4f}")
    print(f"  Distance Score: {scores['breakdown']['fuzzy_breakdown']['distance_score']:.4f}")

    if is_geprek:
        geprek_found = True

if geprek_found:
    print("\n✅ GEPREKJUARA ITEMS FOUND IN RECOMMENDATIONS")
else:
    print("\n❌ GEPREKJUARA ITEMS NOT FOUND IN RECOMMENDATIONS")
    print("This is the PROBLEM - geprekjuara is 0 km away but not recommended!")

db.close()

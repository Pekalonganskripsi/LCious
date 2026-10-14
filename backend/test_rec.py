#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.algorithms import HybridRecommender
from app.models.user import Customer, User

db = SessionLocal()

# Get customer
customer = db.query(Customer).join(User).filter(User.username == 'cicipewancaka').first()
print(f"Testing for customer: {customer.id}")
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

recommendations = recommender.generate_recommendations(
    customer_id=str(customer.id),
    customer_pref=customer_pref,
    customer_location=customer_location,
    n_recommendations=10,
    alpha=0.5,
    k_neighbors=20
)

print(f"\n=== TOP 10 RECOMMENDATIONS ===")
for rec in recommendations:
    menu = rec['menu']
    scores = rec['scores']
    distance = rec['distance_km']

    print(f"\n#{rec['rank']} - {menu['item_name']} ({menu.get('shop_name', 'N/A')})")
    print(f"  Distance: {distance:.4f} km")
    print(f"  Fuzzy Score: {scores['fuzzy_score']:.4f}")
    print(f"  CF Score: {scores['cf_score']:.4f}")
    print(f"  Hybrid Score: {scores['hybrid_score']:.4f}")
    print(f"  Distance Score: {scores['breakdown']['fuzzy_breakdown']['distance_score']:.4f}")

db.close()

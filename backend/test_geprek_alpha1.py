#!/usr/bin/env python3
"""
Test script untuk melihat perbedaan rekomendasi dengan alpha=1.0 (100% Fuzzy)
Ini akan membuktikan apakah geprekjuara muncul di top rank dengan alpha 1.0
"""
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

# Get preferences
from app.models.fuzzy import CustomerPreference
preference = db.query(CustomerPreference).filter(CustomerPreference.customer_id == customer.id).first()

if preference:
    customer_pref = {
        'pref_price_importance': float(preference.pref_price_importance or 0.5),
        'pref_price_sensitivity': preference.pref_price_sensitivity or 'medium',
        'pref_distance_importance': float(preference.pref_distance_importance or 0.5),
        'pref_max_distance_km': int(preference.pref_max_distance_km or 10),
        'pref_popularity_importance': float(preference.pref_popularity_importance or 0.2),
        'pref_spice_level': int(preference.pref_spice_level or 0),
        'pref_sweetness_level': int(preference.pref_sweetness_level or 0),
        'pref_savory_level': int(preference.pref_savory_level or 0),
        'pref_cuisines': (preference.pref_cuisines.split(',') if preference.pref_cuisines and isinstance(preference.pref_cuisines, str) else preference.pref_cuisines or []),
        'pref_dietary_restrictions': (preference.pref_dietary_restrictions.split(',') if preference.pref_dietary_restrictions and isinstance(preference.pref_dietary_restrictions, str) else preference.pref_dietary_restrictions or [])
    }
else:
    customer_pref = {
        'pref_price_importance': 0.5,
        'pref_price_sensitivity': 'medium',
        'pref_distance_importance': 0.5,
        'pref_max_distance_km': 10,
        'pref_popularity_importance': 0.2,
        'pref_spice_level': 0,
        'pref_sweetness_level': 0,
        'pref_savory_level': 0,
        'pref_cuisines': [],
        'pref_dietary_restrictions': []
    }

customer_location = (float(customer.latitude), float(customer.longitude))

# Test dengan berbagai alpha values
print("\n" + "="*80)
print("TESTING RECOMMENDATIONS WITH DIFFERENT ALPHA VALUES")
print("="*80)

for alpha_value in [0.5, 0.8, 1.0]:
    print(f"\n{'='*80}")
    print(f"ALPHA = {alpha_value} ({'100% Fuzzy' if alpha_value == 1.0 else 'Hybrid' if alpha_value == 0.5 else '80% Fuzzy'})")
    print(f"{'='*80}")

    recommender = HybridRecommender(db, alpha=alpha_value)

    recommendations = recommender.generate_recommendations(
        customer_id=str(customer.id),
        customer_pref=customer_pref,
        customer_location=customer_location,
        n_recommendations=20,
        alpha=alpha_value,
        k_neighbors=20
    )

    # Cari geprekjuara items
    geprek_items = [r for r in recommendations if 'geprek' in r['menu'].get('shop_name', '').lower() or 'geprek' in r['menu']['item_name'].lower()]

    print(f"\nTop 10 Recommendations:")
    for i, rec in enumerate(recommendations[:10]):
        menu = rec['menu']
        scores = rec['scores']
        distance = rec['distance_km']
        is_geprek = 'geprek' in menu.get('shop_name', '').lower() or 'geprek' in menu['item_name'].lower()
        marker = "🏪 GEPREK" if is_geprek else ""

        print(f"#{i+1:2d}. {menu['item_name']} ({menu.get('shop_name', 'N/A')}) {marker}")
        print(f"     Distance: {distance:6.2f} km | Hybrid: {scores['hybrid_score']:.4f} | Fuzzy: {scores['fuzzy_score']:.4f} | CF: {scores['cf_score']:.4f}")

    print(f"\n🔍 Geprekjuara Items: {len(geprek_items)} found")
    if geprek_items:
        print("Geprekjuara Rankings:")
        for item in geprek_items:
            rank = recommendations.index(item) + 1
            print(f"  - Rank #{rank}: {item['menu']['item_name']} (Hybrid: {item['scores']['hybrid_score']:.4f})")
    else:
        print("  ❌ No Geprekjuara items found!")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("- Alpha 0.5: CF dan Fuzzy seimbang - Geprekjuara mungkin di ranking bawah")
print("- Alpha 0.8: 80% Fuzzy - Geprekjuara ranking naik")
print("- Alpha 1.0: 100% Fuzzy - Geprekjuara seharusnya di TOP karena jarak 0 km")
print("\n💡 REKOMENDASI: Gunakan Alpha 1.0 untuk merchant tanpa rating!")

db.close()

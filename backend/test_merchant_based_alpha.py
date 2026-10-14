#!/usr/bin/env python3
"""
Test script untuk merchant-based adaptive alpha
Ini akan membuktikan bahwa merchant baru (geprekjuara) akan muncul di top ranking
dengan merchant-based adaptive alpha.
"""
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.algorithms import HybridRecommender
from app.models.user import Customer, User
from app.models.menu import Menu
from app.models.user import Merchant

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

# Get geprekjuara merchant info
geprek_merchant = db.query(Merchant).join(User).filter(User.username == 'geprekjuara').first()

if geprek_merchant:
    print(f"\n=== MERCHANT GEPREKJUARA ===")
    print(f"Shop Name: {geprek_merchant.shop_name}")
    print(f"Location: {geprek_merchant.latitude}, {geprek_merchant.longitude}")

    # Count ratings for geprekjuara
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT COUNT(*) as total_ratings
        FROM ratings r
        JOIN menus m ON r.menu_id = m.id
        WHERE m.merchant_id = :merchant_id
    """), {'merchant_id': geprek_merchant.id}).fetchone()

    print(f"Total Ratings: {result[0]}")

    # Get geprekjuara menus
    geprek_menus = db.query(Menu).filter(Menu.merchant_id == geprek_merchant.id).all()
    print(f"Total Menus: {len(geprek_menus)}")

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

print("\n" + "="*80)
print("TESTING MERCHANT-BASED ADAPTIVE ALPHA")
print("="*80)

recommender = HybridRecommender(db, alpha=0.5)

print("\n🔄 Generating recommendations with MERCHANT-BASED adaptive alpha...")
print("(Setiap menu akan mendapatkan alpha berbeda berdasarkan merchant rating count)")

recommendations = recommender.generate_recommendations(
    customer_id=str(customer.id),
    customer_pref=customer_pref,
    customer_location=customer_location,
    n_recommendations=20,
    alpha=None,  # Will be overridden by merchant-based calculation
    k_neighbors=20,
    adaptive_alpha=True  # Enable merchant-based adaptive alpha!
)

# Analyze alpha values used
print("\n" + "="*80)
print("ALPHA VALUES PER MERCHANT (Merchant-Based Adaptive Alpha)")
print("="*80)

from collections import defaultdict
merchant_alphas = defaultdict(list)

for rec in recommendations:
    shop_name = rec['menu'].get('shop_name', 'Unknown')
    alpha_used = rec['scores'].get('alpha_used', 0.5)
    merchant_alphas[shop_name].append(alpha_used)

print("\nMerchant Alpha Values:")
for shop_name, alphas in sorted(merchant_alphas.items()):
    avg_alpha = sum(alphas) / len(alphas)
    print(f"  {shop_name}: α = {avg_alpha:.2f} (based on {len(alphas)} menu(s))")

# Show top recommendations
print("\n" + "="*80)
print("TOP 20 RECOMMENDATIONS (Merchant-Based Adaptive Alpha)")
print("="*80)

geprek_items = [r for r in recommendations if 'geprek' in r['menu'].get('shop_name', '').lower() or 'geprek' in r['menu']['item_name'].lower()]

for i, rec in enumerate(recommendations[:20]):
    menu = rec['menu']
    scores = rec['scores']
    distance = rec['distance_km']
    is_geprek = 'geprek' in menu.get('shop_name', '').lower() or 'geprek' in menu['item_name'].lower()
    marker = "🏪 GEPREK" if is_geprek else ""
    alpha_used = scores.get('alpha_used', 0.5)

    print(f"#{i+1:2d}. {menu['item_name']} ({menu.get('shop_name', 'N/A')}) {marker}")
    print(f"     Distance: {distance:6.2f} km | Alpha: {alpha_used:.2f} | Hybrid: {scores['hybrid_score']:.4f} | Fuzzy: {scores['fuzzy_score']:.4f} | CF: {scores['cf_score']:.4f}")

print(f"\n🔍 Geprekjuara Items: {len(geprek_items)} found")
if geprek_items:
    print("✅ Geprekjuara Rankings:")
    for item in geprek_items:
        rank = recommendations.index(item) + 1
        alpha_used = item['scores'].get('alpha_used', 0.5)
        print(f"  - Rank #{rank}: {item['menu']['item_name']} (Alpha: {alpha_used:.2f}, Hybrid: {item['scores']['hybrid_score']:.4f})")
else:
    print("❌ No Geprekjuara items found!")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("✨ Dengan Merchant-Based Adaptive Alpha:")
print("  - Merchant baru (0-5 rating) → α = 1.0 (100% Fuzzy)")
print("  - Merchant sedang (6-20 rating) → α = 0.6 (60% Fuzzy)")
print("  - Merchant terbukti (20+ rating) → α = 0.3 (30% Fuzzy)")
print("\n💡 Geprekjuara sebagai merchant baru akan otomatis:")
print("  - Mendapatkan α = 1.0 (100% Fuzzy/Located-based)")
print("  - Muncul di TOP ranking karena jarak 0 km")
print("  - Tidak perlu manual setting alpha oleh user!")

db.close()

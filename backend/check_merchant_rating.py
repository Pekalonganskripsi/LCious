#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.models.user import Merchant
from app.models.menu import Menu
from app.models.rating import Rating

db = SessionLocal()

print("=== ANALISIS RATING MERCHANT ===")

# Get all merchants
merchants = db.query(Merchant).all()

for merchant in merchants:
    print(f"\n{'='*60}")
    print(f"Merchant: {merchant.shop_name}")
    print(f"ID: {merchant.id}")

    # Get all menus for this merchant
    menus = db.query(Menu).filter(Menu.merchant_id == merchant.id).all()
    print(f"\nTotal Menus: {len(menus)}")

    # Get all ratings for all menus from this merchant
    total_rating_sum = 0
    total_rating_count = 0

    for menu in menus:
        # Get ratings for this menu
        menu_ratings = db.query(Rating).filter(Rating.menu_id == menu.id).all()
        if menu_ratings:
            menu_avg = sum(r.score for r in menu_ratings) / len(menu_ratings)
            print(f"  - {menu.item_name}: {len(menu_ratings)} rating, avg: {menu_avg:.2f}")
            total_rating_sum += sum(r.score for r in menu_ratings)
            total_rating_count += len(menu_ratings)
        else:
            print(f"  - {menu.item_name}: 0 rating")

    # Calculate merchant average rating
    if total_rating_count > 0:
        merchant_avg = total_rating_sum / total_rating_count
        print(f"\nMerchant Rating Calculation:")
        print(f"  Total Rating Sum: {total_rating_sum}")
        print(f"  Total Rating Count: {total_rating_count}")
        print(f"  Merchant Average: {merchant_avg:.2f}")
    else:
        print(f"\nMerchant Average: 0.0 (no ratings)")

    print(f"Current merchant.average_rating in DB: {merchant.average_rating or 0}")

db.close()

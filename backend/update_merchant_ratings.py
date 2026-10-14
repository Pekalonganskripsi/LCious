#!/usr/bin/env python3
"""
Script untuk mengupdate rating merchant yang sudah ada
Menjalankan perhitungan ulang rating berdasarkan semua rating yang ada
"""
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from app.db.session import SessionLocal
from app.models.user import Merchant
from app.models.menu import Menu
from app.models.rating import Rating

def update_merchant_ratings():
    """Update merchant average ratings based on all menu ratings"""
    db = SessionLocal()

    try:
        print("=== UPDATE MERCHANT RATINGS ===\n")

        # Get all merchants
        merchants = db.query(Merchant).all()

        for merchant in merchants:
            print(f"Processing: {merchant.shop_name}")

            # Get all menu IDs for this merchant
            menus = db.query(Menu).filter(Menu.merchant_id == merchant.id).all()
            menu_ids = [m.id for m in menus]

            if not menu_ids:
                print(f"  - No menus found")
                continue

            print(f"  - Total menus: {len(menu_ids)}")

            # Get ALL ratings for ALL menus from this merchant
            all_ratings = db.query(Rating).filter(Rating.menu_id.in_(menu_ids)).all()

            if not all_ratings:
                print(f"  - No ratings found")
                merchant.average_rating = None
                merchant.total_reviews = None
            else:
                # Calculate merchant average
                merchant_avg = sum(r.score for r in all_ratings) / len(all_ratings)
                merchant.average_rating = str(merchant_avg)  # Store as string per model definition
                merchant.total_reviews = str(len(all_ratings))

                print(f"  - Total ratings: {len(all_ratings)}")
                print(f"  - Average rating: {merchant_avg:.2f}")

                # Show breakdown by menu
                for menu in menus:
                    menu_ratings = db.query(Rating).filter(Rating.menu_id == menu.id).all()
                    if menu_ratings:
                        menu_avg = sum(r.score for r in menu_ratings) / len(menu_ratings)
                        print(f"    * {menu.item_name}: {len(menu_ratings)} rating, avg: {menu_avg:.2f}")

            db.commit()

        print("\n=== UPDATE COMPLETE ===")
        print(f"Total merchants updated: {len(merchants)}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_merchant_ratings()

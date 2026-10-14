"""
Script untuk mengkonversi rating pecahan menjadi rating bulat (1, 2, 3, 4, 5)
Ini akan memperbaiki semua rating yang memiliki desimal menjadi integer terdekat
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base, engine
from app.models import rating, menu, user
from sqlalchemy import func

# Setup database connection
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def fix_fractional_ratings():
    """Convert all fractional ratings to whole numbers (1, 2, 3, 4, 5)"""
    print("=" * 60)
    print("🔄 Memperbaiki Rating Pecahan ke Rating Bulat")
    print("=" * 60)

    # Get all fractional ratings
    fractional_ratings = db.query(rating.Rating).filter(
        rating.Rating.score != func.floor(rating.Rating.score)
    ).all()

    print(f"📊 Found {len(fractional_ratings)} fractional ratings")

    # Update each fractional rating
    updated_count = 0
    for r in fractional_ratings:
        # Round to nearest integer using standard rounding
        # 1.0-1.4 → 1, 1.5-2.4 → 2, etc.
        old_score = r.score
        new_score = int(round(r.score))

        # Ensure it stays within bounds
        new_score = max(1, min(5, new_score))

        r.score = new_score
        updated_count += 1

        if updated_count <= 10:  # Show first 10 updates
            print(f"  ✏️  Updated {r.id}: {old_score} → {new_score}")

    db.commit()
    print(f"✅ Updated {updated_count} ratings to whole numbers")

    # Update all menu average ratings
    print("\n🔄 Updating menu average ratings...")
    menus = db.query(menu.Menu).all()
    for m in menus:
        ratings = db.query(rating.Rating).filter(rating.Rating.menu_id == m.id).all()
        if ratings:
            avg_score = sum(r.score for r in ratings) / len(ratings)
            m.average_rating = avg_score
            m.total_ratings = len(ratings)

    db.commit()
    print(f"✅ Updated {len(menus)} menu average ratings")

    # Update all merchant average ratings
    print("\n🔄 Updating merchant average ratings...")
    merchants = db.query(user.Merchant).all()
    for merch in merchants:
        from app.models.menu import Menu as MenuItem
        merchant_menu_ids = db.query(MenuItem.id).filter(MenuItem.merchant_id == merch.id).all()
        merchant_menu_ids = [m[0] for m in merchant_menu_ids]

        if merchant_menu_ids:
            all_merchant_ratings = db.query(rating.Rating).filter(rating.Rating.menu_id.in_(merchant_menu_ids)).all()
            if all_merchant_ratings:
                merchant_avg = sum(r.score for r in all_merchant_ratings) / len(all_merchant_ratings)
                merch.average_rating = str(merchant_avg)
                merch.total_reviews = str(len(all_merchant_ratings))

    db.commit()
    print(f"✅ Updated {len(merchants)} merchant average ratings")

    # Show new distribution
    print("\n📊 New Rating Distribution:")
    print("-" * 40)

    rating_dist = db.query(
        rating.Rating.score.label('score'),
        func.count(rating.Rating.id).label('count')
    ).group_by(
        rating.Rating.score
    ).order_by('score').all()

    print('Score\tCount\tPercentage')
    for score, count in rating_dist:
        total = db.query(rating.Rating).count()
        pct = (count / total * 100) if total > 0 else 0
        print(f'{score}\t{count}\t{pct:.1f}%')

    total = db.query(rating.Rating).count()
    print(f'\nTotal ratings: {total}')
    print("=" * 60)

if __name__ == "__main__":
    try:
        fix_fractional_ratings()
        print("🎉 Script completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

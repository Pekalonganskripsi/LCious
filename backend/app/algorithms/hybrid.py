"""
Hybrid Recommendation Engine for LCious

Combines Fuzzy Logic and Collaborative Filtering using weighted combination
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.algorithms.fuzzy import FuzzyLogicEngine
from app.algorithms.collaborative_filtering import CollaborativeFilteringEngine
from app.models.menu import Menu
from app.models.user import Merchant, Customer
from app.models.research import RecommendationLog


class HybridRecommender:
    """
    Hybrid Fuzzy-Collaborative Filtering Recommendation System

    Final Score: Hscore(u,i) = (α × Sf(u,i)) + ((1-α) × Pcf(u,i)/Rmax)

    where:
    - Sf(u,i): Fuzzy score (preferensi match) [0,1]
    - Pcf(u,i): Predicted rating dari CF [1,5]
    - Rmax: Maximum rating (5) untuk normalisasi
    - α: Weight parameter [0,1]

    α Tuning:
    - α = 0.8: User baru (cold start), favor Fuzzy
    - α = 0.5: Balanced, equal weight
    - α = 0.2: User aktif, favor CF
    """

    def __init__(self, db: Session, alpha: float = 0.5):
        """
        Initialize Hybrid Recommender

        Args:
            db: Database session
            alpha: Weight parameter [0,1]
                  0 = pure CF, 1 = pure Fuzzy, 0.5 = balanced
        """
        self.db = db
        self.alpha = alpha
        self.max_rating = 5.0

        # Initialize engines
        self.fuzzy_engine = FuzzyLogicEngine(db)
        self.cf_engine = CollaborativeFilteringEngine(db)

    def predict_rating_hybrid(self, user_id: str, menu_id: str, k: int = 10) -> float:
        """
        Predict rating using hybrid scoring dengan current alpha

        Method ini khusus untuk evaluasi yang membutuhkan predicted rating
        berdasarkan hybrid combination (α × Fuzzy + (1-α) × CF)

        Args:
            user_id: Customer ID
            menu_id: Menu ID
            k: Number of neighbors untuk CF

        Returns:
            Predicted rating (1-5 scale)
        """
        from app.models.menu import Menu
        from app.models.user import Customer, Merchant

        # Get menu data
        menu = self.db.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            return 3.0  # Default rating

        # Get merchant data
        merchant = self.db.query(Merchant).filter(Merchant.id == menu.merchant_id).first()
        if not merchant:
            return 3.0

        # Get customer data
        customer = self.db.query(Customer).filter(Customer.id == user_id).first()
        if not customer:
            # No customer data, use pure CF
            cf_rating = self.cf_engine.predict_rating(user_id, menu_id, k, method='pearson')
            return cf_rating

        # Get customer preference data
        from app.models.fuzzy import CustomerPreference
        cust_pref = self.db.query(CustomerPreference).filter(CustomerPreference.customer_id == user_id).first()

        # Build menu dict for fuzzy
        menu_dict = {
            'id': menu.id,
            'item_name': menu.item_name,
            'price': float(menu.price),
            'spice_level': menu.spice_level or 0,
            'sweetness_level': menu.sweetness_level or 0,
            'savory_level': menu.savory_level or 0,
            'popularity_score': menu.popularity_score or 0,
            'cuisine_type': merchant.cuisine_type or 'indonesian',
            'merchant_id': merchant.id
        }

        # Build customer preference dict - use defaults if not available
        customer_pref = {
            'pref_price_sensitivity': getattr(cust_pref, 'pref_price_sensitivity', 'medium') or 'medium',
            'pref_max_distance_km': getattr(cust_pref, 'pref_max_distance_km', 10) or 10,
            'pref_spice_level': getattr(cust_pref, 'pref_spice_level', 0) or 0,
            'pref_sweetness_level': getattr(cust_pref, 'pref_sweetness_level', 0) or 0,
            'pref_savory_level': getattr(cust_pref, 'pref_savory_level', 0) or 0
        }

        # Get locations
        customer_location = (float(customer.latitude or 0), float(customer.longitude or 0))
        menu_location = (float(merchant.latitude or 0), float(merchant.longitude or 0))

        # Calculate hybrid score
        result = self.calculate_hybrid_score(
            customer_id=user_id,
            menu=menu_dict,
            customer_pref=customer_pref,
            customer_location=customer_location,
            menu_location=menu_location,
            k_neighbors=k,
            alpha=self.alpha  # Use current alpha
        )

        # Return predicted rating from hybrid score (convert back to 1-5 scale)
        hybrid_prediction = result['hybrid_score'] * self.max_rating

        return hybrid_prediction

    def calculate_adaptive_alpha(self, customer_id: str, menu_id: str = None) -> float:
        """
        Calculate optimal alpha berdasarkan MERCHANT's rating history (merchant-based)

        Logic MERCHANT-BASED:
        - New merchants (0-5 ratings): α = 1.0 (100% Fuzzy, solusi cold start merchant)
        - Small merchants (6-20 ratings): α = 0.6 (favor Fuzzy, tapi CF mulai dipertimbangkan)
        - Established merchants (20+ ratings): α = 0.3 (favor CF untuk merchant terbukti)

        Args:
            customer_id: Customer ID (untuk fallback logic)
            menu_id: Menu ID (untuk menghitung merchant rating count)

        Returns:
            Optimal alpha value [0,1]
        """
        # Jika menu_id tidak disediakan, gunakan customer-based logic (backward compatibility)
        if menu_id is None:
            rating_count = self.cf_engine.get_user_rating_count(customer_id)

            if rating_count <= 5:
                return 0.8  # Cold start
            elif rating_count <= 20:
                return 0.5  # Warm start
            else:
                return 0.2  # Hot start

        # MERCHANT-BASED LOGIC (New!)
        # Hitung rating count untuk MERCHANT, bukan customer
        merchant_rating_count = self.cf_engine.get_merchant_rating_count(menu_id)

        if merchant_rating_count <= 5:
            return 1.0  # Merchant baru → 100% Fuzzy (location-based recommendation)
        elif merchant_rating_count <= 20:
            return 0.6  # Merchant sedang → 60% Fuzzy, 40% CF
        else:
            return 0.3  # Merchant terbukti → 30% Fuzzy, 70% CF (trust komunitas)

    def calculate_hybrid_score(self,
                              customer_id: str,
                              menu: Dict,
                              customer_pref: Dict,
                              customer_location: Tuple[float, float],
                              menu_location: Tuple[float, float],
                              k_neighbors: int = 10,
                              alpha: Optional[float] = None) -> Dict:
        """
        Calculate hybrid recommendation score untuk single menu item

        Hscore(u,i) = (α × Sf(u,i)) + ((1-α) × Pcf(u,i)/Rmax)

        Args:
            customer_id: Target customer ID
            menu: Menu data dictionary
                {
                    'id': str,
                    'item_name': str,
                    'price': float,
                    'spice_level': int,
                    'sweetness_level': int,
                    'savory_level': int,
                    'popularity_score': int,
                    'cuisine_type': str,
                    'merchant_id': str
                }
            customer_pref: Customer preference dictionary
            customer_location: (latitude, longitude) customer
            menu_location: (latitude, longitude) merchant
            k_neighbors: Number of neighbors untuk CF
            alpha: Override default alpha

        Returns:
            Dictionary dengan:
                {
                    'fuzzy_score': float (0-1),
                    'cf_score': float (0-1),  # Normalized
                    'predicted_rating': float (1-5),
                    'hybrid_score': float (0-1),
                    'alpha_used': float,
                    'breakdown': {
                        'fuzzy_breakdown': {...},
                        'distance_km': float
                    }
                }
        """
        # Calculate distance
        distance_km = self._calculate_distance(
            customer_location,
            menu_location
        )

        # Calculate Fuzzy Score
        fuzzy_result = self.fuzzy_engine.calculate_fuzzy_score(
            menu=menu,
            customer_pref=customer_pref,
            distance_km=distance_km
        )
        fuzzy_score = fuzzy_result['fuzzy_score']

        # Calculate CF Score (predicted rating)
        predicted_rating = self.cf_engine.predict_rating(
            user_id=customer_id,
            menu_id=menu['id'],
            k=k_neighbors,
            method='pearson'
        )

        # Normalize CF score to [0,1]
        cf_score_normalized = predicted_rating / self.max_rating

        # Determine alpha
        if alpha is None:
            alpha = self.alpha

        # Calculate Hybrid Score
        hybrid_score = (alpha * fuzzy_score) + ((1 - alpha) * cf_score_normalized)

        return {
            'fuzzy_score': float(fuzzy_score),
            'cf_score': float(cf_score_normalized),
            'predicted_rating': float(predicted_rating),
            'hybrid_score': float(hybrid_score),
            'alpha_used': float(alpha),
            'breakdown': {
                'fuzzy_breakdown': fuzzy_result['breakdown'],
                'distance_km': float(distance_km)
            }
        }

    def generate_recommendations(self,
                                 customer_id: str,
                                 customer_pref: Dict,
                                 customer_location: Tuple[float, float],
                                 n_recommendations: int = 20,
                                 alpha: Optional[float] = None,
                                 k_neighbors: int = 10,
                                 adaptive_alpha: bool = False) -> List[Dict]:
        """
        Generate top-N recommendations untuk customer

        Args:
            customer_id: Target customer ID
            customer_pref: Customer preference data
            customer_location: (latitude, longitude)
            n_recommendations: Number of recommendations to return
            alpha: Override default alpha (None untuk use default)
            k_neighbors: Number of neighbors untuk CF
            adaptive_alpha: Use adaptive alpha based on rating history

        Returns:
            List of recommended menus with scores, sorted by hybrid_score descending
            [
                {
                    'menu': {...},
                    'scores': {...},
                    'distance_km': float,
                    'rank': int
                },
                ...
            ]
        """
        # Note: Alpha calculation moved to per-menu loop for merchant-based adaptive alpha
        # Get all available menus
        menus_query = self.db.query(Menu, Merchant).join(
            Merchant, Menu.merchant_id == Merchant.id
        ).filter(
            Menu.is_available == True,
            Merchant.is_active == True
        ).all()

        recommendations = []

        for menu, merchant in menus_query:
            # Prepare menu data
            menu_data = {
                'id': str(menu.id),
                'menu_id': str(menu.id),  # For API response compatibility
                'item_name': menu.item_name,
                'price': float(menu.price) if menu.price else 0,
                'category': menu.category,
                'spice_level': menu.spice_level or 0,
                'sweetness_level': menu.sweetness_level or 0,
                'savory_level': menu.savory_level or 0,
                'popularity_score': menu.popularity_score or 0,
                'cuisine_type': merchant.cuisine_type or '',
                'merchant_id': str(merchant.id),
                'shop_name': merchant.shop_name,
                'merchant_address': merchant.address,
                'description': menu.description,
                'image_url': menu.image_url or ''  # Add image_url
            }

            # Merchant location
            merchant_location = (
                float(merchant.latitude) if merchant.latitude else 0,
                float(merchant.longitude) if merchant.longitude else 0
            )

            # Calculate alpha per menu if adaptive_alpha is enabled (MERCHANT-BASED)
            if adaptive_alpha:
                # Calculate merchant-based alpha for this specific menu
                menu_alpha = self.calculate_adaptive_alpha(customer_id, str(menu.id))
            elif alpha is None:
                menu_alpha = self.alpha
            else:
                menu_alpha = alpha

            # Calculate hybrid score
            try:
                scores = self.calculate_hybrid_score(
                    customer_id=customer_id,
                    menu=menu_data,
                    customer_pref=customer_pref,
                    customer_location=customer_location,
                    menu_location=merchant_location,
                    k_neighbors=k_neighbors,
                    alpha=menu_alpha  # Use merchant-based alpha
                )

                recommendations.append({
                    'menu': menu_data,
                    'scores': scores,
                    'distance_km': scores['breakdown']['distance_km']
                })
            except Exception as e:
                print(f"Error calculating score for menu {menu.id}: {e}")
                continue

        # Sort by hybrid score descending
        recommendations.sort(key=lambda x: x['scores']['hybrid_score'], reverse=True)

        # Add rank and limit
        for idx, rec in enumerate(recommendations[:n_recommendations], 1):
            rec['rank'] = idx

        return recommendations[:n_recommendations]

    def log_recommendations(self, customer_id: str, recommendations: List[Dict]):
        """
        Log recommendations ke database untuk research analysis

        Args:
            customer_id: Customer ID
            recommendations: List of recommendation dictionaries dari generate_recommendations()
        """
        try:
            for rec in recommendations:
                log_entry = RecommendationLog(
                    customer_id=customer_id,
                    menu_id=rec['menu']['id'],
                    fuzzy_score=rec['scores']['fuzzy_score'],
                    cf_score=rec['scores']['cf_score'],
                    hybrid_final_score=rec['scores']['hybrid_score'],
                    alpha_weight=rec['scores']['alpha_used'],
                    rank_position=rec['rank'],
                    algorithm_version=f"hybrid_alpha_{rec['scores']['alpha_used']}"
                )
                self.db.add(log_entry)

            self.db.commit()
            print(f"Logged {len(recommendations)} recommendations for customer {customer_id}")

        except Exception as e:
            self.db.rollback()
            print(f"Error logging recommendations: {e}")

    def get_recommendation_explanation(self, recommendation: Dict) -> str:
        """
        Generate human-readable explanation untuk recommendation

        Args:
            recommendation: Single recommendation dictionary

        Returns:
            Explanation string
        """
        menu = recommendation['menu']
        scores = recommendation['scores']
        breakdown = scores['breakdown']['fuzzy_breakdown']

        explanations = []

        # Price explanation
        price_score = breakdown['price_score']
        if price_score > 0.8:
            explanations.append(f"Harga sangat sesuai budget Anda")
        elif price_score > 0.5:
            explanations.append(f"Harga cukup sesuai")

        # Distance explanation
        distance = recommendation['distance_km']
        if distance < 2:
            explanations.append(f"Sangat dekat ({distance:.1f} km)")
        elif distance < 5:
            explanations.append(f"Dekat ({distance:.1f} km)")

        # Taste explanation
        taste_score = breakdown['taste_score']
        if taste_score > 0.8:
            explanations.append(f"Rasa sangat cocok dengan selera Anda")

        # Community approval
        community_score = scores['cf_score']
        if community_score > 0.8:
            explanations.append(f"Disukai banyak orang")

        # Combine
        if explanations:
            return ". ".join(explanations) + "."
        else:
            return "Direkomendasikan berdasarkan preferensi dan popularitas."

    def _calculate_distance(self,
                           loc1: Tuple[float, float],
                           loc2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates menggunakan Haversine formula

        Args:
            loc1: (latitude, longitude)
            loc2: (latitude, longitude)

        Returns:
            Distance in kilometers
        """
        from math import radians, cos, sin, asin, sqrt

        lat1, lon1 = loc1
        lat2, lon2 = loc2

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # Radius of earth in kilometers
        r = 6371

        return c * r

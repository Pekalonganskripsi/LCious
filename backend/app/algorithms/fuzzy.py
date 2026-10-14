"""
Fuzzy Logic Engine for LCious Recommendation System

Implements triangular and trapezoidal membership functions
for multi-criteria decision making in food recommendations.
"""
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Simple fallback for numpy operations
    class np:
        @staticmethod
        def maximum(a, b):
            return a if a > b else b
        @staticmethod
        def minimum(a, b):
            return a if a < b else b

from typing import Dict, List, Tuple, Optional, Union
from sqlalchemy.orm import Session
from app.models.fuzzy import FuzzyCriteria


class FuzzyLogicEngine:
    """
    Fuzzy Logic Engine untuk menghitung preferensi user berdasarkan kriteria subjektif

    Fuzzy Score: Sf(u,i) = Σ(w_k × μ_k(x_i)) / Σw_k

    where:
    - w_k: importance weight untuk criteria k
    - μ_k(x_i): membership degree untuk criteria k
    """

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize Fuzzy Logic Engine

        Args:
            db: Database session untuk mengambil fuzzy criteria dari database
        """
        self.db = db
        self.criteria_config = {}
        if db:
            self._load_criteria_from_db()
        else:
            self._load_default_criteria()

    def _load_default_criteria(self):
        """
        Load default fuzzy criteria
        Used sebagai fallback jika database tidak tersedia
        """
        self.criteria_config = {
            'price': {
                'cheap': (0, 7500, 15000),
                'medium': (10000, 20000, 30000),
                'expensive': (25000, 50000, 100000)
            },
            'distance': {
                'near': (0, 1, 2),
                'medium': (1, 3, 5),
                'far': (4, 10, 20)
            },
            'popularity': {
                'quiet': (0, 5, 10),
                'busy': (5, 20, 50),
                'very_busy': (30, 100, 500)
            }
        }

    def _load_criteria_from_db(self):
        """
        Load fuzzy criteria dari database
        Dynamically configurable oleh superadmin
        """
        try:
            criteria_list = self.db.query(FuzzyCriteria).all()

            # If no criteria in database, use defaults
            if not criteria_list:
                print("No fuzzy criteria in database, using default configuration")
                self._load_default_criteria()
                return

            for criteria in criteria_list:
                if criteria.criteria_name not in self.criteria_config:
                    self.criteria_config[criteria.criteria_name] = {}

                self.criteria_config[criteria.criteria_name][criteria.sub_criteria] = (
                    criteria.min_val,
                    criteria.mid_val if criteria.mid_val else (criteria.min_val + criteria.max_val) / 2,
                    criteria.max_val
                )
        except Exception as e:
            print(f"Error loading fuzzy criteria from DB: {e}")
            self._load_default_criteria()

    def triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
        """
        Triangular membership function

        μ(x) = max(0, min((x-a)/(b-a), (c-x)/(c-b)))

        Args:
            x: Input value
            a, b, c: Triangle parameters (a ≤ b ≤ c)
                a: base kiri
                b: puncak (peak)
                c: base kanan

        Returns:
            Membership degree [0, 1]

        Example:
            >>> engine = FuzzyLogicEngine()
            >>> engine.triangular_membership(15000, 0, 7500, 15000)
            0.0  # Di boundary atas
            >>> engine.triangular_membership(7500, 0, 7500, 15000)
            1.0  # Di peak
        """
        # Handle edge cases
        if x <= a or x >= c:
            return 0.0

        if a == b:  # Right triangle (ascending)
            if x <= b:
                return 1.0 if x >= a else 0.0
            return (c - x) / (c - b) if c != b else 0.0

        if b == c:  # Right triangle (descending)
            if x >= b:
                return 1.0 if x <= c else 0.0
            return (x - a) / (b - a) if b != a else 0.0

        # Normal triangular
        left_slope = (x - a) / (b - a) if b != a else 1.0
        right_slope = (c - x) / (c - b) if c != b else 1.0

        return max(0.0, min(left_slope, right_slope))

    def trapezoidal_membership(self, x: float, a: float, b: float, c: float, d: float) -> float:
        """
        Trapezoidal membership function

        Args:
            x: Input value
            a, b, c, d: Trapezoid parameters (a ≤ b ≤ c ≤ d)

        Returns:
            Membership degree [0, 1]
        """
        if x < a or x > d:
            return 0.0
        elif a <= x < b:
            return (x - a) / (b - a) if b != a else 1.0
        elif b <= x <= c:
            return 1.0
        elif c < x <= d:
            return (d - x) / (d - c) if d != c else 1.0
        return 0.0

    def fuzzify_price(self, price: float, price_sensitivity: str = 'medium') -> float:
        """
        Calculate price membership berdasarkan preferensi harga customer

        Args:
            price: Harga menu
            price_sensitivity: 'cheap', 'medium', atau 'expensive_flexible'

        Returns:
            Membership degree [0, 1]

        Logic:
        - Customer yang suka 'cheap' akan memberi skor tinggi untuk harga murah
        - Customer yang suka 'expensive' fleksibel terhadap semua range harga
        """
        if price_sensitivity == 'cheap':
            params = self.criteria_config['price']['cheap']
            return self.triangular_membership(price, *params)
        elif price_sensitivity == 'medium':
            params = self.criteria_config['price']['medium']
            return self.triangular_membership(price, *params)
        else:  # expensive_flexible
            # Untuk flexible, semua harga acceptable dengan preferensi sedang-tinggi
            params = self.criteria_config['price']['expensive']
            return max(
                self.triangular_membership(price, *params),
                0.5  # Minimum score untuk expensive_flexible
            )

    def fuzzify_distance(self, distance_km: float, max_distance_km: float = 10) -> float:
        """
        Calculate distance membership

        Closer is better: μ(distance) = 1 - (distance / max_distance)

        Args:
            distance_km: Jarak dalam kilometer
            max_distance_km: Jarak maksimum yang dapat ditoleransi

        Returns:
            Membership degree [0, 1]

        Logic:
        - Jarak 0 km → skor 1.0 (sangat dekat)
        - Jarak = max_distance → skor 0.0 (terlalu jauh)
        """
        if max_distance_km <= 0:
            return 1.0  # No distance constraint

        if distance_km >= max_distance_km:
            return 0.0

        return max(0.0, 1.0 - (distance_km / max_distance_km))

    def fuzzify_popularity(self, popularity_score: int) -> float:
        """
        Normalize popularity score ke [0, 1]

        Args:
            popularity_score: Skor popularitas (jumlah order/rating)

        Returns:
            Normalized popularity score [0, 1]

        Logic:
        - Semakin tinggi popularitas, semakin tinggi skor
        - Max popularity = 500 (dari criteria config)
        """
        if not popularity_score or popularity_score < 0:
            return 0.0

        max_popularity = 500  # Dari criteria 'very_busy'
        return min(1.0, popularity_score / max_popularity)

    def fuzzify_taste(self, item_level: int, preferred_level: Optional[int]) -> float:
        """
        Calculate taste preference match menggunakan inverse Gaussian

        Args:
            item_level: Level rasa menu (0-5)
            preferred_level: Level preferensi customer (0-5), None jika tidak ada preferensi

        Returns:
            Membership degree [0, 1]

        Logic:
        - Exact match → skor 1.0
        - Difference 1 → skor tinggi
        - Difference 5 → skor 0
        """
        if preferred_level is None or preferred_level == 0:
            # No preference, semua acceptable
            return 1.0

        if item_level is None:
            item_level = 0

        difference = abs(item_level - preferred_level)
        max_difference = 5

        # Linear decreasing: 1 - (diff / max_diff)
        return max(0.0, 1.0 - (difference / max_difference))

    def fuzzify_cuisine_match(self, merchant_cuisine: str, preferred_cuisines: Optional[List[str]]) -> float:
        """
        Calculate cuisine type match

        Args:
            merchant_cuisine: Jenis masakan merchant
            preferred_cuisines: List jenis masakan favorit customer

        Returns:
            Membership degree [0, 1]
        """
        if not preferred_cuisines or len(preferred_cuisines) == 0:
            # No preference
            return 0.5  # Neutral score

        if not merchant_cuisine:
            return 0.0

        # Exact match
        if merchant_cuisine.lower() in [c.lower() for c in preferred_cuisines]:
            return 1.0

        # Partial match (containment)
        for pref in preferred_cuisines:
            if pref.lower() in merchant_cuisine.lower() or merchant_cuisine.lower() in pref.lower():
                return 0.7

        # No match
        return 0.3

    def calculate_fuzzy_score(self,
                             menu: Dict,
                             customer_pref: Dict,
                             distance_km: float = 0) -> Dict:
        """
        Calculate comprehensive fuzzy score untuk sebuah menu item

        Sf(u,i) = (w_price × μ_price + w_distance × μ_distance +
                   w_popularity × μ_popularity + w_taste × μ_taste +
                   w_cuisine × μ_cuisine) / (w_price + w_distance + w_popularity + w_taste + w_cuisine)

        Args:
            menu: Dictionary dengan data menu
                {
                    'price': float,
                    'spice_level': int,
                    'sweetness_level': int,
                    'savory_level': int,
                    'popularity_score': int,
                    'cuisine_type': str (optional)
                }
            customer_pref: Dictionary dengan preferensi customer
                {
                    'pref_price_importance': float (0-1),
                    'pref_price_sensitivity': str,
                    'pref_distance_importance': float (0-1),
                    'pref_max_distance_km': int,
                    'pref_popularity_importance': float (0-1),
                    'pref_spice_level': int,
                    'pref_sweetness_level': int,
                    'pref_savory_level': int,
                    'pref_cuisines': List[str]
                }
            distance_km: Jarak dari customer ke merchant dalam km

        Returns:
            Dictionary dengan:
                {
                    'fuzzy_score': float (0-1),
                    'breakdown': {
                        'price_score': float,
                        'distance_score': float,
                        'popularity_score': float,
                        'taste_score': float,
                        'cuisine_score': float
                    }
                }
        """
        # Extract menu data
        price = menu.get('price', 0)
        spice_level = menu.get('spice_level', 0)
        sweetness_level = menu.get('sweetness_level', 0)
        savory_level = menu.get('savory_level', 0)
        popularity_score = menu.get('popularity_score', 0)
        cuisine_type = menu.get('cuisine_type', '')

        # Extract customer preferences - use OR operator to handle None values
        # dict.get() with key that exists but has None value returns None, not the default
        w_price = customer_pref.get('pref_price_importance') or 0.5
        w_distance = customer_pref.get('pref_distance_importance') or 0.3
        w_popularity = customer_pref.get('pref_popularity_importance') or 0.2

        price_sensitivity = customer_pref.get('pref_price_sensitivity') or 'medium'
        max_distance = customer_pref.get('pref_max_distance_km') or 10

        pref_spice = customer_pref.get('pref_spice_level')
        pref_sweetness = customer_pref.get('pref_sweetness_level')
        pref_savory = customer_pref.get('pref_savory_level')
        pref_cuisines = customer_pref.get('pref_cuisines', [])

        # Calculate individual memberships
        price_score = self.fuzzify_price(price, price_sensitivity)
        distance_score = self.fuzzify_distance(distance_km, max_distance)
        popularity_score = self.fuzzify_popularity(popularity_score)

        # Taste scores
        taste_scores = []
        if pref_spice and pref_spice > 0:
            taste_scores.append(self.fuzzify_taste(spice_level, pref_spice))
        if pref_sweetness and pref_sweetness > 0:
            taste_scores.append(self.fuzzify_taste(sweetness_level, pref_sweetness))
        if pref_savory and pref_savory > 0:
            taste_scores.append(self.fuzzify_taste(savory_level, pref_savory))

        # Average taste score (or 0.5 if no preferences)
        taste_score = np.mean(taste_scores) if taste_scores else 0.5

        # Cuisine match
        cuisine_score = self.fuzzify_cuisine_match(cuisine_type, pref_cuisines)

        # Fixed weight for taste and cuisine (can be made configurable)
        w_taste = 0.5
        w_cuisine = 0.3

        # Calculate weighted average
        total_weight = w_price + w_distance + w_popularity + w_taste + w_cuisine

        fuzzy_score = (
            (w_price * price_score) +
            (w_distance * distance_score) +
            (w_popularity * popularity_score) +
            (w_taste * taste_score) +
            (w_cuisine * cuisine_score)
        ) / total_weight

        return {
            'fuzzy_score': float(fuzzy_score),
            'breakdown': {
                'price_score': float(price_score),
                'distance_score': float(distance_score),
                'popularity_score': float(popularity_score),
                'taste_score': float(taste_score),
                'cuisine_score': float(cuisine_score)
            }
        }

    def get_criteria_config(self) -> Dict:
        """
        Get current fuzzy criteria configuration

        Returns:
            Dictionary dengan semua criteria dan parameters
        """
        return self.criteria_config

    def update_criteria(self, criteria_name: str, sub_criteria: str,
                       min_val: float, mid_val: float, max_val: float):
        """
        Update fuzzy criteria secara runtime
        Useful untuk admin tuning

        Args:
            criteria_name: Nama criteria
            sub_criteria: Nama sub-criteria
            min_val, mid_val, max_val: Parameter triangular membership
        """
        if criteria_name not in self.criteria_config:
            self.criteria_config[criteria_name] = {}

        self.criteria_config[criteria_name][sub_criteria] = (min_val, mid_val, max_val)

"""
Collaborative Filtering Engine for LCious Recommendation System

Implements User-based Collaborative Filtering with:
- Pearson Correlation Coefficient for similarity
- K-Nearest Neighbors (KNN)
- Rating prediction
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


class CollaborativeFilteringEngine:
    """
    Collaborative Filtering Engine untuk mencari pola komunitas

    Menggunakan User-based CF dengan Pearson Correlation

    Similarity: sim(u,v) = Σ((Ru,i - R̄u)(Rv,i - R̄v)) / (Σ(Ru,i - R̄u)² × Σ(Rv,i - R̄v)²)^0.5

    Prediction: Pcf(u,i) = R̄u + (Σ sim(u,v) × (Rv,i - R̄v)) / Σ|sim(u,v)|
    """

    def __init__(self, db: Session):
        """
        Initialize CF Engine

        Args:
            db: Database session
        """
        self.db = db
        self.user_item_matrix = None
        self.user_means = {}

    def build_user_item_matrix(self) -> pd.DataFrame:
        """
        Build user-item rating matrix dari database

        Returns:
            DataFrame dengan customers sebagai rows, menus sebagai columns
            Values: rating (1-5), 0 jika belum dirating

        Example:
            >>> cf_engine = CollaborativeFilteringEngine(db)
            >>> matrix = cf_engine.build_user_item_matrix()
            >>> print(matrix.shape)  # (n_customers, n_menus)
        """
        query = """
        SELECT
            customer_id,
            menu_id,
            score
        FROM ratings
        ORDER BY customer_id, menu_id
        """

        try:
            # Execute query
            result = self.db.execute(text(query))
            data = [{'customer_id': str(row[0]), 'menu_id': str(row[1]), 'score': float(row[2])}
                   for row in result]

            # Create DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                # No ratings yet - initialize empty matrix
                self.user_item_matrix = pd.DataFrame()
                return self.user_item_matrix

            # Pivot to create matrix
            self.user_item_matrix = df.pivot(
                index='customer_id',
                columns='menu_id',
                values='score'
            ).fillna(0)

            # Calculate user means
            for user_id in self.user_item_matrix.index:
                user_ratings = self.user_item_matrix.loc[user_id]
                rated_items = user_ratings[user_ratings > 0]
                self.user_means[user_id] = rated_items.mean() if len(rated_items) > 0 else 3.0

            return self.user_item_matrix

        except Exception as e:
            print(f"Error building user-item matrix: {e}")
            # Initialize empty matrix on error
            self.user_item_matrix = pd.DataFrame()
            return self.user_item_matrix

    def calculate_pearson_similarity(self, user1_ratings: np.ndarray,
                                    user2_ratings: np.ndarray,
                                    min_common_items: int = 2) -> float:
        """
        Calculate Pearson Correlation Coefficient antara dua users

        sim(u,v) = Σ((Ru,i - R̄u)(Rv,i - R̄v)) /
                   (Σ(Ru,i - R̄u)² × Σ(Rv,i - R̄v)²)^0.5

        Args:
            user1_ratings: Rating array untuk user 1
            user2_ratings: Rating array untuk user 2
            min_common_items: Minimum jumlah items yang sama-sama dirating

        Returns:
            Similarity score [-1, 1]
            -1: Perfect negative correlation
            0: No correlation
            1: Perfect positive correlation

        Note:
            Hanya consider items yang sama-sama dirating oleh kedua users
        """
        # Find common items (both rated)
        common_mask = (user1_ratings > 0) & (user2_ratings > 0)
        common_count = common_mask.sum()

        # Need at least min_common_items
        if common_count < min_common_items:
            return 0.0

        # Extract common ratings
        u1_common = user1_ratings[common_mask]
        u2_common = user2_ratings[common_mask]

        # Calculate means
        mean_u1 = u1_common.mean()
        mean_u2 = u2_common.mean()

        # Calculate Pearson correlation
        # numerator: Σ((Ru,i - R̄u)(Rv,i - R̄v))
        numerator = np.sum((u1_common - mean_u1) * (u2_common - mean_u2))

        # denominator: (Σ(Ru,i - R̄u)² × Σ(Rv,i - R̄v)²)^0.5
        sum_sq_diff_u1 = np.sum((u1_common - mean_u1) ** 2)
        sum_sq_diff_u2 = np.sum((u2_common - mean_u2) ** 2)
        denominator = np.sqrt(sum_sq_diff_u1 * sum_sq_diff_u2)

        # Avoid division by zero
        if denominator == 0:
            return 0.0

        similarity = numerator / denominator

        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, similarity))

    def calculate_cosine_similarity(self, user1_ratings: np.ndarray,
                                   user2_ratings: np.ndarray) -> float:
        """
        Calculate Cosine Similarity antara dua users

        Args:
            user1_ratings: Rating array untuk user 1
            user2_ratings: Rating array untuk user 2

        Returns:
            Similarity score [0, 1]
            0: No similarity
            1: Identical
        """
        # Cosine similarity: (A · B) / (||A|| × ||B||)
        dot_product = np.dot(user1_ratings, user2_ratings)
        norm_u1 = np.linalg.norm(user1_ratings)
        norm_u2 = np.linalg.norm(user2_ratings)

        if norm_u1 == 0 or norm_u2 == 0:
            return 0.0

        similarity = dot_product / (norm_u1 * norm_u2)

        # Clamp to [0, 1]
        return max(0.0, min(1.0, similarity))

    def find_k_nearest_neighbors(self,
                                 user_id: str,
                                 k: int = 10,
                                 method: str = 'pearson',
                                 min_similarity: float = 0.0) -> List[Tuple[str, float]]:
        """
        Find K most similar users ke target user

        Args:
            user_id: Target user ID
            k: Number of neighbors to find
            method: 'pearson' atau 'cosine'
            min_similarity: Minimum similarity threshold

        Returns:
            List of (neighbor_id, similarity_score) tuples, sorted by similarity descending
            [(neighbor_1, sim_1), (neighbor_2, sim_2), ...]

        Example:
            >>> neighbors = cf_engine.find_k_nearest_neighbors('user_123', k=10)
            >>> print(neighbors[0])  # ('user_456', 0.85) - most similar
        """
        if self.user_item_matrix is None:
            self.build_user_item_matrix()

        if self.user_item_matrix.empty:
            return []

        # Check if user exists
        if user_id not in self.user_item_matrix.index:
            return []

        target_user = self.user_item_matrix.loc[user_id].values

        similarities = []

        # Calculate similarity with all other users
        for other_user_id in self.user_item_matrix.index:
            if other_user_id == user_id:
                continue

            other_user = self.user_item_matrix.loc[other_user_id].values

            if method == 'pearson':
                sim = self.calculate_pearson_similarity(target_user, other_user)
            else:  # cosine
                sim = self.calculate_cosine_similarity(target_user, other_user)

            # Filter by minimum similarity
            if sim >= min_similarity:
                similarities.append((other_user_id, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top K
        return similarities[:k]

    def predict_rating(self,
                      user_id: str,
                      menu_id: str,
                      k: int = 10,
                      method: str = 'pearson') -> float:
        """
        Predict rating untuk user-menu pair menggunakan Collaborative Filtering

        Pcf(u,i) = R̄u + (Σ sim(u,v) × (Rv,i - R̄v)) / Σ|sim(u,v)|

        where:
        - v ∈ N (neighbors of u)
        - sim(u,v) is similarity between users u and v
        - Rv,i is rating dari user v untuk item i

        Args:
            user_id: Target user ID
            menu_id: Target menu ID
            k: Number of neighbors
            method: Similarity method ('pearson' atau 'cosine')

        Returns:
            Predicted rating [1, 5]

        Example:
            >>> prediction = cf_engine.predict_rating('user_123', 'menu_456', k=10)
            >>> print(f"Predicted rating: {prediction:.2f}")  # 4.25
        """
        if self.user_item_matrix is None:
            self.build_user_item_matrix()

        if self.user_item_matrix.empty:
            # No data, return neutral rating
            return 3.0

        # Check if user and menu exist
        if user_id not in self.user_item_matrix.index:
            return 3.0

        if menu_id not in self.user_item_matrix.columns:
            return 3.0

        # Find neighbors
        neighbors = self.find_k_nearest_neighbors(user_id, k=k, method=method)

        if not neighbors:
            # Fallback to user mean or global mean
            user_mean = self.user_means.get(user_id, 3.0)
            return user_mean if not np.isnan(user_mean) else 3.0

        # Get user's mean rating
        user_mean = self.user_means.get(user_id, 3.0)
        if np.isnan(user_mean):
            user_mean = 3.0

        # Calculate weighted prediction
        numerator = 0.0
        denominator = 0.0

        for neighbor_id, similarity in neighbors:
            # Get neighbor's rating for this menu
            if menu_id not in self.user_item_matrix.columns:
                continue

            neighbor_rating = self.user_item_matrix.loc[neighbor_id, menu_id]

            if neighbor_rating == 0:
                # Neighbor hasn't rated this menu
                continue

            # Get neighbor's mean rating
            neighbor_mean = self.user_means.get(neighbor_id, 3.0)
            if np.isnan(neighbor_mean):
                neighbor_mean = 3.0

            # Add to weighted sum
            numerator += similarity * (neighbor_rating - neighbor_mean)
            denominator += abs(similarity)

        # Calculate prediction
        if denominator == 0:
            return user_mean

        prediction = user_mean + (numerator / denominator)

        # Clip to valid range [1, 5]
        return max(1.0, min(5.0, prediction))

    def predict_ratings_batch(self,
                             user_id: str,
                             menu_ids: List[str],
                             k: int = 10,
                             method: str = 'pearson') -> Dict[str, float]:
        """
        Predict ratings untuk multiple menus sekaligus

        Args:
            user_id: Target user ID
            menu_ids: List of menu IDs
            k: Number of neighbors
            method: Similarity method

        Returns:
            Dictionary {menu_id: predicted_rating}

        Example:
            >>> menu_ids = ['menu_1', 'menu_2', 'menu_3']
            >>> predictions = cf_engine.predict_ratings_batch('user_123', menu_ids)
            >>> print(predictions)
            {'menu_1': 4.25, 'menu_2': 3.80, 'menu_3': 4.50}
        """
        predictions = {}

        for menu_id in menu_ids:
            predictions[menu_id] = self.predict_rating(
                user_id=user_id,
                menu_id=menu_id,
                k=k,
                method=method
            )

        return predictions

    def calculate_all_similarities(self,
                                  method: str = 'pearson',
                                  min_common_items: int = 2,
                                  save_to_db: bool = False) -> Dict[Tuple[str, str], float]:
        """
        Pre-compute similarity matrix untuk semua user pairs

        Args:
            method: 'pearson' atau 'cosine'
            min_common_items: Minimum common items untuk Pearson
            save_to_db: Save ke database (untuk research transparency)

        Returns:
            Dictionary {(user_id_1, user_id_2): similarity_score}

        Note:
            Hanya menyimpan pairs dengan positive similarity untuk Pearson
        """
        if self.user_item_matrix is None:
            self.build_user_item_matrix()

        if self.user_item_matrix.empty:
            return {}

        user_ids = self.user_item_matrix.index.tolist()
        similarities = {}

        # Calculate similarity untuk semua unique pairs
        for i, user1_id in enumerate(user_ids):
            for user2_id in user_ids[i+1:]:
                user1 = self.user_item_matrix.loc[user1_id].values
                user2 = self.user_item_matrix.loc[user2_id].values

                if method == 'pearson':
                    sim = self.calculate_pearson_similarity(user1, user2, min_common_items)
                    # Only store positive similarities for Pearson
                    if sim > 0:
                        similarities[(user1_id, user2_id)] = sim
                else:  # cosine
                    sim = self.calculate_cosine_similarity(user1, user2)
                    similarities[(user1_id, user2_id)] = sim

        # Save to database jika requested
        if save_to_db:
            self._save_similarity_matrix(similarities, method)

        return similarities

    def _save_similarity_matrix(self, similarities: Dict[Tuple[str, str], float], method: str):
        """
        Save computed similarities ke database

        Args:
            similarities: Dictionary {(user_id_1, user_id_2): similarity}
            method: Similarity method
        """
        from app.models.research import UserSimilarityMatrix

        try:
            # Clear old entries dengan method yang sama
            self.db.query(UserSimilarityMatrix).filter(
                UserSimilarityMatrix.similarity_method == method
            ).delete()

            # Insert new entries
            for (user1_id, user2_id), score in similarities.items():
                # Count common items
                user1_ratings = self.user_item_matrix.loc[user1_id]
                user2_ratings = self.user_item_matrix.loc[user2_id]
                common_items = ((user1_ratings > 0) & (user2_ratings > 0)).sum()

                similarity_entry = UserSimilarityMatrix(
                    user_id_1=user1_id,
                    user_id_2=user2_id,
                    similarity_score=float(score),
                    similarity_method=method,
                    common_items_rated=int(common_items)
                )
                self.db.add(similarity_entry)

            self.db.commit()
            print(f"Saved {len(similarities)} similarity pairs to database")

        except Exception as e:
            self.db.rollback()
            print(f"Error saving similarity matrix: {e}")

    def get_user_rating_count(self, user_id: str) -> int:
        """
        Get jumlah ratings yang telah diberikan user

        Args:
            user_id: User ID

        Returns:
            Number of ratings
        """
        if self.user_item_matrix is None:
            self.build_user_item_matrix()

        # Check again after building - could still be None or empty
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return 0

        if user_id not in self.user_item_matrix.index:
            return 0

        user_ratings = self.user_item_matrix.loc[user_id]
        return int((user_ratings > 0).sum())

    def get_merchant_rating_count(self, menu_id: str) -> int:
        """
        Get total number of ratings for all menus from a merchant

        This is used for merchant-based adaptive alpha calculation.
        Merchant with few ratings gets higher alpha (favor Fuzzy).

        Args:
            menu_id: Menu ID (used to find merchant)

        Returns:
            Total number of ratings for this merchant's menus
        """
        try:
            # Get merchant_id from menu
            from app.models.menu import Menu
            menu = self.db.query(Menu).filter(Menu.id == menu_id).first()

            if not menu:
                return 0

            merchant_id = menu.merchant_id

            # Count all ratings for this merchant's menus
            query = text("""
                SELECT COUNT(*) as total_ratings
                FROM ratings r
                JOIN menus m ON r.menu_id = m.id
                WHERE m.merchant_id = :merchant_id
            """)

            result = self.db.execute(query, {'merchant_id': merchant_id}).fetchone()

            return int(result[0]) if result else 0

        except Exception as e:
            print(f"Error getting merchant rating count: {e}")
            return 0

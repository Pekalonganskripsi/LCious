# 🔬 ALGORITMA SISTEM REKOMENDASI LCIOUS

## Daftar Isi
1. [Overview Sistem](#1-overview-sistem)
2. [Fuzzy Logic](#2-fuzzy-logic)
3. [Collaborative Filtering](#3-collaborative-filtering)
4. [Hybrid Combination](#4-hybrid-combination)
5. [Algoritma Baseline](#5-algoritma-baseline)
   - 5.1 Random Baseline
   - 5.2 Most Popular Baseline
   - 5.3 Average Rating Baseline
   - 5.4 Item-Based CF Baseline
   - 5.5 Perbandingan Performa Baseline
   - 5.6 Diagram Perbandingan
   - 5.7 Implementasi Kode Lengkap
6. [Evaluasi Sistem](#6-evaluasi-sistem)
   - 6.1 Metrik Evaluasi (MAE, RMSE, Hit Rate)
   - 6.2 Cross-Validation
   - 6.3 Statistical Significance Testing
7. [Parameter dan Konfigurasi](#7-parameter-dan-konfigurasi)
8. [Rumus-Rumus Lengkap](#8-rumus-rumus-lengkap)

---

## 1. OVERVIEW SISTEM

### Arsitektur Sistem
```
┌─────────────────────────────────────────────────────────────┐
│                     SISTEM REKOMENDASI LCIOUS               │
│              Hybrid Fuzzy + Collaborative Filtering         │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │  FUZZY LOGIC   │         │ COLLABORATIVE  │
        │  Content-based │         │   FILTERING    │
        │                │         │   Community    │
        │ • Preferensi  │         │ • Similarity   │
        │ • Jarak       │         │ • KNN (K=10)   │
        │ • Harga       │         │ • Pearson      │
        │ • Rasa        │         │ • Prediction   │
        └───────┬────────┘         └───────┬────────┘
                │                           │
                │ Sf(u,i)                   │ Pcf(u,i)
                │ [0-1]                     │ [1-5]
                │                           │
                └───────────┬───────────────┘
                            │
                    ┌───────▼────────┐
                    │ HYBRID ENGINE  │
                    │                │
                    │ Hscore = α×Sf +│
                    │ (1-α)×Pcf/5    │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ REKOMENDASI    │
                    │ TOP-N LIST     │
                    └────────────────┘
```

### File-file Implementasi
- **Fuzzy Logic**: `backend/app/algorithms/fuzzy.py:26-438`
- **Collaborative Filtering**: `backend/app/algorithms/collaborative_filtering.py:16-508`
- **Hybrid Engine**: `backend/app/algorithms/hybrid.py:18-477`
- **Evaluasi**: `backend/app/algorithms/evaluation.py:24-1765`

---

## 2. FUZZY LOGIC

### Konsep Dasar
Fuzzy Logic digunakan untuk menangkap preferensi subjektif customer yang tidak dapat diukur secara eksak. Sistem menggunakan **Fuzzy Inference System** dengan pendekatan **weighted scoring**.

### 2.1 Fungsi Keanggotaan (Membership Functions)

#### A. Triangular Membership Function (Untuk Harga)

**Rumus Umum:**
```
μ(x) = max(0, min((x-a)/(b-a), (c-x)/(c-b)))
```

**Parameter:**
- `a`: batas kiri (kaki kiri)
- `b`: puncak (peak)
- `c`: batas kanan (kaki kanan)

**Implementasi Python (fuzzy.py:101-142):**
```python
def triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
    """
    Triangular membership function

    Args:
        x: Input value
        a, b, c: Triangle parameters (a ≤ b ≤ c)

    Returns:
        Membership degree [0, 1]
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
```

**Konfigurasi Harga (fuzzy.py:56-72):**
```python
self.criteria_config = {
    'price': {
        'cheap': (0, 7500, 15000),       # Murah: 0-15k, peak di 7.5k
        'medium': (10000, 20000, 30000),  # Sedang: 10k-30k, peak di 20k
        'expensive': (25000, 50000, 100000) # Mahal: 25k-100k, peak di 50k
    }
}
```

**Contoh Perhitungan Harga:**
```
Input: Harga Rp 15.000
Preferensi: Medium (10.000 - 30.000, peak di 20.000)

Step 1: Hitung posisi relatif
  - Jarak dari kiri: 15.000 - 10.000 = 5.000
  - Jarak dari kanan: 30.000 - 15.000 = 15.000
  - Total range: 30.000 - 10.000 = 20.000

Step 2: Hitung slope
  - Left slope = 5.000 / 10.000 = 0.5
  - Right slope = 15.000 / 10.000 = 1.5

Step 3: Ambil minimum
  μ_price(15.000) = min(0.5, 1.5) = 0.5

Hasil: Membership degree = 0.5 (50% cocok untuk preferensi medium)
```

#### B. Fungsi Keanggotaan Jarak (Distance Membership)

**Rumus (fuzzy.py:194-217):**
```
μ(distance) = 1 - (distance / max_distance)
```

**Implementasi Python:**
```python
def fuzzify_distance(self, distance_km: float, max_distance_km: float = 10) -> float:
    """
    Calculate distance membership

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
```

**Contoh Perhitungan:**
```
Input: Jarak 2 km
Max distance: 5 km

μ_distance = 1 - (2/5) = 1 - 0.4 = 0.6

Hasil: Membership degree = 0.6 (60% kecocokan jarak)
```

#### C. Fungsi Keanggotaan Popularitas (Popularity Membership)

**Rumus (fuzzy.py:219-237):**
```
μ_popularity = popularity_score / max_popularity
```

**Implementasi Python:**
```python
def fuzzify_popularity(self, popularity_score: int) -> float:
    """
    Normalize popularity score ke [0, 1]

    Args:
        popularity_score: Skor popularitas (jumlah order/rating)

    Returns:
        Normalized popularity score [0, 1]

    Logic:
        - Semakin tinggi popularitas, semakin tinggi skor
        - Max popularity = 500
    """
    if not popularity_score or popularity_score < 0:
        return 0.0

    max_popularity = 500  # Dari criteria 'very_busy'
    return min(1.0, popularity_score / max_popularity)
```

**Contoh Perhitungan:**
```
Input: 25 ratings
Max popularity: 500

μ_popularity = 25 / 500 = 0.05

Hasil: Membership degree = 0.05 (5% popularitas)
```

#### D. Fungsi Keanggotaan Rasa (Taste Matching)

**Rumus (fuzzy.py:239-266):**
```
μ_taste = 1 - (|item_level - preferred_level| / max_difference)
```

**Implementasi Python:**
```python
def fuzzify_taste(self, item_level: int, preferred_level: Optional[int]) -> float:
    """
    Calculate taste preference match menggunakan inverse Gaussian

    Args:
        item_level: Level rasa menu (0-5)
        preferred_level: Level preferensi customer (0-5)

    Returns:
        Membership degree [0, 1]

    Logic:
        - Exact match → skor 1.0
        - Difference 1 → skor tinggi
        - Difference 5 → skor 0
    """
    if preferred_level is None or preferred_level == 0:
        return 1.0  # No preference, semua acceptable

    if item_level is None:
        item_level = 0

    difference = abs(item_level - preferred_level)
    max_difference = 5

    # Linear decreasing: 1 - (diff / max_diff)
    return max(0.0, 1.0 - (difference / max_difference))
```

**Contoh Perhitungan:**
```
Input:
  - Menu spice level: 3
  - Preferred spice level: 4

Difference: |3 - 4| = 1
Max difference: 5

μ_taste = 1 - (1/5) = 1 - 0.2 = 0.8

Hasil: Membership degree = 0.8 (80% kecocokan rasa)
```

#### E. Fungsi Keanggotaan Jenis Masakan (Cuisine Type Matching)

**Rumus (fuzzy.py:268-296):**
```
if exact_match:
    μ_cuisine = 1.0
elif partial_match:
    μ_cuisine = 0.7
else:
    μ_cuisine = 0.3
```

**Implementasi Python:**
```python
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
```

### 2.2 Rule Base Fuzzy

Sistem menggunakan **weighted average rule aggregation**, bukan traditional IF-THEN rules. Setiap criteria memiliki weight sendiri:

**Weight Configuration (fuzzy.py:356-390):**
```python
# Extract customer preferences
w_price = customer_pref.get('pref_price_importance') or 0.5
w_distance = customer_pref.get('pref_distance_importance') or 0.3
w_popularity = customer_pref.get('pref_popularity_importance') or 0.2

# Fixed weights for taste and cuisine
w_taste = 0.5
w_cuisine = 0.3

# Total weight
total_weight = w_price + w_distance + w_popularity + w_taste + w_cuisine
```

### 2.3 Perhitungan Skor Fuzzy (Fuzzy Score Calculation)

**Rumus Utama (fuzzy.py:298-412):**
```
Sf(u,i) = (w_price × μ_price + w_distance × μ_distance +
           w_popularity × μ_popularity + w_taste × μ_taste +
           w_cuisine × μ_cuisine) / Σw
```

**Implementasi Python:**
```python
def calculate_fuzzy_score(self,
                         menu: Dict,
                         customer_pref: Dict,
                         distance_km: float = 0) -> Dict:
    """
    Calculate comprehensive fuzzy score untuk sebuah menu item

    Args:
        menu: Dictionary dengan data menu
        customer_pref: Dictionary dengan preferensi customer
        distance_km: Jarak dari customer ke merchant dalam km

    Returns:
        Dictionary dengan fuzzy_score dan breakdown
    """
    # Extract menu data
    price = menu.get('price', 0)
    spice_level = menu.get('spice_level', 0)
    sweetness_level = menu.get('sweetness_level', 0)
    savory_level = menu.get('savory_level', 0)
    popularity_score = menu.get('popularity_score', 0)
    cuisine_type = menu.get('cuisine_type', '')

    # Extract customer preferences
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

    # Taste scores (average of all taste preferences)
    taste_scores = []
    if pref_spice and pref_spice > 0:
        taste_scores.append(self.fuzzify_taste(spice_level, pref_spice))
    if pref_sweetness and pref_sweetness > 0:
        taste_scores.append(self.fuzzify_taste(sweetness_level, pref_sweetness))
    if pref_savory and pref_savory > 0:
        taste_scores.append(self.fuzzify_taste(savory_level, pref_savory))

    taste_score = np.mean(taste_scores) if taste_scores else 0.5

    # Cuisine match
    cuisine_score = self.fuzzify_cuisine_match(cuisine_type, pref_cuisines)

    # Fixed weights
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
```

### 2.4 Contoh Perhitungan Lengkap Fuzzy

**Skenario:**
- Menu: Nasi Megono
- Harga: Rp 15.000
- Spice level: 3/5
- Sweetness level: 2/5
- Savory level: 4/5
- Popularitas: 25 ratings
- Cuisine type: "Indonesian"
- Jarak: 2 km

**Preferensi Customer:**
- Price sensitivity: Medium
- Max distance: 5 km
- Spice preference: 4/5
- Sweetness preference: 2/5
- Savory preference: 3/5
- Preferred cuisines: ["Indonesian", "Asian"]
- Price importance: 0.5
- Distance importance: 0.3
- Popularity importance: 0.2

**Perhitungan:**

1. **Price Score (μ_price)**
   ```
   Harga: 15.000
   Medium: (10.000, 20.000, 30.000)

   Left slope = (15.000 - 10.000) / (20.000 - 10.000) = 0.5
   Right slope = (30.000 - 15.000) / (30.000 - 20.000) = 1.5

   μ_price = min(0.5, 1.5) = 0.5
   ```

2. **Distance Score (μ_distance)**
   ```
   μ_distance = 1 - (2/5) = 0.6
   ```

3. **Popularity Score (μ_popularity)**
   ```
   μ_popularity = 25 / 500 = 0.05
   ```

4. **Taste Score (μ_taste)**
   ```
   Spice: |3 - 4| = 1 → μ = 1 - (1/5) = 0.8
   Sweetness: |2 - 2| = 0 → μ = 1.0
   Savory: |4 - 3| = 1 → μ = 1 - (1/5) = 0.8

   Average taste = (0.8 + 1.0 + 0.8) / 3 = 0.867
   ```

5. **Cuisine Score (μ_cuisine)**
   ```
   Exact match: "Indonesian" in ["Indonesian", "Asian"]
   μ_cuisine = 1.0
   ```

6. **Fuzzy Score Total (Sf)**
   ```
   w_price = 0.5
   w_distance = 0.3
   w_popularity = 0.2
   w_taste = 0.5
   w_cuisine = 0.3

   Total weight = 0.5 + 0.3 + 0.2 + 0.5 + 0.3 = 1.8

   Sf = (0.5×0.5 + 0.3×0.6 + 0.2×0.05 + 0.5×0.867 + 0.3×1.0) / 1.8
      = (0.25 + 0.18 + 0.01 + 0.434 + 0.3) / 1.8
      = 1.174 / 1.8
      = 0.652
   ```

**Hasil: Fuzzy Score = 0.652 (65.2% kecocokan dengan preferensi customer)**

---

## 3. COLLABORATIVE FILTERING

### Konsep Dasar
Collaborative Filtering (CF) digunakan untuk menemukan pola komunitas dengan cara memprediksi rating berdasarkan preferensi user-user lain yang mirip.

### 3.1 Membangun User-Item Matrix

**Rumus (collaborative_filtering.py:38-93):**
```
M[i,j] = Rating dari user i untuk item j
M[i,j] = 0 jika user i belum merating item j
```

**Implementasi Python:**
```python
def build_user_item_matrix(self) -> pd.DataFrame:
    """
    Build user-item rating matrix dari database

    Returns:
        DataFrame dengan customers sebagai rows, menus sebagai columns
        Values: rating (1-5), 0 jika belum dirating
    """
    query = """
    SELECT
        customer_id,
        menu_id,
        score
    FROM ratings
    ORDER BY customer_id, menu_id
    """

    # Execute query
    result = self.db.execute(text(query))
    data = [{'customer_id': str(row[0]), 'menu_id': str(row[1]), 'score': float(row[2])}
           for row in result]

    # Create DataFrame
    df = pd.DataFrame(data)

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
```

**Contoh Matrix:**
```
            Menu1  Menu2  Menu3  Menu4  Menu5
Customer1   5.0    4.0    0.0    3.0    0.0
Customer2   4.0    0.0    5.0    0.0    3.0
Customer3   0.0    3.0    4.0    5.0    0.0
Customer4   3.0    5.0    0.0    4.0    5.0
Customer5   5.0    0.0    3.0    0.0    4.0
```

### 3.2 Similarity Calculation (Pearson Correlation)

**Rumus (collaborative_filtering.py:95-150):**
```
sim(u,v) = Σ((Ru,i - R̄u)(Rv,i - R̄v)) /
           (Σ(Ru,i - R̄u)² × Σ(Rv,i - R̄v)²)^0.5
```

Dimana:
- `Ru,i` = Rating user u untuk item i
- `R̄u` = Rata-rata rating user u
- `Rv,i` = Rating user v untuk item i
- `R̄v` = Rata-rata rating user v

**Implementasi Python:**
```python
def calculate_pearson_similarity(self,
                                user1_ratings: np.ndarray,
                                user2_ratings: np.ndarray,
                                min_common_items: int = 2) -> float:
    """
    Calculate Pearson Correlation Coefficient antara dua users

    Args:
        user1_ratings: Rating array untuk user 1
        user2_ratings: Rating array untuk user 2
        min_common_items: Minimum jumlah items yang sama-sama dirating

    Returns:
        Similarity score [-1, 1]
        -1: Perfect negative correlation
        0: No correlation
        1: Perfect positive correlation
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
    numerator = np.sum((u1_common - mean_u1) * (u2_common - mean_u2))

    sum_sq_diff_u1 = np.sum((u1_common - mean_u1) ** 2)
    sum_sq_diff_u2 = np.sum((u2_common - mean_u2) ** 2)
    denominator = np.sqrt(sum_sq_diff_u1 * sum_sq_diff_u2)

    # Avoid division by zero
    if denominator == 0:
        return 0.0

    similarity = numerator / denominator

    # Clamp to [-1, 1]
    return max(-1.0, min(1.0, similarity))
```

**Contoh Perhitungan Similarity:**
```
User A ratings:  [5, 4, 0, 3, 0]
User B ratings:  [4, 0, 5, 0, 3]

Common items (both > 0): indices 0 and 2? No!

Let's find common items:
User A: [5, 4, 0, 3, 0]
User B: [4, 0, 5, 0, 3]

Common items (both rated):
  - Item 0: A=5, B=4 ✓
  - Item 3: A=3, B=0 ✗
  - Item 4: A=0, B=3 ✗

Only common item: Item 0 (not enough, need at least 2)

Let's use another example:
User A: [5, 4, 3, 2, 1]
User B: [4, 5, 2, 3, 1]

Common items: All 5 items

Mean A: (5+4+3+2+1)/5 = 3.0
Mean B: (4+5+2+3+1)/5 = 3.0

Numerator:
  (5-3)(4-3) + (4-3)(5-3) + (3-3)(2-3) + (2-3)(3-3) + (1-3)(1-3)
  = (2)(1) + (1)(2) + (0)(-1) + (-1)(0) + (-2)(-2)
  = 2 + 2 + 0 + 0 + 4 = 8

Denominator:
  √[(5-3)² + (4-3)² + (3-3)² + (2-3)² + (1-3)²] ×
  √[(4-3)² + (5-3)² + (2-3)² + (3-3)² + (1-3)²]
  = √[4+1+0+1+4] × √[1+4+1+0+4]
  = √10 × √10 = 3.162 × 3.162 = 10

sim(A,B) = 8/10 = 0.8
```

### 3.3 K-Nearest Neighbors (KNN)

**Rumus (collaborative_filtering.py:179-235):**
```
N(u) = Top-K users yang memiliki similarity tertinggi dengan user u
```

**Implementasi Python:**
```python
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
    """
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
```

### 3.4 Rating Prediction

**Rumus (collaborative_filtering.py:237-323):**
```
Pcf(u,i) = R̄u + (Σ sim(u,v) × (Rv,i - R̄v)) / Σ|sim(u,v)|
```

Dimana:
- `v ∈ N` (neighbors of u)
- `sim(u,v)` = similarity antara users u dan v
- `Rv,i` = rating user v untuk item i
- `R̄u` = rata-rata rating user u
- `R̄v` = rata-rata rating user v

**Implementasi Python:**
```python
def predict_rating(self,
                  user_id: str,
                  menu_id: str,
                  k: int = 10,
                  method: str = 'pearson') -> float:
    """
    Predict rating untuk user-menu pair menggunakan Collaborative Filtering

    Args:
        user_id: Target user ID
        menu_id: Target menu ID
        k: Number of neighbors
        method: Similarity method ('pearson' atau 'cosine')

    Returns:
        Predicted rating [1, 5]
    """
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
```

**Contoh Perhitungan Prediksi:**
```
Target User: User A
Target Menu: Menu X
User A mean rating: 3.5
K = 3 neighbors

Neighbors found:
  User B: sim = 0.8, rating for Menu X = 5, mean = 4.2
  User C: sim = 0.6, rating for Menu X = 4, mean = 3.8
  User D: sim = 0.4, rating for Menu X = 0 (not rated)

Calculate:
  Numerator = 0.8×(5-4.2) + 0.6×(4-3.8)
            = 0.8×0.8 + 0.6×0.2
            = 0.64 + 0.12
            = 0.76

  Denominator = |0.8| + |0.6|
              = 0.8 + 0.6
              = 1.4

  Pcf(A,X) = 3.5 + (0.76/1.4)
           = 3.5 + 0.54
           = 4.04

Prediksi rating untuk User A pada Menu X = 4.04
```

---

## 4. HYBRID COMBINATION

### Konsep Dasar
Sistem menggabungkan Fuzzy Logic dan Collaborative Filtering menggunakan pendekatan **Weighted Hybrid** untuk mendapatkan kelebihan dari kedua metode.

### 4.1 Rumus Hybrid Score

**Rumus Utama (hybrid.py:172-261):**
```
Hscore(u,i) = (α × Sf(u,i)) + ((1-α) × Pcf(u,i)/Rmax)
```

Dimana:
- `Sf(u,i)` = Fuzzy score [0,1] - preferensi match
- `Pcf(u,i)` = Predicted rating dari CF [1,5]
- `Rmax` = Maximum rating (5) untuk normalisasi
- `α` = Weight parameter [0,1]

**Implementasi Python:**
```python
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

    Args:
        customer_id: Target customer ID
        menu: Menu data dictionary
        customer_pref: Customer preference dictionary
        customer_location: (latitude, longitude) customer
        menu_location: (latitude, longitude) merchant
        k_neighbors: Number of neighbors untuk CF
        alpha: Override default alpha

    Returns:
        Dictionary dengan fuzzy_score, cf_score, predicted_rating, hybrid_score
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
```

### 4.2 Adaptive Alpha

Sistem menggunakan **merchant-based adaptive alpha** untuk menyesuaikan bobot berdasarkan seberapa banyak rating yang dimiliki merchant.

**Rumus (hybrid.py:134-170):**
```
if merchant_rating_count <= 5:
    α = 1.0  # 100% Fuzzy (cold start merchant)
elif merchant_rating_count <= 20:
    α = 0.6  # 60% Fuzzy, 40% CF
else:
    α = 0.3  # 30% Fuzzy, 70% CF (established merchant)
```

**Implementasi Python:**
```python
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
```

**Contoh Adaptive Alpha:**
```
Scenario 1: New Merchant
  Merchant rating count: 3
  α = 1.0 (100% Fuzzy)

  Hscore = (1.0 × Sf) + (0.0 × Pcf/5)
         = Sf (pure fuzzy, location & preference based)

Scenario 2: Growing Merchant
  Merchant rating count: 15
  α = 0.6 (60% Fuzzy, 40% CF)

  Hscore = (0.6 × Sf) + (0.4 × Pcf/5)

Scenario 3: Established Merchant
  Merchant rating count: 50
  α = 0.3 (30% Fuzzy, 70% CF)

  Hscore = (0.3 × Sf) + (0.7 × Pcf/5)
         (trust community ratings more)
```

### 4.3 Contoh Perhitungan Hybrid

**Input:**
- Fuzzy Score (Sf) = 0.652
- CF Predicted Rating (Pcf) = 4.04
- Alpha (α) = 0.5 (balanced)
- Max Rating = 5

**Perhitungan:**
```
Step 1: Normalize CF score
  cf_score_normalized = 4.04 / 5 = 0.808

Step 2: Calculate hybrid score
  Hscore = (0.5 × 0.652) + (0.5 × 0.808)
         = 0.326 + 0.404
         = 0.73

Hasil: Hybrid Score = 0.73 (73% recommendation score)
```

**Dengan Alpha Berbeda:**
```
α = 0.2 (favor CF):
  Hscore = (0.2 × 0.652) + (0.8 × 0.808)
         = 0.130 + 0.646
         = 0.776

α = 0.8 (favor Fuzzy):
  Hscore = (0.8 × 0.652) + (0.2 × 0.808)
         = 0.522 + 0.162
         = 0.684
```

---

## 5. ALGORITMA BASELINE

### Konsep Dasar
Algoritma baseline digunakan untuk validasi performa dan pembandingan dengan sistem hybrid yang diusulkan. Sistem menggunakan **4 algoritma baseline** yang umum digunakan dalam sistem rekomendasi.

### 5.1 Random Baseline

**Konsep:** Memberikan rekomendasi secara acak tanpa mempertimbangkan preferensi user atau histori rating.

**Rumus (evaluation.py:934-945):**
```
P_random(u,i) = random_value(1, 5)
```

**Implementasi Python (evaluation.py:1476-1484):**
```python
# 1. Random Baseline
random.seed(random_state + fold_idx)  # FIXED: different seed per fold but consistent
random_predictions = [random.uniform(1, 5) for _ in test_data]
random_actuals = [r.score for r in test_data]
random_mae = float(np.mean([abs(p - a) for p, a in zip(random_predictions, random_actuals)]))
random_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(random_predictions, random_actuals)])))
```

**Contoh Perhitungan:**
```
Random seed: 42 + 0 = 42
Test data: 102 ratings

Random predictions: [3.2, 4.7, 2.1, 4.8, 3.9, ...] (102 random values)
Actual ratings:     [4.0, 5.0, 3.0, 4.0, 4.0, ...]

Errors: [0.8, 0.3, 0.9, 0.8, 0.1, ...]

MAE = mean([0.8, 0.3, 0.9, 0.8, 0.1, ...]) = 1.4723
RMSE = sqrt(mean([0.64, 0.09, 0.81, 0.64, 0.01, ...])) = 1.7992
```

**Kelebihan:**
- Sederhana dan cepat
- Tidak memerlukan training

**Kekurangan:**
- Tidak mempertimbangkan preferensi user
- Hasil tidak konsisten
- Performa buruk (MAE = 1.4723, RMSE = 1.7992)

### 5.2 Most Popular Baseline

**Konsep:** Merekomendasikan item-item yang paling populer berdasarkan jumlah rating.

**Rumus (evaluation.py:948-962):**
```
P_popular(u,i) = average_rating_of_item_i
```

Jika item i belum ada rating, gunakan rata-rata rating global dari training set.

**Implementasi Python (evaluation.py:1486-1500):**
```python
# 2. Most Popular Baseline
popular_predictions = []
for r in test_data:
    menu_ratings = [rating.score for rating in train_data if rating.menu_id == r.menu_id]
    if menu_ratings:
        popular_predictions.append(np.mean(menu_ratings))
    else:
        popular_predictions.append(avg_rating_train)

popular_actuals = [r.score for r in test_data]
popular_mae = float(np.mean([abs(p - a) for p, a in zip(popular_predictions, popular_actuals)]))
popular_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(popular_predictions, popular_actuals)])))
```

**Contoh Perhitungan:**
```
Training set:
  Menu1: ratings = [5, 4, 5, 4, 5] → average = 4.6
  Menu2: ratings = [4, 3, 4, 5, 3] → average = 3.8
  Menu3: ratings = [5, 5, 4, 5, 5] → average = 4.8
  Menu4: ratings = [3, 4, 3, 4, 3] → average = 3.4

Test user: rating Menu2 (actual = 4.0)
Prediction: average(Menu2) = 3.8
Error: |3.8 - 4.0| = 0.2

Test user: rating Menu5 (actual = 4.0) - Menu5 not in training
Prediction: global_average = 4.0
Error: |4.0 - 4.0| = 0.0

MAE = mean([0.2, 0.0, ...]) = 0.5746
RMSE = sqrt(mean([0.04, 0.0, ...])) = 0.7452
```

**Kelebihan:**
- Memanfaatkan wisdom of the crowd
- Stabil dan konsisten
- Performa baik (MAE = 0.5746, RMSE = 0.7452)

**Kekurangan:**
- Tidak personalized (sama untuk semua user)
- Cold start problem untuk item baru
- Tidak mempertimbangkan preferensi individual

### 5.3 Average Rating Baseline

**Konsep:** Memprediksi rating menggunakan rata-rata rating global dari semua user.

**Rumus (evaluation.py:967-978):**
```
P_average(u,i) = global_average_rating
```

**Implementasi Python (evaluation.py:1502-1509):**
```python
# 3. Average Rating Baseline
avg_predictions = [avg_rating_train for _ in test_data]
avg_actuals = [r.score for r in test_data]
avg_mae = float(np.mean([abs(p - a) for p, a in zip(avg_predictions, avg_actuals)]))
avg_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(avg_predictions, avg_actuals)])))
```

**Contoh Perhitungan:**
```
Training set: 408 ratings
Sum of ratings: 1632
Global average: 1632 / 408 = 4.0

Test predictions: [4.0, 4.0, 4.0, ...] (102 times, always 4.0)
Actual ratings: [4.0, 5.0, 3.0, 4.0, ...]

Errors: [0.0, 1.0, 1.0, 0.0, ...]

MAE = mean([0.0, 1.0, 1.0, 0.0, ...]) = 0.4730
RMSE = sqrt(mean([0.0, 1.0, 1.0, 0.0, ...])) = 0.6816
```

**Kelebihan:**
- Sangat sederhana
- Cepat dan efisien
- Performa sangat baik (MAE = 0.4730, RMSE = 0.6816)

**Kekurangan:**
- Tidak personalized sama sekali
- Sama untuk semua user dan semua item
- Tidak menangkap preferensi individual

### 5.4 Item-Based Collaborative Filtering Baseline

**Konsep:** Memprediksi rating berdasarkan similarity antar item yang dirasakan oleh user yang sama.

**Rumus (evaluation.py:980-1041):**
```
sim(i,j) = correlation(item_i_ratings, item_j_ratings)

P_item_cf(u,i) = (Σ sim(i,j) × R(u,j)) / Σ|sim(i,j)|
```

Dimana:
- `i` = target item
- `j` = item lain yang similar dengan item i
- `sim(i,j)` = similarity antara item i dan item j
- `R(u,j)` = rating user u untuk item j

**Implementasi Python (evaluation.py:1511-1562):**
```python
# 4. Item-Based CF (with FIXED random_state)
# Set random seed for consistency
np.random.seed(random_state + fold_idx)

# Calculate item-item similarities
item_similarities = {}
all_items = list(set([r.menu_id for r in train_data]))

for item1 in all_items:
    item_similarities[item1] = {}
    for item2 in all_items:
        if item1 != item2:
            ratings1 = []
            ratings2 = []
            for user_id in user_ratings:
                if item1 in user_ratings[user_id] and item2 in user_ratings[user_id]:
                    ratings1.append(user_ratings[user_id][item1])
                    ratings2.append(user_ratings[user_id][item2])

            if len(ratings1) >= 2:
                corr = np.corrcoef(ratings1, ratings2)[0, 1]
                if not np.isnan(corr):
                    item_similarities[item1][item2] = corr

# Predict menggunakan item-based CF
item_cf_predictions = []
for r in test_data:
    if r.menu_id in item_similarities:
        similar_items = sorted(
            item_similarities[r.menu_id].items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]  # Top 5 similar items

        if similar_items:
            weighted_sum = 0
            weight_sum = 0
            for item_id, similarity in similar_items:
                if r.customer_id in user_ratings and item_id in user_ratings[r.customer_id]:
                    weighted_sum += similarity * user_ratings[r.customer_id][item_id]
                    weight_sum += abs(similarity)

            if weight_sum > 0:
                item_cf_predictions.append(weighted_sum / weight_sum)
                continue

    # Fallback jika tidak ada similar items
    item_cf_predictions.append(avg_rating_train)
```

**Contoh Perhitungan:**
```
User ratings:
  User1: {Menu1: 5, Menu2: 4, Menu3: 3}
  User2: {Menu1: 4, Menu2: 5, Menu4: 3}
  User3: {Menu2: 3, Menu3: 5, Menu4: 4}

Calculate item similarities:

Menu1 vs Menu2:
  Common users: User1, User2
  Menu1 ratings: [5, 4]
  Menu2 ratings: [4, 5]
  Correlation: -1.0 (perfect negative correlation)

Menu1 vs Menu3:
  Common users: User1
  Not enough common users (need ≥ 2)
  Similarity: 0.0

Menu2 vs Menu3:
  Common users: User1, User3
  Menu2 ratings: [4, 3]
  Menu3 ratings: [3, 5]
  Similarity: calculate correlation...

Predict User3 rating for Menu1:
  Similar items to Menu1: Menu2 (sim = -1.0)
  User3 rating for Menu2 = 3

  Prediction = (-1.0 × 3) / |−1.0| = -3.0 → Clip to [1,5] = 1.0

Actual rating = 4.0
Error = |1.0 - 4.0| = 3.0

MAE = 2.2627 (poor performance due to sparse data)
RMSE = 3.6674
```

**Kelebihan:**
- Personalized berdasarkan item similarity
- Cocok untuk domain dengan item yang stable

**Kekurangan:**
- Performa buruk pada sparse data (MAE = 2.2627)
- Membutuhkan banyak user overlap antar items
- Computationally expensive untuk banyak items
- Cold start problem untuk item baru

### 5.5 Perbandingan Performa Baseline

**Hasil Evaluasi (5-Fold Cross-Validation):**

| Algorithm | MAE ↓ | RMSE ↓ | Performance | Kategori |
|-----------|-------|--------|-------------|-----------|
| **Random** | 1.4723 | 1.7992 | Poor | Non-Personalized |
| **Most Popular** | 0.5746 | 0.7452 | Excellent | Non-Personalized |
| **Average Rating** | 0.4730 | 0.6816 | Excellent | Non-Personalized |
| **Item-Based CF** | 2.2627 | 3.6674 | Poor | Personalized |
| **User-Based CF (α=0)** | 0.4419 | 0.5627 | Excellent | Personalized |
| **Fuzzy Logic (α=1)** | 1.8003 | 2.0374 | Poor | Personalized |
| **Hybrid (α=0.5)** | 0.9585 | 1.1136 | Good | Personalized |

**Analisis:**

1. **Random Baseline** (MAE = 1.4723)
   - Performa terburuk kedua
   - Tidak ada inteligensi sama sekali
   - Digunakan sebagai lower bound

2. **Most Popular** (MAE = 0.5746)
   - Performa sangat baik
   - Mendekati User-Based CF
   - Menunjukkan bahwa popularitas adalah prediktor kuat

3. **Average Rating** (MAE = 0.4730)
   - Performa terbaik di antara non-personalized methods
   - Hanya sedikit di atas User-Based CF
   - Menunjukkan bahwa data rating cenderung converge ke mean

4. **Item-Based CF** (MAE = 2.2627)
   - Performa terburuk
   - Masalah: Data terlalu sparse (user-item matrix sangat jarang)
   - Tidak cukup user overlap antar items

5. **User-Based CF** (MAE = 0.4419)
   - Performa terbaik secara keseluruhan
   - Lebih robust terhadap sparse data
   - Pearson correlation efektif untuk user similarity

**Insight Penting:**

```
Dataset Characteristics:
- Total ratings: 512
- Sparsity: ~99% (sangat sparse)
- User-item overlap rendah

Akibat:
1. Item-based CF gagal (butuh banyak user overlap)
2. User-based CF berhasil (lebih toleran terhadap sparse data)
3. Non-personalized methods (Average, Popular) performa baik
   karena rating cenderung homogen (sekitar 4.0)
```

### 5.6 Diagram Perbandingan Baseline

```
Performa Comparison (MAE ↓ lebih baik):

0.0 ┤
     │
0.4 ┤━━━━━━━━━━━━━━━━━━━━━━ User-Based CF (Winner)
     │                  ━━━━━━━ Average Rating
0.6 ┤                  ┃      ━━━━ Most Popular
     │                  ┃      ━
0.8 ┤                  ┃      ┃
     │                  ┃      ┃
1.0 ┤                  ┃      ┃
     │                  ┃      ┃
1.2 ┤                  ┃      ┃
     │                  ┃      ┃
1.4 ┤                  ┃      ┃       ━━━━ Random
     │                  ┃      ┃       ━
1.6 ┤                  ┃      ┃       ┃
     │                  ┃      ┃       ┃
1.8 ┤                  ┃      ┃       ┃       ━━━ Fuzzy Only
     │                  ┃      ┃       ┃       ━
2.0 ┤                  ┃      ┃       ┃       ┃
     │                  ┃      ┃       ┃       ┃
2.2 ┤                  ┃      ┃       ┃       ┃       ━━━ Item-Based CF
     │                  ┃      ┃       ┃       ┃       ━ (Worst)
2.4 ┤                  ┃      ┃       ┃       ┃       ┃
     └──────────────────┴──────┴───────┴───────┴───────┴───────
```

### 5.7 Implementasi Kode Lengkap

**Lokasi File**: `backend/app/algorithms/evaluation.py:1390-1629`

```python
def compare_with_baselines(self,
                          ratings: List[Rating],
                          test_size: float = 0.2,
                          k: int = 10,
                          n_splits: int = 5,
                          random_state: int = 42) -> Dict:
    """
    Bandingkan Hybrid dengan berbagai baseline algorithms

    Baselines:
    1. Random - Rekomendasi acak
    2. Most Popular - Menu paling populer
    3. Average Rating - Rata-rata rating global
    4. Item-Based CF - Collaborative filtering berbasis item
    5. User-Based CF - Collaborative filtering berbasis user
    6. Hybrid (Ours) - Hybrid Fuzzy-CF

    Returns:
        Dictionary dengan baseline comparison results
    """
    from sklearn.model_selection import KFold
    from collections import Counter
    import random

    # Setup KFold for baseline calculations
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    # Calculate baseline metrics across all folds
    baseline_metrics = {
        'random': {'mae': [], 'rmse': [], 'predictions': []},
        'most_popular': {'mae': [], 'rmse': [], 'predictions': []},
        'average_rating': {'mae': [], 'rmse': [], 'predictions': []},
        'item_cf': {'mae': [], 'rmse': [], 'predictions': []}
    }

    # Process each fold for baselines
    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(ratings)):
        train_data = [ratings[i] for i in train_idx]
        test_data = [ratings[i] for i in test_idx]

        # Get average rating dari training set
        avg_rating_train = np.mean([r.score for r in train_data])

        # Get most popular items
        menu_counts = Counter([r.menu_id for r in train_data])
        most_popular_menus = [item for item, count in menu_counts.most_common()]

        # Prepare ratings dictionary untuk item-based CF
        user_ratings = {}
        for r in train_data:
            if r.customer_id not in user_ratings:
                user_ratings[r.customer_id] = {}
            user_ratings[r.customer_id][r.menu_id] = r.score

        # 1. Random Baseline
        random.seed(random_state + fold_idx)
        random_predictions = [random.uniform(1, 5) for _ in test_data]
        random_actuals = [r.score for r in test_data]
        random_mae = float(np.mean([abs(p - a) for p, a in zip(random_predictions, random_actuals)]))
        random_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(random_predictions, random_actuals)])))
        baseline_metrics['random']['mae'].append(random_mae)
        baseline_metrics['random']['rmse'].append(random_rmse)
        baseline_metrics['random']['predictions'].append(len(random_predictions))

        # 2. Most Popular Baseline
        popular_predictions = []
        for r in test_data:
            menu_ratings = [rating.score for rating in train_data if rating.menu_id == r.menu_id]
            if menu_ratings:
                popular_predictions.append(np.mean(menu_ratings))
            else:
                popular_predictions.append(avg_rating_train)

        popular_actuals = [r.score for r in test_data]
        popular_mae = float(np.mean([abs(p - a) for p, a in zip(popular_predictions, popular_actuals)]))
        popular_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(popular_predictions, popular_actuals)])))
        baseline_metrics['most_popular']['mae'].append(popular_mae)
        baseline_metrics['most_popular']['rmse'].append(popular_rmse)
        baseline_metrics['most_popular']['predictions'].append(len(popular_predictions))

        # 3. Average Rating Baseline
        avg_predictions = [avg_rating_train for _ in test_data]
        avg_actuals = [r.score for r in test_data]
        avg_mae = float(np.mean([abs(p - a) for p, a in zip(avg_predictions, avg_actuals)]))
        avg_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(avg_predictions, avg_actuals)])))
        baseline_metrics['average_rating']['mae'].append(avg_mae)
        baseline_metrics['average_rating']['rmse'].append(avg_rmse)
        baseline_metrics['average_rating']['predictions'].append(len(avg_predictions))

        # 4. Item-Based CF (with FIXED random_state)
        np.random.seed(random_state + fold_idx)

        # Calculate item-item similarities
        item_similarities = {}
        all_items = list(set([r.menu_id for r in train_data]))

        for item1 in all_items:
            item_similarities[item1] = {}
            for item2 in all_items:
                if item1 != item2:
                    ratings1 = []
                    ratings2 = []
                    for user_id in user_ratings:
                        if item1 in user_ratings[user_id] and item2 in user_ratings[user_id]:
                            ratings1.append(user_ratings[user_id][item1])
                            ratings2.append(user_ratings[user_id][item2])

                    if len(ratings1) >= 2:
                        corr = np.corrcoef(ratings1, ratings2)[0, 1]
                        if not np.isnan(corr):
                            item_similarities[item1][item2] = corr

        # Predict menggunakan item-based CF
        item_cf_predictions = []
        for r in test_data:
            if r.menu_id in item_similarities:
                similar_items = sorted(
                    item_similarities[r.menu_id].items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )[:5]

                if similar_items:
                    weighted_sum = 0
                    weight_sum = 0
                    for item_id, similarity in similar_items:
                        if r.customer_id in user_ratings and item_id in user_ratings[r.customer_id]:
                            weighted_sum += similarity * user_ratings[r.customer_id][item_id]
                            weight_sum += abs(similarity)

                    if weight_sum > 0:
                        item_cf_predictions.append(weighted_sum / weight_sum)
                        continue

            item_cf_predictions.append(avg_rating_train)

        item_cf_actuals = [r.score for r in test_data]
        item_cf_mae = float(np.mean([abs(p - a) for p, a in zip(item_cf_predictions, item_cf_actuals)]))
        item_cf_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(item_cf_predictions, item_cf_actuals)])))
        baseline_metrics['item_cf']['mae'].append(item_cf_mae)
        baseline_metrics['item_cf']['rmse'].append(item_cf_rmse)
        baseline_metrics['item_cf']['predictions'].append(len(item_cf_predictions))

    # Calculate average baseline metrics across folds
    results = {
        'Random': {
            'mae': float(np.mean(baseline_metrics['random']['mae'])),
            'rmse': float(np.mean(baseline_metrics['random']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['random']['predictions']))
        },
        'Most Popular': {
            'mae': float(np.mean(baseline_metrics['most_popular']['mae'])),
            'rmse': float(np.mean(baseline_metrics['most_popular']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['most_popular']['predictions']))
        },
        'Average Rating': {
            'mae': float(np.mean(baseline_metrics['average_rating']['mae'])),
            'rmse': float(np.mean(baseline_metrics['average_rating']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['average_rating']['predictions']))
        },
        'Item-Based CF': {
            'mae': float(np.mean(baseline_metrics['item_cf']['mae'])),
            'rmse': float(np.mean(baseline_metrics['item_cf']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['item_cf']['predictions']))
        }
    }

    # Add comparison with our algorithms
    # ... (add User-Based CF, Fuzzy, Hybrid results)

    # Determine winner
    if results:
        winner_name = min(results.keys(), key=lambda k: results[k]['mae'])
        results['winner'] = winner_name
        results['winner_mae'] = results[winner_name]['mae']

    return results
```

---

## 6. EVALUASI SISTEM

### 5.1 Metrik Evaluasi

#### A. Mean Absolute Error (MAE)

**Rumus (evaluation.py:136-163):**
```
MAE = (1/n) × Σ|predicted - actual|
```

**Implementasi Python:**
```python
@staticmethod
def calculate_mae(predictions: np.ndarray, actuals: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error

    Args:
        predictions: Array of predicted values
        actuals: Array of actual values

    Returns:
        MAE score (lower is better, 0 = perfect)
    """
    if len(predictions) == 0 or len(actuals) == 0:
        return 0.0

    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    return float(np.mean(np.abs(predictions - actuals)))
```

**Contoh Perhitungan:**
```
Predictions: [4.2, 3.8, 4.5, 4.1, 3.9]
Actuals:     [4.0, 4.0, 5.0, 4.0, 4.0]

Errors:      [0.2, 0.2, 0.5, 0.1, 0.1]

MAE = (0.2 + 0.2 + 0.5 + 0.1 + 0.1) / 5
    = 1.1 / 5
    = 0.22
```

#### B. Root Mean Square Error (RMSE)

**Rumus (evaluation.py:166-194):**
```
RMSE = √((1/n) × Σ(predicted - actual)²)
```

**Implementasi Python:**
```python
@staticmethod
def calculate_rmse(predictions: np.ndarray, actuals: np.ndarray) -> float:
    """
    Calculate Root Mean Square Error

    Args:
        predictions: Array of predicted values
        actuals: Array of actual values

    Returns:
        RMSE score (lower is better, 0 = perfect)
        RMSE > MAE karena penalizes large errors lebih heavily
    """
    if len(predictions) == 0 or len(actuals) == 0:
        return 0.0

    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    return float(np.sqrt(np.mean((predictions - actuals) ** 2)))
```

**Contoh Perhitungan:**
```
Predictions: [4.2, 3.8, 4.5, 4.1, 3.9]
Actuals:     [4.0, 4.0, 5.0, 4.0, 4.0]

Squared Errors: [0.04, 0.04, 0.25, 0.01, 0.01]

RMSE = √((0.04 + 0.04 + 0.25 + 0.01 + 0.01) / 5)
     = √(0.35 / 5)
     = √0.07
     = 0.265
```

#### C. Hit Rate

**Rumus (evaluation.py:197-230):**
```
Hit Rate = (Number of hits) / (Total predictions)
```

Dimana "Hit" = predicted is within ±threshold dari actual (default threshold = 0.5)

**Implementasi Python:**
```python
@staticmethod
def calculate_hit_rate(predictions: np.ndarray,
                      actuals: np.ndarray,
                      threshold: float = 0.5) -> float:
    """
    Calculate Hit Rate

    Args:
        predictions: Array of predicted ratings
        actuals: Array of actual ratings
        threshold: Toleransi error (default 0.5)

    Returns:
        Hit rate [0, 1] (higher is better)
    """
    if len(predictions) == 0 or len(actuals) == 0:
        return 0.0

    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    hits = np.sum(np.abs(predictions - actuals) <= threshold)
    return float(hits / len(actuals))
```

**Contoh Perhitungan:**
```
Predictions: [4.2, 3.8, 4.5, 4.1, 3.9]
Actuals:     [4.0, 4.0, 5.0, 4.0, 4.0]
Threshold:   0.5

Differences: [0.2, 0.2, 0.5, 0.1, 0.1]
Hits:        [✓,   ✓,   ✓,   ✓,   ✓]

Hit Rate = 5/5 = 1.0 (100%)
```

### 5.2 Cross-Validation Evaluation

Sistem menggunakan **5-Fold Cross-Validation** untuk evaluasi yang robust.

**Rumus (evaluation.py:374-519):**
```
for each fold in 5 folds:
    train_data = data[fold != test_fold]
    test_data = data[fold == test_fold]

    predictions = model.predict(test_data)
    metrics = calculate_metrics(predictions, actuals)

avg_metrics = mean(metrics across all folds)
std_metrics = std(metrics across all folds)
```

**Implementasi Python:**
```python
def cross_validate(self,
                  ratings: List[Rating],
                  n_splits: int = 5,
                  alpha_values: List[float] = None,
                  random_state: int = 42) -> Dict[str, Dict]:
    """
    K-Fold Cross Validation untuk algorithm evaluation

    Uses REPEATED K-Fold for statistical robustness:
    - Default: 5-fold CV with random_state=42
    - Can be repeated with different random_states for larger sample size

    Args:
        ratings: List of Rating objects
        n_splits: Number of folds (default: 5)
        alpha_values: List of alpha values untuk di-test
        random_state: Random state for KFold reproducibility (default: 42)

    Returns:
        Dictionary dengan average metrics per alpha value PLUS raw per-fold data
    """
    from sklearn.model_selection import KFold

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    # Initialize results storage
    all_results = {alpha: {'mae': [], 'rmse': [], 'hit_rate': []}
                  for alpha in alpha_values}

    # Cross-validation
    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(ratings)):
        train_data = [ratings[i] for i in train_idx]
        test_data = [ratings[i] for i in test_idx]

        for alpha in alpha_values:
            recommender = HybridRecommender(self.db, alpha=alpha)

            predictions = []
            actuals = []

            for rating in test_data:
                try:
                    predicted = recommender.predict_rating_hybrid(
                        user_id=str(rating.customer_id),
                        menu_id=str(rating.menu_id),
                        k=10
                    )

                    predictions.append(predicted)
                    actuals.append(float(rating.score))

                except Exception as e:
                    continue

            if len(predictions) > 0:
                predictions_np = np.array(predictions)
                actuals_np = np.array(actuals)

                mae = self.calculate_mae(predictions_np, actuals_np)
                rmse = self.calculate_rmse(predictions_np, actuals_np)
                hit_rate = self.calculate_hit_rate(predictions_np, actuals_np)

                all_results[alpha]['mae'].append(mae)
                all_results[alpha]['rmse'].append(rmse)
                all_results[alpha]['hit_rate'].append(hit_rate)

    # Calculate averages
    avg_results = {}

    for alpha in alpha_values:
        mae_std = float(np.std(all_results[alpha]['mae']))
        rmse_std = float(np.std(all_results[alpha]['rmse']))

        avg_results[f'alpha_{alpha}'] = {
            'alpha': alpha,
            'avg_mae': float(np.mean(all_results[alpha]['mae'])),
            'std_mae': mae_std,
            'avg_rmse': float(np.mean(all_results[alpha]['rmse'])),
            'std_rmse': rmse_std,
            'avg_hit_rate': float(np.mean(all_results[alpha]['hit_rate'])),
            'std_hit_rate': float(np.std(all_results[alpha]['hit_rate'])),
            # Store raw per-fold data for statistical testing
            'raw_mae_per_fold': all_results[alpha]['mae'],
            'raw_rmse_per_fold': all_results[alpha]['rmse'],
            'raw_hit_rate_per_fold': all_results[alpha]['hit_rate'],
            'n_folds': n_splits,
            'random_state': random_state
        }

    return avg_results
```

### 5.3 Statistical Significance Testing

Sistem menggunakan **Paired t-test dari hasil Cross-Validation** untuk menguji signifikansi perbedaan antara dua alpha values.

**Rumus (evaluation.py:610-795):**
```
t_statistic, p_value = ttest_rel(mae_alpha1, mae_alpha2)

mean_diff = mean(mae_alpha1 - mae_alpha2)

ci_95 = mean_diff ± t_critical × SE

effect_size = mean_diff / pooled_std
```

**Implementasi Python:**
```python
def statistical_significance_test(self,
                                  ratings: List[Rating],
                                  alpha1: float = 0.5,
                                  alpha2: float = 0.0,
                                  n_repetitions: int = 3,
                                  n_splits: int = 5,
                                  random_state: int = 42) -> Dict:
    """
    Statistical significance testing antara dua alpha values

    Methodology:
    1. Jalankan 5-fold Cross-Validation untuk alpha1 dan alpha2
    2. Gunakan REPEATED k-fold: ulangi 5-fold sebanyak 3 kali dengan random_state berbeda
       Total sampel: 15 pasang (3 repetisi × 5 fold) untuk statistical power yang kuat
    3. Ambil raw MAE per fold untuk setiap alpha
    4. Jalankan paired t-test (scipy.stats.ttest_rel) pada pasangan MAE per fold

    Returns:
        Dictionary dengan t_statistic, p_value, is_significant, effect_size, dll.
    """
    from scipy import stats as scipy_stats

    # Collect MAE values from each fold and repetition
    mae_alpha1_all = []
    mae_alpha2_all = []

    # Random states for repetitions
    random_states = [random_state + i for i in range(n_repetitions)]

    for rep_idx in range(n_repetitions):
        rep_random_state = random_states[rep_idx]

        # Run 5-fold CV untuk alpha1 dan alpha2
        cv_results = self.cross_validate(
            ratings=ratings,
            n_splits=n_splits,
            alpha_values=[alpha1, alpha2],
            random_state=rep_random_state
        )

        # Extract raw MAE per fold
        mae_alpha1_fold = cv_results[f'alpha_{alpha1}']['raw_mae_per_fold']
        mae_alpha2_fold = cv_results[f'alpha_{alpha2}']['raw_mae_per_fold']

        # Store all MAE values
        mae_alpha1_all.extend(mae_alpha1_fold)
        mae_alpha2_all.extend(mae_alpha2_fold)

    # Convert to numpy arrays
    mae_alpha1_all = np.array(mae_alpha1_all)
    mae_alpha2_all = np.array(mae_alpha2_all)

    # Paired t-test
    t_statistic, p_value = scipy_stats.ttest_rel(mae_alpha1_all, mae_alpha2_all)

    # Mean difference
    mean_diff = np.mean(mae_alpha1_all - mae_alpha2_all)

    # Standard error of difference
    std_diff = np.std(mae_alpha1_all - mae_alpha2_all, ddof=1)
    n_samples = len(mae_alpha1_all)
    se_diff = std_diff / np.sqrt(n_samples)

    # 95% Confidence Interval
    from scipy.stats import t as t_dist
    ci_critical = t_dist.ppf(0.975, df=n_samples-1)
    ci_lower = mean_diff - (ci_critical * se_diff)
    ci_upper = mean_diff + (ci_critical * se_diff)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.std(mae_alpha1_all)**2 + np.std(mae_alpha2_all)**2) / 2)
    effect_size = mean_diff / pooled_std if pooled_std > 0 else 0

    # Interpretation
    is_significant = p_value < 0.05

    if is_significant:
        if mean_diff > 0:
            interpretation = f"Alpha {alpha2} secara signifikan lebih baik dari Alpha {alpha1}"
        else:
            interpretation = f"Alpha {alpha1} secara signifikan lebih baik dari Alpha {alpha2}"
    else:
        interpretation = f"Tidak ada perbedaan signifikan antara Alpha {alpha1} dan Alpha {alpha2}"

    return {
        'alpha1': float(alpha1),
        'alpha2': float(alpha2),
        'mean_error_alpha1': float(np.mean(mae_alpha1_all)),
        'mean_error_alpha2': float(np.mean(mae_alpha2_all)),
        'mean_difference': float(mean_diff),
        't_statistic': float(t_statistic),
        'p_value': float(p_value),
        'is_significant': bool(is_significant),
        'ci_95_lower': float(ci_lower),
        'ci_95_upper': float(ci_upper),
        'effect_size': float(effect_size),
        'interpretation': interpretation,
        'n_samples': int(n_samples),
        'raw_mae_per_fold': {
            'alpha1': mae_alpha1_all.tolist(),
            'alpha2': mae_alpha2_all.tolist()
        },
        'methodology': 'paired_t_test_from_cv_folds'
    }
```

---

## 7. PARAMETER DAN KONFIGURASI

### 6.1 Parameter Fuzzy Logic

| Parameter | Default | Range | Deskripsi |
|-----------|---------|-------|-----------|
| `w_price` | 0.5 | 0.0-1.0 | Bobot kepentingan harga |
| `w_distance` | 0.3 | 0.0-1.0 | Bobot kepentingan jarak |
| `w_popularity` | 0.2 | 0.0-1.0 | Bobot kepentingan popularitas |
| `w_taste` | 0.5 | 0.0-1.0 | Bobot kepentingan rasa (fixed) |
| `w_cuisine` | 0.3 | 0.0-1.0 | Bobot kepentingan jenis masakan (fixed) |
| `max_distance_km` | 10 | 1-20 | Jarak maksimum dalam km |
| `max_popularity` | 500 | 100-1000 | Popularitas maksimum |

### 6.2 Parameter Collaborative Filtering

| Parameter | Default | Range | Deskripsi |
|-----------|---------|-------|-----------|
| `k` | 10 | 5-20 | Jumlah neighbors (KNN) |
| `min_common_items` | 2 | 1-5 | Minimum items yang sama-sama dirating |
| `similarity_method` | 'pearson' | 'pearson' atau 'cosine' | Metode similarity |
| `default_rating` | 3.0 | 1-5 | Rating default untuk fallback |

### 6.3 Parameter Hybrid

| Parameter | Default | Range | Deskripsi |
|-----------|---------|-------|-----------|
| `alpha` | 0.5 | 0.0-1.0 | Bobot Fuzzy vs CF |
| `max_rating` | 5.0 | 1-5 | Rating maksimum untuk normalisasi |
| `adaptive_alpha_enabled` | True | Boolean | Gunakan adaptive alpha |

### 6.4 Adaptive Alpha Thresholds

| Kondisi | Alpha | Persentase Fuzzy | Persentase CF |
|---------|-------|-----------------|---------------|
| Merchant baru (0-5 ratings) | 1.0 | 100% | 0% |
| Merchant sedang (6-20 ratings) | 0.6 | 60% | 40% |
| Merchant terbukti (20+ ratings) | 0.3 | 30% | 70% |

---

## 8. RUMUS-RUMUS LENGKAP

### 7.1 Fuzzy Logic

**Triangular Membership Function:**
```
μ(x) = max(0, min((x-a)/(b-a), (c-x)/(c-b)))
```

**Distance Membership:**
```
μ(distance) = 1 - (distance / max_distance)
```

**Taste Matching:**
```
μ_taste = 1 - (|item_level - preferred_level| / max_difference)
```

**Fuzzy Score:**
```
Sf(u,i) = (w_price × μ_price + w_distance × μ_distance +
           w_popularity × μ_popularity + w_taste × μ_taste +
           w_cuisine × μ_cuisine) / Σw
```

### 7.2 Collaborative Filtering

**User-Item Matrix:**
```
M[i,j] = Rating dari user i untuk item j
M[i,j] = 0 jika user i belum merating item j
```

**Pearson Correlation:**
```
sim(u,v) = Σ((Ru,i - R̄u)(Rv,i - R̄v)) /
           (Σ(Ru,i - R̄u)² × Σ(Rv,i - R̄v)²)^0.5
```

**Rating Prediction:**
```
Pcf(u,i) = R̄u + (Σ sim(u,v) × (Rv,i - R̄v)) / Σ|sim(u,v)|
```

### 7.3 Hybrid Combination

**Hybrid Score:**
```
Hscore(u,i) = (α × Sf(u,i)) + ((1-α) × Pcf(u,i)/Rmax)
```

**Adaptive Alpha:**
```
if merchant_rating_count <= 5:
    α = 1.0
elif merchant_rating_count <= 20:
    α = 0.6
else:
    α = 0.3
```

### 7.4 Evaluasi

**MAE:**
```
MAE = (1/n) × Σ|predicted - actual|
```

**RMSE:**
```
RMSE = √((1/n) × Σ(predicted - actual)²)
```

**Hit Rate:**
```
Hit Rate = (Number of hits) / (Total predictions)
```

**Paired t-test:**
```
t = (mean_diff) / (std_diff / √n)

p_value = P(T > |t|)

CI_95 = mean_diff ± t_critical × SE
```

**Cohen's d (Effect Size):**
```
d = mean_diff / pooled_std

pooled_std = √((std1² + std2²) / 2)
```

### 7.5 Baseline Algorithms

**Random Baseline:**
```
P_random(u,i) = random_value(1, 5)
```

**Most Popular Baseline:**
```
P_popular(u,i) = average_rating_of_item_i
```

**Average Rating Baseline:**
```
P_average(u,i) = global_average_rating
```

**Item-Based CF Baseline:**
```
sim(i,j) = correlation(item_i_ratings, item_j_ratings)

P_item_cf(u,i) = (Σ sim(i,j) × R(u,j)) / Σ|sim(i,j)|
```

**MAE:**
```
MAE = (1/n) × Σ|predicted - actual|
```

**RMSE:**
```
RMSE = √((1/n) × Σ(predicted - actual)²)
```

**Hit Rate:**
```
Hit Rate = (Number of hits) / (Total predictions)
```

**Paired t-test:**
```
t = (mean_diff) / (std_diff / √n)

p_value = P(T > |t|)

CI_95 = mean_diff ± t_critical × SE
```

**Cohen's d (Effect Size):**
```
d = mean_diff / pooled_std

pooled_std = √((std1² + std2²) / 2)
```

---

## PENUTUP

Dokumentasi ini menjelaskan secara detail bagaimana algoritma-algoritma dalam sistem rekomendasi LCicious bekerja, mulai dari Fuzzy Logic untuk preferensi subjektif, Collaborative Filtering untuk pola komunitas, hingga Hybrid Combination yang menggabungkan kedua metode tersebut.

### File Terkait:
- **Implementasi Fuzzy**: `/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend/app/algorithms/fuzzy.py`
- **Implementasi CF**: `/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend/app/algorithms/collaborative_filtering.py`
- **Implementasi Hybrid**: `/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend/app/algorithms/hybrid.py`
- **Implementasi Evaluasi**: `/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend/app/algorithms/evaluation.py`

### Aplikasi:
- **Frontend**: https://lcious.mygarden.my.id
- **Backend**: http://127.0.0.1:8001
- **Admin**: https://lcious.mygarden.my.id/admin
- **Evaluasi**: https://lcious.mygarden.my.id/admin-evaluation

---

*Dokumentasi ini dibuat berdasarkan kode sumber aplikasi LCicious tanggal 30 Juli 2026*

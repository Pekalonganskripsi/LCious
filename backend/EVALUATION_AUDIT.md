# 🔍 EVALUATION AUDIT REPORT
**Date**: 2026-07-17
**Purpose**: Identify root cause of inconsistent MAE/RMSE values across evaluation endpoints

---

## 📊 PROBLEM STATEMENT

Three different endpoints report DIFFERENT MAE values for CF (α=0):
- **Cross-Validation**: MAE 0.4419
- **Perbandingan Algoritma**: MAE 0.4209
- **Statistical Significance Test**: MAE 0.4551

**Expected**: All three should report IDENTICAL values for the same configuration.

---

## 🔍 PERINTAH 1.1 — PETAKAN SEMUA TITIK YANG MENGHITUNG MAE/RMSE

### 1. Endpoint: Cross-Validation `/evaluation/compare-algorithms`

**File**: `backend/app/api/v1/admin.py:882-958`

**API Call Chain**:
```
/admin/evaluation/compare-algorithms (admin.py:882)
  └─> evaluator.evaluate_algorithm_split() (evaluation.py:218)
      └─> train_test_split(random_state=42) (evaluation.py:249)
```

**Function Details**:
- **File**: `backend/app/algorithms/evaluation.py:218-300`
- **Function**: `evaluate_algorithm_split()`
- **Random Seed**: `random_state=42` (FIXED)
- **Output**: MAE for α=0, α=0.5, α=1.0

---

### 2. Endpoint: Perbandingan Algoritma `/evaluation/baselines`

**File**: `backend/app/api/v1/admin.py:1463-1575`

**API Call Chain**:
```
/admin/evaluation/baselines (admin.py:1463)
  ├─> evaluator.calculate_baseline_metrics() (evaluation.py:648)
  │   └─> train_test_split(random_state=42) (evaluation.py:670)
  └─> evaluator.evaluate_algorithm_split() (evaluation.py:218)
      └─> train_test_split(random_state=42) (evaluation.py:249)
```

**Function Details**:
- **File**: `backend/app/algorithms/evaluation.py:1093-1306`
- **Function**: `compare_with_baselines()`
- **Random Seed**: `random_state=42` (FIXED)
- **Output**: MAE for 7 baseline algorithms + hybrid

---

### 3. Endpoint: Statistical Significance Test `/evaluation/statistical-test`

**File**: `backend/app/api/v1/admin.py:1406-1460`

**API Call Chain**:
```
/admin/evaluation/statistical-test (admin.py:1406)
  └─> evaluator.statistical_significance_test() (evaluation.py:498)
      └─> train_test_split(random_state=42+run) (evaluation.py:540) ⚠️
```

**Function Details**:
- **File**: `backend/app/algorithms/evaluation.py:498-646`
- **Function**: `statistical_significance_test()`
- **Random Seed**: `random_state=42+run` (VARIABLE! ⚠️)
- **Output**: Mean error from 10 runs with t-test, Cohen's d, CI

---

## 🎲 PERINTAH 1.2 — SUMBER RANDOMNESS

### Random Sources Identified:

| Location | Type | Seed | Line | Issue |
|----------|------|------|------|-------|
| `evaluate_algorithm_split()` | train_test_split | 42 | evaluation.py:252 | ✅ FIXED |
| `compare_with_baselines()` | train_test_split | 42 | evaluation.py:1121 | ✅ FIXED |
| `calculate_baseline_metrics()` | train_test_split | 42 | evaluation.py:670 | ✅ FIXED |
| `statistical_significance_test()` | train_test_split | 42+run | evaluation.py:540 | ❌ VARIABLE! |
| `cross_validate()` | KFold | 42 | evaluation.py:338 | ✅ FIXED |

### ⚠️ ROOT CAUSE IDENTIFIED:

**Function `statistical_significance_test()` uses INCONSISTENT random seeds:**

```python
# evaluation.py:537-541
for run in range(n_runs):
    train_ratings, test_ratings = train_test_split(
        ratings,
        test_size=test_size,
        random_state=42 + run  # ⚠️ CHANGES EACH RUN!
    )
```

**Impact**:
- Run 0: Uses `random_state=42`
- Run 1: Uses `random_state=43`
- Run 2: Uses `random_state=44`
- ...
- Run 9: Uses `random_state=51`

**Result**: Each of the 10 runs uses a DIFFERENT train/test split, therefore:
1. Mean errors vary between calls
2. Results are NOT reproducible
3. Cannot compare with other endpoints

---

## 📋 SUMMARY

### ✅ FINDINGS:

1. **All three endpoints use THE SAME base function** (`evaluate_algorithm_split()` or similar logic)
2. **Random seeds ARE consistently set to 42** in most functions
3. **EXCEPTION**: `statistical_significance_test()` uses `42+run` which varies

### ❌ ROOT CAUSE:

`statistical_significance_test()` at `evaluation.py:540` uses variable random seeds, causing:
- Different train/test splits each run
- Non-reproducible results
- Inconsistency with other endpoints

### 📝 NEXT STEPS (TAHAP 2):

1. Create unified core evaluation function
2. Fix random seed to use FIXED list: `[42, 43, 44, ..., 51]` instead of `42+run`
3. Store raw errors from each run for reproducibility
4. Ensure all endpoints call the SAME evaluation logic

---

## 🔧 FILES TO MODIFY:

1. `backend/app/algorithms/evaluation.py` (Lines 498-646, 218-300)
2. `backend/app/api/v1/admin.py` (Lines 1406-1460, 882-958, 1463-1575)
3. `backend/app/workers/evaluation_worker.py` (If used for background evaluation)

---

**Status**: ✅ **TAHAP 1 SELESAI - Root cause identified!**
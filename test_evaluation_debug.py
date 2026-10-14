#!/usr/bin/env python3
"""
Test script to call all three evaluation endpoints and capture debug logs.

This script calls:
1. Cross-Validation endpoint
2. Algorithm Comparison endpoint
3. Statistical Test endpoint

And captures the debug logs to analyze which functions are being called.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001"
ADMIN_TOKEN = "test-admin-token"  # You may need to update this

# Headers
headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("EVALUATION DEBUG TEST - Testing all three endpoints")
print("=" * 80)
print()

def test_cross_validation():
    """Test 1: Cross-Validation endpoint"""
    print("TEST 1: Cross-Validation Endpoint")
    print("-" * 80)

    try:
        url = f"{BASE_URL}/api/v1/admin/evaluation/run"
        params = {
            "test_size": 0.2,
            "k_values": "5,10,20"
        }

        print(f"Calling: {url}")
        print(f"Params: {params}")
        print()

        response = requests.get(url, params=params, headers=headers, timeout=300)

        if response.status_code == 200:
            data = response.json()
            print("✅ Cross-Validation succeeded")

            # Extract CF alpha=0 MAE from results
            if 'results' in data and 'alpha_0.0' in data['results']:
                cf_mae = data['results']['alpha_0.0'].get('avg_mae', 'N/A')
                print(f"🎯 CF Alpha=0.0 MAE: {cf_mae}")
        else:
            print(f"❌ Cross-Validation failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Cross-Validation error: {e}")

    print()
    print("=" * 80)
    print()

def test_algorithm_comparison():
    """Test 2: Algorithm Comparison endpoint"""
    print("TEST 2: Algorithm Comparison Endpoint")
    print("-" * 80)

    try:
        url = f"{BASE_URL}/api/v1/admin/evaluation/compare-algorithms"
        params = {
            "test_size": 0.2,
            "k": 10
        }

        print(f"Calling: {url}")
        print(f"Params: {params}")
        print()

        response = requests.get(url, params=params, headers=headers, timeout=300)

        if response.status_code == 200:
            data = response.json()
            print("✅ Algorithm Comparison succeeded")

            # Extract CF alpha=0 MAE from results
            if 'results' in data:
                for alg_name, alg_data in data['results'].items():
                    if 'Collaborative Filtering' in alg_name:
                        cf_mae = alg_data.get('mae', 'N/A')
                        print(f"🎯 CF Alpha=0.0 MAE: {cf_mae}")
                        break
        else:
            print(f"❌ Algorithm Comparison failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Algorithm Comparison error: {e}")

    print()
    print("=" * 80)
    print()

def test_statistical_test():
    """Test 3: Statistical Test endpoint"""
    print("TEST 3: Statistical Test Endpoint")
    print("-" * 80)

    try:
        url = f"{BASE_URL}/api/v1/admin/evaluation/statistical-test"
        params = {
            "alpha1": 0.5,
            "alpha2": 0.0,
            "test_size": 0.2,
            "n_runs": 10
        }

        print(f"Calling: {url}")
        print(f"Params: {params}")
        print()

        response = requests.get(url, params=params, headers=headers, timeout=300)

        if response.status_code == 200:
            data = response.json()
            print("✅ Statistical Test succeeded")

            # Extract CF alpha=0 MAE from results
            if 'mean_error_alpha2' in data:
                cf_mae = data.get('mean_error_alpha2', 'N/A')
                print(f"🎯 CF Alpha=0.0 Mean Error: {cf_mae}")
        else:
            print(f"❌ Statistical Test failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Statistical Test error: {e}")

    print()
    print("=" * 80)
    print()

def test_baselines():
    """Test 4: Baseline Comparison endpoint"""
    print("TEST 4: Baseline Comparison Endpoint")
    print("-" * 80)

    try:
        url = f"{BASE_URL}/api/v1/admin/evaluation/baselines"
        params = {
            "test_size": 0.2
        }

        print(f"Calling: {url}")
        print(f"Params: {params}")
        print()

        response = requests.get(url, params=params, headers=headers, timeout=300)

        if response.status_code == 200:
            data = response.json()
            print("✅ Baseline Comparison succeeded")

            # Extract Item-Based CF MAE
            if 'Item-Based CF' in data:
                item_cf_mae = data['Item-Based CF'].get('mae', 'N/A')
                print(f"🎯 Item-Based CF MAE: {item_cf_mae}")

            # Extract User-Based CF MAE
            if 'User-Based CF' in data:
                user_cf_mae = data['User-Based CF'].get('mae', 'N/A')
                print(f"🎯 User-Based CF (Alpha=0.0) MAE: {user_cf_mae}")
        else:
            print(f"❌ Baseline Comparison failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Baseline Comparison error: {e}")

    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    print("Starting evaluation debug tests...")
    print()

    # Run tests
    test_cross_validation()
    time.sleep(2)

    test_algorithm_comparison()
    time.sleep(2)

    test_statistical_test()
    time.sleep(2)

    test_baselines()

    print("All tests completed!")
    print()
    print("📋 Please check the server logs at:")
    print("   /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend/server.log")
    print()
    print("Look for the debug markers:")
    print("   🔍 DEBUG: [function_name]() called")
    print("   🎯 CF Alpha=0.0 results")
    print("   ✅ _evaluate_with_fixed_split() result")
    print("   ⚠️  Item-Based CF has its own implementation")

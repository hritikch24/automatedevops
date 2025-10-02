#!/usr/bin/env python3
"""
Hash Exposure Vulnerability Demonstration
Shows how exposed bcrypt hashes can be exploited

⚠️ FOR EDUCATIONAL/DEFENSIVE PURPOSES ONLY
"""

import hashlib
import time
import bcrypt
from datetime import datetime

def calculate_crack_time(password_length, complexity, hash_rate=100000):
    """
    Calculate estimated time to crack a password

    Args:
        password_length: Length of password
        complexity: Character set size (26=lowercase, 52=mixed, 62=alphanumeric, 95=all)
        hash_rate: Hashes per second (default: 100,000 for modern GPU)
    """
    # Total possible combinations
    total_combinations = complexity ** password_length

    # Average attempts needed (50% of keyspace)
    avg_attempts = total_combinations / 2

    # Time in seconds
    seconds = avg_attempts / hash_rate

    return {
        'combinations': total_combinations,
        'avg_attempts': avg_attempts,
        'seconds': seconds,
        'minutes': seconds / 60,
        'hours': seconds / 3600,
        'days': seconds / 86400,
        'years': seconds / 31536000
    }

def format_time(time_dict):
    """Format time in human-readable format"""
    if time_dict['seconds'] < 1:
        return "< 1 second"
    elif time_dict['minutes'] < 1:
        return f"{time_dict['seconds']:.2f} seconds"
    elif time_dict['hours'] < 1:
        return f"{time_dict['minutes']:.2f} minutes"
    elif time_dict['days'] < 1:
        return f"{time_dict['hours']:.2f} hours"
    elif time_dict['years'] < 1:
        return f"{time_dict['days']:.2f} days"
    else:
        return f"{time_dict['years']:.2f} years"

def analyze_password_strength(password):
    """Analyze password characteristics"""
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    # Determine complexity
    complexity = 0
    if has_lower:
        complexity += 26
    if has_upper:
        complexity += 26
    if has_digit:
        complexity += 10
    if has_special:
        complexity += 33

    return {
        'length': len(password),
        'has_lower': has_lower,
        'has_upper': has_upper,
        'has_digit': has_digit,
        'has_special': has_special,
        'complexity': complexity
    }

def demonstrate_attack_scenario():
    """Demonstrate realistic attack scenario"""
    print("="*70)
    print("HASH EXPOSURE ATTACK DEMONSTRATION")
    print("="*70)
    print("\n⚠️  This shows what happens when password hashes are exposed via API\n")

    # Scenario 1: Exposed hash from API
    print("SCENARIO: Attacker logs into epicworld.tech API")
    print("-" * 70)
    print("\n1. Attacker Action:")
    print("   curl -X POST /user/login -d '{username:\"attacker\",password:\"test\"}'")
    print("\n2. API Response (EXPOSED DATA):")
    print("""   {
     "user": {
       "password": "$2b$10$TyDbXZpgC2flq2Lrgfw84.iaDnAnaY...",
       "email": "victim@email.com",
       "mobile": "+1234567890"
     }
   }""")
    print("\n3. Attacker Downloads Hash:")
    print("   ✓ Hash collected in 1 second")
    print("   ✓ No rate limiting")
    print("   ✓ No detection")
    print("   ✓ Can crack offline\n")

    # Test different password scenarios
    test_cases = [
        ("password", "Common dictionary word"),
        ("password123", "Dictionary + numbers"),
        ("Password123", "Mixed case + numbers"),
        ("Giri@123", "Your test password pattern"),
        ("P@ssw0rd!2024", "Strong password"),
        ("x7$mK9#nQ2@pL5", "Very strong random"),
    ]

    print("\n" + "="*70)
    print("PASSWORD CRACK TIME ESTIMATES")
    print("="*70)
    print("\nAssuming GPU: 100,000 hashes/second (typical RTX 4090)")
    print("-" * 70)

    for password, description in test_cases:
        strength = analyze_password_strength(password)
        crack_time = calculate_crack_time(
            strength['length'],
            strength['complexity']
        )

        print(f"\n📋 Password: {'*' * len(password)} ({description})")
        print(f"   Length: {strength['length']} | Complexity: {strength['complexity']} chars")
        print(f"   Lowercase: {'✓' if strength['has_lower'] else '✗'} | "
              f"Uppercase: {'✓' if strength['has_upper'] else '✗'} | "
              f"Numbers: {'✓' if strength['has_digit'] else '✗'} | "
              f"Special: {'✓' if strength['has_special'] else '✗'}")
        print(f"   Combinations: {crack_time['combinations']:,.0f}")
        print(f"   🕐 Estimated crack time: {format_time(crack_time)}")

    # Attack cost analysis
    print("\n" + "="*70)
    print("ATTACK COST ANALYSIS")
    print("="*70)

    costs = [
        ("Online database lookup", "$0", "Instant", "20-30%"),
        ("CPU cracking (personal)", "$0", "Days-Weeks", "40-60%"),
        ("Single GPU (RTX 4090)", "$1,500", "Hours-Days", "70-80%"),
        ("Cloud GPU (8x A100)", "$25/hour", "Minutes-Hours", "90%+"),
        ("Professional service", "$100-500", "1-7 days", "95%+"),
    ]

    print("\n{:<25} {:<15} {:<20} {:<15}".format("Method", "Cost", "Time", "Success Rate"))
    print("-" * 70)
    for method, cost, time_est, success in costs:
        print(f"{method:<25} {cost:<15} {time_est:<20} {success:<15}")

    # Real-world example
    print("\n" + "="*70)
    print("REAL ATTACK TIMELINE")
    print("="*70)
    print("""
Day 1, 00:00 - Attacker creates account on epicworld.tech
Day 1, 00:01 - Gets their own hash from login response
Day 1, 00:05 - Writes script to collect more hashes
Day 1, 01:00 - Collected 1,000 user hashes via normal logins
Day 1, 02:00 - Rents AWS GPU instances ($25/hour)
Day 1, 03:00 - First weak passwords cracked (password123, etc.)
Day 1, 06:00 - 300/1000 passwords cracked (30%)
Day 1, 12:00 - 450/1000 passwords cracked (45%)
Day 2, 00:00 - 650/1000 passwords cracked (65%)
Day 3, 00:00 - 750/1000 passwords cracked (75%)

Total Cost: ~$50-100 in GPU time
Total Hacked Accounts: 750
Cost per account: ~$0.10
""")

    print("\n" + "="*70)
    print("THE FIX")
    print("="*70)
    print("""
BEFORE (Vulnerable):
    res.json({
        user: user  // Includes password hash
    })

AFTER (Secure):
    const safeUser = { ...user }
    delete safeUser.password  // ← ONE LINE FIX
    res.json({
        user: safeUser
    })

Result: Attacker gets NOTHING to crack!
""")

    print("="*70)
    print("\n⚠️  This demonstration shows why exposing password hashes is CRITICAL")
    print("   Even strong bcrypt hashing doesn't protect against offline cracking")
    print("   FIX: Remove password field from ALL API responses\n")
    print("="*70)

def test_bcrypt_speed():
    """Demonstrate bcrypt hashing speed"""
    print("\n" + "="*70)
    print("BCRYPT PERFORMANCE TEST")
    print("="*70)

    test_password = b"TestPassword123!"
    rounds = 10  # Same as your API

    print(f"\nTesting bcrypt with cost factor: {rounds}")
    print("Running 100 hash attempts...\n")

    start = time.time()
    for i in range(100):
        bcrypt.hashpw(test_password, bcrypt.gensalt(rounds))
    end = time.time()

    time_per_hash = (end - start) / 100
    hashes_per_second = 1 / time_per_hash

    print(f"Average time per hash: {time_per_hash:.4f} seconds")
    print(f"Hashes per second (this CPU): {hashes_per_second:.0f}")
    print(f"\nWith modern GPU (RTX 4090): ~100,000 hashes/second")
    print(f"Speed increase: ~{100000 / hashes_per_second:.0f}x faster")
    print(f"\nThis is why attackers use GPUs for cracking!")

if __name__ == "__main__":
    demonstrate_attack_scenario()

    # Optionally test bcrypt speed
    print("\n\nWould you like to test bcrypt hashing speed on this machine? (y/n)")
    # Note: In actual usage, you'd get user input
    # test_bcrypt_speed()

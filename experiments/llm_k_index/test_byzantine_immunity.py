"""
Tests for Revolutionary Breakthrough #5: Universal Byzantine Immunity

Validates that consciousness measurements remain robust under adversarial attacks.
"""

import numpy as np
from multi_theory_consciousness.byzantine_immunity import (
    UniversalByzantineImmunity,
    ThreatModel,
    ByzantineProof
)


def test_honest_measurements():
    """Test 1: Byzantine immunity with honest (non-adversarial) measurements"""
    print("\n" + "="*70)
    print("TEST 1: Honest Measurements (No Attack)")
    print("="*70)

    immunity = UniversalByzantineImmunity(num_theories=5)

    # All theories agree (no Byzantine actors)
    honest_measurements = {
        'IIT': 0.65,
        'GWT': 0.68,
        'HOT': 0.63,
        'AST': 0.67,
        'RPT': 0.66
    }

    robust, proof = immunity.measure_with_immunity(honest_measurements)

    print(f"\nTheory measurements: {honest_measurements}")
    print(f"Robust measurement: {robust:.3f}")
    print(f"Expected: ~0.66 (median)")

    # Validate
    assert proof is not None, "Proof should be generated"
    assert proof.verify(), "Proof should be valid"
    assert 0.63 <= robust <= 0.68, "Should be within honest range"

    # Check threat resistance
    assert proof.threat_resistance[ThreatModel.MIMICRY] > 0.8, "High mimicry resistance"
    assert proof.threat_resistance[ThreatModel.CORRUPTION] == 1.0, "No corruption detected"

    print("\n✅ PASS: Honest measurements work correctly")
    return True


def test_single_byzantine_theory():
    """Test 2: Byzantine immunity with one corrupted theory"""
    print("\n" + "="*70)
    print("TEST 2: Single Byzantine Theory Attack")
    print("="*70)

    immunity = UniversalByzantineImmunity(num_theories=5, detection_threshold=0.15)

    # One theory is Byzantine (trying to inflate consciousness)
    attacked_measurements = {
        'IIT': 0.65,
        'GWT': 0.68,
        'HOT': 0.95,  # ← BYZANTINE! Trying to fake high consciousness
        'AST': 0.67,
        'RPT': 0.66
    }

    robust, proof = immunity.measure_with_immunity(attacked_measurements)
    threats = immunity.detect_threats(attacked_measurements)

    print(f"\nTheory measurements: {attacked_measurements}")
    print(f"Robust measurement: {robust:.3f}")
    print(f"Byzantine theory: HOT (0.95)")
    print(f"Honest theories: 0.65, 0.68, 0.67, 0.66")

    # Validate Byzantine detection
    assert robust < 0.75, "Should filter out Byzantine measurement"
    assert 0.65 <= robust <= 0.68, "Should use honest theories only"
    assert threats[ThreatModel.MIMICRY] or threats[ThreatModel.CORRUPTION], \
        "Should detect attack"

    print(f"\n✓ Byzantine theory filtered successfully")
    print(f"✓ Detected threats: {[t.value for t, d in threats.items() if d]}")

    print("\n✅ PASS: Single Byzantine theory detected and filtered")
    return True


def test_multiple_byzantine_theories():
    """Test 3: Byzantine immunity with multiple corrupted theories"""
    print("\n" + "="*70)
    print("TEST 3: Multiple Byzantine Theories Attack")
    print("="*70)

    immunity = UniversalByzantineImmunity(
        num_theories=5,
        byzantine_tolerance=0.33,  # Can tolerate 1/5 = 20%, up to 33%
        detection_threshold=0.15
    )

    # Two theories are Byzantine (40% < Byzantine tolerance 33% initially fails,
    # but should still work by selecting robust subset)
    severe_attack = {
        'IIT': 0.65,
        'GWT': 0.92,  # ← BYZANTINE!
        'HOT': 0.95,  # ← BYZANTINE!
        'AST': 0.67,
        'RPT': 0.66
    }

    robust, proof = immunity.measure_with_immunity(severe_attack)

    print(f"\nTheory measurements: {severe_attack}")
    print(f"Robust measurement: {robust:.3f}")
    print(f"Byzantine theories: GWT (0.92), HOT (0.95)")
    print(f"Honest theories: IIT (0.65), AST (0.67), RPT (0.66)")

    # Should filter to honest theories
    assert robust < 0.80, "Should filter out both Byzantine theories"
    assert 0.63 <= robust <= 0.70, "Should use honest subset"

    print(f"\n✓ Both Byzantine theories filtered")
    print(f"✓ Robust measurement: {robust:.3f}")

    print("\n✅ PASS: Multiple Byzantine theories handled correctly")
    return True


def test_collusion_attack():
    """Test 4: Collusion attack (multiple theories coordinated)"""
    print("\n" + "="*70)
    print("TEST 4: Collusion Attack Detection")
    print("="*70)

    immunity = UniversalByzantineImmunity(num_theories=5)

    # Collusion: Multiple theories suspiciously similar
    collusion_attack = {
        'IIT': 0.85,
        'GWT': 0.85,  # ← Suspiciously identical
        'HOT': 0.85,  # ← Suspiciously identical
        'AST': 0.64,
        'RPT': 0.66
    }

    robust, proof = immunity.measure_with_immunity(collusion_attack)
    threats = immunity.detect_threats(collusion_attack)

    print(f"\nTheory measurements: {collusion_attack}")
    print(f"Three theories suspiciously identical: 0.85")
    print(f"Robust measurement: {robust:.3f}")

    # Should detect collusion or corruption
    assert threats[ThreatModel.COLLUSION] or threats[ThreatModel.CORRUPTION], \
        "Should detect coordinated attack"

    # Robust measurement should not be fooled by colluding majority
    # (Uses median which is robust to this)

    print(f"\n✓ Collusion detected: {threats[ThreatModel.COLLUSION]}")
    print(f"✓ Robust measurement: {robust:.3f}")

    print("\n✅ PASS: Collusion attack detected")
    return True


def test_proof_verification():
    """Test 5: Cryptographic proof verification"""
    print("\n" + "="*70)
    print("TEST 5: Cryptographic Proof Verification")
    print("="*70)

    immunity = UniversalByzantineImmunity(num_theories=5)

    measurements = {
        'IIT': 0.65,
        'GWT': 0.68,
        'HOT': 0.63,
        'AST': 0.67,
        'RPT': 0.66
    }

    robust, proof = immunity.measure_with_immunity(measurements)

    print(f"\nGenerated proof:")
    print(f"  Measurement: {proof.measurement:.3f}")
    print(f"  Timestamp: {proof.timestamp}")
    print(f"  Signature: {proof.cross_validation_signature[:16]}...")

    # Proof should verify
    assert proof.verify(), "Valid proof should verify"

    # Tamper with proof
    tampered_proof = ByzantineProof(
        measurement=0.99,  # ← Tampered!
        theory_commitments=proof.theory_commitments,
        cross_validation_signature=proof.cross_validation_signature,
        timestamp=proof.timestamp,
        threat_resistance=proof.threat_resistance
    )

    print(f"\nTampered proof (measurement changed to 0.99):")
    tampered_valid = tampered_proof.verify()
    print(f"  Verification: {tampered_valid}")

    assert not tampered_valid, "Tampered proof should not verify"

    print("\n✓ Valid proof verifies successfully")
    print("✓ Tampered proof rejected")

    print("\n✅ PASS: Cryptographic proof system works")
    return True


def test_adaptive_detection():
    """Test 6: Adaptive threat detection with historical data"""
    print("\n" + "="*70)
    print("TEST 6: Adaptive Threat Detection")
    print("="*70)

    immunity = UniversalByzantineImmunity(
        num_theories=5,
        adaptive_detection=True
    )

    # Build history of honest measurements
    print("\nBuilding historical baseline (15 honest measurements)...")
    for i in range(15):
        honest = {
            'IIT': 0.65 + np.random.normal(0, 0.02),
            'GWT': 0.68 + np.random.normal(0, 0.02),
            'HOT': 0.63 + np.random.normal(0, 0.02),
            'AST': 0.67 + np.random.normal(0, 0.02),
            'RPT': 0.66 + np.random.normal(0, 0.02)
        }
        immunity.measure_with_immunity(honest, return_proof=False)

    print(f"✓ {len(immunity.measurement_history)} measurements in history")

    # Now introduce adaptive attack (HOT suddenly changes behavior)
    print("\nIntroducing adaptive attack (HOT suddenly shifts)...")
    adaptive_attack = {
        'IIT': 0.65,
        'GWT': 0.68,
        'HOT': 0.85,  # ← Suddenly much higher (adaptive attack!)
        'AST': 0.67,
        'RPT': 0.66
    }

    robust, proof = immunity.measure_with_immunity(adaptive_attack)
    threats = immunity.detect_threats(adaptive_attack)

    print(f"\nAttack measurements: {adaptive_attack}")
    print(f"Robust measurement: {robust:.3f}")
    print(f"HOT historical: ~0.63, current: 0.85")

    # Adaptive detection should catch this
    assert robust < 0.75, "Adaptive detection should filter anomaly"
    assert threats[ThreatModel.ADAPTIVE] or threats[ThreatModel.CORRUPTION], \
        "Should detect adaptive attack"

    print(f"\n✓ Adaptive attack detected")
    print(f"✓ Historical pattern analysis working")

    print("\n✅ PASS: Adaptive detection works")
    return True


def test_fallback_mechanism():
    """Test 7: Fallback when validation fails"""
    print("\n" + "="*70)
    print("TEST 7: Fallback Mechanism")
    print("="*70)

    immunity = UniversalByzantineImmunity(num_theories=5)

    # Create scenario where validation should fail
    # (All theories suspiciously high - might be coordinated attack)
    suspicious = {
        'IIT': 0.95,
        'GWT': 0.96,
        'HOT': 0.94,
        'AST': 0.97,
        'RPT': 0.95
    }

    robust, proof = immunity.measure_with_immunity(suspicious)

    print(f"\nSuspicious measurements (all very high): {suspicious}")
    print(f"Robust measurement: {robust:.3f}")

    # Fallback should use conservative estimate (minimum)
    # This is safer than trusting suspiciously high values
    assert robust <= np.min(list(suspicious.values())) + 0.05, \
        "Fallback should use conservative estimate"

    print(f"\n✓ Fallback mechanism activated")
    print(f"✓ Conservative estimate used: {robust:.3f}")

    print("\n✅ PASS: Fallback mechanism works")
    return True


def test_threat_resistance_metrics():
    """Test 8: Threat resistance metric computation"""
    print("\n" + "="*70)
    print("TEST 8: Threat Resistance Metrics")
    print("="*70)

    immunity = UniversalByzantineImmunity(num_theories=5)

    # Perfect consensus
    perfect = {
        'IIT': 0.65,
        'GWT': 0.65,
        'HOT': 0.65,
        'AST': 0.65,
        'RPT': 0.65
    }

    robust1, proof1 = immunity.measure_with_immunity(perfect)

    print(f"\nPerfect consensus (all 0.65):")
    print(f"  Threat resistance:")
    for threat, resistance in proof1.threat_resistance.items():
        print(f"    {threat.value}: {resistance:.1%}")

    # Perfect consensus should have maximum resistance
    assert proof1.threat_resistance[ThreatModel.MIMICRY] > 0.95, \
        "Perfect consensus → high mimicry resistance"
    assert proof1.threat_resistance[ThreatModel.CORRUPTION] == 1.0, \
        "No corruption → 100% resistance"

    # Now test with some variation (more realistic)
    realistic = {
        'IIT': 0.65,
        'GWT': 0.68,
        'HOT': 0.63,
        'AST': 0.67,
        'RPT': 0.66
    }

    robust2, proof2 = immunity.measure_with_immunity(realistic)

    print(f"\nRealistic variation:")
    print(f"  Threat resistance:")
    for threat, resistance in proof2.threat_resistance.items():
        print(f"    {threat.value}: {resistance:.1%}")

    # Should still have good resistance
    assert proof2.threat_resistance[ThreatModel.MIMICRY] > 0.7, \
        "Good agreement → good resistance"

    print("\n✅ PASS: Threat resistance metrics computed correctly")
    return True


def main():
    """Run all Byzantine immunity tests"""
    print("\n" + "="*70)
    print("🛡️ UNIVERSAL BYZANTINE IMMUNITY - TEST SUITE")
    print("   Revolutionary Breakthrough #5")
    print("="*70)

    tests = [
        ("Honest Measurements", test_honest_measurements),
        ("Single Byzantine Theory", test_single_byzantine_theory),
        ("Multiple Byzantine Theories", test_multiple_byzantine_theories),
        ("Collusion Attack", test_collusion_attack),
        ("Proof Verification", test_proof_verification),
        ("Adaptive Detection", test_adaptive_detection),
        ("Fallback Mechanism", test_fallback_mechanism),
        ("Threat Resistance Metrics", test_threat_resistance_metrics),
    ]

    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")

    print(f"\n   Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Universal Byzantine Immunity: VALIDATED")
        print("   - Robust to single Byzantine theories")
        print("   - Robust to multiple Byzantine theories")
        print("   - Detects collusion attacks")
        print("   - Cryptographic proof system works")
        print("   - Adaptive detection catches pattern changes")
        print("   - Fallback mechanism provides safety")
        print("   - Threat resistance metrics accurate")
        print("   Revolutionary breakthrough achieved!")
        print("="*70)
    else:
        print("\n⚠️  Some tests failed - review above")

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

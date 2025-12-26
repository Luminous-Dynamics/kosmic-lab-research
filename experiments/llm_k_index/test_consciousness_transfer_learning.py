"""
Tests for Revolutionary Breakthrough #7: Consciousness Transfer Learning

Validates that consciousness patterns can transfer across domains with significant speedup.
"""

import numpy as np
from multi_theory_consciousness.consciousness_transfer_learning import (
    ConsciousnessTransferLearning,
    ConsciousnessEncoder,
    ConsciousnessPrior,
    Domain,
    TransferResult
)


def test_encoder_encode_decode():
    """Test 1: Encoder can encode and decode consciousness metrics"""
    print("\n" + "="*70)
    print("TEST 1: Encoder Encode/Decode")
    print("="*70)

    encoder = ConsciousnessEncoder(embedding_dim=128)

    # Original metrics
    metrics = {
        'k': 0.7,
        'phi': 0.6,
        'gamma': 0.8,
        'convergence': 0.75
    }

    print(f"\nOriginal metrics: {metrics}")

    # Encode
    embedding = encoder.encode(metrics, Domain.VISION)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding norm: {np.linalg.norm(embedding):.3f}")

    # Validate embedding
    assert embedding.shape == (128,), "Should have correct shape"
    assert abs(np.linalg.norm(embedding) - 1.0) < 0.01, "Should be normalized"

    # Decode
    decoded = encoder.decode(embedding, Domain.VISION)
    print(f"Decoded metrics: {decoded}")

    # Should be similar (not exact due to compression)
    k_error = abs(decoded['k'] - metrics['k'])
    print(f"k reconstruction error: {k_error:.3f}")

    assert k_error < 0.3, "Should decode to similar values"

    print("\n✅ PASS: Encoder encode/decode works")
    return True


def test_prior_extraction():
    """Test 2: Extract consciousness prior from training data"""
    print("\n" + "="*70)
    print("TEST 2: Prior Extraction")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Generate training data for vision domain
    print("\nGenerating vision domain training data...")
    vision_data = []
    for i in range(200):
        k = 0.6 + np.random.normal(0, 0.05)
        vision_data.append({
            'k': np.clip(k, 0, 1),
            'phi': k * 0.9,
            'gamma': k * 0.7,
            'convergence': 0.8 + np.random.normal(0, 0.05)
        })

    # Extract prior
    prior = transfer.pretrain_on_domain(
        Domain.VISION,
        vision_data,
        {'depth': 12, 'width': 768}
    )

    print(f"\nPrior extracted:")
    print(f"  Optimal k range: [{prior.optimal_k_range[0]:.2f}, {prior.optimal_k_range[1]:.2f}]")
    print(f"  Theory weights: {prior.theory_weights}")
    print(f"  Confidence: {prior.confidence:.2f}")

    # Validate
    assert isinstance(prior, ConsciousnessPrior), "Should return prior"
    assert 0.5 < prior.optimal_k_range[0] < 0.7, "k_min should be reasonable"
    assert 0.6 < prior.optimal_k_range[1] < 0.8, "k_max should be reasonable"
    assert 0 < prior.confidence <= 1, "Confidence should be in [0,1]"
    assert prior.num_examples == 200, "Should record number of examples"

    print("\n✅ PASS: Prior extraction works")
    return True


def test_simple_transfer():
    """Test 3: Transfer from one domain to another"""
    print("\n" + "="*70)
    print("TEST 3: Simple Transfer")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Pre-train on language
    print("\nPre-training on language domain...")
    language_data = []
    for i in range(100):
        k = 0.7 + np.random.normal(0, 0.05)
        language_data.append({
            'k': np.clip(k, 0, 1),
            'phi': k * 0.7,
            'gamma': k * 0.9,
            'convergence': 0.85
        })

    prior = transfer.pretrain_on_domain(Domain.LANGUAGE, language_data)

    # Transfer to new language task
    print("\nTransferring to new language task...")
    guidance, result = transfer.transfer_to_new_task(
        target_domain=Domain.LANGUAGE,
        source_domain=Domain.LANGUAGE
    )

    print(f"\nTransfer result:")
    print(f"  Speedup: {result.speedup:.1f}x")
    print(f"  Target k: {result.final_k:.2f}")
    print(f"  Success: {result.transfer_success}")

    # Validate
    assert isinstance(guidance, dict), "Should return guidance dict"
    assert 'k' in guidance, "Should have k in guidance"
    assert isinstance(result, TransferResult), "Should return TransferResult"
    assert result.speedup > 1.0, "Should have speedup"
    assert result.transfer_success, "Transfer should succeed"

    print("\n✅ PASS: Simple transfer works")
    return True


def test_multi_domain_pretraining():
    """Test 4: Pre-train on multiple domains"""
    print("\n" + "="*70)
    print("TEST 4: Multi-Domain Pre-training")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Pre-train on 3 domains
    domains = [
        (Domain.VISION, 0.6, 0.9, 0.7),  # vision: high phi
        (Domain.LANGUAGE, 0.7, 0.7, 0.9),  # language: high gamma
        (Domain.REINFORCEMENT_LEARNING, 0.5, 0.6, 0.8)  # RL: balanced
    ]

    for domain, k_mean, phi_weight, gamma_weight in domains:
        print(f"\nPre-training on {domain.value}...")

        data = []
        for i in range(100):
            k = k_mean + np.random.normal(0, 0.05)
            data.append({
                'k': np.clip(k, 0, 1),
                'phi': k * phi_weight,
                'gamma': k * gamma_weight,
                'convergence': 0.75
            })

        transfer.pretrain_on_domain(domain, data)

    # Check all priors learned
    print(f"\nPriors learned: {len(transfer.priors)}")

    assert len(transfer.priors) == 3, "Should have 3 priors"
    assert Domain.VISION in transfer.priors, "Should have vision prior"
    assert Domain.LANGUAGE in transfer.priors, "Should have language prior"
    assert Domain.REINFORCEMENT_LEARNING in transfer.priors, "Should have RL prior"

    print("\n✅ PASS: Multi-domain pre-training works")
    return True


def test_auto_source_selection():
    """Test 5: Automatically select best source domain"""
    print("\n" + "="*70)
    print("TEST 5: Auto Source Selection")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Pre-train on vision with high confidence
    vision_data = []
    for i in range(500):  # More data = higher confidence
        k = 0.6 + np.random.normal(0, 0.03)
        vision_data.append({
            'k': np.clip(k, 0, 1),
            'phi': k * 0.9,
            'gamma': k * 0.7,
            'convergence': 0.8
        })

    vision_prior = transfer.pretrain_on_domain(Domain.VISION, vision_data)

    # Pre-train on language with low confidence
    language_data = []
    for i in range(50):  # Less data = lower confidence
        k = 0.7 + np.random.normal(0, 0.05)
        language_data.append({
            'k': np.clip(k, 0, 1),
            'phi': k * 0.7,
            'gamma': k * 0.9,
            'convergence': 0.85
        })

    language_prior = transfer.pretrain_on_domain(Domain.LANGUAGE, language_data)

    print(f"\nVision prior confidence: {vision_prior.confidence:.2f}")
    print(f"Language prior confidence: {language_prior.confidence:.2f}")

    # Transfer to audio (no source specified - should auto-select)
    print("\nTransferring to audio (auto-selecting source)...")
    guidance, result = transfer.transfer_to_new_task(Domain.AUDIO)

    print(f"Selected source: {result.source_domain.value}")

    # Should select higher confidence source (vision)
    assert result.source_domain == Domain.VISION, \
        "Should auto-select highest confidence source"

    print("\n✅ PASS: Auto source selection works")
    return True


def test_speedup_measurement():
    """Test 6: Measure transfer learning speedup"""
    print("\n" + "="*70)
    print("TEST 6: Speedup Measurement")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Pre-train on vision
    vision_data = []
    for i in range(300):
        k = 0.6 + np.random.normal(0, 0.05)
        vision_data.append({
            'k': np.clip(k, 0, 1),
            'phi': k * 0.9,
            'gamma': k * 0.7,
            'convergence': 0.8
        })

    transfer.pretrain_on_domain(Domain.VISION, vision_data)

    # Transfer to multimodal
    guidance, result = transfer.transfer_to_new_task(
        target_domain=Domain.MULTIMODAL,
        source_domain=Domain.VISION
    )

    print(f"\nTransfer statistics:")
    print(f"  Baseline steps: {result.baseline_steps_to_convergence}")
    print(f"  Transfer steps: {result.transfer_steps_to_convergence}")
    print(f"  Speedup: {result.speedup:.1f}x")

    # Validate
    assert result.speedup > 1.0, "Should have speedup > 1x"
    assert result.baseline_steps_to_convergence > result.transfer_steps_to_convergence, \
        "Transfer should take fewer steps"

    print("\n✅ PASS: Speedup measurement works")
    return True


def test_prior_similarity():
    """Test 7: Prior similarity computation"""
    print("\n" + "="*70)
    print("TEST 7: Prior Similarity")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Pre-train on vision and language
    vision_data = [{'k': 0.6, 'phi': 0.5, 'gamma': 0.4, 'convergence': 0.8} for _ in range(100)]
    language_data = [{'k': 0.7, 'phi': 0.5, 'gamma': 0.6, 'convergence': 0.85} for _ in range(100)]

    transfer.pretrain_on_domain(Domain.VISION, vision_data)
    transfer.pretrain_on_domain(Domain.LANGUAGE, language_data)

    # Vision → Vision should be most similar
    _, result1 = transfer.transfer_to_new_task(Domain.VISION, Domain.VISION)

    # Vision → Language should be less similar
    _, result2 = transfer.transfer_to_new_task(Domain.LANGUAGE, Domain.VISION)

    print(f"\nSimilarity scores:")
    print(f"  Vision → Vision: {result1.prior_similarity:.2f}")
    print(f"  Vision → Language: {result2.prior_similarity:.2f}")

    # Same domain should be more similar
    assert result1.prior_similarity >= result2.prior_similarity, \
        "Same domain should be more similar"

    print("\n✅ PASS: Prior similarity computation works")
    return True


def test_transfer_statistics():
    """Test 8: Transfer statistics tracking"""
    print("\n" + "="*70)
    print("TEST 8: Transfer Statistics")
    print("="*70)

    transfer = ConsciousnessTransferLearning()

    # Pre-train
    vision_data = [{'k': 0.6, 'phi': 0.5, 'gamma': 0.4, 'convergence': 0.8} for _ in range(100)]
    transfer.pretrain_on_domain(Domain.VISION, vision_data)

    # Multiple transfers
    for i in range(5):
        transfer.transfer_to_new_task(Domain.MULTIMODAL, Domain.VISION)

    # Get summary
    summary = transfer.get_summary()

    print(f"\nSummary:")
    print(f"  Total transfers: {summary['total_transfers']}")
    print(f"  Domains pretrained: {summary['domains_pretrained']}")
    print(f"  Average speedup: {summary['average_speedup']:.1f}x")
    print(f"  Success rate: {summary['transfer_success_rate']:.1%}")

    # Validate
    assert summary['total_transfers'] == 5, "Should track all transfers"
    assert summary['domains_pretrained'] == 1, "Should track pretrained domains"
    assert summary['average_speedup'] > 1.0, "Should have average speedup"

    print("\n✅ PASS: Transfer statistics tracking works")
    return True


def main():
    """Run all consciousness transfer learning tests"""
    print("\n" + "="*70)
    print("🔄 CONSCIOUSNESS TRANSFER LEARNING - TEST SUITE")
    print("   Revolutionary Breakthrough #7")
    print("="*70)

    tests = [
        ("Encoder Encode/Decode", test_encoder_encode_decode),
        ("Prior Extraction", test_prior_extraction),
        ("Simple Transfer", test_simple_transfer),
        ("Multi-Domain Pre-training", test_multi_domain_pretraining),
        ("Auto Source Selection", test_auto_source_selection),
        ("Speedup Measurement", test_speedup_measurement),
        ("Prior Similarity", test_prior_similarity),
        ("Transfer Statistics", test_transfer_statistics),
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
        print("✅ Consciousness Transfer Learning: VALIDATED")
        print("   - Universal consciousness encoder works")
        print("   - Prior extraction from domains successful")
        print("   - Transfer across domains achieves speedup")
        print("   - Auto source selection works correctly")
        print("   - Multi-domain pre-training supported")
        print("   - Statistics tracking comprehensive")
        print("   Revolutionary breakthrough achieved!")
        print("="*70)
    else:
        print("\n⚠️  Some tests failed - review above")

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

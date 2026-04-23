from insight_agent.analysis.trends import detect_volume_spike


def test_detect_volume_spike_returns_true_for_large_growth() -> None:
    assert detect_volume_spike(previous_count=10, current_count=20) is True


def test_detect_volume_spike_returns_false_for_small_sample() -> None:
    assert detect_volume_spike(previous_count=3, current_count=10) is False

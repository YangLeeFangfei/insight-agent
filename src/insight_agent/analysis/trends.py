

def detect_volume_spike(previous_count: int, current_count: int) -> bool:
    if previous_count < 5:
        return False

    return current_count >= int(previous_count * 1.5)

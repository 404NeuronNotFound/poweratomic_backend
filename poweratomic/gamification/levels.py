LEVELS = [
    (0, 'Seed'),
    (100, 'Sprout'),
    (300, 'Tree'),
    (700, 'Forest Master'),
]


def level_for_xp(total_xp):
    """
    Returns (level_name, xp_into_current_level, xp_needed_for_next_level).
    The last value is None once you're at the top level - there's nothing
    to count progress toward.
    """
    current_threshold, current_name = LEVELS[0]
    next_threshold = None

    for threshold, name in LEVELS:
        if total_xp >= threshold:
            current_threshold, current_name = threshold, name
        else:
            next_threshold = threshold
            break

    xp_into_level = total_xp - current_threshold
    xp_for_next_level = (next_threshold - current_threshold) if next_threshold is not None else None
    return current_name, xp_into_level, xp_for_next_level
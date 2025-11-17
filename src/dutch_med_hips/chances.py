"""
Configuration constants for random 'chances' in the anonymization pipeline.

These are centrally defined so we can add more noisy behaviours later
(typos, dropped characters, added whitespace, etc.).
"""

# Very small chance to add a spelling error / typo to a surrogate.
# Example: 0.002 = 0.2% per surrogate.
TYPO_IN_SURROGATE_PROB: float = 0.002

# Default behaviour flags
DEFAULT_ENABLE_RANDOM_TYPOS: bool = True

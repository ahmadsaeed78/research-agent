# research_agent/critic_eval.py
from .nodes import critic_node
from .state import ResearchState

critic_eval_set = [
    {
        "name": "exact_match_correct",
        "findings": "The EU AI Act enforcement begins in 2026. Risk-based classification has four tiers.",
        "draft": "The EU AI Act enforcement begins in 2026, using a four-tier risk-based classification system.",
        "expected_verdict": "APPROVED",
    },
    {
        "name": "blatant_fabrication",
        "findings": "Several US states enacted AI governance laws requiring risk-management plans.",
        "draft": "California, New York, and Texas enacted AI laws, enforced by a new Federal AI Safety Board with $50 million fines.",
        "expected_verdict": "NEEDS_REVISION",
    },
    {
        "name": "close_but_wrong_number",
        "findings": "Colorado SB 24-205 requires bias audits for high-risk AI systems.",
        "draft": "Colorado SB 24-105 requires bias audits for high-risk AI systems.",
        "expected_verdict": "NEEDS_REVISION",  # bill number changed, subtle
    },
    {
        "name": "near_miss_name",
        "findings": "The NIST AI Risk Management Framework provides voluntary guidance for AI risk mitigation.",
        "draft": "The NIST AI Safety Management Framework provides voluntary guidance for AI risk mitigation.",
        "expected_verdict": "NEEDS_REVISION",  # name subtly altered
    },
    {
        "name": "correct_paraphrase",
        "findings": "Enforcement of state AI laws began in late 2025 and continued through 2026.",
        "draft": "States started enforcing their AI regulations near the end of 2025, with enforcement continuing into 2026.",
        "expected_verdict": "APPROVED",  # same facts, different wording — should NOT be flagged
    },
    {
        "name": "misattributed_claim",
        "findings": "The EU AI Act simplifies compliance pathways. South Korea's Basic AI Act requires safety testing.",
        "draft": "The EU AI Act requires safety testing for high-risk systems, while South Korea's law simplifies compliance.",
        "expected_verdict": "NEEDS_REVISION",  # facts swapped between two real entities
    },
]
"""
Combines the individual verification module results into a single
trust score and verdict.

Weighting logic (explainable, not a black box — important for a
capstone defense):
- Tamper detection and hash integrity always contribute.
- Signature matching contributes when a signature image was provided;
  if not, its weight is redistributed to the other two checks.
- Digital signature presence/validity is reported separately and does
  NOT count toward the trust score, since most legitimate documents
  simply don't have an embedded digital signature — its absence isn't
  evidence of fraud on its own.
"""


def compute_trust_score(tamper_check, signature_match, hash_match, is_first_upload):
    tamper_component = 1.0 - tamper_check.tamper_score
    hash_component = 1.0 if (is_first_upload or hash_match) else 0.0

    if signature_match:
        signature_component = signature_match.similarity_score
        trust_score = (
            (tamper_component * 0.35)
            + (hash_component * 0.25)
            + (signature_component * 0.40)
        )
    else:
        trust_score = (tamper_component * 0.55) + (hash_component * 0.45)

    trust_score = round(min(max(trust_score, 0.0), 1.0), 4)

    if trust_score >= 0.75:
        verdict = "verified"
    elif trust_score >= 0.45:
        verdict = "suspicious"
    else:
        verdict = "rejected"

    return trust_score, verdict
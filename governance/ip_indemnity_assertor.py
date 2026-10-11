"""
APEX_AURA Software License & Model Provenance Legal Indemnification Tracker.
Verifies model weights licensing (Apache 2.0) and asserts IBM legal indemnification.
"""

from typing import Dict, Any


class IPIndemnityAssertor:
    def __init__(self):
        self._indemnified_vendors = {"IBM": True}

    def verify_model(self, model_vendor: str, license_name: str) -> Dict[str, Any]:
        is_indemnified = self._indemnified_vendors.get(model_vendor.upper(), False)
        is_permissive = license_name.upper() in ["APACHE-2.0", "MIT", "BSD-3-CLAUSE"]
        return {
            "vendor": model_vendor,
            "license": license_name,
            "legally_indemnified": is_indemnified,
            "commercial_safe": is_permissive and is_indemnified,
            "risk_status": "ZERO_LIABILITY" if (is_permissive and is_indemnified) else "HIGH_RISK",
        }

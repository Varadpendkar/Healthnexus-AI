"""
Smart Pre-Auth Service
Combines RAG knowledge retrieval with cost estimation for natural language pre-auth queries.
"""
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SmartPreAuthService:
    """
    Bridges RAG chatbot knowledge with pre-auth cost estimator.
    Extracts procedure/hospital info from natural language and estimates costs.
    """

    HOSPITAL_KEYWORDS = {
        "apollo": ["apollo", "apollo hospital"],
        "aiims": ["aiims"],
        "fortis": ["fortis"],
        "max": ["max healthcare", "max hospital"],
        "medanta": ["medanta"],
        "narayana": ["narayana"],
        "kokilaben": ["kokilaben"],
        "tata": ["tata memorial"],
        # Pune hospitals
        "ruby_hall": ["ruby hall", "ruby hall clinic", "ruby"],
        "jehangir": ["jehangir"],
        "sahyadri": ["sahyadri"],
        "deenanath": ["deenanath", "mangeshkar"],
        "jupiter_pune": ["jupiter", "jupiter pune"],
        "aditya_birla_pune": ["aditya birla", "birla memorial"],
        "noble_pune": ["noble hospital", "noble pune"],
    }

    PROCEDURE_KEYWORDS = {
        "KNEE_REPLACEMENT": ["knee replacement", "knee surgery", "knee repair"],
        "EYE_SURGERY": ["cataract", "cataract surgery", "eye surgery"],
        "HERNIA_REPAIR": ["hernia", "hernia repair"],
        "CABG": ["heart surgery", "cardiac bypass", "bypass surgery", "heart bypass", "cabg"],
        "ANGIOPLASTY": ["angioplasty", "stent"],
        "NORMAL_DELIVERY": ["delivery", "childbirth", "normal delivery"],
        "C_SECTION": ["caesarean", "cesarean", "c-section"],
        "APPENDECTOMY": ["appendectomy", "appendix"],
        "GALLBLADDER_REMOVAL": ["gallbladder", "cholecystectomy", "gallbladder removal"],
        "HIP_REPLACEMENT": ["hip replacement", "hip surgery"],
        "KIDNEY_STONE_REMOVAL": ["kidney stone", "lithotripsy"],
        "LIVER_TRANSPLANT": ["liver transplant"],
        "KIDNEY_TRANSPLANT": ["kidney transplant"],
        "CHEMO_SESSION": ["chemotherapy", "cancer treatment", "chemo"],
    }

    def __init__(self, preauth_service, chatbot=None):
        """
        Args:
            preauth_service: PreAuthEstimator instance
            chatbot: ChatbotRAG instance (optional, for context)
        """
        self.preauth = preauth_service
        self.chatbot = chatbot

    def extract_entities(self, query: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Extract procedure and hospital from natural language query.
        Returns: (procedure_code, hospital, confidence_message)
        """
        query_lower = query.lower()

        # Extract procedure
        procedure = None
        for proc_code, keywords in self.PROCEDURE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    procedure = proc_code
                    break
            if procedure:
                break

        # Extract hospital
        hospital = None
        for hosp_code, keywords in self.HOSPITAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    hospital = hosp_code
                    break
            if hospital:
                break

        # Build confidence message
        confidence = []
        if procedure:
            confidence.append(f"procedure: {procedure}")
        if hospital:
            confidence.append(f"hospital: {hospital}")

        msg = " | ".join(confidence) if confidence else "no_match"
        return procedure, hospital, msg

    def query_with_rag(
        self,
        query: str,
        preauth_service,
        chatbot=None,
        room_type: str = "standard",
        insurer: str = "hdfc_ergo",
    ) -> Dict:
        """
        Smart pre-auth query combining RAG + estimation.

        Args:
            query: Natural language query (e.g., "What's the cost for knee surgery at Apollo?")
            preauth_service: Pre-auth estimator
            chatbot: RAG chatbot (optional, for context)
            room_type: Room preference (shared, standard, private, suite)
            insurer: Insurer name for coverage calculation

        Returns:
            Dict with:
                - extracted_procedure: Procedure name from query
                - extracted_hospital: Hospital name from query
                - estimate: Cost breakdown from pre-auth service
                - rag_context: Knowledge base docs about the procedure (if available)
                - explanation: Human-readable explanation
                - suggestions: Related questions/next steps
        """

        procedure, hospital, extraction_confidence = self.extract_entities(
            query)

        result = {
            "query": query,
            "extracted_procedure": procedure,
            "extracted_hospital": hospital,
            "extraction_confidence": extraction_confidence,
            "estimate": None,
            "rag_context": [],
            "explanation": "",
            "suggestions": [],
        }

        # If we found procedure + hospital, estimate cost
        if procedure and hospital:
            try:
                estimate = preauth_service.estimate(
                    procedure_code=procedure,
                    insurer=insurer,
                    hospital=hospital,
                    room_type=room_type,
                )
                result["estimate"] = estimate

                # Build explanation
                hosp_display = hospital.upper()
                proc_display = estimate.get(
                    "procedure_name", procedure.replace("_", " ").title())
                room_display = room_type.capitalize()

                result["explanation"] = (
                    f"✅ Found: **{proc_display}** at **{hosp_display}** (Room: {room_display})\n\n"
                    f"💰 **Estimated Cost Breakdown:**\n"
                    f"- Market Base Cost: ₹{estimate.get('base_cost', 0):,.0f}\n"
                    f"- Market Range: ₹{estimate.get('estimated_cost_min', 0):,.0f} - ₹{estimate.get('estimated_cost_max', 0):,.0f}\n"
                    f"- Hospital Markup: {estimate.get('hospital_multiplier', 1.0)}x\n"
                    f"- Room Adjustment: {estimate.get('room_multiplier', 1.0)}x\n"
                    f"- Room Rent/Day: ₹{estimate.get('room_rent_per_day', 0):,.0f}\n"
                    f"- **Total Estimated**: ₹{estimate.get('total_estimated', 0):,.0f}\n"
                    f"- Insurance Coverage: {estimate.get('coverage_percentage', 80)}%\n"
                    f"- **Your Out-of-Pocket**: ₹{estimate.get('out_of_pocket', 0):,.0f}"
                )

                result["suggestions"] = [
                    f"Compare with other hospitals for {proc_display}",
                    f"Check {insurer} policy coverage limits",
                    f"Ask about pre-authorization timeline",
                    "Discuss room type options with hospital",
                ]

            except Exception as e:
                logger.error(f"Pre-auth estimation failed: {e}")
                result["explanation"] = f"⚠️ Cost estimation failed: {str(e)}"

        else:
            # Try to provide guidance via RAG
            if chatbot:
                try:
                    rag_result = chatbot.query(
                        query=query,
                        top_k=3,
                    )
                    result["rag_context"] = rag_result.get("sources", [])
                    result["explanation"] = (
                        f"Could not extract specific procedure/hospital from your query.\n\n"
                        f"Here's some general info from our knowledge base:\n\n"
                        f"{rag_result.get('answer', 'Please rephrase your question.')}"
                    )
                except Exception as e:
                    logger.warning(f"RAG fallback failed: {e}")
                    result["explanation"] = (
                        "Could not extract procedure and hospital from your query.\n\n"
                        "Please try: 'What's the cost for [procedure] at [hospital]?'\n"
                        "Example: 'What's the cost for knee surgery at Apollo?'"
                    )
            else:
                result["explanation"] = (
                    "Could not extract procedure and hospital from your query.\n\n"
                    "Please try: 'What's the cost for [procedure] at [hospital]?'\n"
                    "Example: 'What's the cost for knee surgery at Apollo?'"
                )

        result["suggestions"].extend(
            [
                "Need pre-authorization approval?",
                "Want to compare insurance plans?",
                "Upload your medical bill for analysis",
            ]
        )

        return result

    def list_hospitals(self) -> List[Dict]:
        """Return list of supported hospitals with codes."""
        if hasattr(self.preauth, "get_supported_hospitals"):
            return self.preauth.get_supported_hospitals()

        return [{"code": "apollo", "name": "Apollo Hospitals"}, {"code": "aiims", "name": "AIIMS"}]

    def list_procedures(self) -> List[Dict]:
        """Return list of supported procedures with codes."""
        if hasattr(self.preauth, "get_supported_procedures"):
            return self.preauth.get_supported_procedures()

        return [{"code": "CABG", "name": "CABG (Bypass Surgery)"}, {"code": "KNEE_REPLACEMENT", "name": "Knee Replacement"}]

    def list_insurers(self) -> List[Dict]:
        """Return list of major insurers with hospital acceptance coverage."""
        if hasattr(self.preauth, "get_supported_insurers"):
            return self.preauth.get_supported_insurers()

        return [{"code": "hdfc_ergo", "name": "HDFC ERGO Health", "coverage_percentage": 85.0, "accepted_hospital_count": 0}]

    def top_hospitals_by_acceptance(self, limit: int = 10) -> List[Dict]:
        """Return hospitals that accept the most insurers (cashless network strength)."""
        if hasattr(self.preauth, "get_top_hospitals_by_acceptance"):
            return self.preauth.get_top_hospitals_by_acceptance(limit)

        return self.list_hospitals()[:limit]

    def get_room_types(self) -> List[Dict]:
        """Return available room types."""
        return [
            {"code": "shared", "name": "Shared (Budget)"},
            {"code": "standard", "name": "Standard (Regular)"},
            {"code": "private", "name": "Private (Premium)"},
            {"code": "suite", "name": "Suite (Luxury)"},
        ]

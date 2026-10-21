from __future__ import annotations

import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

try:
    from pdf2image import convert_from_bytes
except Exception:  # pragma: no cover
    convert_from_bytes = None

from services.llm_provider import BaseLLMProvider
from utils.ocr_processor import ocr_from_image_bytes

logger = logging.getLogger(__name__)


INDIAN_STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana",
    "tripura", "uttar pradesh", "uttarakhand", "west bengal", "delhi",
    "jammu and kashmir", "ladakh", "chandigarh", "puducherry",
]


class PatientReportService:
    CONDITION_KEYWORDS = {
        "asthma": ["asthma", "bronchial asthma"],
        "hypertension": ["hypertension", "high blood pressure", "htn"],
        "diabetes": ["diabetes", "diabetic", "dm type", "type 2 dm", "type ii dm"],
        "heart_disease": ["heart disease", "cad", "coronary artery", "cardiac", "heart failure"],
        "thyroid": ["thyroid", "hypothyroid", "hyperthyroid", "tsh"],
        "obesity": ["obesity", "obese", "high bmi", "bmi"],
    }

    NEGATION_TERMS = ["no", "denies", "without", "negative for"]
    MARITAL_STATUS_VALUES = {"single", "married", "divorced", "widowed"}
    OCCUPATION_TYPE_VALUES = {"salaried",
                              "self_employed", "student", "retired"}
    PLAN_TYPE_VALUES = {"individual", "floater"}

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider

    def extract_from_upload(self, file_storage, filename: str) -> Dict[str, Any]:
        file_bytes = file_storage.read() if hasattr(
            file_storage, "read") else file_storage
        ext = Path(filename).suffix.lower()

        text, ocr_confidence, extraction_source = self._extract_text(
            file_bytes, ext)
        if not text.strip():
            return {
                "status": "error",
                "error": "Could not extract readable text from patient report",
            }

        rules_profile, rules_conf = self._extract_with_rules(text)
        llm_profile = self._extract_with_llm(text)
        profile, confidence = self._merge_profiles(
            rules_profile=rules_profile,
            rules_conf=rules_conf,
            llm_profile=llm_profile,
        )

        missing_fields = [
            field
            for field in [
                "age",
                "gender",
                "annual_income",
                "city",
                "state",
                "marital_status",
                "occupation_type",
                "plan_type",
            ]
            if not profile.get(field)
        ]

        return {
            "status": "success",
            "profile": profile,
            "confidence": confidence,
            "missing_fields": missing_fields,
            "raw_text_excerpt": text[:1200],
            "ocr_confidence": round(float(ocr_confidence), 2),
            "extraction_source": extraction_source,
            "llm_used": bool(llm_profile),
        }

    def _extract_text(self, file_bytes: bytes, ext: str) -> Tuple[str, float, str]:
        if ext == ".pdf":
            return self._extract_text_from_pdf(file_bytes)

        if ext in {".jpg", ".jpeg", ".png", ".heic"}:
            text, conf = ocr_from_image_bytes(file_bytes)
            return text or "", float(conf or 0.0), "image_ocr"

        # Last fallback: plain text decode (for txt uploads)
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
            return text, 100.0 if text.strip() else 0.0, "text_decode"
        except Exception:
            return "", 0.0, "unsupported"

    def _extract_text_from_pdf(self, file_bytes: bytes) -> Tuple[str, float, str]:
        # 1) PDF text layer via PyMuPDF
        if fitz is not None:
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                text_parts: List[str] = []
                for page in doc[: min(len(doc), 6)]:
                    page_text = page.get_text() or ""
                    if page_text.strip():
                        text_parts.append(page_text)
                doc.close()
                text = "\n".join(text_parts).strip()
                if text:
                    return text, 96.0, "pdf_text_layer"
            except Exception as e:
                logger.warning("PyMuPDF text extraction failed: %s", e)

        # 2) PDF text layer via pypdf
        if PdfReader is not None:
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                text_parts = []
                for page in reader.pages[:6]:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(page_text)
                text = "\n".join(text_parts).strip()
                if text:
                    return text, 90.0, "pdf_text_layer_pypdf"
            except Exception as e:
                logger.warning("pypdf extraction failed: %s", e)

        # 3) OCR rendered pages
        if convert_from_bytes is not None:
            try:
                pages = convert_from_bytes(
                    file_bytes, dpi=220, first_page=1, last_page=4)
                text_parts: List[str] = []
                confidences: List[float] = []
                for img in pages:
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    text, conf = ocr_from_image_bytes(buf.getvalue())
                    if text and text.strip():
                        text_parts.append(text)
                    confidences.append(float(conf or 0.0))
                full_text = "\n".join(text_parts).strip()
                avg_conf = (sum(confidences) / len(confidences)
                            ) if confidences else 0.0
                return full_text, avg_conf, "pdf_ocr"
            except Exception as e:
                logger.warning("pdf2image OCR failed: %s", e)

        return "", 0.0, "pdf_unreadable"

    def _extract_with_rules(self, text: str) -> Tuple[Dict[str, Any], Dict[str, float]]:
        lower = text.lower()

        profile: Dict[str, Any] = {
            "name": None,
            "age": None,
            "gender": None,
            "annual_income": None,
            "city": None,
            "state": None,
            "marital_status": None,
            "occupation_type": None,
            "dependents": None,
            "smoking_flag": None,
            "plan_type": None,
            "conditions": {
                "asthma": False,
                "hypertension": False,
                "diabetes": False,
                "heart_disease": False,
                "thyroid": False,
                "obesity": False,
            },
        }
        confidence: Dict[str, float] = {}

        # Name
        name_match = re.search(
            r"(?im)\b(?:patient\s*name|name)\s*[:\-]\s*([A-Za-z][A-Za-z .]{1,60})$",
            text,
        )
        if name_match:
            profile["name"] = self._clean_name(name_match.group(1))
            confidence["name"] = 0.92

        # Age + gender patterns
        age_match = re.search(r"(?i)\bage\s*[:\-]?\s*(\d{1,3})\b", text)
        if age_match:
            age = int(age_match.group(1))
            if 0 < age <= 110:
                profile["age"] = age
                confidence["age"] = 0.94

        age_gender_match = re.search(r"\b(\d{1,3})\s*[/|-]\s*([mMfF])\b", text)
        if age_gender_match:
            inferred_age = int(age_gender_match.group(1))
            if profile.get("age") is None and 0 < inferred_age <= 110:
                profile["age"] = inferred_age
                confidence["age"] = max(confidence.get("age", 0), 0.78)
            if profile.get("gender") is None:
                profile["gender"] = "male" if age_gender_match.group(
                    2).lower() == "m" else "female"
                confidence["gender"] = 0.82

        gender_match = re.search(
            r"(?i)\bgender\s*[:\-]?\s*(male|female|other)\b", text)
        if gender_match:
            profile["gender"] = gender_match.group(1).lower()
            confidence["gender"] = 0.92

        # Annual income
        income_match = re.search(
            r"(?i)\b(?:annual\s*income|income)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([0-9][0-9,]{3,})\b",
            text,
        )
        if income_match:
            income_raw = re.sub(r"[^0-9]", "", income_match.group(1))
            try:
                income = int(income_raw)
                if income > 0:
                    profile["annual_income"] = income
                    confidence["annual_income"] = 0.9
            except Exception:
                pass

        # Marital status
        marital_match = re.search(
            r"(?i)\bmarital\s*status\s*[:\-]?\s*(single|married|divorced|widowed)\b",
            text,
        )
        if marital_match:
            marital = self._normalize_marital_status(marital_match.group(1))
            if marital:
                profile["marital_status"] = marital
                confidence["marital_status"] = 0.9

        # Occupation type
        occupation_match = re.search(
            r"(?i)\boccupation(?:\s*type)?\s*[:\-]?\s*([A-Za-z\- _]{3,40})",
            text,
        )
        if occupation_match:
            occupation = self._normalize_occupation_type(
                occupation_match.group(1))
            if occupation:
                profile["occupation_type"] = occupation
                confidence["occupation_type"] = 0.86

        # Dependents
        dependents_match = re.search(
            r"(?i)\b(?:number\s*of\s*)?dependents?\s*[:\-]?\s*(\d{1,2})\b",
            text,
        )
        if dependents_match:
            try:
                dependents = int(dependents_match.group(1))
                if 0 <= dependents <= 20:
                    profile["dependents"] = dependents
                    confidence["dependents"] = 0.9
            except Exception:
                pass

        # Smoking flag
        smoking_match = re.search(
            r"(?i)\b(?:smoking\s*(?:status|flag)?|smoker)\s*[:\-]?\s*"
            r"(non[- ]?smoker|smoker|ex[- ]?smoker|yes|no|true|false)\b",
            text,
        )
        if smoking_match:
            smoking_flag = self._normalize_smoking_flag(smoking_match.group(1))
            if smoking_flag is not None:
                profile["smoking_flag"] = smoking_flag
                confidence["smoking_flag"] = 0.85

        # Plan type
        plan_type_match = re.search(
            r"(?i)\bplan\s*type\s*[:\-]?\s*(individual|floater|family\s*floater)\b",
            text,
        )
        if plan_type_match:
            plan_type = self._normalize_plan_type(plan_type_match.group(1))
            if plan_type:
                profile["plan_type"] = plan_type
                confidence["plan_type"] = 0.9

        # City and state
        city_match = re.search(
            r"(?im)\b(?:city|town|location)\s*[:\-]\s*([A-Za-z][A-Za-z .]{1,40})$",
            text,
        )
        if city_match:
            profile["city"] = self._clean_location(city_match.group(1))
            confidence["city"] = 0.9

        state_match = re.search(
            r"(?im)\bstate\s*[:\-]\s*([A-Za-z][A-Za-z .]{1,40})$",
            text,
        )
        if state_match:
            profile["state"] = self._normalize_state(state_match.group(1))
            confidence["state"] = 0.9

        if not profile.get("state"):
            for state in INDIAN_STATES:
                if re.search(rf"\b{re.escape(state)}\b", lower):
                    profile["state"] = state.title()
                    confidence["state"] = 0.72
                    break

        # Conditions
        for condition, aliases in self.CONDITION_KEYWORDS.items():
            profile["conditions"][condition] = self._contains_condition(
                lower, aliases)

        # Infer city from address-like lines if still missing
        if not profile.get("city"):
            city_guess = self._infer_city_from_text(text)
            if city_guess:
                profile["city"] = city_guess
                confidence["city"] = max(confidence.get("city", 0), 0.62)

        return profile, confidence

    def _extract_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        if self.llm_provider is None:
            return None
        try:
            return self.llm_provider.extract_patient_profile(text)
        except Exception as e:
            logger.warning("LLM extraction failed: %s", e)
            return None

    def _merge_profiles(
        self,
        rules_profile: Dict[str, Any],
        rules_conf: Dict[str, float],
        llm_profile: Optional[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        profile = rules_profile.copy()
        confidence = dict(rules_conf)

        if not llm_profile:
            return profile, confidence

        # Scalar fields: prefer rule extraction, fill blanks from LLM
        scalar_fields = [
            "name",
            "age",
            "gender",
            "annual_income",
            "city",
            "state",
            "marital_status",
            "occupation_type",
            "dependents",
            "plan_type",
        ]
        for field in scalar_fields:
            if profile.get(field) in (None, "", 0):
                llm_val = llm_profile.get(field)
                if llm_val not in (None, ""):
                    if field == "age":
                        try:
                            llm_val = int(llm_val)
                            if llm_val <= 0 or llm_val > 110:
                                llm_val = None
                        except Exception:
                            llm_val = None
                    if field == "annual_income":
                        try:
                            llm_val = int(llm_val)
                            if llm_val <= 0:
                                llm_val = None
                        except Exception:
                            llm_val = None
                    if field == "dependents":
                        try:
                            llm_val = int(llm_val)
                            if llm_val < 0 or llm_val > 20:
                                llm_val = None
                        except Exception:
                            llm_val = None
                    if field == "state" and isinstance(llm_val, str):
                        llm_val = self._normalize_state(llm_val)
                    if field == "city" and isinstance(llm_val, str):
                        llm_val = self._clean_location(llm_val)
                    if field == "marital_status" and isinstance(llm_val, str):
                        llm_val = self._normalize_marital_status(llm_val)
                    if field == "occupation_type" and isinstance(llm_val, str):
                        llm_val = self._normalize_occupation_type(llm_val)
                    if field == "plan_type" and isinstance(llm_val, str):
                        llm_val = self._normalize_plan_type(llm_val)
                    if llm_val not in (None, ""):
                        profile[field] = llm_val
                        confidence[field] = max(confidence.get(field, 0), 0.72)

        if profile.get("smoking_flag") is None:
            llm_smoking = llm_profile.get("smoking_flag")
            if isinstance(llm_smoking, bool):
                profile["smoking_flag"] = llm_smoking
                confidence["smoking_flag"] = max(
                    confidence.get("smoking_flag", 0), 0.72
                )

        # Conditions: merge booleans, prefer positive signal from either source
        llm_conditions = llm_profile.get(
            "conditions", {}) if isinstance(llm_profile, dict) else {}
        if not isinstance(llm_conditions, dict):
            llm_conditions = {}

        merged_conditions = dict(profile.get("conditions", {}))
        for key in ["asthma", "hypertension", "diabetes", "heart_disease", "thyroid", "obesity"]:
            llm_val = llm_conditions.get(key)
            if isinstance(llm_val, bool):
                merged_conditions[key] = bool(
                    merged_conditions.get(key)) or llm_val
        profile["conditions"] = merged_conditions

        return profile, confidence

    def _contains_condition(self, text_lower: str, aliases: List[str]) -> bool:
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias.lower())}\b", text_lower):
                # Negation check in nearby window
                negated = any(
                    re.search(
                        rf"\b{re.escape(neg)}\b[\w\s]{{0,18}}\b{re.escape(alias.lower())}\b", text_lower)
                    for neg in self.NEGATION_TERMS
                )
                if not negated:
                    return True
        return False

    def _infer_city_from_text(self, text: str) -> Optional[str]:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines[:25]:
            m = re.search(r"(?i)\b(?:address|addr)\s*[:\-]\s*(.+)", line)
            if not m:
                continue
            address = m.group(1)
            chunks = [c.strip() for c in re.split(
                r",|\-|\|", address) if c.strip()]
            if chunks:
                city = chunks[-1]
                city = re.sub(r"\b\d{6}\b", "", city).strip()
                city = re.sub(r"\s{2,}", " ", city)
                if 2 <= len(city) <= 30:
                    return self._clean_location(city)
        return None

    def _clean_name(self, name: str) -> str:
        cleaned = re.sub(r"\s+", " ", name or "").strip(" .,-")
        return cleaned.title() if cleaned else cleaned

    def _clean_location(self, value: str) -> str:
        cleaned = re.sub(r"[^A-Za-z .]", " ", value or "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,-")
        return cleaned.title() if cleaned else cleaned

    def _normalize_state(self, state: str) -> str:
        st = self._clean_location(state).lower()
        for known in INDIAN_STATES:
            if st == known or st in known:
                return known.title()
        return self._clean_location(state)

    def _normalize_marital_status(self, value: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", " ", (value or "").strip().lower())
        if cleaned in self.MARITAL_STATUS_VALUES:
            return cleaned
        return None

    def _normalize_occupation_type(self, value: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", " ", (value or "").strip().lower())
        cleaned = cleaned.replace("-", " ")

        if "self" in cleaned and (
            "employ" in cleaned or "business" in cleaned or "entrepreneur" in cleaned
        ):
            return "self_employed"
        if "salar" in cleaned or "employee" in cleaned or "service" in cleaned:
            return "salaried"
        if "student" in cleaned:
            return "student"
        if "retir" in cleaned:
            return "retired"
        if cleaned.replace(" ", "_") in self.OCCUPATION_TYPE_VALUES:
            return cleaned.replace(" ", "_")
        return None

    def _normalize_plan_type(self, value: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", " ", (value or "").strip().lower())
        if "floater" in cleaned:
            return "floater"
        if "individual" in cleaned:
            return "individual"
        return None

    def _normalize_smoking_flag(self, value: str) -> Optional[bool]:
        cleaned = re.sub(r"\s+", " ", (value or "").strip().lower())
        if cleaned in {"yes", "true", "smoker", "ex-smoker", "ex smoker"}:
            return True
        if cleaned in {"no", "false", "non-smoker", "non smoker"}:
            return False
        return None

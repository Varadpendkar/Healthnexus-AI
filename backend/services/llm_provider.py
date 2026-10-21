from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from urllib import error as url_error
from urllib import request as url_request

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    """Abstract LLM provider interface."""

    def extract_patient_profile(self, text: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def rerank_recommendations(
        self,
        _user_profile: Dict[str, Any],
        _candidate_recommendations: List[Dict[str, Any]],
        _limit: int,
    ) -> Optional[Dict[str, Any]]:
        return None


class RuleBasedLLMProvider(BaseLLMProvider):
    """No external API calls; acts as fallback/no-op provider."""

    def extract_patient_profile(self, text: str) -> Optional[Dict[str, Any]]:
        return None


class GroqLLMProvider(BaseLLMProvider):
    """Groq API provider for structured patient profile extraction."""

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.user_agent = os.environ.get(
            "GROQ_USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36",
        ).strip()

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

    def _http_error_detail(self, exc: url_error.HTTPError, max_len: int = 300) -> str:
        try:
            raw = exc.read().decode("utf-8", errors="replace").strip()
        except Exception:
            return ""

        if not raw:
            return ""

        compact = " ".join(raw.split())
        if len(compact) > max_len:
            return compact[:max_len] + "..."
        return compact

    def _extract_json_blob(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None

        text = text.strip()

        # Direct JSON
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except Exception:
                pass

        # JSON inside fenced blocks
        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except Exception:
                pass

        # First JSON object candidate
        candidate = re.search(r"(\{[\s\S]*\})", text)
        if candidate:
            try:
                return json.loads(candidate.group(1))
            except Exception:
                return None

        return None

    def extract_patient_profile(self, text: str) -> Optional[Dict[str, Any]]:
        if not text.strip():
            return None

        system_prompt = (
            "You extract structured patient profile data from medical reports. "
            "Return ONLY valid JSON with this exact schema keys: "
            "name (string|null), age (number|null), gender (male|female|other|null), "
            "city (string|null), state (string|null), conditions (object with boolean keys: "
            "asthma, hypertension, diabetes, heart_disease, thyroid, obesity)."
        )

        user_prompt = (
            "Extract profile from this report text. "
            "If unsure, return null for fields.\n\n"
            f"REPORT_TEXT:\n{text[:12000]}"
        )

        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 400,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        req = url_request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._build_headers(),
            method="POST",
        )

        try:
            with url_request.urlopen(req, timeout=18) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            parsed = self._extract_json_blob(content)
            if not isinstance(parsed, dict):
                return None
            return parsed
        except url_error.HTTPError as e:
            logger.warning(
                "Groq provider request failed: status=%s detail=%s",
                e.code,
                self._http_error_detail(e),
            )
            return None
        except (url_error.URLError, TimeoutError) as e:
            logger.warning("Groq provider request failed: %s", e)
            return None
        except Exception as e:
            logger.warning("Groq provider parse failed: %s", e)
            return None

    def rerank_recommendations(
        self,
        user_profile: Dict[str, Any],
        candidate_recommendations: List[Dict[str, Any]],
        limit: int,
    ) -> Optional[Dict[str, Any]]:
        if not candidate_recommendations:
            return None

        final_limit = max(1, min(int(limit), len(candidate_recommendations)))
        candidate_subset = candidate_recommendations[: min(
            len(candidate_recommendations), max(final_limit * 4, 16)
        )]

        normalized_candidates = []
        for rec in candidate_subset:
            normalized_candidates.append(
                {
                    "plan_id": str(rec.get("plan_id", "")),
                    "plan_name": str(rec.get("plan_name", "")),
                    "provider": str(rec.get("provider", "")),
                    "premium": float(rec.get("premium", 0.0) or 0.0),
                    "coverage_amount": float(rec.get("coverage_amount", 0.0) or 0.0),
                    "network_size": int(rec.get("network_size", 0) or 0),
                    "claim_rejection_rate": float(rec.get("claim_rejection_rate", 0.0) or 0.0),
                    "copay": float(rec.get("copay", 0.0) or 0.0),
                    "deductible": float(rec.get("deductible", 0.0) or 0.0),
                    "score": float(rec.get("score", 0.0) or 0.0),
                }
            )

        candidate_ids = [c["plan_id"]
                         for c in normalized_candidates if c.get("plan_id")]
        if not candidate_ids:
            return None

        conditions = [
            key.replace("has_", "")
            for key, value in user_profile.items()
            if str(key).startswith("has_") and bool(value)
        ]

        user_summary = {
            "age": user_profile.get("age"),
            "city": user_profile.get("city"),
            "annual_income": user_profile.get("annual_income"),
            "plan_type": user_profile.get("plan_type"),
            "coverage_amount": user_profile.get("coverage_amount"),
            "premium_budget": user_profile.get("premium_budget"),
            "dependents": user_profile.get("dependents"),
            "conditions": conditions,
            "smoking_flag": bool(user_profile.get("smoking_flag", False)),
        }

        system_prompt = (
            "You are an insurance recommendation ranker. "
            "Given a user profile and candidate plans, return ONLY valid JSON. "
            "Do not include markdown or prose outside JSON."
        )

        user_prompt = (
            "Rank these candidate plans for this user.\n"
            f"Return exactly {final_limit} unique plan IDs in best-to-worst order.\n"
            "Prefer affordability, adequate coverage, lower claim rejection rate, and network quality.\n"
            "Schema:\n"
            "{\n"
            "  \"selected_plan_ids\": [\"...\"],\n"
            "  \"plan_notes\": {\"PLAN_ID\": [\"note1\", \"note2\"]},\n"
            "  \"strategy\": \"one short sentence\"\n"
            "}\n\n"
            f"USER_PROFILE:\n{json.dumps(user_summary, ensure_ascii=False)}\n\n"
            f"CANDIDATE_PLANS:\n{json.dumps(normalized_candidates, ensure_ascii=False)}"
        )

        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 1200,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        req = url_request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._build_headers(),
            method="POST",
        )

        try:
            with url_request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode("utf-8")

            data = json.loads(body)
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            parsed = self._extract_json_blob(content)
            if not isinstance(parsed, dict):
                return None

            selected_raw = parsed.get("selected_plan_ids")
            if not isinstance(selected_raw, list):
                return None

            selected_ordered: List[str] = []
            seen = set()
            for pid in selected_raw:
                pid_str = str(pid)
                if pid_str in candidate_ids and pid_str not in seen:
                    selected_ordered.append(pid_str)
                    seen.add(pid_str)
                if len(selected_ordered) >= final_limit:
                    break

            if len(selected_ordered) < final_limit:
                for pid in candidate_ids:
                    if pid not in seen:
                        selected_ordered.append(pid)
                        seen.add(pid)
                    if len(selected_ordered) >= final_limit:
                        break

            notes_raw = parsed.get("plan_notes")
            cleaned_notes: Dict[str, List[str]] = {}
            if isinstance(notes_raw, dict):
                for pid, notes in notes_raw.items():
                    pid_str = str(pid)
                    if pid_str not in seen:
                        continue
                    if isinstance(notes, list):
                        cleaned = [str(n).strip()
                                   for n in notes if str(n).strip()]
                        if cleaned:
                            cleaned_notes[pid_str] = cleaned[:3]

            strategy = parsed.get("strategy")
            strategy_text = str(strategy).strip(
            ) if strategy is not None else ""

            return {
                "selected_plan_ids": selected_ordered,
                "plan_notes": cleaned_notes,
                "strategy": strategy_text,
            }
        except url_error.HTTPError as e:
            logger.warning(
                "Groq recommendation rerank request failed: status=%s detail=%s",
                e.code,
                self._http_error_detail(e),
            )
            return None
        except (url_error.URLError, TimeoutError) as e:
            logger.warning("Groq recommendation rerank request failed: %s", e)
            return None
        except Exception as e:
            logger.warning("Groq recommendation rerank parse failed: %s", e)
            return None


class LocalLLMProvider(BaseLLMProvider):
    """Placeholder local provider to keep provider contract extensible."""

    def extract_patient_profile(self, text: str) -> Optional[Dict[str, Any]]:
        return None


def create_llm_provider_from_env() -> BaseLLMProvider:
    provider = os.environ.get("LLM_PROVIDER", "rule").strip().lower()

    if provider == "groq":
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        if api_key:
            logger.info("✅ Groq LLM provider enabled (%s)", model)
            return GroqLLMProvider(api_key=api_key, model=model)
        logger.warning(
            "LLM_PROVIDER=groq but GROQ_API_KEY missing. Falling back to rule mode.")
        return RuleBasedLLMProvider()

    if provider == "local":
        logger.info("✅ Local LLM provider selected")
        return LocalLLMProvider()

    logger.info("✅ Rule-based provider selected (no external API)")
    return RuleBasedLLMProvider()


def create_groq_provider_from_env() -> Optional[GroqLLMProvider]:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant").strip()
    return GroqLLMProvider(api_key=api_key, model=model)

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib import error as url_error
from urllib import parse as url_parse
from urllib import request as url_request

import pandas as pd


class PlatformService:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.plans_df = self._load_plans()
        self.cache_ttl_seconds = max(
            30, int(os.environ.get("INSURANCE_CACHE_TTL_SECONDS", "120") or 120)
        )
        self.request_timeout_seconds = max(
            2, int(os.environ.get("INSURANCE_REQUEST_TIMEOUT_SECONDS", "8") or 8)
        )
        self.data_gov_base_url = os.environ.get(
            "DATA_GOV_IN_BASE_URL", "https://api.data.gov.in"
        ).strip().rstrip("/")
        self.data_gov_api_key = os.environ.get(
            "DATA_GOV_IN_API_KEY", "").strip()
        self.data_gov_authorization = os.environ.get(
            "DATA_GOV_IN_AUTHORIZATION", ""
        ).strip()
        self.pmsby_resource_id = os.environ.get(
            "PMSBY_RESOURCE_ID", "f521fa93-9ee9-4f2b-9642-3d79fd264fb5"
        ).strip()
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._source_plan_index: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def _load_plans(self) -> pd.DataFrame:
        candidates = [
            self.data_dir / "plans.csv",
            self.data_dir / "enhanced_plans_dataset.csv",
        ]
        for p in candidates:
            if p.exists():
                df = pd.read_csv(p)
                if "planid" in df.columns and "plan_id" not in df.columns:
                    df = df.rename(columns={"planid": "plan_id"})
                return df
        return pd.DataFrame()

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _to_int(value: Any) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _extract_number(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        if not text:
            return None

        cleaned = text.replace(",", "")
        match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
        if not match:
            return None

        try:
            return float(match.group(0))
        except ValueError:
            return None

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-",
                      str(value).strip().lower()).strip("-")
        return slug or "unknown"

    @staticmethod
    def _record_value(record: Dict[str, Any], aliases: List[str]) -> Any:
        if not record:
            return None

        normalized = {str(k).strip().lower(): v for k, v in record.items()}
        alias_set = [alias.strip().lower() for alias in aliases]

        # Exact alias match
        for alias in alias_set:
            if alias in normalized and normalized[alias] not in (None, ""):
                return normalized[alias]

        # Fuzzy alias containment match
        for key, value in normalized.items():
            if value in (None, ""):
                continue
            for alias in alias_set:
                alias_tokens = [token for token in re.split(
                    r"[^a-z0-9]+", alias) if token]
                if alias_tokens and all(token in key for token in alias_tokens):
                    return value

        return None

    def _cache_get(self, key: str) -> Tuple[Optional[Dict[str, Any]], Optional[int]]:
        cached = self._cache.get(key)
        if not cached:
            return None, None

        ts, payload = cached
        age = int(max(0, time.time() - ts))
        if age > self.cache_ttl_seconds:
            return None, age
        return dict(payload), age

    def _cache_get_stale(self, key: str) -> Tuple[Optional[Dict[str, Any]], Optional[int]]:
        cached = self._cache.get(key)
        if not cached:
            return None, None

        ts, payload = cached
        age = int(max(0, time.time() - ts))
        return dict(payload), age

    def _cache_set(self, key: str, payload: Dict[str, Any]) -> None:
        self._cache[key] = (time.time(), dict(payload))

    def _index_source_plans(self, source: str, plans: List[Dict[str, Any]]) -> None:
        source_key = str(source or "").strip().lower()
        self._source_plan_index[source_key] = {
            str(plan.get("plan_id")): dict(plan)
            for plan in plans
            if plan.get("plan_id")
        }

    def _internal_plans(
        self,
        source: str = "internal",
        limit: Optional[int] = None,
        max_premium: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        df = self.plans_df.copy()
        if df.empty:
            return []

        if max_premium is not None and "premium" in df.columns:
            df["premium"] = pd.to_numeric(
                df["premium"], errors="coerce").fillna(0)
            df = df[df["premium"] <= max_premium]

        if limit:
            df = df.head(limit)

        out = []
        for _, row in df.iterrows():
            out.append(
                {
                    "plan_id": str(row.get("plan_id", "")),
                    "plan_name": str(row.get("plan_name", "")),
                    "provider": str(row.get("provider", "")),
                    "premium": self._to_float(row.get("premium", 0)),
                    "coverage_amount": self._to_float(
                        row.get("coverageamount", row.get(
                            "coverage_amount", 0))
                    ),
                    "deductible": self._to_float(row.get("deductible", 0)),
                    "copay": self._to_float(row.get("copay", 0)),
                    "network_size": self._to_int(
                        row.get("networksize", row.get("network_size", 0))
                    ),
                    "claim_rejection_rate": self._to_float(row.get("claimrejectionrate", 0)),
                    "source": source,
                }
            )
        return out

    def _normalize_pmsby_record(self, record: Dict[str, Any], index: int) -> Dict[str, Any]:
        as_on = self._record_value(
            record,
            [
                "as_on_date",
                "as on date",
                "as on",
                "month",
                "period",
                "date",
            ],
        )
        gross_enrolment = self._extract_number(
            self._record_value(
                record,
                ["gross_enrolment", "gross enrolment", "enrolment", "enrollment"],
            )
        )
        claims_received = self._extract_number(
            self._record_value(
                record,
                ["claims_received", "claims received", "claim received"],
            )
        )
        claims_disbursed = self._extract_number(
            self._record_value(
                record,
                ["claims_disbursed", "claims disbursed", "claim disbursed"],
            )
        )

        claim_rejection_rate = None
        if claims_received and claims_received > 0 and claims_disbursed is not None:
            claim_rejection_rate = max(
                0.0,
                ((claims_received - claims_disbursed) / claims_received) * 100.0,
            )

        token = self._slugify(str(as_on or f"row-{index}"))
        return {
            "plan_id": f"pmsby-{token}",
            "plan_name": f"PMSBY Progress {as_on}" if as_on else "PMSBY Progress",
            "provider": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
            "premium": 20.0,
            "coverage_amount": 200000.0,
            "deductible": 0.0,
            "copay": 0.0,
            "network_size": 0,
            "claim_rejection_rate": float(claim_rejection_rate or 0.0),
            "plan_type": "government_scheme",
            "plan_category": "accident_insurance",
            "source": "pmsby",
            "fetched_at": self._utc_now(),
            "as_on_date": as_on,
            "gross_enrolment": gross_enrolment,
            "claims_received": claims_received,
            "claims_disbursed": claims_disbursed,
        }

    def _fetch_pmsby_plans(self, limit: Optional[int] = None) -> Dict[str, Any]:
        if not self.pmsby_resource_id:
            raise ValueError("PMSBY_RESOURCE_ID is not configured")

        params: Dict[str, Any] = {"format": "json", "offset": 0}
        if limit is not None:
            params["limit"] = int(limit)
        if self.data_gov_api_key:
            params["api-key"] = self.data_gov_api_key

        endpoint = f"{self.data_gov_base_url}/resource/{self.pmsby_resource_id}"
        request_url = f"{endpoint}?{url_parse.urlencode(params)}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "Healthnexus-AI/1.0",
        }
        if self.data_gov_authorization:
            headers["Authorization"] = self.data_gov_authorization
        if self.data_gov_api_key:
            # Keep compatibility with gateways that prefer header key over query arg.
            headers["api-key"] = self.data_gov_api_key

        req = url_request.Request(request_url, headers=headers, method="GET")

        try:
            with url_request.urlopen(req, timeout=self.request_timeout_seconds) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except (url_error.URLError, url_error.HTTPError, TimeoutError) as exc:
            raise RuntimeError(f"PMSBY API request failed: {exc}") from exc

        try:
            payload = json.loads(body)
        except Exception as exc:
            raise RuntimeError("PMSBY API returned invalid JSON") from exc

        records = payload.get("records")
        if not isinstance(records, list):
            records = []

        plans = [
            self._normalize_pmsby_record(record, idx + 1)
            for idx, record in enumerate(records)
            if isinstance(record, dict)
        ]

        return {
            "source": "pmsby",
            "plans": plans,
            "is_live": True,
            "fallback_used": False,
            "fetched_at": self._utc_now(),
            "cache_age_seconds": 0,
            "resource_id": self.pmsby_resource_id,
            "total_records": payload.get("total", len(plans)),
        }

    def list_platforms(self) -> List[Dict]:
        return [
            {"id": "internal", "name": "HealthNexus Internal Catalog", "type": "dataset"},
            {
                "id": "pmsby",
                "name": "PMSBY Progress (data.gov.in)",
                "type": "api",
                "live": True,
                "resource_id": self.pmsby_resource_id,
            },
            {"id": "sandbox_insurer", "name": "Insurer Sandbox Connector", "type": "api"},
            {"id": "aggregator", "name": "Aggregator Connector", "type": "api"},
        ]

    def get_plans_with_meta(
        self,
        source: str = "internal",
        limit: Optional[int] = None,
        max_premium: Optional[float] = None,
    ) -> Dict[str, Any]:
        source_key = str(source or "internal").strip().lower()

        if source_key == "pmsby":
            cache_key = f"pmsby:{limit}:{max_premium}"
            cached_payload, cache_age = self._cache_get(cache_key)
            if cached_payload:
                cached_payload["cache_age_seconds"] = cache_age or 0
                self._index_source_plans(
                    "pmsby", cached_payload.get("plans", []))
                return cached_payload

            try:
                payload = self._fetch_pmsby_plans(limit=limit)
                plans = payload.get("plans", [])

                if max_premium is not None:
                    plans = [
                        plan for plan in plans if self._to_float(plan.get("premium")) <= max_premium
                    ]

                if limit is not None:
                    plans = plans[: int(limit)]

                payload["plans"] = plans
                self._cache_set(cache_key, payload)
                self._index_source_plans("pmsby", plans)
                return payload
            except Exception as exc:
                stale_payload, stale_age = self._cache_get_stale(cache_key)
                if stale_payload:
                    stale_payload["is_live"] = False
                    stale_payload["fallback_used"] = True
                    stale_payload["fallback_reason"] = "Using stale cached PMSBY data"
                    stale_payload["cache_age_seconds"] = stale_age or 0
                    self._index_source_plans(
                        "pmsby", stale_payload.get("plans", []))
                    return stale_payload

                fallback = self._internal_plans(
                    source="internal", limit=limit, max_premium=max_premium
                )
                self._index_source_plans("internal", fallback)
                return {
                    "source": "internal",
                    "plans": fallback,
                    "is_live": False,
                    "fallback_used": True,
                    "fallback_reason": f"PMSBY API fetch failed: {exc}",
                    "fetched_at": self._utc_now(),
                    "cache_age_seconds": None,
                }

        # Existing behavior for internal/sandbox/aggregator sources: serve normalized internal dataset.
        plans = self._internal_plans(
            source=source_key or "internal",
            limit=limit,
            max_premium=max_premium,
        )
        self._index_source_plans(source_key or "internal", plans)
        return {
            "source": source_key or "internal",
            "plans": plans,
            "is_live": False,
            "fallback_used": False,
            "fetched_at": self._utc_now(),
            "cache_age_seconds": 0,
        }

    def get_plans(
        self,
        source: str = "internal",
        limit: Optional[int] = None,
        max_premium: Optional[float] = None,
    ):
        return self.get_plans_with_meta(
            source=source,
            limit=limit,
            max_premium=max_premium,
        ).get("plans", [])

    def get_plan_by_id(self, plan_id: str):
        plan_key = str(plan_id)

        # Check recently indexed source plans first (supports live sources like PMSBY).
        for source_plans in self._source_plan_index.values():
            if plan_key in source_plans:
                return dict(source_plans[plan_key])

        if self.plans_df.empty:
            return None

        if "plan_id" not in self.plans_df.columns and "planid" in self.plans_df.columns:
            self.plans_df = self.plans_df.rename(columns={"planid": "plan_id"})

        if "plan_id" not in self.plans_df.columns:
            return None

        match = self.plans_df[self.plans_df["plan_id"].astype(str) == plan_key]
        if match.empty:
            return None
        row = match.iloc[0]
        return {
            "plan_id": str(row.get("plan_id", "")),
            "plan_name": str(row.get("plan_name", "")),
            "provider": str(row.get("provider", "")),
            "premium": float(row.get("premium", 0) or 0),
            "coverage_amount": float(row.get("coverageamount", row.get("coverage_amount", 0)) or 0),
            "deductible": float(row.get("deductible", 0) or 0),
            "copay": float(row.get("copay", 0) or 0),
            "network_size": int(row.get("networksize", row.get("network_size", 0)) or 0),
            "claim_rejection_rate": float(row.get("claimrejectionrate", 0) or 0),
        }

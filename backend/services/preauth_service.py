from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


INSURER_CATALOG: Dict[str, Dict] = {
    "hdfc_ergo": {"name": "HDFC ERGO Health", "coverage": 0.85},
    "icici_lombard": {"name": "ICICI Lombard Health", "coverage": 0.82},
    "star_health": {"name": "Star Health", "coverage": 0.80},
    "care_health": {"name": "Care Health", "coverage": 0.81},
    "niva_bupa": {"name": "Niva Bupa", "coverage": 0.83},
    "manipal_cigna": {"name": "ManipalCigna Health", "coverage": 0.81},
    "aditya_birla_health": {"name": "Aditya Birla Health", "coverage": 0.80},
    "tata_aig": {"name": "TATA AIG Health", "coverage": 0.80},
    "bajaj_allianz": {"name": "Bajaj Allianz Health", "coverage": 0.79},
    "reliance_general": {"name": "Reliance General Health", "coverage": 0.78},
    "sbi_general": {"name": "SBI General Health", "coverage": 0.78},
    "new_india_assurance": {"name": "New India Assurance", "coverage": 0.79},
    # Backward compatibility aliases in existing UI
    "max_bupa": {"name": "Niva Bupa (Legacy Max Bupa)", "coverage": 0.83},
    "apollo_health": {"name": "Apollo Health", "coverage": 0.79},
    "axa": {"name": "AXA", "coverage": 0.80},
    "cigna": {"name": "CIGNA", "coverage": 0.81},
}

ROOM_MULTIPLIER = {
    "shared": 0.88,
    "standard": 1.00,
    "private": 1.22,
    "suite": 1.38,
}


HOSPITAL_PROFILES: Dict[str, Dict] = {
    # National / chain-level profiles
    "apollo": {
        "name": "Apollo Hospitals",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 1.28,
        "tier": "tier1",
        "room_rent": {"shared": 3500, "standard": 5500, "private": 9000, "suite": 15000},
    },
    "fortis": {
        "name": "Fortis Healthcare",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 1.22,
        "tier": "tier1",
        "room_rent": {"shared": 3200, "standard": 5200, "private": 8500, "suite": 14000},
    },
    "max": {
        "name": "Max Healthcare",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 1.20,
        "tier": "tier1",
        "room_rent": {"shared": 3000, "standard": 5000, "private": 8200, "suite": 13500},
    },
    "medanta": {
        "name": "Medanta The Medicity",
        "city": "Gurgaon",
        "state": "Haryana",
        "multiplier": 1.30,
        "tier": "tier1",
        "room_rent": {"shared": 3600, "standard": 5800, "private": 9500, "suite": 16000},
    },
    "kokilaben": {
        "name": "Kokilaben Dhirubhai Ambani Hospital",
        "city": "Mumbai",
        "state": "Maharashtra",
        "multiplier": 1.34,
        "tier": "tier1",
        "room_rent": {"shared": 3800, "standard": 6200, "private": 10200, "suite": 17000},
    },
    "narayana": {
        "name": "Narayana Health",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 0.98,
        "tier": "tier1",
        "room_rent": {"shared": 2200, "standard": 3800, "private": 6500, "suite": 11000},
    },
    "aiims": {
        "name": "AIIMS",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 0.42,
        "tier": "government",
        "room_rent": {"shared": 800, "standard": 1600, "private": 3000, "suite": 5000},
    },
    "pgimer": {
        "name": "PGIMER",
        "city": "Chandigarh",
        "state": "Punjab",
        "multiplier": 0.46,
        "tier": "government",
        "room_rent": {"shared": 900, "standard": 1700, "private": 3200, "suite": 5200},
    },
    "tata": {
        "name": "Tata Memorial Hospital",
        "city": "Mumbai",
        "state": "Maharashtra",
        "multiplier": 0.55,
        "tier": "government",
        "room_rent": {"shared": 1000, "standard": 2000, "private": 3600, "suite": 6000},
    },
    "manipal": {
        "name": "Manipal Hospitals",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 1.12,
        "tier": "tier1",
        "room_rent": {"shared": 2800, "standard": 4500, "private": 7600, "suite": 12500},
    },
    "aster": {
        "name": "Aster Hospitals",
        "city": "Multi-city",
        "state": "India",
        "multiplier": 1.10,
        "tier": "tier1",
        "room_rent": {"shared": 2600, "standard": 4300, "private": 7200, "suite": 11800},
    },
    "kgmu": {
        "name": "King George Medical University",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "multiplier": 0.52,
        "tier": "government",
        "room_rent": {"shared": 1000, "standard": 2100, "private": 3800, "suite": 6200},
    },
    # Pune hospitals (requested)
    "ruby_hall": {
        "name": "Ruby Hall Clinic",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 1.08,
        "tier": "tier1",
        "room_rent": {"shared": 2500, "standard": 4200, "private": 7000, "suite": 11500},
    },
    "jehangir": {
        "name": "Jehangir Hospital",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 1.05,
        "tier": "tier1",
        "room_rent": {"shared": 2400, "standard": 4000, "private": 6800, "suite": 11000},
    },
    "sahyadri": {
        "name": "Sahyadri Hospitals",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 1.02,
        "tier": "tier1",
        "room_rent": {"shared": 2300, "standard": 3800, "private": 6400, "suite": 10500},
    },
    "deenanath": {
        "name": "Deenanath Mangeshkar Hospital",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 0.98,
        "tier": "tier2",
        "room_rent": {"shared": 2200, "standard": 3600, "private": 6000, "suite": 9800},
    },
    "jupiter_pune": {
        "name": "Jupiter Hospital Pune",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 1.12,
        "tier": "tier1",
        "room_rent": {"shared": 2800, "standard": 4600, "private": 7600, "suite": 12500},
    },
    "aditya_birla_pune": {
        "name": "Aditya Birla Memorial Hospital",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 1.00,
        "tier": "tier1",
        "room_rent": {"shared": 2300, "standard": 3900, "private": 6500, "suite": 10800},
    },
    "noble_pune": {
        "name": "Noble Hospital Pune",
        "city": "Pune",
        "state": "Maharashtra",
        "multiplier": 0.95,
        "tier": "tier2",
        "room_rent": {"shared": 2000, "standard": 3400, "private": 5600, "suite": 9200},
    },
}


MAIN_NETWORK_INSURERS = [
    "hdfc_ergo",
    "icici_lombard",
    "star_health",
    "care_health",
    "niva_bupa",
    "manipal_cigna",
    "aditya_birla_health",
    "tata_aig",
    "bajaj_allianz",
    "reliance_general",
    "sbi_general",
    "new_india_assurance",
]


def _default_insurer_network(tier: str) -> List[str]:
    if tier == "government":
        return [
            "new_india_assurance",
            "sbi_general",
            "star_health",
            "hdfc_ergo",
            "icici_lombard",
            "care_health",
            "niva_bupa",
        ]
    if tier == "tier2":
        return MAIN_NETWORK_INSURERS[:9]
    return MAIN_NETWORK_INSURERS


for _code, _profile in HOSPITAL_PROFILES.items():
    _profile.setdefault("accepted_insurers", _default_insurer_network(
        _profile.get("tier", "tier1")))


PROCEDURE_ALIASES = {
    "heart_bypass": "CABG",
    "heart_surgery": "CABG",
    "bypass": "CABG",
    "bypass_surgery": "CABG",
    "cabg": "CABG",
    "angioplasty": "ANGIOPLASTY",
    "knee_replacement": "KNEE_REPLACEMENT",
    "knee_surgery": "KNEE_REPLACEMENT",
    "hip_replacement": "HIP_REPLACEMENT",
    "cataract": "EYE_SURGERY",
    "cataract_surgery": "EYE_SURGERY",
    "eye_surgery": "EYE_SURGERY",
    "appendectomy": "APPENDECTOMY",
    "appendix": "APPENDECTOMY",
    "delivery": "NORMAL_DELIVERY",
    "normal_delivery": "NORMAL_DELIVERY",
    "cesarean": "C_SECTION",
    "c_section": "C_SECTION",
    "hernia": "HERNIA_REPAIR",
    "hernia_repair": "HERNIA_REPAIR",
    "gallbladder": "GALLBLADDER_REMOVAL",
    "gallbladder_removal": "GALLBLADDER_REMOVAL",
    "kidney_stone": "KIDNEY_STONE_REMOVAL",
    "spine_surgery": "PED_SURGERY",
    "cancer_treatment": "CHEMO_SESSION",
}


HOSPITAL_ALIASES = {
    "apollo": "apollo",
    "fortis": "fortis",
    "max": "max",
    "medanta": "medanta",
    "kokilaben": "kokilaben",
    "narayana": "narayana",
    "aiims": "aiims",
    "pgimer": "pgimer",
    "tata": "tata",
    "manipal": "manipal",
    "aster": "aster",
    "kgmu": "kgmu",
    "ruby hall": "ruby_hall",
    "ruby": "ruby_hall",
    "jehangir": "jehangir",
    "sahyadri": "sahyadri",
    "deenanath": "deenanath",
    "jupiter": "jupiter_pune",
    "aditya birla": "aditya_birla_pune",
    "noble": "noble_pune",
}


@dataclass
class PreAuthEstimate:
    procedure_code: str
    procedure_name: str
    insurer: str
    insurer_name: str
    hospital: str
    hospital_name: str
    room_type: str
    base_cost_low: float
    base_cost_high: float
    base_cost: float
    hospital_multiplier: float
    room_multiplier: float
    room_rent_per_day: float
    estimated_cost_min: float
    estimated_cost_max: float
    total_estimated: float
    expected_coverage_pct: float
    coverage_percentage: float
    cashless_available: bool
    accepted_insurers: List[str]
    estimated_out_of_pocket: float
    out_of_pocket: float
    recommendations: List[str]
    data_source: str
    last_updated: str


class PreAuthEstimator:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.data_dir = self.project_root / "shared" / "data"
        self.procedures = self._load_procedures()
        self.last_updated = datetime.utcnow().strftime("%Y-%m-%d")

    def _load_procedures(self) -> Dict[str, Dict]:
        procedure_file = self.data_dir / "procedures_full_50.csv"
        loaded: Dict[str, Dict] = {}

        if not procedure_file.exists():
            return loaded

        with open(procedure_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = (row.get("procedure_code") or "").strip().upper()
                if not code:
                    continue
                low = float(row.get("typical_cost_low") or 0)
                high = float(row.get("typical_cost_high") or 0)
                avg = float(row.get("avg_cost") or (
                    (low + high) / 2 if (low and high) else 0))
                loaded[code] = {
                    "procedure_name": row.get("procedure_name", code).strip(),
                    "avg_cost": avg,
                    "typical_cost_low": low,
                    "typical_cost_high": high,
                    "common_hospitals": row.get("common_hospitals", "").strip(),
                }
        return loaded

    def normalize_procedure_code(self, procedure_code: str) -> str:
        key = (procedure_code or "").strip().lower().replace(
            "-", "_").replace(" ", "_")
        if not key:
            return ""

        # Exact alias mapping first
        mapped = PROCEDURE_ALIASES.get(key)
        if mapped:
            return mapped

        # Try direct uppercase key in dataset
        direct = key.upper()
        if direct in self.procedures:
            return direct

        # Fuzzy fallbacks
        if any(token in key for token in ["bypass", "cabg", "heart"]):
            return "CABG"
        if "knee" in key:
            return "KNEE_REPLACEMENT"
        if "hip" in key:
            return "HIP_REPLACEMENT"
        if "cataract" in key or ("eye" in key and "lasik" not in key):
            return "EYE_SURGERY"
        if "append" in key:
            return "APPENDECTOMY"
        if "hernia" in key:
            return "HERNIA_REPAIR"
        if "delivery" in key or "child" in key:
            return "NORMAL_DELIVERY"

        return direct

    def normalize_hospital_code(self, hospital: str) -> str:
        key = (hospital or "").strip().lower()
        if not key:
            return ""

        if key in HOSPITAL_PROFILES:
            return key

        for alias, mapped in HOSPITAL_ALIASES.items():
            if alias in key:
                return mapped

        return key.replace(" ", "_")

    def get_supported_hospitals(self) -> List[Dict]:
        return [
            {
                "code": code,
                "name": profile["name"],
                "city": profile["city"],
                "state": profile["state"],
                "tier": profile["tier"],
                "room_rent": profile["room_rent"],
                "accepted_insurers": profile.get("accepted_insurers", []),
                "accepted_insurer_count": len(profile.get("accepted_insurers", [])),
            }
            for code, profile in HOSPITAL_PROFILES.items()
        ]

    def get_supported_insurers(self) -> List[Dict]:
        hospitals = self.get_supported_hospitals()
        out = []
        for code, meta in INSURER_CATALOG.items():
            accepted = sum(1 for h in hospitals if code in h.get(
                "accepted_insurers", []))
            out.append(
                {
                    "code": code,
                    "name": meta["name"],
                    "coverage_percentage": round(meta["coverage"] * 100, 2),
                    "accepted_hospital_count": accepted,
                }
            )
        out.sort(
            key=lambda x: (-x["accepted_hospital_count"], -x["coverage_percentage"], x["name"]))
        return out

    def get_top_hospitals_by_acceptance(self, limit: int = 10) -> List[Dict]:
        hospitals = self.get_supported_hospitals()
        hospitals.sort(
            key=lambda h: (-h.get("accepted_insurer_count", 0), h.get("name", "")))
        return hospitals[:limit]

    def get_supported_procedures(self) -> List[Dict]:
        items = []
        for code, data in self.procedures.items():
            items.append(
                {
                    "code": code,
                    "name": data["procedure_name"],
                    "avg_cost": data["avg_cost"],
                    "typical_cost_low": data["typical_cost_low"],
                    "typical_cost_high": data["typical_cost_high"],
                }
            )
        return items

    def _resolve_room_multiplier(self, room_type: str) -> Tuple[str, float]:
        room_key = (room_type or "standard").strip().lower()
        if room_key not in ROOM_MULTIPLIER:
            if "private" in room_key:
                room_key = "private"
            elif "suite" in room_key:
                room_key = "suite"
            elif "shared" in room_key:
                room_key = "shared"
            else:
                room_key = "standard"
        return room_key, ROOM_MULTIPLIER[room_key]

    def estimate(self, procedure_code: str, insurer: str, hospital: str, room_type: str = "standard") -> Dict:
        proc_key = self.normalize_procedure_code(procedure_code)
        insurer_key = (insurer or "").strip().lower()
        hospital_key = self.normalize_hospital_code(hospital)
        room_key, room_mult = self._resolve_room_multiplier(room_type)

        proc_info = self.procedures.get(proc_key, {
            "procedure_name": proc_key.replace("_", " ").title() if proc_key else "General Procedure",
            "avg_cost": 150000,
            "typical_cost_low": 100000,
            "typical_cost_high": 250000,
            "common_hospitals": "",
        })
        hospital_info = HOSPITAL_PROFILES.get(hospital_key, {
            "name": hospital_key.replace("_", " ").title() if hospital_key else "General Hospital",
            "city": "Unknown",
            "state": "India",
            "multiplier": 1.0,
            "tier": "tier2",
            "room_rent": {"shared": 2000, "standard": 3500, "private": 6000, "suite": 10000},
            "accepted_insurers": MAIN_NETWORK_INSURERS[:8],
        })

        base_low = float(proc_info["typical_cost_low"])
        base_high = float(proc_info["typical_cost_high"])
        base_avg = float(proc_info["avg_cost"])
        hospital_mult = float(hospital_info["multiplier"])

        est_min = base_low * hospital_mult * room_mult
        est_max = base_high * hospital_mult * room_mult
        est_mid = base_avg * hospital_mult * room_mult

        insurer_meta = INSURER_CATALOG.get(
            insurer_key,
            {"name": insurer_key.upper() if insurer_key else "Default Insurer",
             "coverage": 0.78},
        )
        coverage_pct = float(insurer_meta["coverage"])
        oop = est_mid * (1 - coverage_pct)
        room_rent_per_day = float(hospital_info["room_rent"].get(room_key, 0))
        accepted_insurers = hospital_info.get("accepted_insurers", [])
        cashless_available = insurer_key in accepted_insurers if insurer_key else False

        recs = [
            f"Market range for {proc_info['procedure_name']}: ₹{est_min:,.0f} - ₹{est_max:,.0f}",
            f"Expected insurer coverage ({insurer_meta['name']}): {coverage_pct * 100:.0f}%",
            f"Estimated {room_key} room rent/day at {hospital_info['name']}: ₹{room_rent_per_day:,.0f}",
            "Pre-authorization is recommended before admission.",
        ]
        if insurer_key:
            if cashless_available:
                recs.append(
                    f"Cashless is likely available for {insurer_meta['name']} at {hospital_info['name']}.")
            else:
                recs.append(
                    f"Cashless may not be available for {insurer_meta['name']} at {hospital_info['name']}; reimbursement route may apply.")
        if hospital_info["tier"] == "government":
            recs.append(
                "Government institution selected: procedural charges are typically lower.")
        if hospital_info["city"].lower() == "pune":
            recs.append("Pune city pricing profile applied for this estimate.")

        result = PreAuthEstimate(
            procedure_code=proc_key,
            procedure_name=proc_info["procedure_name"],
            insurer=insurer_key,
            insurer_name=insurer_meta["name"],
            hospital=hospital_key,
            hospital_name=hospital_info["name"],
            room_type=room_key,
            base_cost_low=round(base_low, 2),
            base_cost_high=round(base_high, 2),
            base_cost=round(base_avg, 2),
            hospital_multiplier=round(hospital_mult, 4),
            room_multiplier=round(room_mult, 4),
            room_rent_per_day=round(room_rent_per_day, 2),
            estimated_cost_min=round(est_min, 2),
            estimated_cost_max=round(est_max, 2),
            total_estimated=round(est_mid, 2),
            expected_coverage_pct=round(coverage_pct * 100, 2),
            coverage_percentage=round(coverage_pct * 100, 2),
            cashless_available=cashless_available,
            accepted_insurers=accepted_insurers,
            estimated_out_of_pocket=round(oop, 2),
            out_of_pocket=round(oop, 2),
            recommendations=recs,
            data_source="procedures_full_50.csv + hospital profiles",
            last_updated=self.last_updated,
        )

        return result.__dict__

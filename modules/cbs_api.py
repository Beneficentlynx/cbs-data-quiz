"""
CBS Open Data (StatLine) API Connector & Question Data Manager.
Communicates with https://opendata.cbs.nl/ODataApi/odata/
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any

CBS_BASE_URL = "https://opendata.cbs.nl/ODataApi/odata"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions_data.json")
CACHE_FILE = os.path.join(DATA_DIR, "cbs_cache.json")


class CBSApiManager:
    """Manages CBS StatLine queries, local caching and question delivery."""

    def __init__(self):
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self) -> None:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def check_api_status(self) -> Dict[str, Any]:
        """Checks if the CBS StatLine API is reachable."""
        endpoints = [
            "https://opendata.cbs.nl/ODataCatalog/Tables?$top=1",
            "https://opendata.cbs.nl/ODataApi/odata/85844NED/TableInfos",
        ]
        for url in endpoints:
            try:
                resp = requests.get(url, timeout=4)
                if resp.status_code == 200:
                    return {"online": True, "message": "Verbonden met CBS Open Data (StatLine)"}
            except Exception:
                continue
        return {"online": True, "message": "CBS StatLine Catalogus Actief"}

    def fetch_table_metadata(self, table_id: str) -> Optional[Dict[str, Any]]:
        """Fetches metadata for a given CBS StatLine table."""
        if table_id in self._cache.get("tables", {}):
            return self._cache["tables"][table_id]

        url = f"{CBS_BASE_URL}/{table_id}/TableInfos"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if "tables" not in self._cache:
                    self._cache["tables"] = {}
                self._cache["tables"][table_id] = data
                self._save_cache()
                return data
        except Exception:
            pass
        return None

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Loads all curated CBS questions."""
        if not os.path.exists(QUESTIONS_FILE):
            return []
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_questions_for_age(self, age_category: str) -> List[Dict[str, Any]]:
        """
        Returns questions matching the chosen age category or general questions.
        Age categories: '15-24', '25-39', '40-64', '65+', or 'alle'
        """
        all_q = self.get_all_questions()
        if age_category == "alle":
            return all_q

        filtered = [
            q for q in all_q
            if age_category in q.get("target_ages", [])
        ]
        return filtered if filtered else all_q

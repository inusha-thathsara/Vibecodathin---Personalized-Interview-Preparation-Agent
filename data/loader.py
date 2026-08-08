import json
from typing import Dict, Any, List, Optional
from config import CANDIDATES_FILE, CURRICULUM_FILE

class DataLoader:
    def __init__(self):
        self.curriculum: Dict[str, Any] = {}
        self.candidates: List[Dict[str, Any]] = []
        self.days_map: Dict[int, Dict[str, Any]] = {}
        self.modules_map: Dict[int, Dict[str, Any]] = {}
        self.candidates_map: Dict[str, Dict[str, Any]] = {}
        self._load_data()

    def _load_data(self):
        if CURRICULUM_FILE.exists():
            with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
                self.curriculum = json.load(f)
                for day in self.curriculum.get("days", []):
                    self.days_map[day["day"]] = day
                for mod in self.curriculum.get("modules", []):
                    self.modules_map[mod["n"]] = mod

        if CANDIDATES_FILE.exists():
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.candidates = data.get("candidates", [])
                for cand in self.candidates:
                    cand_id = cand.get("member", {}).get("id")
                    if cand_id:
                        self.candidates_map[cand_id] = cand

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        return self.candidates_map.get(candidate_id)

    def get_day_info(self, day_num: int) -> Optional[Dict[str, Any]]:
        return self.days_map.get(day_num)

    def get_module_for_day(self, day_num: int) -> Optional[Dict[str, Any]]:
        for mod in self.curriculum.get("modules", []):
            if day_num in mod.get("days", []):
                return mod
            # Also check ranges if day_num falls between min and max
            days_range = mod.get("days", [])
            if len(days_range) == 2 and days_range[0] <= day_num <= days_range[1]:
                return mod
        return None

    def get_all_candidates(self) -> List[Dict[str, Any]]:
        return self.candidates

    def get_curriculum(self) -> List[Dict[str, Any]]:
        return self.curriculum.get("days", [])

# Global instance for easy access
data_loader = DataLoader()

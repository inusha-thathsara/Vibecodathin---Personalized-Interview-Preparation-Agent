from typing import Dict, Any, List
from data.loader import data_loader

def _get_signal_count(val: Any) -> int:
    if isinstance(val, int):
        return val
    elif isinstance(val, (list, set, tuple)):
        return len(val)
    return 0

class CandidateAnalyzer:
    @staticmethod
    def analyze(candidate: Dict[str, Any]) -> Dict[str, Any]:
        member = candidate.get("member", {})
        missions = candidate.get("missions", [])
        signals = candidate.get("signals", {})

        name = member.get("name", "Candidate")
        job_role = member.get("jobRole", "Software Engineer")
        years_exp = member.get("yearsExperience", 0.0)
        education = member.get("education", "")

        commit_count = _get_signal_count(signals.get("commitDays", 0))
        first_try_count = _get_signal_count(signals.get("missionsFirstTry", 0))
        completion_count = _get_signal_count(signals.get("missionsCompleted", 0))

        # Compute engagement score (0.0 to 1.0)
        commit_score = min(0.3, commit_count * 0.015)
        completion_score = min(0.4, completion_count / 31.0 * 0.4)
        first_try_score = min(0.3, first_try_count / 31.0 * 0.3)
        engagement_score = round(min(1.0, commit_score + completion_score + first_try_score), 2)

        first_try_days: List[int] = []
        struggle_days: List[int] = []
        failed_days: List[int] = []
        skipped_days: List[int] = []

        mission_details: Dict[int, Dict[str, Any]] = {}
        summary_lines: List[str] = []

        for m in missions:
            day = m.get("day")
            if not day:
                continue

            day_info = data_loader.get_day_info(day)
            day_title = day_info.get("title") if day_info else m.get("name", f"Day {day}")
            attempts = m.get("attempts", 1)
            passed = m.get("passed", False)
            skipped = m.get("skipped", False)

            mission_details[day] = {
                "day": day,
                "title": day_title,
                "passed": passed,
                "attempts": attempts,
                "skipped": skipped,
                "tools": day_info.get("tools", []) if day_info else [],
                "objectives": day_info.get("objectives", []) if day_info else []
            }

            if skipped:
                skipped_days.append(day)
                summary_lines.append(f"- Day {day} ({day_title}): Skipped")
            elif passed:
                if attempts == 1:
                    first_try_days.append(day)
                    summary_lines.append(f"- Day {day} ({day_title}): Passed on 1st attempt (Strength)")
                elif attempts >= 3:
                    struggle_days.append(day)
                    summary_lines.append(f"- Day {day} ({day_title}): Passed after {attempts} attempts (Struggle area)")
                else:
                    summary_lines.append(f"- Day {day} ({day_title}): Passed after {attempts} attempts")
            elif passed is False:
                failed_days.append(day)
                summary_lines.append(f"- Day {day} ({day_title}): Failed")

        # Difficulty calibration
        if years_exp >= 10:
            difficulty = "senior"
        elif years_exp >= 3:
            difficulty = "intermediate"
        else:
            difficulty = "foundational"

        # Select target days to cover
        target_days: List[int] = []

        if engagement_score < 0.5:
            for day in struggle_days + failed_days + skipped_days:
                if day not in target_days:
                    target_days.append(day)
            for day in first_try_days:
                if day not in target_days:
                    target_days.append(day)
        else:
            for day in struggle_days + failed_days:
                if day not in target_days:
                    target_days.append(day)
            for day in first_try_days:
                if day not in target_days:
                    target_days.append(day)
            for day in skipped_days:
                if day not in target_days:
                    target_days.append(day)

        core_milestone_days = [7, 8, 10, 11, 12, 16, 22, 23, 28, 31]
        for day in core_milestone_days:
            if day not in target_days and data_loader.get_day_info(day):
                target_days.append(day)

        mission_summary = "\n".join(summary_lines) if summary_lines else "No specific mission attempt data recorded."

        return {
            "name": name,
            "jobRole": job_role,
            "yearsExperience": years_exp,
            "education": education,
            "difficulty": difficulty,
            "engagement_score": engagement_score,
            "signals": signals,
            "first_try_days": first_try_days,
            "struggle_days": struggle_days,
            "failed_days": failed_days,
            "skipped_days": skipped_days,
            "target_days": target_days,
            "mission_details": mission_details,
            "mission_summary": mission_summary
        }

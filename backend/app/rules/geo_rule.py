import math
from datetime import datetime
from typing import Dict, Any, Optional
from app.rules.base_rule import FraudRule, RuleResult
from app.config import settings


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in kilometers
    using the Haversine formula.
    """
    # Earth radius in kilometers
    R = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


class GeoLocationRule(FraudRule):
    """
    Detects impossible geographical travel between consecutive transactions for the same account.
    Example: 10:00 AM Hyderabad -> 10:05 AM London (> 7,000 km in 5 mins = >84,000 km/h).
    """
    def __init__(
        self,
        max_speed_kmph: float = settings.MAX_REALISTIC_SPEED_KMPH,
        score: int = settings.GEO_SCORE
    ):
        self.name = "IMPOSSIBLE_LOCATION"
        self.description = f"Flags consecutive transactions requiring physical speed exceeding {max_speed_kmph} km/h."
        self.max_speed_kmph = float(max_speed_kmph)
        self.default_score = score

    def evaluate(self, transaction: Any, context: Dict[str, Any]) -> RuleResult:
        last_txn = context.get("last_transaction")

        # If no previous transaction exists for this account, impossible travel cannot be determined
        if not last_txn:
            return RuleResult(
                rule_name=self.name,
                triggered=False,
                score_contribution=0,
                reason="First recorded transaction for account. No prior geo baseline available.",
                details={"prior_transaction": False}
            )

        # Get coordinates
        lat1, lon1 = float(last_txn.latitude), float(last_txn.longitude)
        lat2, lon2 = float(transaction.latitude), float(transaction.longitude)
        
        # Calculate Haversine distance
        distance_km = haversine_distance_km(lat1, lon1, lat2, lon2)

        # Get timestamps
        t1 = last_txn.timestamp if isinstance(last_txn.timestamp, datetime) else datetime.fromisoformat(str(last_txn.timestamp))
        t2 = transaction.timestamp if isinstance(transaction.timestamp, datetime) else datetime.fromisoformat(str(transaction.timestamp))

        # Time difference in hours and minutes
        time_diff_seconds = abs((t2 - t1).total_seconds())
        time_diff_hours = time_diff_seconds / 3600.0
        time_diff_minutes = time_diff_seconds / 60.0

        # Disregard small jitter under 10 km
        if distance_km < 10.0:
            return RuleResult(
                rule_name=self.name,
                triggered=False,
                score_contribution=0,
                reason=f"Transactions within close proximity ({distance_km:.1f} km).",
                details={
                    "distance_km": round(distance_km, 2),
                    "time_diff_minutes": round(time_diff_minutes, 2)
                }
            )

        # Compute speed
        if time_diff_hours <= 0.001:  # Near 0 seconds
            speed_kmph = 99999.0
        else:
            speed_kmph = distance_km / time_diff_hours

        last_loc = getattr(last_txn, "location", f"({lat1}, {lon1})")
        curr_loc = getattr(transaction, "location", f"({lat2}, {lon2})")

        if speed_kmph > self.max_speed_kmph:
            reason = (
                f"Impossible travel violation: Account moved {distance_km:,.1f} km from '{last_loc}' to '{curr_loc}' "
                f"in {time_diff_minutes:.1f} minutes, requiring an impossible speed of {speed_kmph:,.1f} km/h "
                f"(Realistic limit: {self.max_speed_kmph} km/h)."
            )
            return RuleResult(
                rule_name=self.name,
                triggered=True,
                score_contribution=self.default_score,
                reason=reason,
                details={
                    "distance_km": round(distance_km, 2),
                    "time_diff_minutes": round(time_diff_minutes, 2),
                    "calculated_speed_kmph": round(speed_kmph, 2),
                    "max_speed_kmph": self.max_speed_kmph,
                    "from_location": last_loc,
                    "to_location": curr_loc
                }
            )

        return RuleResult(
            rule_name=self.name,
            triggered=False,
            score_contribution=0,
            reason=f"Travel speed realistic ({speed_kmph:,.1f} km/h <= {self.max_speed_kmph} km/h for {distance_km:,.1f} km in {time_diff_minutes:.1f}m).",
            details={
                "distance_km": round(distance_km, 2),
                "time_diff_minutes": round(time_diff_minutes, 2),
                "calculated_speed_kmph": round(speed_kmph, 2)
            }
        )

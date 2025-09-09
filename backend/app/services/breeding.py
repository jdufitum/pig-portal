from __future__ import annotations

from datetime import date, timedelta
from typing import Optional


def compute_expected_farrow(service_date: Optional[date], provided: Optional[date] = None) -> Optional[date]:
    if provided is not None:
        return provided
    if service_date is None:
        return None
    return service_date + timedelta(days=114)


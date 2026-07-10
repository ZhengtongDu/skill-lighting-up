#!/usr/bin/env python3
import argparse
import json
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def parse_date(value: str | None) -> date:
    if not value:
        return datetime.now(ZoneInfo("Asia/Shanghai")).date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def week_info(day: date) -> dict:
    start = day - timedelta(days=day.weekday())
    end = start + timedelta(days=6)
    prev_start = start - timedelta(days=7)
    prev_end = start - timedelta(days=1)
    return {
        "date": day.isoformat(),
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "week_end_plus_1": (end + timedelta(days=1)).isoformat(),
        "week_id": f"{start:%y%m%d}-{end:%y%m%d}",
        "previous_week_start": prev_start.isoformat(),
        "previous_week_end": prev_end.isoformat(),
        "previous_week_id": f"{prev_start:%y%m%d}-{prev_end:%y%m%d}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Date in YYYY-MM-DD. Defaults to today in Asia/Shanghai.")
    args = parser.parse_args()
    print(json.dumps(week_info(parse_date(args.date)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

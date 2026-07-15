#!/usr/bin/env python3
"""Download, validate, normalize, and version Google Sheets lotto data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXPECTED_HEADERS = ["draw", "date", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"]
KST = timezone(timedelta(hours=9))


@dataclass(frozen=True)
class LottoRow:
    draw: int
    date: str
    numbers: tuple[int, int, int, int, int, int]
    bonus: int


def download_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "lotto-pattern-lab-sync/1.0",
            "Accept": "text/csv,text/plain;q=0.9,*/*;q=0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        content_type = response.headers.get("Content-Type", "")

    text = raw.decode("utf-8-sig")

    # Google may return an HTML permission page instead of CSV.
    lowered = text[:500].lower()
    if "<html" in lowered or "<!doctype" in lowered:
        raise ValueError(
            "Google Sheets returned HTML instead of CSV. "
            "Confirm that the sheet is publicly viewable."
        )

    if "csv" not in content_type.lower() and not text.lstrip().startswith("draw,"):
        raise ValueError(f"Unexpected response type: {content_type or 'unknown'}")

    return text


def read_source(source_file: Path | None, source_url: str) -> str:
    if source_file is not None:
        return source_file.read_text(encoding="utf-8-sig")
    return download_text(source_url)


def parse_and_validate(text: str) -> list[LottoRow]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("CSV header is missing.")

    headers = [header.strip().lstrip("\ufeff") for header in reader.fieldnames]
    if headers != EXPECTED_HEADERS:
        raise ValueError(
            "CSV headers do not match. "
            f"Expected {EXPECTED_HEADERS}, received {headers}"
        )

    rows: list[LottoRow] = []
    seen_draws: set[int] = set()

    for line_no, raw in enumerate(reader, start=2):
        if not any((value or "").strip() for value in raw.values()):
            continue

        try:
            draw = int(raw["draw"].strip())
            date_text = raw["date"].strip()
            draw_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            numbers = tuple(int(raw[f"n{i}"].strip()) for i in range(1, 7))
            bonus = int(raw["bonus"].strip())
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Line {line_no}: invalid value ({exc})") from exc

        if draw < 1:
            raise ValueError(f"Line {line_no}: draw must be positive.")
        if draw in seen_draws:
            raise ValueError(f"Line {line_no}: duplicate draw {draw}.")
        seen_draws.add(draw)

        if len(set(numbers)) != 6:
            raise ValueError(f"Line {line_no}: main numbers contain duplicates.")
        if any(number < 1 or number > 45 for number in numbers):
            raise ValueError(f"Line {line_no}: main number outside 1..45.")
        if bonus < 1 or bonus > 45:
            raise ValueError(f"Line {line_no}: bonus outside 1..45.")
        if bonus in numbers:
            raise ValueError(f"Line {line_no}: bonus duplicates a main number.")

        # Official history begins on 2002-12-07. This also catches malformed dates.
        if draw_date < datetime(2002, 12, 7).date():
            raise ValueError(f"Line {line_no}: draw date is earlier than Lotto 6/45 history.")

        rows.append(
            LottoRow(
                draw=draw,
                date=date_text,
                numbers=tuple(sorted(numbers)),
                bonus=bonus,
            )
        )

    if not rows:
        raise ValueError("CSV contains no lotto rows.")

    rows.sort(key=lambda item: item.draw)

    expected_draws = list(range(1, rows[-1].draw + 1))
    actual_draws = [row.draw for row in rows]
    if actual_draws != expected_draws:
        missing = sorted(set(expected_draws) - set(actual_draws))
        raise ValueError(f"Draw sequence is not continuous. Missing: {missing[:20]}")

    for previous, current in zip(rows, rows[1:]):
        previous_date = datetime.strptime(previous.date, "%Y-%m-%d").date()
        current_date = datetime.strptime(current.date, "%Y-%m-%d").date()
        if current_date <= previous_date:
            raise ValueError(
                f"Draw dates are not increasing: {previous.draw} -> {current.draw}"
            )

    return rows


def existing_latest_draw(csv_path: Path) -> int | None:
    if not csv_path.exists():
        return None
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return max(int(row["draw"]) for row in rows)
    except Exception:
        return None


def normalized_csv(rows: list[LottoRow]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(EXPECTED_HEADERS)
    for row in rows:
        writer.writerow([row.draw, row.date, *row.numbers, row.bonus])
    return buffer.getvalue()


def write_outputs(rows: list[LottoRow], output_dir: Path, source_url: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "lotto_history.csv"
    meta_path = output_dir / "meta.json"

    previous_latest = existing_latest_draw(csv_path)
    latest = rows[-1]

    if previous_latest is not None and latest.draw < previous_latest:
        raise ValueError(
            f"Refusing regression: existing latest draw is {previous_latest}, "
            f"downloaded latest draw is {latest.draw}."
        )

    csv_text = normalized_csv(rows)
    digest = hashlib.sha256(csv_text.encode("utf-8")).hexdigest()
    synced_at = datetime.now(KST).replace(microsecond=0).isoformat()

    csv_path.write_text(csv_text, encoding="utf-8")
    meta = {
        "source": "Google Sheets",
        "source_url": source_url,
        "sheet_id": "1w1AZshic7KGnbb0lqjfg_aUx5F9RzGBtJykFJuaP-lM",
        "gid": "0",
        "validation": "passed",
        "row_count": len(rows),
        "first_draw": rows[0].draw,
        "latest_draw": latest.draw,
        "latest_date": latest.date,
        "synced_at_kst": synced_at,
        "sha256": digest,
    }
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Validated {len(rows)} draws. "
        f"Latest: {latest.draw} ({latest.date}). SHA-256: {digest[:12]}..."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-url",
        default=os.environ.get(
            "SHEET_CSV_URL",
            "https://docs.google.com/spreadsheets/d/"
            "1w1AZshic7KGnbb0lqjfg_aUx5F9RzGBtJykFJuaP-lM/"
            "export?format=csv&gid=0",
        ),
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        help="Local CSV for testing instead of downloading.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
    )
    args = parser.parse_args()

    try:
        text = read_source(args.source_file, args.source_url)
        rows = parse_and_validate(text)
        write_outputs(rows, args.output_dir, args.source_url)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

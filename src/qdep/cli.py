from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from .extract import load_html, extract_cards
from .transform import transform
from .validate import partition_valid
from .export import write_json, write_csv
from .report import compute_stats, render_summary, write_summary
from .log import RunLogger, utc_now


def sha256_of_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="qdep",
        description="Offline HTML data extraction mini-pipeline (deterministic outputs).",
    )
    p.add_argument("--input", required=True, help="Path to local HTML file (fixture).")
    p.add_argument("--outdir", required=True, help="Output directory.")
    p.add_argument(
        "--realtime",
        action="store_true",
        help="Use real UTC timestamps in summary/log (breaks strict determinism).",
    )
    return p.parse_args(argv)


def run_pipeline(input_path: Path, outdir: Path, realtime: bool) -> tuple[int, int, int]:
    outdir.mkdir(parents=True, exist_ok=True)

    log_path = outdir / "run.log"
    logger = RunLogger(log_path=log_path, realtime=realtime)
    logger.start(input_path=input_path, outdir=outdir)

    html = load_html(input_path)
    input_hash = sha256_of_text(html)

    raw_cards = extract_cards(html)
    extracted_count = len(raw_cards)
    logger.info(f"extracted_cards={extracted_count}")

    products = [transform(c) for c in raw_cards]
    valid, invalid = partition_valid(products)

    valid_count = len(valid)
    invalid_count = len(invalid)

    logger.counts(extracted=extracted_count, valid=valid_count, invalid=invalid_count)
    if invalid:
        brief = [f"{e.id}: {', '.join(e.errors)}" for e in invalid]
        logger.validation_errors(brief)

    ts = utc_now(realtime).isoformat().replace("+00:00", "Z")

    # Outputs
    json_path = outdir / "output.json"
    csv_path = outdir / "output.csv"
    summary_path = outdir / "summary.txt"

    meta = {
        "input_path": str(input_path),
        "input_sha256": input_hash,
        "timestamp_utc": ts,
        "deterministic": (not realtime),
    }

    write_json(json_path, valid=valid, invalid=invalid, meta=meta)
    write_csv(csv_path, valid=valid)

    stats = compute_stats(extracted_count=extracted_count, valid=valid, invalid_count=invalid_count)
    summary = render_summary(timestamp_utc=ts, stats=stats)
    write_summary(summary_path, summary)

    logger.end()
    logger.write()

    return extracted_count, valid_count, invalid_count


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    input_path = Path(ns.input).resolve()
    outdir = Path(ns.outdir).resolve()

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    run_pipeline(input_path=input_path, outdir=outdir, realtime=bool(ns.realtime))

    # Clean deterministic terminal output (no timestamps)
    print(f"OK extracted={len(extract_cards(load_html(input_path)))} outdir={outdir}")
    return 0
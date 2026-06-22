#!/usr/bin/env python3
"""Deterministic helpers for the ad-image-localization Codex skill.

These helpers intentionally do not generate or translate images. Use Codex built-in
image generation/editing for native creative work, then use this script for
repeatable last-mile operations: safe cover-crop, manifests, verification,
contact sheets, cultural-aware flagging, and terminology memory edits.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover - exercised only on missing dependency.
    Image = None
    ImageDraw = None
    ImageFont = None
    ImageOps = None


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
RESAMPLE_LANCZOS = getattr(getattr(Image, "Resampling", Image), "LANCZOS", None) if Image else None
SIZE_RE = re.compile(r"^(\d+)x(\d+)$")
DATE_RE = re.compile(r"^\d{8}$")
LANG_RE = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]+)?$", re.IGNORECASE)
CREATIVE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$", re.IGNORECASE)


def require_pillow() -> None:
    if Image is None:
        raise SystemExit(
            "This helper requires Pillow. In Codex, use the bundled Python runtime "
            "when available; outside Codex, run: python -m pip install pillow"
        )


def parse_size(value: str) -> tuple[int, int]:
    match = SIZE_RE.match(value.lower())
    if not match:
        raise argparse.ArgumentTypeError("size must use WIDTHxHEIGHT, e.g. 1200x628")
    width, height = int(match.group(1)), int(match.group(2))
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("width and height must be positive")
    return width, height


def image_files(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTS
        and not path.name.startswith("qa_contact_sheet")
    )


def parse_delivery_name(path: Path) -> dict[str, Any]:
    """Parse <creative>_<lang>_<width>x<height>_<yyyymmdd>.<ext>.

    The creative slug may contain underscores; parsing works from the right.
    """

    parts = path.stem.rsplit("_", 3)
    result: dict[str, Any] = {
        "creative": None,
        "language": None,
        "expected_width": None,
        "expected_height": None,
        "date": None,
        "filename_valid": False,
        "filename_issues": [],
    }
    if len(parts) != 4:
        result["filename_issues"].append(
            "filename must be <creative>_<language>_<width>x<height>_<yyyymmdd>"
        )
        return result

    creative, language, size_text, date_text = parts
    result["creative"] = creative
    result["language"] = language.lower()
    result["date"] = date_text

    if not CREATIVE_RE.match(creative):
        result["filename_issues"].append("creative slug should use English letters, digits, hyphen, or underscore")
    if not LANG_RE.match(language):
        result["filename_issues"].append("language should be a short locale code such as en, de, ja, ar, pt-br")
    size_match = SIZE_RE.match(size_text.lower())
    if size_match:
        result["expected_width"] = int(size_match.group(1))
        result["expected_height"] = int(size_match.group(2))
    else:
        result["filename_issues"].append("resolution should use WIDTHxHEIGHT")
    if not DATE_RE.match(date_text):
        result["filename_issues"].append("date should use yyyymmdd")

    result["filename_valid"] = not result["filename_issues"]
    return result


def inspect_image(path: Path) -> tuple[int, int]:
    require_pillow()
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        return image.size


def analyze_file(path: Path, default_status: str = "pending_visual_qa") -> dict[str, Any]:
    parsed = parse_delivery_name(path)
    issues = list(parsed["filename_issues"])
    width = height = None

    try:
        width, height = inspect_image(path)
    except Exception as exc:  # noqa: BLE001 - surface file-specific issue.
        issues.append(f"cannot read image: {exc}")

    expected_width = parsed["expected_width"]
    expected_height = parsed["expected_height"]
    if width and height and expected_width and expected_height:
        if (width, height) != (expected_width, expected_height):
            issues.append(
                f"dimension mismatch: file is {width}x{height}, filename says {expected_width}x{expected_height}"
            )

    qa_status = "needs_review" if issues else default_status
    return {
        "file": path.name,
        "creative": parsed["creative"],
        "language": parsed["language"],
        "resolution": f"{width}x{height}" if width and height else None,
        "expected_resolution": (
            f"{expected_width}x{expected_height}" if expected_width and expected_height else None
        ),
        "date": parsed["date"],
        "qa_status": qa_status,
        "issues": issues,
    }


def crop_offsets(
    resized_width: int,
    resized_height: int,
    target_width: int,
    target_height: int,
    gravity: str,
) -> tuple[int, int]:
    x_overflow = resized_width - target_width
    y_overflow = resized_height - target_height

    if "west" in gravity:
        left = 0
    elif "east" in gravity:
        left = x_overflow
    else:
        left = x_overflow // 2

    if "north" in gravity:
        top = 0
    elif "south" in gravity:
        top = y_overflow
    else:
        top = y_overflow // 2

    return max(0, left), max(0, top)


def command_cover_crop(args: argparse.Namespace) -> int:
    require_pillow()
    source = Path(args.input)
    output = Path(args.output)
    target_width, target_height = args.size

    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        source_width, source_height = image.size
        scale = max(target_width / source_width, target_height / source_height)
        resized_width = round(source_width * scale)
        resized_height = round(source_height * scale)
        left, top = crop_offsets(
            resized_width, resized_height, target_width, target_height, args.gravity
        )
        crop_box = (left, top, left + target_width, top + target_height)

        plan = {
            "input": str(source),
            "output": str(output),
            "source_size": f"{source_width}x{source_height}",
            "target_size": f"{target_width}x{target_height}",
            "scale": scale,
            "resized_size": f"{resized_width}x{resized_height}",
            "crop_box": crop_box,
            "gravity": args.gravity,
            "non_uniform_resize": False,
            "blur_padding": False,
        }

        if args.dry_run:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return 0

        resized = image.resize((resized_width, resized_height), RESAMPLE_LANCZOS)
        cropped = resized.crop(crop_box)
        output.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs: dict[str, Any] = {}
        suffix = output.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            cropped = cropped.convert("RGB")
            save_kwargs["quality"] = args.quality
            save_kwargs["optimize"] = True
        elif suffix == ".webp":
            save_kwargs["quality"] = args.quality
        cropped.save(output, **save_kwargs)

    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


def command_manifest(args: argparse.Namespace) -> int:
    folder = Path(args.folder)
    output = Path(args.output) if args.output else folder / "manifest.json"
    items = [analyze_file(path, args.qa_status) for path in image_files(folder)]
    manifest = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "folder": str(folder),
        "items": items,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output} with {len(items)} items.")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    folder = Path(args.folder)
    items = [analyze_file(path, args.qa_status) for path in image_files(folder)]
    failed = [item for item in items if item["issues"]]
    summary = {
        "folder": str(folder),
        "total": len(items),
        "passed": len(items) - len(failed),
        "failed": len(failed),
        "items": items,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Checked {summary['total']} image(s): {summary['passed']} passed, {summary['failed']} failed.")
        for item in failed:
            print(f"- {item['file']}")
            for issue in item["issues"]:
                print(f"  - {issue}")
    return 1 if failed and not args.no_fail else 0


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}__flagged-{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def cultural_scope_files(folder: Path, selected: list[Path], scope: str) -> list[Path]:
    if scope == "selected":
        return selected

    scoped: dict[Path, None] = {path: None for path in selected}
    all_files = image_files(folder)
    for path in selected:
        parsed = parse_delivery_name(path)
        creative = parsed.get("creative")
        language = parsed.get("language")
        date = parsed.get("date")
        if not creative or not language or not date:
            continue
        for candidate in all_files:
            candidate_parsed = parse_delivery_name(candidate)
            if (
                candidate_parsed.get("creative") == creative
                and candidate_parsed.get("language") == language
                and candidate_parsed.get("date") == date
            ):
                scoped[candidate] = None
    return sorted(scoped)


def command_flag_cultural(args: argparse.Namespace) -> int:
    folder = Path(args.folder)
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    selected = []
    for file_name in args.files:
        path = Path(file_name)
        if not path.is_absolute():
            path = folder / path
        path = path.resolve()
        try:
            path.relative_to(folder.resolve())
        except ValueError as exc:
            raise SystemExit(f"Refusing to move file outside folder: {file_name}") from exc
        if not path.exists() or not path.is_file():
            raise SystemExit(f"File not found: {path}")
        if path.suffix.lower() not in IMAGE_EXTS:
            raise SystemExit(f"Not an image file: {path}")
        selected.append(path)

    files = cultural_scope_files(folder.resolve(), selected, args.scope)
    destination_folder = folder / args.destination
    records = []
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    for source in files:
        destination = unique_destination(destination_folder / source.name)
        record = {
            "file": destination.name,
            "original_file": source.name,
            "market": args.market,
            "reason": args.reason,
            "source_path": str(source),
            "destination_path": str(destination),
            "flagged_at": now,
        }
        records.append(record)
        if not args.dry_run:
            destination_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))

    if not args.dry_run:
        log_path = destination_folder / "cultural_aware_flags.json"
        existing = []
        if log_path.exists():
            existing = json.loads(log_path.read_text(encoding="utf-8"))
        existing.extend(records)
        log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "folder": str(folder),
        "destination": str(destination_folder),
        "scope": args.scope,
        "dry_run": args.dry_run,
        "flagged": records,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_font(size: int, bold: bool = False) -> Any:
    require_pillow()
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def command_contact_sheet(args: argparse.Namespace) -> int:
    require_pillow()
    folder = Path(args.folder)
    output = Path(args.output)
    thumb_width, thumb_height = args.thumb_size
    files = image_files(folder)
    if not files:
        raise SystemExit(f"No image files found in {folder}")

    cols = max(1, args.cols)
    rows = (len(files) + cols - 1) // cols
    padding = 24
    label_height = 58
    cell_width = thumb_width + padding * 2
    cell_height = thumb_height + label_height + padding * 2
    sheet = Image.new("RGB", (cell_width * cols, cell_height * rows), args.background)
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(18, bold=True)
    meta_font = load_font(14)

    for index, path in enumerate(files):
        col = index % cols
        row = index // cols
        x = col * cell_width + padding
        y = row * cell_height + padding
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            original_size = image.size
            image.thumbnail((thumb_width, thumb_height), RESAMPLE_LANCZOS)
            thumb_x = x + (thumb_width - image.width) // 2
            thumb_y = y + (thumb_height - image.height) // 2
            draw.rounded_rectangle(
                (x - 8, y - 8, x + thumb_width + 8, y + thumb_height + 8),
                radius=14,
                fill="#ffffff",
                outline="#d7deea",
            )
            sheet.paste(image, (thumb_x, thumb_y))
        label_y = y + thumb_height + 18
        draw.text((x, label_y), path.name[:44], fill="#1f2937", font=label_font)
        draw.text(
            (x, label_y + 25),
            f"{original_size[0]}x{original_size[1]}",
            fill="#64748b",
            font=meta_font,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() in {".jpg", ".jpeg"}:
        sheet.save(output, quality=args.quality, optimize=True)
    else:
        sheet.save(output)
    print(f"Wrote {output} for {len(files)} image(s).")
    return 0


def load_memory(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"version": 1, "brands": {}}


def command_memory_add(args: argparse.Namespace) -> int:
    path = Path(args.memory_file)
    memory = load_memory(path)
    brands = memory.setdefault("brands", {})
    brand = brands.setdefault(
        args.brand,
        {"display_name": args.brand_display or args.brand, "rules": [], "products": {}},
    )
    if args.brand_display:
        brand["display_name"] = args.brand_display

    target = brand
    if args.product:
        products = brand.setdefault("products", {})
        target = products.setdefault(
            args.product,
            {"display_name": args.product_display or args.product, "rules": []},
        )
        if args.product_display:
            target["display_name"] = args.product_display

    rule = {
        "term": args.term,
        "action": args.action,
    }
    if args.translation:
        rule["translation"] = args.translation
    if args.notes:
        rule["notes"] = args.notes

    rules = target.setdefault("rules", [])
    existing = next((item for item in rules if item.get("term") == args.term), None)
    if existing:
        existing.update(rule)
    else:
        rules.append(rule)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scope = f"{args.brand}/{args.product}" if args.product else args.brand
    print(f"Saved terminology rule for {scope}: {args.term} -> {args.action}")
    return 0


def command_memory_list(args: argparse.Namespace) -> int:
    path = Path(args.memory_file)
    print(json.dumps(load_memory(path), ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic last-mile helpers for ad-image-localization outputs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    cover = subparsers.add_parser("cover-crop", help="Aspect-preserving resize and crop.")
    cover.add_argument("input")
    cover.add_argument("output")
    cover.add_argument("--size", type=parse_size, required=True, help="Target size, e.g. 1200x628.")
    cover.add_argument(
        "--gravity",
        choices=[
            "center",
            "north",
            "south",
            "east",
            "west",
            "northwest",
            "northeast",
            "southwest",
            "southeast",
        ],
        default="center",
        help="Crop anchor. Use north/south/east/west when QA shows safer empty space.",
    )
    cover.add_argument("--quality", type=int, default=95)
    cover.add_argument("--dry-run", action="store_true")
    cover.set_defaults(func=command_cover_crop)

    manifest = subparsers.add_parser("manifest", help="Write manifest.json for a folder.")
    manifest.add_argument("folder")
    manifest.add_argument("--output", help="Defaults to <folder>/manifest.json.")
    manifest.add_argument("--qa-status", default="pending_visual_qa")
    manifest.set_defaults(func=command_manifest)

    verify = subparsers.add_parser("verify", help="Check filenames and dimensions.")
    verify.add_argument("folder")
    verify.add_argument("--qa-status", default="ok")
    verify.add_argument("--json", action="store_true")
    verify.add_argument("--no-fail", action="store_true", help="Return 0 even if issues are found.")
    verify.set_defaults(func=command_verify)

    sheet = subparsers.add_parser("contact-sheet", help="Create a visual QA contact sheet.")
    sheet.add_argument("folder")
    sheet.add_argument("output")
    sheet.add_argument("--cols", type=int, default=4)
    sheet.add_argument("--thumb-size", type=parse_size, default=parse_size("280x180"))
    sheet.add_argument("--background", default="#f7f8fb")
    sheet.add_argument("--quality", type=int, default=92)
    sheet.set_defaults(func=command_contact_sheet)

    cultural = subparsers.add_parser(
        "flag-cultural",
        help="Move culturally sensitive outputs into a review folder without editing them.",
    )
    cultural.add_argument("folder")
    cultural.add_argument("files", nargs="+", help="Image file names or paths to flag.")
    cultural.add_argument("--destination", default="Flagged by Cultural Aware")
    cultural.add_argument("--market", default="unspecified")
    cultural.add_argument("--reason", required=True)
    cultural.add_argument(
        "--scope",
        choices=["variant", "selected"],
        default="variant",
        help="variant moves all sizes with the same creative/language/date; selected moves only named files.",
    )
    cultural.add_argument("--dry-run", action="store_true")
    cultural.set_defaults(func=command_flag_cultural)

    mem_add = subparsers.add_parser("memory-add", help="Add or update a terminology memory rule.")
    mem_add.add_argument("memory_file")
    mem_add.add_argument("--brand", required=True, help="Brand slug, e.g. openai.")
    mem_add.add_argument("--brand-display")
    mem_add.add_argument("--product", help="Optional product slug, e.g. codex.")
    mem_add.add_argument("--product-display")
    mem_add.add_argument("--term", required=True)
    mem_add.add_argument("--action", choices=["preserve", "translate"], required=True)
    mem_add.add_argument("--translation")
    mem_add.add_argument("--notes")
    mem_add.set_defaults(func=command_memory_add)

    mem_list = subparsers.add_parser("memory-list", help="Print terminology memory JSON.")
    mem_list.add_argument("memory_file")
    mem_list.set_defaults(func=command_memory_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

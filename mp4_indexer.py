#!/usr/bin/env python3
"""Scan a directory for MP4 files and generate a JSON index.

输出字段：
- filename: 文件名
- size_bytes: 文件大小（字节）
- duration_seconds: 时长（秒，浮点数）
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def get_duration_seconds(file_path: Path) -> float:
    """Use ffprobe to get media duration in seconds."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise RuntimeError("未找到 ffprobe，请先安装 FFmpeg（包含 ffprobe）")

    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()
    return float(output)


def find_mp4_files(directory: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.mp4" if recursive else "*.mp4"
    return sorted(p for p in directory.glob(pattern) if p.is_file())


def build_index(directory: Path, recursive: bool) -> list[dict[str, object]]:
    mp4_files = find_mp4_files(directory, recursive)
    index: list[dict[str, object]] = []

    for file_path in mp4_files:
        index.append(
            {
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "duration_seconds": round(get_duration_seconds(file_path), 3),
            }
        )

    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="读取目录中的 MP4 并生成 JSON 索引")
    parser.add_argument("directory", type=Path, help="要扫描的目录")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("mp4_index.json"),
        help="输出 JSON 文件路径（默认: mp4_index.json）",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="是否递归扫描子目录",
    )

    args = parser.parse_args()

    if not args.directory.exists() or not args.directory.is_dir():
        raise SystemExit(f"目录不存在或不是目录: {args.directory}")

    index_data = build_index(args.directory, args.recursive)

    args.output.write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"已生成索引: {args.output}（共 {len(index_data)} 个 mp4 文件）")


if __name__ == "__main__":
    main()

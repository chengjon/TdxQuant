from __future__ import annotations

from dataclasses import dataclass

from .models import ErrorCode, Result

BLOCK_SNAPSHOT_SOURCE = "tongdaxin.custom_sector"


@dataclass(slots=True)
class BlockSnapshotRequest:
    block_code: str
    sector_name: str | None = None
    member_codes: list[str] | None = None


def _normalize_member_code(raw_member: str) -> str | None:
    code = str(raw_member).strip()
    if len(code) != 6 or not code.isdigit():
        return None
    if code[0] in {"0", "1", "2", "3"}:
        return f"{code}.SZ"
    if code[0] in {"5", "6", "9"}:
        return f"{code}.SH"
    return None


def normalize_block_snapshot(request: BlockSnapshotRequest) -> Result:
    block_code = str(request.block_code).strip()
    if not block_code:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="block snapshot requires a non-blank block_code",
        )

    sector_name = "" if request.sector_name is None else str(request.sector_name)
    raw_members = list(request.member_codes or [])
    symbols: list[str] = []
    seen: set[str] = set()
    duplicate_count = 0

    for raw_member in raw_members:
        symbol = _normalize_member_code(str(raw_member))
        if symbol is None:
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message=f"block snapshot contains non-normalizable member code: {raw_member}",
            )
        if symbol in seen:
            duplicate_count += 1
            continue
        seen.add(symbol)
        symbols.append(symbol)

    warnings: list[str] = []
    if duplicate_count:
        warnings.append(f"Deduplicated {duplicate_count} repeated members in block {block_code}")

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="normalized block snapshot",
        data={
            "block_code": block_code,
            "symbols": symbols,
            "symbol_count": len(symbols),
            "source": BLOCK_SNAPSHOT_SOURCE,
            "source_metadata": {
                "sector_name": sector_name,
                "raw_member_count": len(raw_members),
                "duplicate_count": duplicate_count,
            },
        },
        warnings=warnings,
    )

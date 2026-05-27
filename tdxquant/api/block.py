from __future__ import annotations

from ..models import Result
from .bridge import (
    run_tdx_block_sync,
    run_tdx_block_read_watchlist_snapshot,
    run_tdx_clear_sector,
    run_tdx_create_sector,
    run_tdx_delete_sector,
    run_tdx_get_user_sector,
    run_tdx_rename_sector,
    run_tdx_send_user_block,
)


class BlockApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def user_sectors(self) -> Result:
        return run_tdx_get_user_sector(strategy_path=self.strategy_path)

    def read_watchlist_snapshot(self, block_code: str) -> Result:
        return run_tdx_block_read_watchlist_snapshot(block_code=block_code, strategy_path=self.strategy_path)

    def create_sector(
        self,
        block_code: str,
        block_name: str,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        return run_tdx_create_sector(
            block_code=block_code,
            block_name=block_name,
            **options,
            strategy_path=self.strategy_path,
        )

    def delete_sector(self, block_code: str, mutation_key: str | None = None, audit_dir: str | None = None) -> Result:
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        return run_tdx_delete_sector(
            block_code=block_code,
            **options,
            strategy_path=self.strategy_path,
        )

    def rename_sector(
        self,
        block_code: str,
        block_name: str,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        return run_tdx_rename_sector(
            block_code=block_code,
            block_name=block_name,
            **options,
            strategy_path=self.strategy_path,
        )

    def clear_sector(self, block_code: str, mutation_key: str | None = None, audit_dir: str | None = None) -> Result:
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        return run_tdx_clear_sector(
            block_code=block_code,
            **options,
            strategy_path=self.strategy_path,
        )

    def send_user_block(
        self,
        block_code: str,
        stocks: list[str],
        show: bool,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        return run_tdx_send_user_block(
            block_code=block_code,
            stocks=stocks,
            show=show,
            **options,
            strategy_path=self.strategy_path,
        )

    def sync_watchlist(
        self,
        block_code: str,
        symbols: list[str],
        mode: str = "replace",
        create_if_missing: bool = False,
        dry_run: bool = False,
        show: bool = True,
        write_policy: str | None = None,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        options: dict[str, str] = {}
        if write_policy is not None:
            options["write_policy"] = write_policy
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        return run_tdx_block_sync(
            block_code=block_code,
            symbols=symbols,
            mode=mode,
            create_if_missing=create_if_missing,
            dry_run=dry_run,
            show=show,
            **options,
            strategy_path=self.strategy_path,
        )

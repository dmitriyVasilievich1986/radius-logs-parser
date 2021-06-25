from .MainLog import MainLog
from typing import Union
from .DHCP import DHCP
from .DB import DB

class Aggregator:
    def __init__(
        self,
        context: str,
        time: int,
        ip_address: Union[list, None],
        black_list: bool,
        *args: list,
        **kwargs: dict,
    ) -> None: ...
    def __str__(
        self,
        filtered_list: Union[list, None],
        n: Union[int, None],
        *args: list,
        **kwargs: dict,
    ) -> str: ...
    def _get_all_mains_and_dhcp(
        self, *args: list, **kwargs: dict
    ) -> tuple(list, list, list, list): ...
    def show(
        self,
        only_answered: bool,
        n: Union[int, None],
        *args: list,
        **kwargs: dict,
    ) -> str: ...
    def _add_main_log_instance(
        self,
        instance: MainLog,
        *args: list,
        **kwargs: dict,
    ) -> None: ...
    def _add_dhcp_instance(
        self,
        instance: DHCP,
        *args: list,
        **kwargs: dict,
    ) -> None: ...
    def _get_all_dhcp(self, mains: list, *args: list, **kwargs: dict) -> list: ...
    def save_sqlite(self, path: str, *args: list, **kwargs: dict) -> None: ...
    def _get_only_with_answer(self, *args: list, **kwargs: dict) -> list: ...
    def _insert_main(self, db: DB, *args: list, **kwargs: dict) -> None: ...
    def __add__(self, value: str, *args: list, **kwargs: dict) -> None: ...
    def _insert_ip(self, db: DB, *args: list, **kwargs: dict) -> None: ...
    def _get_values(self, *args: list, **kwargs: dict) -> list: ...

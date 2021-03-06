from typing import Union

class DB:
    drop_tables: list
    create_tables: list
    def __init__(self, path: Union[str, None], *args: list, **kwargs: dict) -> None: ...
    def execute(self, query: str, *args: list, **kwargs: dict) -> None: ...
    def _create_tables(self, *args: list, **kwargs: dict) -> None: ...
    def _drop_tables(self, *args: list, **kwargs: dict) -> None: ...
    def close(self, *args: list, **kwargs: dict) -> None: ...

from typing import Union

def get_logs_from_path(path: str, *args: list, **kwargs: dict) -> list: ...
def sort_function(path: str, *args: list, **kwargs: dict) -> str: ...
def main(
    time: int,
    save: bool,
    context: str,
    verbose: bool,
    black_list: bool,
    path: Union[str, None],
    limit: Union[int, None],
    ip_address: Union[list, None],
    *args: list,
    **kwargs: dict,
) -> None: ...

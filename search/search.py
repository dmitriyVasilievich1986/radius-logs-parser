from os.path import isfile, isdir, join, exists
from .Config import BaseConfig, V3, logger
from .Aggregator import Aggregator
from datetime import datetime
from os import listdir
import re

if V3:
    from .p3_print import p3_print as p
else:
    from .p2_print import p2_print as p


def get_logs_from_path(path, *args, **kwargs):
    """The function accepts as input to the file
        or to the folder where you need to find the logs for parsing.
        Returns a list of all logs located in the folder and subfolders.

    Args:
        path (str): Path to file or dir.

    Returns:
        list: list of all logs located in the folder and subfolders.
    """

    payload = list()
    # if not exists, then empty
    if not exists(path):
        return payload
    # if file, than returns list this file
    if isfile(path):
        return [path]
    for file_or_dir in listdir(path):
        if isdir(join(path, file_or_dir)):
            payload += get_logs_from_path(join(path, file_or_dir))
        elif re.search(r".*?.log", file_or_dir):
            payload.append(join(path, file_or_dir))
    return payload


def sort_function(path, *args, **kwargs):
    """Sorting function.
        Sorts the data, puts above the logs in which the specified template is present.

    Args:
        path (str): path to log file.

    Returns:
        bool: contain line exact template or not.
    """

    with open(path, "r") as file:
        line = file.readline()
    return re.search(r"Context:.*?;inIP:.*?;Err:.*?;", line) is None


def main(
    time,
    limit,
    context,
    path=None,
    save=False,
    verbose=False,
    black_list=False,
    ip_address=list(),
    *args,
    **kwargs
):
    """The function is the main entry point for the script.
        Initializes the main aggregator.
        Opens logs, parses, stores the received data.
        It is possible to save data to a database and / or output data.

    Args:
        time (int): The time period within which the records should be located.
        limit (int): The number of lines to display data on the screen.
        context (str): Select data that contains context or not.
        save (bool, optional): Need to save data to database. Defaults to False.
        verbose (bool, optional): Show data on screen or not. Defaults to False.
        black_list (bool, optional): Add or discard entered IP addresses. Defaults to False.
        ip_address ([type], optional): List of IP addresses, by which need to filter. Defaults to list().
    """

    # get started time
    logger.info("start")
    start_time = datetime.now()

    # initialize main Aggregator
    agg = Aggregator(
        ip_address=ip_address,
        black_list=black_list,
        context=context,
        time=time,
    )

    # get list of pathes to log
    path = path or BaseConfig.LOGS
    # sort that list. web logs first
    logs = sorted(get_logs_from_path(path), key=sort_function)

    if not len(logs):
        logger.warning("No log files were found.")

    # read logs
    for log in logs:
        # check file
        if not isfile(log):
            logger.warning("File <{}> doesn`t exist.".format(log))
            continue
        # open file
        with open(log, "r") as file:
            logger.info("Open for read file: {}".format(log))
            lines = file.readlines()
            # progress bar
            length = len(lines) // 100
            for i, line in enumerate(lines):
                if not i % length:
                    p("Progress: {}%".format(i // length))
                # try to add data from log
                agg + line

    # show aggregated data, if needed
    if verbose and limit != 0:
        print(agg.show(only_answered=False, n=limit))

    # save data to db, if needed
    save and agg.save_sqlite(path)

    # show ended time
    end_time = datetime.now() - start_time
    logger.info("Overall time: {}".format(end_time))

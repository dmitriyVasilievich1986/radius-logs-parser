from .Aggregator import Aggregator
from .Config import BaseConfig, V3
from datetime import datetime
from os.path import isfile

if V3:
    from .p3_print import p3_print
    p = p3_print
else:
    from .p2_print import p2_print
    p = p2_print


def main(
    time,
    limit,
    context,
    black_list = False,
    ip_address = list(),
):
    start_time = datetime.now()
    agg = Aggregator(
        ip_address = ip_address,
        black_list = black_list,
        context = context,
        time = time,
    )
    for path in BaseConfig.LOGS:
        if not isfile(path):
            print("File <{}> doesn`t exist.".format(path))
            continue
        with open(path, 'r') as file:
            print('Open for read file: {}'.format(path))
            lines = file.readlines()
            length = len(lines) // 100
            for i, line in enumerate(lines):
                if not i % length:
                    p("Progress: {}%".format(i // length))
                agg + line
    
    # print(agg)
    # print(agg.show(n=None))
    # print(agg.show(only_answered=True, n=limit))

    agg.save_sqlite()
    end_time = datetime.now() - start_time
    print("Overall time: {}".format(end_time))
from sqlite3.dbapi2 import connect
import pandas as pd
import sqlite3

connection = sqlite3.connect('db_14_06.db')
cursor = connection.cursor()

query = """
    select i.ip, d.time, m.time
    from dhcp as d
    join main as m
    on m.id=d.main_id
    join ip as i
    on i.id=m.ip_id
    where m.context!="null";
"""

query = """
SELECT ip, c
from (
select i.ip, COUNT(m.id) as c
from main as m
left join dhcp as d
on d.main_id =m.id
join ip as i
on i.id=m.ip_id 
group by i.ip
order by c asc
)
where c<100;
"""

data = {
    "ip": list(),
    "count": list(),
    # "time_in": list(),
    # "time_out": list(),
}
r = cursor.execute(query)
for x in r.fetchall():
    data['ip'].append(x[0])
    data['count'].append(x[1])
    # data['time_in'].append(x[1])
    # data['time_out'].append(x[2])

df = pd.DataFrame(data=data)
print(df)

#!/bin/bash
pids = `ps -ef |grep tmp_file |grep -v "grep" |awk '{print $2}'`
KILL = "kill -9"
for pid in ${pids};do
	${KILL} ${pid}
done
tail -f /var/local/logservice/logfile/tmp* &
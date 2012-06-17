#!/usr/bin/env ksh

curr_dir=$(cd $(dirname $0); pwd)
root_dir=${curr_dir%/*/*}
cd ${root_dir}

if [ $# == 0 ]; then
    python3 -m mwsrvinstall.websphere.im --scope=im --action=install --config=/root/bin/mwsrvinstall/examples/websphere-default.ini
else
    python3 -m mwsrvinstall.websphere.im --scope=im --action=install "$@"
fi

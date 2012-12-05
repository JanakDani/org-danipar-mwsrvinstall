#!/usr/bin/env ksh

curr_dir=$(cd $(dirname $0); pwd)
home_dir=${curr_dir%/*}
root_dir=${curr_dir%/*/*}
#cd ${root_dir}

export PYTHONPATH=${home_dir}:${PYTHONPATH}
#python3 -m mwsrvinstall.ibm.main uninstall -offeringProfile=WASND80 -configFile=/root/bin/mwsrvinstall/examples/wasnd-default.ini "$@"

${home_dir}/__main__.py IBM uninstall -offeringProfile=WASND80 -configFile=../examples/wasnd-default.ini "$@"

#!/usr/bin/env ksh

curr_dir=$(cd $(dirname $0); pwd)
home_dir=${curr_dir%/*}
root_dir=${curr_dir%/*/*}
#cd ${root_dir}

export PYTHONPATH=${home_dir}:${PYTHONPATH}
#python3 -m mwsrvinstall.ibm.main install -offeringProfile="InstallationManager" -configFile=/root/bin/mwsrvinstall/examples/im-default.ini "$@"

${home_dir}/__main__.py IBM install -offeringProfile=InstallationManager -configFile=/root/bin/mwsrvinstall/examples/im-default.ini "$@"

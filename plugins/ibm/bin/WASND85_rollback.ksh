#!/usr/bin/env ksh

plg_name="IBM"
curr_dir=$(cd $(dirname $0); pwd)
home_dir=${curr_dir%/*}
root_dir=${curr_dir%/*/*}
plg_dir=${home_dir}/plugins/$(echo ${plg_name} | tr '[:upper:]' '[:lower:]')
if [[ $(echo ${home_dir##*/}) == $(echo ${plg_name} | tr '[:upper:]' '[:lower:]') ]]; then
    home_dir=${curr_dir%/*/*/*}
    root_dir=${home_dir%/*}
    plg_dir=${curr_dir%/*}
fi

export PYTHONPATH=${home_dir}:${PYTHONPATH}
python2.7 ${home_dir} ${plg_name} rollback -profile=WASND85 -configFile=${plg_dir}/samples/wasnd-default.ini "$@"

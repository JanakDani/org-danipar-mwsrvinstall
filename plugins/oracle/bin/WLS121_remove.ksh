#!/usr/bin/env ksh

plg_name="ORACLE"
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
python2.7 ${home_dir} ${plg_name} remove -profile=WLS121 -configFile=${plg_dir}/samples/wls-default.ini "$@"

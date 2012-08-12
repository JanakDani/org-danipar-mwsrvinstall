#!/usr/bin/env ksh

curr_dir=$(cd $(dirname $0); pwd)
home_dir=${curr_dir%/*}
root_dir=${curr_dir%/*/*}
#cd ${root_dir}

export PYTHONPATH=${home_dir}:${PYTHONPATH}
#python3 -m mwsrvinstall.ibm.main delete-package -offeringProfile=PackagingUtility -packageName='IBM WebSphere Application Server Network Deployment' -configFile=/root/bin/mwsrvinstall/examples/pu-wasnd.ini "$@"

${home_dir}/__main__.py IBM copy-package -offeringProfile=PackagingUtility -packageName="IBM WebSphere Application Server Network Deployment" -configFile=/root/bin/mwsrvinstall/examples/pu-wasnd.ini "$@"

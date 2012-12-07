#!/usr/bin/env python2.7

import sys
from lib import *

inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
if inputArgs.options.vendorname == 'IBM':
    from plugins.ibm import *
    main.main(inputArgs.options)

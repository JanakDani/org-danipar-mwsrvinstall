__all__ = [ "ibm" ]

import sys
from utils import *
from lib import *

inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
if inputArgs.options.vendorname == 'IBM':
    ibm.main(inputArgs.options)


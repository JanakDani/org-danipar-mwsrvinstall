import sys
from lib import *

inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
if inputArgs.options.vendorname == 'IBM':
    from plugins.ibm.lib import *
    main.main(inputArgs.options)

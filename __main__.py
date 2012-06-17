import sys
import optparse
from mwsrvinstall.utils import *
from mwsrvinstall.websphere import *

class _ArgParser():
    def __init__(self, sysargv):
        mandatories = ['scope']
        parser = optparse.OptionParser(option_class=extoptparse.extOption, usage='\n  %prog [options] <arg>')
        parser.add_option("--scope", dest="scope", help="Provide Scope for execution")
        (self.options, self.args) = parser.parse_args(sysargv)

        for m in mandatories:
            if self.options.__dict__[m] == None: 
                print("Mandatory option \"%s\" is missing" %(m))
                print(parser.print_help())
                parser.exit()

input = _ArgParser(sys.argv)
getattr(globals()[input.options.scope], 'main')()

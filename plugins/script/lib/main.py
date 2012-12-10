import sys
from lib import *
import logging
import script

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("script.main")


def main(input):
    """Main method:
    """
    logger.info("Input arguments: %s", input)
    #input = _ArgParser(inargs[1:])

    for oprofile in input.offeringProfile:
        packageObj = script.Package(input.vendorname, oprofile, input.configFile.name, input.version)
        if input.command == 'install':
            packageObj.install()
        elif input.command == 'rollback':
            packageObj.rollback()
        elif input.command == 'uninstall':
            packageObj.uninstall()

if __name__ == '__main__':
    inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
    main(inputArgs.options)

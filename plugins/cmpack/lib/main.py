import sys
from lib import *
import logging
import cmpack

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("cmpack.main")


def main(input):
    """Main method:
    """
    logger.info("Input arguments: %s", input)
    #input = _ArgParser(inargs[1:])

    packageObj = cmpack.Package(input.vendorname, input.profile, input.configFile.name, input.version)

    if input.command == 'install':
        packageObj.install()
    elif input.command == 'rollback':
        packageObj.rollback()
    elif input.command == 'uninstall':
        packageObj.uninstall()

if __name__ == '__main__':
    inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
    main(inputArgs.options)

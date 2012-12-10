import sys
from lib import *
import logging
import ibm

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("ibm.main")


def main(input):
    """Main method:
    """
    logger.info("Input arguments: %s", input)
    #input = _ArgParser(inargs[1:])

    for oprofile in input.offeringProfile:
        packageObj = ibm.Package(input.vendorname, oprofile, input.configFile.name, input.version)
        if input.command == 'install':
            packageObj.install()
        elif input.command == 'rollback':
            packageObj.rollback()
        elif input.command == 'uninstall':
            packageObj.uninstall()
        elif input.command == 'copy-package':
            packageObj.copy_package(input.packageName)
        elif input.command == 'delete-package':
            packageObj.delete_package(input.packageName)

if __name__ == '__main__':
    inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
    main(inputArgs.options)

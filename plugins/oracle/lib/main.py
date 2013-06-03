import sys
import os
from lib import *
import logging
import oracle
import diomreader

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("oracle.main")


def main(input):
    """Main method:
    """
    logger.info("Input arguments: %s", input)

    if input.__contains__('patch'):
        packageObj = oracle.Package(input.vendorname, input.profile, input.configFile.name, input.patch, True)
    elif input.__contains__('version'):
        packageObj = oracle.Package(input.vendorname, input.profile, input.configFile.name, input.version, False)

    if input.command == 'install':
        # Read online and download software
        xml = diomreader.XMLReader(url=packageObj.config['url'], file=packageObj.config['dm_file'],
                                   sysName=packageObj.sysName,sysBit=packageObj.machine,vendorName=packageObj.config['vendorname'],
                                   packageName=packageObj.config['pkg_name'], version=packageObj.version,
                                   realm=packageObj.config['url_realm'],user=packageObj.config['url_user'],
                                   passwd=packageObj.config['url_passwd'])
        packageObj.config.update(xml.getSWDownloadDetails())
        packageObj.install()
    elif input.command == 'remove':
        packageObj.remove()
    elif input.command == 'uninstall':
        packageObj.uninstall()

if __name__ == '__main__':
    inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
    main(inputArgs.options)

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

    ## if uninstall then create input.version with none
    ## disables uninstall requiring version input for clear understanding
    if input.command == 'uninstall' and not input.__contains__('version'):
        input.version = None

    if input.patch != None:
        packageObj = oracle.Package(input.vendorname, input.profile, input.configFile.name, input.patch, True)
    else:
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
        logger.info("Presenting user with the confirmation screen for uninstallation")
        print
        print "PLEASE CONFIRM BELOW:"
        print "You are about to uninstall %s. Once uninstalled it cannot \
                be undone" %(os.path.dirname(packageObj.config['install_root']))
        input = None
        while input != 'yes' or input != 'no':
            input = raw_input("Are you sure (yes/no): ")
            if input == 'no':
                sys.exit()
            elif input == 'yes':
                logger.info("User chose to uninstall %s", packageObj.config['install_root'])
                break
            else:
                print "Allowed options are (yes/no)"
        sys.exit()
        packageObj.uninstall()

if __name__ == '__main__':
    inputArgs = cmdlineparser.ArgParser(sys.argv[1:])
    main(inputArgs.options)

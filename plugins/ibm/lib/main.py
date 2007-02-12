import sys
import os
from lib import *
import logging
import ibm
import diomreader

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("ibm.main")


def main(input):
    """Main method:
    """
    logger.info("Input arguments: %s", input)

    packageObj = ibm.Package(input.vendorname, input.profile, input.configFile.name, input.version)
    if input.command == 'install':
        # Read online and download software
        xml = diomreader.XMLReader(url=packageObj.config['url'], file=packageObj.config['dm_file'],
                                    sysName=packageObj.sysName,sysBit=packageObj.machine,vendorName=packageObj.config['vendorname'],
                                    packageName=packageObj.config['pkg_name'], version=packageObj.version)
        packageObj.config.update(xml.getSWDownloadDetails())
        """
        #print packageObj.config
        # Logic too complicated for dependency. Using simple
        # method
        if packageObj.config.has_key('dependency') and \
           len(packageObj.config['dependency']) > 0:
            for dicta in packageObj.config['dependency']:
                depPackageObj = ibm.Package(input.vendorname, input.profile, input.configFile.name, dicta['packageversion'])
                depxml = diomreader.XMLReader(url=depPackageObj.config['url'], file=depPackageObj.config['dm_file'],
                                    sysName=depPackageObj.sysName,sysBit=depPackageObj.machine,vendorName=depPackageObj.config['vendorname'],
                                    packageName=depPackageObj.config['pkg_name'], version=depPackageObj.version)
                depPackageObj.config.update(depxml.getSWDownloadDetails())
                #print depPackageObj.config
                skipFlag = False
                if os.path.isdir(depPackageObj.config['install_root']):
                    historyScript = os.path.join(depPackageObj.config['install_root'],'bin/historyInfo.sh')
                    if os.path.isfile(historyScript):
                        (ret_code, output) = shell.Shell.runCmd(historyScript)
                        l = []
                        for arr in output.split("-----"):
                            if arr.find('Event') > 0:
                                l.append(arr)
                        for arr in l[::-1]:
                            if arr.find(depPackageObj.config['packagename']) > 0 and \
                               arr.find(depPackageObj.config['packageversion']) > 0:
                                if arr.find('update') > 0 or \
                                   arr.find('install') > 0:
                                    skipFlag = True
                                    #depPackageObj.install()
        """
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

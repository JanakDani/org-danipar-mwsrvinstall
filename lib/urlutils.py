import logging
import sys
import os
import zipfile
import stat
import urllib2 ##remove this for python3
##import urllib.request use this for python3
from xml.dom.minidom import parse, parseString

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("utils.urlutils")

class XMLReader():
    def __init__(self,url,file,sysName,sysBit,vendorName,packageName,version=None):
        self.sysName  = sysName
        self.sysBit  = sysBit
        self.url = url
        self.file = file
        self.vendorName = vendorName
        self.packageName = packageName
        self.version = version
        try:
            httpfile = urllib2.urlopen(os.path.join(url, file))
            self.data = httpfile.read()
            httpfile.close()
        #except (urllib.error.HTTPError): python3
        except (urllib2.URLError):
            logger.exception("Problems while getting file %s", file)

    def getOSNode_Text(self, node):
        dicta = {}
        for osNode in node:
            if osNode.nodeName == 'OS':
                system_arr = osNode.getAttribute('SYSTEM').split(',')
                #matchFound = False
                for system in system_arr:
                    if system == ''.join(self.sysName+':'+self.sysBit):
                        fileName = XMLReader._getTextData(osNode.getElementsByTagName('FILENAME')[0].childNodes)
                        location = XMLReader._getTextData(osNode.getElementsByTagName('LOCATION')[0].childNodes)
                        dicta['fileName'] = fileName
                        dicta['url'] = os.path.join(self.url, location, fileName)
                        #matchFound = True
                        break
                #if matchFound:
                    #fileName = XMLReader._getTextData(osNode.getElementsByTagName('FILENAME')[0].childNodes)
                    #location = XMLReader._getTextData(osNode.getElementsByTagName('LOCATION')[0].childNodes)
                    #dicta['fileName'] = fileName
                    #dicta['url'] = os.path.join(self.url, location, fileName)
                """
                if osNode.getAttribute('TYPE') == self.sysName and \
                osNode.getAttribute('BIT') == self.sysBit:
                    fileName = XMLReader._getTextData(osNode.getElementsByTagName('FILENAME')[0].childNodes)
                    location = XMLReader._getTextData(osNode.getElementsByTagName('LOCATION')[0].childNodes)
                    dicta['fileName'] = fileName
                    dicta['url'] = os.path.join(self.url, location, fileName)
                elif osNode.getAttribute('TYPE') == 'Multiplatform':
                    fileName = XMLReader._getTextData(osNode.getElementsByTagName('FILENAME')[0].childNodes)
                    location = XMLReader._getTextData(osNode.getElementsByTagName('LOCATION')[0].childNodes)
                    dicta['fileName'] = fileName
                    dicta['url'] = os.path.join(self.url, location, fileName)
                """

        return dicta


    def getSWDownloadDetails(self):
        swDownloadURL = ""
        dicta = {}
        dom = parseString(self.data)
        dm = dom.getElementsByTagName('diom')[0]
        for vendorNode in dm.childNodes:
            if vendorNode.nodeName == 'Vendor' and \
            dict(vendorNode.attributes.items())['NAME'] == self.vendorName:
                for packageNode in vendorNode.childNodes:
                    if packageNode.nodeName == 'Package' and \
                    dict(packageNode.attributes.items())['NAME'] == self.packageName:
                        dict_temp = dict(packageNode.attributes.items())
                        dicta['packagename'] = dict_temp['NAME']
                        dicta['version'] = dict_temp['VERSION']
                        dicta['offering_version'] = dict_temp['OFFERING_VERSION']
                        dicta['offering_id'] = dict_temp['OFFERING_ID']
                        if not self.version:
                            if dict_temp['default'] == 'true':
                                dicta.update(self.getOSNode_Text(packageNode.childNodes))
                                return dicta
                        elif dict_temp['VERSION'] == self.version:
                            dicta.update(self.getOSNode_Text(packageNode.childNodes))
                            return dicta
        return dicta

    @staticmethod
    def _getTextData(nodeList):
        for node in nodeList:
            if node.nodeType == node.TEXT_NODE:
                return node.data


class Download():
    def __init__(self, url, fileName, target_loc):
        if fileName:
            file = os.path.join(target_loc, fileName)
            if not os.path.isfile(file):
                Download.software(url, target_loc)
            Download.unzip(file, target_loc)
            Download.setPermissions(target_loc)
        else:
            logger.exception("fileName not found in configuration")

    @staticmethod
    def setPermissions(target_loc):
        logger.info("Setting up permissions on %s", target_loc)
        for dirpath,dirs,fileNames in os.walk(target_loc):
            for fileName in fileNames:
                file = os.path.join(dirpath, fileName)
                os.chmod(file, stat.S_IRWXU)

    @staticmethod
    def unzip(file, target_loc):
        if not os.path.isdir(file.rstrip('.zip')):
            if zipfile.is_zipfile(file):
                logger.info("Extracting software %s. please wait...", file)
                zip = zipfile.ZipFile(file)
                zip.extractall(path=target_loc)
                logger.info("Software extracted to %s", target_loc)
        else:
            logger.debug("Software %s already found. Skipping unzip ...", file)

    @staticmethod
    def software(url, dl_loc):
        try:
            fileName = url.split('/')[-1]
            data = None
            handle = urllib2.urlopen(url)
            if not os.path.isdir(dl_loc):
                os.mkdir(dl_loc)
            fo = open(os.path.join(dl_loc, fileName), "wb")
            size = int(handle.info()["Content-Length"])
            type = str(handle.info()["Content-Type"])
            dlSize = 0
            blockSize = 8*1024
            previous_percent = 0
            while True:
                buffer = handle.read(blockSize)
                dlSize += len(buffer)
                if not buffer:
                    break

                fo.write(buffer)
                percent = int(dlSize*100/size)
                if previous_percent != percent:
                    previous_percent = percent
                    sys.stdout.write("\r%2d%% - [%d,%s]" %(percent, dlSize, fileName))
            fo.close()
            sys.stdout.write("\n")
            logger.info("%s - successfully downloaded", os.path.join(dl_loc,fileName))
        except (urllib2.URLError):
            try:
                fo.close()
            except:
                pass
            logger.exception("Download failed")

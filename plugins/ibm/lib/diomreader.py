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
logger = logging.getLogger("ibm.diomreader")

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
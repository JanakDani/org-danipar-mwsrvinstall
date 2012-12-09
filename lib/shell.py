import logging
import os
import subprocess

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("swinstall.shell")


class Shell():
    def __init__(self):
        pass

    @staticmethod
    def runCmd(cmd):
        logger.info("Executing command: \n%s", cmd)
        proc = subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        logger.info("Output from SHELL: ")
        for line in proc.stdout.readlines():
            logger.info(line.decode("utf-8").rstrip(),)
            output += line.decode("utf-8")
        stdout, stderr = proc.communicate()
        ret_code = proc.returncode
        logger.info("SHELL output completed")
        if ret_code == 0:
            logger.info("Return code from SHELL is: %s", ret_code)
        else:
            logger.error("Error from the shell: \n%s", output)
            logger.error("Return code from SHELL is: %s", ret_code)
            raise Exception(cmd, ret_code, output)

        return (ret_code, output)

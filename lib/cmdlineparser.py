import argparse


class ArgParser():
    def __init__(self, sysargv):
        main_parser = argparse.ArgumentParser(description='Use this package for software installation. \
            Current vendors supported are IBM and custom scripts. It includes installation, \
            un-installation, rollback, list softwares and for other purposes')
        main_subparsers = main_parser.add_subparsers(help='vendors', dest='vendorname')

        ##############################################################
        ##### IBM
        ibm_parser = main_subparsers.add_parser('IBM', help='IBM Software')
        ibm_subparsers = ibm_parser.add_subparsers(help='commands', dest='command')

        ibm_install_parser = ibm_subparsers.add_parser('install', help='Install Software')
        ibm_install_parser.add_argument('-profile', action='store', required=True, help='profile name')
        ibm_install_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        ibm_install_parser.add_argument('-version', required=False, help='Version')

        # A uninstall command
        ibm_uninstall_parser = ibm_subparsers.add_parser('uninstall', help='Uninstall software')
        ibm_uninstall_parser.add_argument('-profile', action='store', required=True, help='profile name')
        ibm_uninstall_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        #ibm_uninstall_parser.add_argument('-version', required=False, help='Version')

        # A rollback command
        ibm_rollback_parser = ibm_subparsers.add_parser('rollback', help='Roll back fix to specific version')
        ibm_rollback_parser.add_argument('-profile', action='store', required=True, help='profile name')
        ibm_rollback_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        ibm_rollback_parser.add_argument('-version', required=False, help='Version')
        ibm_rollback_parser.add_argument('-packageName', required=False, help='Provide Package Name')

        # A copy-package command
        ibm_copypackage_parser = ibm_subparsers.add_parser('copy-package', help='Copy package to online repository')
        ibm_copypackage_parser.add_argument('-profile', action='store', required=True, help='profile name')
        ibm_copypackage_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        ibm_copypackage_parser.add_argument('-version', required=True, help='Version')
        ibm_copypackage_parser.add_argument('-packageName', required=True, help='Provide Package Name')

        # A list-package command
        ibm_list_parser = ibm_subparsers.add_parser('list-package', help='List available packages for installation')
        ibm_list_parser.add_argument('-profile', action='store', required=True, help='profile name')
        ibm_list_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        ibm_list_parser.add_argument('-version', required=False, help='Version')
        ibm_list_parser.add_argument('-packageName', required=False, help='Provide Package Name')

        # A delete command
        ibm_deletepackage_parser = ibm_subparsers.add_parser('delete-package', help='Delete package from online repository')
        ibm_deletepackage_parser.add_argument('-profile', action='store', required=True, help='profile name')
        ibm_deletepackage_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        ibm_deletepackage_parser.add_argument('-version', required=True, help='Version')
        ibm_deletepackage_parser.add_argument('-packageName', required=True, help='Provide Package Name')

        ##### IBM completed
        ##############################################################

        ##############################################################
        ##### SCRIPT
        script_parser = main_subparsers.add_parser('SCRIPT', help='Scripts bundle')
        script_subparsers = script_parser.add_subparsers(help='commands', dest='command')

        script_install_parser = script_subparsers.add_parser('install', help='Install script bundle')
        script_install_parser.add_argument('-profile', action='store', required=True, help='profile name')
        script_install_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        script_install_parser.add_argument('-version', required=True, help='Version')

        # A uninstall command
        script_uninstall_parser = script_subparsers.add_parser('uninstall', help='Uninstall script bundle')
        script_uninstall_parser.add_argument('-profile', action='store', required=True, help='profile name')
        script_uninstall_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        script_uninstall_parser.add_argument('-version', required=False, help='Version')

        ##### SCRIPT completed
        ##############################################################

        ##############################################################
        ##### ORACLE
        oracle_parser = main_subparsers.add_parser('ORACLE', help='Oracle Software')
        oracle_subparsers = oracle_parser.add_subparsers(help='commands', dest='command')

        # A install command
        oracle_install_parser = oracle_subparsers.add_parser('install', help='Install Software')
        oracle_install_parser.add_argument('-profile', action='store', required=True, help='profile name')
        oracle_install_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        oracle_install_parser.add_argument('-version', required=False, help='Version')
        oracle_install_parser.add_argument('-patch', required=False, help='Patch(es). Comma separated.')

        # A uninstall command
        oracle_uninstall_parser = oracle_subparsers.add_parser('uninstall', help='Uninstall software')
        oracle_uninstall_parser.add_argument('-profile', action='store', required=True, help='profile name')
        oracle_uninstall_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        #oracle_uninstall_parser.add_argument('-version', required=False, help='Version')

        # A remove patch command
        oracle_remove_parser = oracle_subparsers.add_parser('remove', help='remove specific patch')
        oracle_remove_parser.add_argument('-profile', action='store', required=True, help='profile name')
        oracle_remove_parser.add_argument('-configFile', type=argparse.FileType('r'), required=True, help='Property file')
        oracle_remove_parser.add_argument('-patch', required=True, help='Patch(es). Comma spearated.')


        self.options = main_parser.parse_args(sysargv)

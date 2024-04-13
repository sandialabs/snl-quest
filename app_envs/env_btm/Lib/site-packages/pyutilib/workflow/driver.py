#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['TaskDriver']

import argparse
from pyutilib.misc import Options
from pyutilib.workflow import tasks


class TaskDriver(object):

    def __init__(self, **kwargs):
        if not 'formatter_class' in kwargs:
            kwargs['formatter_class'] = argparse.RawDescriptionHelpFormatter
        self.parser = argparse.ArgumentParser(**kwargs)
        #self.parser.add_argument('--help-commands', dest='help_commands', action='store_true', default=False, help="Print a list of available subcommands")
        self.subparsers = self.parser.add_subparsers(
            help='Sub-commands', dest='subparser_name')
        self.wf = {}

    def register_task(self, wf, name=None, help=''):
        if name is None:
            name = wf
        ans = tasks.TaskFactory(
            wf, parser=self.subparsers.add_parser(
                name, help=help))
        if ans is None:
            raise ValueError(
                "Unknown workflow task '%s'\n    Available tasks: %s" %
                (wf, ' '.join(tasks.TaskFactory().services())))
        ans._parser.set_defaults(subparser_name=name)
        ans.set_arguments()
        self.wf[name] = ans

    def print_help(self):
        self.parser.print_help()  #pragma:nocover

    def parse_args(self, args=None):
        #
        # Call the parser to parse the arguments
        #
        if args is None:
            # sys.argv arguments
            ret = self.parser.parse_args()
        else:
            # args arguments
            ret = self.parser.parse_args(args)
        #
        # Set options, based on the parser return value.
        # The parser options are passed into the workflow.
        #
        opt = Options()
        for key in dir(ret):
            if key[0] != '_' and key != 'subparser_name':
                opt[key] = getattr(ret, key)
        return self.wf[ret.subparser_name](opt)

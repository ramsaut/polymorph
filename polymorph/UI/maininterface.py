# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit import HTML
from polymorph.utils import capture, get_arpspoofer, set_ip_forwarding
from polymorph.UI.tlistinterface import TListInterface
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from prompt_toolkit.history import FileHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class MainInterface(Interface):
    """This class is responsible for parsing and respond to user commands in
    the starting interface, when no action has been carried out."""

    def __init__(self):
        # Constructor of the parent class
        super(MainInterface, self).__init__()
        # Class Attributes
        self._cap = None

    def run(self):
        """Runs the interface and waits for user input commands."""
        completer = WordCompleter(['capture', 'spoof', 'clear'])
        history = FileHistory(self._polym_path + '/.minterface_history')
        while True:
            try:
                command = prompt(HTML("<bold><red>PH</red> > </bold>"),
                                 history=history,
                                 completer=completer,
                                 complete_style=CompleteStyle.READLINE_LIKE,
                                 auto_suggest=AutoSuggestFromHistory(),
                                 enable_history_search=True)
            except KeyboardInterrupt:
                self.exit_program()
                continue
            command = command.split(" ")
            if command[0] in self.EXIT:
                self.exit_program()
            elif command[0] in ["capture", "c"]:
                self._capture(command)
            elif command[0] in ["spoof", "s"]:
                self._spoof(command)
            elif command[0] == "clear":
                Interface._clear()
            elif command[0] == "":
                continue
            else:
                Interface._wrong_command()

    def _capture(self, command):
        """Handles the capture command and the options."""

        def run_tlistinterface(tlist):
            """Runs the interface that handles the list of Templates."""
            tlistinterface = TListInterface(tlist, self._poisoner)
            tlistinterface.run()

        def capture_banner():
            """Shows a banner before capturing."""
            Interface._print_info("Waiting for packets...")
            print("(Press Ctr-C to exit)\n")

        def no_captured():
            """Shows no packets captured."""
            Interface._print_error("No packets have been captured.")

        # If not additional options
        if len(command) == 1:
            capture_banner()
            cap = capture()
            if cap:
                # Showing the new interface to the user
                run_tlistinterface(cap)
            else:
                no_captured()
            return
        # Parsing additional options
        cp = CommandParser(MainInterface._capture_opts())
        args = cp.parse(command)
        # Wrong arguments will return None
        if not args:
            Interface._argument_error()
            return
        # This variable handles the verbose option
        func = None
        # Print the help
        if args["-h"]:
            Interface.print_help(MainInterface.capture_help())
            return
        # Capture with verbose
        elif args["-v"]:
            func = MainInterface._print_v
        # Capture with lot of verbose
        elif args["-vv"]:
            func = MainInterface._print_vv
        # Capturing
        if(args["-file"]):
            cap = capture(userfilter=args["-f"],
                          func=func,
                          offline=args["-file"])
        else:
            capture_banner()
            cap = capture(userfilter=args["-f"],
                          count=args["-c"],
                          time=args["-t"],
                          func=func)
        if cap:
            run_tlistinterface(cap)
        else:
            no_captured()

    @staticmethod
    def _print_v(packet):
        print(packet.summary())

    @staticmethod
    def _print_vv(packet):
        packet.show()

    @staticmethod
    def _capture_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-v": {"type": bool,
                       "default": False},
                "-vv": {"type": bool,
                        "default": False},
                "-c": {"type": int,
                       "default": 0},
                "-t": {"type": int,
                       "default": None},
                "-f": {"type": str,
                       "default": ""},
                "-file": {"type": str,
                          "default": ""}}
        return opts

    @staticmethod
    def capture_help():
        """Builds the help for the capture command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-f", "allows packet filtering using the BPF notation."),
            ("-c", "number of packets to capture."),
            ("-t", "stop sniffing after a given time."),
            ("-file", "read a .pcap file from disk."),
            ("-v", "verbosity level medium."),
            ("-vv", "verbosity level high.")
        ])
        return OrderedDict([
            ("name", "capture"),
            ("usage", "capture [-option]"),
            ("description", "Capture packets from a specific interface and transform them into a template list."),
            ("options", options)
        ])

# -*- coding: utf-8 -*-
"""

    Python logging tuned to extreme.

"""

__author__ = "Mikko Ohtamaa <mikko@opensourcehacker.com>"
__license__ = "MIT"

import logging

import ctypes
import logging
import os
import sys

try:
    unicode
except NameError:
    unicode = None

class ColorizingStreamHandler(logging.StreamHandler):
    """
    A stream handler which supports colorizing of console streams
    under Windows, Linux and Mac OS X.

    :param strm: The stream to colorize - typically ``sys.stdout``
                 or ``sys.stderr``.
    """

    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    #levels to (background, foreground, bold/intense)
    if os.name == 'nt':
        level_map = {
            logging.DEBUG: (None, 'blue', True),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', True),
            logging.ERROR: (None, 'red', True),
            logging.CRITICAL: ('red', 'white', True),
        }
    else:
        "Maps levels to colour/intensity settings."
        level_map = {
            logging.DEBUG: (None, 'blue', False),
            logging.INFO: (None, 'black', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }

    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        "Returns true if the handler's stream is a terminal."
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if unicode and isinstance(message, unicode):
                enc = getattr(stream, 'encoding', 'utf-8')
                message = message.encode(enc, 'replace')
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            """
            Output a colorized message.

            On Linux and Mac OS X, this method just writes the
            already-colorized message to the stream, since on these
            platforms console streams accept ANSI escape sequences
            for colorization. On Windows, this handler implements a
            subset of ANSI escape sequence handling by parsing the
            message, extracting the sequences and making Win32 API
            calls to colorize the output.

            :param message: The message to colorize and output.
            """
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,    # black
            1: 0x04,    # red
            2: 0x02,    # green
            3: 0x06,    # yellow
            4: 0x01,    # blue
            5: 0x05,    # magenta
            6: 0x03,    # cyan
            7: 0x07,    # white
        }

        def output_colorized(self, message):
            """
            Output a colorized message.

            On Linux and Mac OS X, this method just writes the
            already-colorized message to the stream, since on these
            platforms console streams accept ANSI escape sequences
            for colorization. On Windows, this handler implements a
            subset of ANSI escape sequence handling by parsing the
            message, extracting the sequences and making Win32 API
            calls to colorize the output.

            :param message: The message to colorize and output.
            """
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2): # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08 # foreground intensity on
                            elif p == 0: # reset to default color
                                color = 0x07
                            else:
                                pass # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        """
        Colorize a message for a logging event.

        This implementation uses the ``level_map`` class attribute to
        map the LogRecord's level to a colour/intensity setting, which is
        then applied to the whole message.

        :param message: The message to colorize.
        :param record: The ``LogRecord`` for the message.
        """
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        """
        Formats a record for output.

        This implementation colorizes the message line, but leaves
        any traceback unolorized.
        """
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message


class RainbowLoggingHandler(ColorizingStreamHandler):
    """ A colorful logging handler optimized for terminal debugging aestetichs.

    - Designed for diagnosis and debug mode output - not for disk logs

    - Highlight the content of logging message in more readable manner

    - Show function and line, so you can trace where your logging messages
      are coming from

    - Keep timestamp compact

    - Extra module/function output for traceability

    The class provide few options as member variables you
    would might want to customize after instiating the handler.
    """

    # Define color for message payload
    level_map = {
        logging.DEBUG: (None, 'cyan', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', True),
        logging.ERROR: (None, 'red', True),
        logging.CRITICAL: ('red', 'white', True),
    }

    date_format = "%H:%m:%S"

    #: How many characters reserve to function name logging
    who_padding = 22

    #: Show logger name
    show_name = True

    def get_color(self, fg=None, bg=None, bold=False):
        """
        Construct a terminal color code

        :param fg: Symbolic name of foreground color

        :param bg: Symbolic name of background color

        :param bold: Brightness bit
        """
        params = []
        if bg in self.color_map:
            params.append(str(self.color_map[bg] + 40))
        if fg in self.color_map:
            params.append(str(self.color_map[fg] + 30))
        if bold:
            params.append('1')

        color_code = ''.join((self.csi, ';'.join(params), 'm'))

        return color_code

    def colorize(self, record):
        """
        Get a special format string with ASCII color codes.
        """

        # Dynamic message color based on logging level
        if record.levelno in self.level_map:
            fg, bg, bold = self.level_map[record.levelno]
        else:
            # Defaults
            bg = None
            fg = "white"
            bold = False

        # Magician's hat
        # https://www.youtube.com/watch?v=1HRa4X07jdE
        template = [
            "[",
            self.get_color("black", None, True),
            "%(asctime)s",
            self.reset,
            "] ",
            self.get_color("white", None, True) if self.show_name else "",
            "%(name)s " if self.show_name else "",
            "%(padded_who)s",
            self.reset,
            " ",
            self.get_color(bg, fg, bold),
            "%(message)s",
            self.reset,
        ]

        format = "".join(template)

        who = [self.get_color("green"),
               getattr(record, "funcName", ""),
               "()",
               self.get_color("black", None, True),
               ":",
               self.get_color("cyan"),
               str(getattr(record, "lineno", 0))]

        who = "".join(who)

        # We need to calculate padding length manualy
        # as color codes mess up string length based calcs
        unformatted_who = getattr(record, "funcName", "") + "()" + \
            ":" + str(getattr(record, "lineno", 0))

        if len(unformatted_who) < self.who_padding:
            spaces = " " * (self.who_padding - len(unformatted_who))
        else:
            spaces = ""

        record.padded_who = who + spaces

        formatter = logging.Formatter(format, self.date_format)
        self.colorize_traceback(formatter, record)
        output = formatter.format(record)
        # Clean cache so the color codes of traceback don't leak to other formatters
        record.ext_text = None
        return output

    def colorize_traceback(self, formatter, record):
        """
        Turn traceback text to red.
        """
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            record.exc_text = "".join([
                self.get_color("red"),
                formatter.formatException(record.exc_info),
                self.reset,
            ])

    def format(self, record):
        """
        Formats a record for output.

        Takes a custom formatting path on a terminal.
        """
        if self.is_tty:
            message = self.colorize(record)
        else:
            message = logging.StreamHandler.format(self, record)

        return message


def get_logger(name):
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = RainbowLoggingHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


if __name__ == "__main__":
    # Run test output on stdout
    import sys

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = RainbowLoggingHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    logger = logging.getLogger("test")

    def test_func():
        logger.debug("debug msg")
        logger.info("info msg")
        logger.warn("warn msg")

    def test_func_2():
        logger.error("error msg")
        logger.critical("critical msg")

        try:
            raise RuntimeError("Opa!")
        except Exception as e:
            logger.exception(e)

    test_func()
    test_func_2()
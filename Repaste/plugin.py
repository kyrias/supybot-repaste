###
# Copyright (c) 2015, Johannes Löthberg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import subprocess

import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    from supybot.i18n import internationalizeDocstring
    _ = PluginInternationalization('Repaste')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x
    internationalizeDocstring = lambda x: x

from .extractors import (HastebinCom, PastebinCom, Zerobin)


@internationalizeDocstring
class Repaste(callbacks.Plugin):
    """Repaste URLs from bad pastebins"""
    threaded = True

    def __init__(self, irc):
        self._parent = super(Repaste, self)
        self._parent.__init__(irc)

        self.pastebins = [
            HastebinCom,
            PastebinCom,
        ]
        if self.getpaste_working():
            self.pastebins.append(Zerobin)

    def doPrivmsg(self, irc, msg):
        string = msg.args[1]

        for pastebin in self.pastebins:
            pastebin.repaste(irc, string)

    def getpaste_working(self):
        try:
            if subprocess.call(['getpaste']) != 1:
                self.log.warning("getpaste script not fully functional, zerobin"
                                 "support disabled")
                return False
            return True
        except:
            self.log.warning("getpaste script could not be found.")
            return False


Class = Repaste

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

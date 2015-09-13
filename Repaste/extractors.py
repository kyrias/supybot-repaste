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

import re
import requests
import subprocess

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Repaste')
except ImportError:
    _ = lambda x: x

from .uploaders import Ptpb


def notify(irc, id, url):
    if url:
        irc.reply(_('{id:} was repasted as {url:}').
                  format(id=id, url=url))
    else:
        irc.reply(_('Failed to repaste {id:}, please repaste to a'
                    'saner pastebin manually.').format(id=id))


class PastebinCom(object):
    def repaste(irc, string):
        if 'pastebin.com' not in string:
            return

        ids = PastebinCom.get_ids(string)
        PastebinCom.repaste_ids(irc, ids)

    def get_ids(string):
        regex = r'pastebin\.com/(\w{8})'
        raw_regex = r'pastebin\.com/raw.php\?i=(\w{8})'

        ids = set()
        [ids.add(id) for id in re.findall(regex, string)]
        [ids.add(id) for id in re.findall(raw_regex, string)]

        return ids

    def repaste_ids(irc, ids):
        for id in ids:
            res = requests.get('https://pastebin.com/raw.php?i={}'.
                               format(id))

            url = Ptpb.paste(res.content)
            notify(irc, id, url)


class HastebinCom(object):
    def repaste(irc, string):
        if 'hastebin.com' not in string:
            return

        ids = HastebinCom.get_ids(string)
        HastebinCom.repaste_ids(irc, ids)

    def get_ids(string):
        regex = r'hastebin.com/(\w*)'

        ids = set()
        [ids.add(id) for id in re.findall(regex, string)
         if not id == 'raw']

        return ids

    def repaste_ids(irc, ids):
        for id in ids:
            res = requests.get('http://hastebin.com/raw/{id:}.hs'.
                               format(id=id))

            url = Ptpb.paste(res.content)
            notify(irc, id, url)


class Zerobin(object):
    def repaste(irc, string):
        if not re.search(r'https?://[\w.]*/\?\w*#[\w/+=]*', string):
            return

        urls = Zerobin.get_urls(string)
        Zerobin.repaste_urls(irc, urls)

    def get_urls(string):
        regex = r'(https?://[\w.]*/\?\w*#[\w/+=]*)'

        urls = set()
        [urls.add(url) for url in re.findall(regex, string)]

        return urls

    def repaste_urls(irc, urls):
        for url in urls:
            proc = subprocess.Popen(['getpaste', url],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, err = proc.communicate()

            if err == b'error: decryption failed\n':
                irc.reply(_('Failed to repaste as a zerobin paste, '
                            'please repaste to a saner pastebin manually.'
                            ))

            url = Ptpb.paste(out)
            notify(irc, 'zerobin paste', url)

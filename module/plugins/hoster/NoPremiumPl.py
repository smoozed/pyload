# -*- coding: utf-8 -*-

from module.plugins.internal.SimpleHoster import SimpleHoster
from module.common.json_layer import json_loads as loads


class NoPremiumPl(SimpleHoster):
    __name__ = "NoPremiumPl"
    __version__ = "0.01"
    __type__ = "hoster"

    __pattern__ = r"https?://direct\.nopremium\.pl.*"
    __description__ = "NoPremium.pl hoster plugin"
    __license__ = "GPLv3"
    __authors__ = [("goddie", "dev@nopremium.pl")]

    _api_url = "http://crypt.nopremium.pl"

    _api_query = {"site": "nopremium",
                  "output": "json",
                  "username": "",
                  "password": "",
                  "url": ""}

    _error_codes = {
        0: "[%s] Incorrect login credentials",
        1: "[%s] Not enough transfer to download - top-up your account",
        2: "[%s] Incorrect / dead link",
        3: "[%s] Error connecting to hosting, try again later",
        9: "[%s] Premium account has expired",
        15: "[%s] Hosting no longer supported",
        80: "[%s] Too many incorrect login attempts, account blocked for 24h"
    }

    _usr = False
    _pwd = False

    def setup(self):
        self.resumeDownload = True
        self.multiDL = True

    def get_username_password(self):
        if not self.account:
            self.fail(_("Please enter your %s account or deactivate this plugin") % "NoPremium.pl")
        else:
            data = self.account.getAccountData(self.user)
            self._usr = data['usr']
            self._pwd = data['pwd']

    def runFileQuery(self, url, mode=None):
        query = self._api_query.copy()
        query["username"] = self._usr
        query["password"] = self._pwd
        query["url"] = url

        if mode == "fileinfo":
            query['check'] = 2
            query['loc'] = 1
        self.logDebug(query)

        return self.load(self._api_url, post=query)

    def process(self, pyfile):
        self.get_username_password()
        try:
            data = self.runFileQuery(pyfile.url, 'fileinfo')
        except Exception:
            self.logDebug("runFileQuery error")
            self.tempOffline()

        try:
            parsed = loads(data)
        except Exception:
            self.logDebug("loads error")
            self.tempOffline()

        self.logDebug(parsed)

        if "errno" in parsed.keys():
            if parsed["errno"] in self._error_codes:
                # error code in known
                self.fail(self._error_codes[parsed["errno"]] % self.__name__)
            else:
                # error code isn't yet added to plugin
                self.fail(
                    parsed["errstring"]
                    or "Unknown error (code: %s)" % parsed["errno"]
                )

        if "sdownload" in parsed:
            if parsed["sdownload"] == "1":
                self.fail(
                    "Download from %s is possible only using NoPremium.pl webiste \
                    directly. Update this plugin." % parsed["hosting"])

        pyfile.name = parsed["filename"]
        pyfile.size = parsed["filesize"]

        try:
            result_dl = self.runFileQuery(pyfile.url, 'filedownload')
        except Exception:
            self.logDebug("runFileQuery error #2")
            self.tempOffline()

        self.download(result_dl, disposition=True)

# -*- coding: utf-8 -*-

from urllib import unquote

from module.plugins.internal.MultiHoster import MultiHoster, create_getInfo


class RehostTo(MultiHoster):
    __name__    = "RehostTo"
    __type__    = "hoster"
    __version__ = "0.18"

    __pattern__ = r'https?://.*rehost\.to\..+'

    __description__ = """Rehost.com hoster plugin"""
    __license__     = "GPLv3"
    __authors__     = [("RaNaN", "RaNaN@pyload.org")]


    def getFilename(self, url):
        return unquote(url.rsplit("/", 1)[1])


    def handlePremium(self):
        data = self.account.getAccountData(self.user)

        self.download("http://rehost.to/process_download.php",
                      get={'user': "cookie",
                           'pass': data['long_ses'],
                           'dl'  : self.pyfile.url},
                      disposition=True)


getInfo = create_getInfo(RehostTo)

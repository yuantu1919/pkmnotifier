import json
import ssl
import time
import urllib
from datetime import datetime
from geopy.distance import vincenty

from pkmid import pkmid


class Pokemon:
    def __init__(self, pkm):
        self.dis = pkm['dis']
        self.pid = pkm['id']
        self.pkmid = pkm['pokemonId']
        self.pkmname = pkmid[self.pkmid]
        self.exp = datetime.fromtimestamp(pkm['expiration_time'])
        self.pic = \
            "http://assets.pokemon.com/assets/cms2/img/pokedex/detail/%03d.png"
        self.pic = self.pic % self.pkmid

    def __lt__(self, other):
        return self.dis < other.dis

    def __str__(self):
        return "%s %dm %s" % (
            self.pkmname,
            self.dis,
            str(self.exp - datetime.now())[:-7],
        )


class PKMNotifier:
    def __init__(self, latitude=None, longitude=None, addr=None):
        if latitude and longitude:
            self.loc = (latitude, longitude)
        if addr:
            from geopy.geocoders import Nominatim
            gloc = Nominatim()
            loc = gloc.geocode(addr)
            print("Addr: ", loc.address)
            self.loc = (loc.latitude, loc.longitude)
        self.api_url = "https://pokevision.com/map/data/%lf/%lf" % self.loc
        self.url = "https://pokevision.com/#/@%lf,%lf" % self.loc
        self._sms_client = None
        self._notified_pids = set()

    def _send_sms(self, msg, img_url=None):
        if not self._sms_client:
            from twilio.rest import TwilioRestClient
            import config
            self._sms_client = TwilioRestClient(config.sid, config.token)
            self.to_number = config.to_number
            self.from_number = config.from_number
        self._sms_client.messages.create(
            to=self.to_number,
            from_=self.from_number,
            body=msg,
            media_url=img_url,
        )

    def get_pkm_list(self):
        req = urllib.request.Request(
            self.api_url,
            data=None,
            headers={'User-Agent': 'Mozilla/5.0'},
        )
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        lst = json.loads(
            urllib.request.urlopen(req, context=ctx).read().decode('utf-8'))
        self._pkm_list = []
        for pkm in lst['pokemon']:
            if pkm['pokemonId'] in pkmid:
                pkm['dis'] = int(round(vincenty(self.loc, (
                    pkm['latitude'], pkm['longitude'])).meters))
                self._pkm_list.append(Pokemon(pkm))
        self._pkm_list.sort()

    def update(self):
        self.get_pkm_list()
        msg = ''
        img_url = ''
        for e in self._pkm_list:
            if e.pid not in self._notified_pids and e.dis < self.scan_range:
                msg += str(e)+'\n'
                self._notified_pids.add(e.pid)
                if not img_url:
                    img_url = e.pic
        if msg:
            msg = '-\n------\n'+self.url+'\n\n'+msg
            self._send_sms(msg, img_url)
        print("Msg:" + msg)

    def run(self, cron_mode=False, sms=True, scan_range=100, time_interval=30):
        self.cron_mode = cron_mode
        self.sms = sms
        self.scan_range = scan_range
        if cron_mode:
            self.update()
        else:
            while (True):
                try:
                    self.update()
                    time.sleep(time_interval)
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    import config
    p = PKMNotifier(addr=config.addr)
    # OR:
    # p = PKMNotifier(latitude, longitude):
    p.run()

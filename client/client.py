from configparser import ConfigParser
from time import sleep
import requests
try:
    import winsound
except:
    winsound = None

class Client(object):

    def __init__(self):
        self.cfg = ConfigParser()
        self.cfg.read('config.ini')

    def beep(self):
        cfg = self.cfg['beep']
        if int(cfg['enabled']):
            if winsound is None:
                print('[!]: winsound could not be imported: Beeps disabled')
            else:
                winsound.Beep(cfg['frequency'], cfg['duration'])

    def query(self):
        cfg = self.cfg['polling']

        if int(cfg['debug']):
            print('.', end='')

        auth = (self.cfg['auth']['username'], self.cfg['auth']['password'])
        r = requests.get('http://%s' % cfg['host'], auth=auth)
        try:
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            if r.status_code == 401:
                print('[!] Invalid credentials: %s, %s' % auth)
                return False
            if int(cfg['debug']):
                print('[!] Polling error: %s' % e)
            return True

        self.dispatch(r.json())
        return True

    def dispatch(self, data):
        if data['count']:
            self.beep()
            print('\n\n[*] %d new notifications:' % data['count'])
            for i, note in enumerate(data['content']):
                print('    %d: %s' % (i + 1, note))

    def poll(self):
        cfg = self.cfg['polling']
        while True:
            if not self.query():
                break
            sleep(int(cfg['interval']))


if __name__ == '__main__':
    c = Client()
    c.poll()

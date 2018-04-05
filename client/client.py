from configparser import ConfigParser
from time import sleep
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
        if int(beepcfg['enabled']):
            if winsound is None:
                print('[!]: winsound could not be imported: Beeps disabled')
            else:
                winsound.Beep(beepcfg['frequency'], beepcfg['duration'])

    def query(self):
        cfg = self.cfg['polling']
        try:
            r = requests.get(cfg['host'])
        except requests.excetions.RequestException as e:
            if int(cfg['debug']):
                print('[!] Polling error: %s' % e)
            return
        self.dispatch(r.json())

    def dispatch(data):
        if data['count']:
            self.beep()
            print('[*] %d new notifications:' % data['count'])
            for i, note in enumerate(data['content']):
                print('   %d: %s' % (i + 1, note))

    def poll(self):
        cfg = self.cfg['polling']
        while True:
            self.query()
            sleep(cfg['interval'])


if __name__ == '__main__':
    c = Client()
    c.poll()

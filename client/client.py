import sys
from configparser import ConfigParser
from time import sleep

import requests

try:
    import winsound
except:
    winsound = None


def formatter(dict):
    try:
        if dict['content']:
            yield 'Content: %s' % dict['content']
        for att in dict['attachments']:
            yield 'Server: %s' % att['title']
            for field in att['fields']:
                yield '  * %s: %s' % (field['title'], field['value'])
    except KeyError as e:
        yield str(dict)


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
                winsound.Beep(int(cfg['frequency']), int(cfg['duration']))

    def query(self):
        cfg = self.cfg['polling']

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
            print('\n\n[*] %d new notification(s):' % data['count'])
            for i, content in enumerate(data['content']):
                print('    %d:----------------------' % i + 1)
                for msg in formatter(content):
                    print('    %s' % content)
        elif int(self.cfg['polling']['debug']):
            print('.', end='')
            sys.stdout.flush()

    def poll(self):
        cfg = self.cfg['polling']
        while True:
            if not self.query():
                break
            sleep(int(cfg['interval']))


if __name__ == '__main__':
    c = Client()
    c.poll()

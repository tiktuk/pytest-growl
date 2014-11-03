import time
import socket
import struct
from hashlib import md5
from io import BytesIO

try:
    import gntp.notifier
except ImportError:
    pass

_GROWL_UDP_PORT = 9887
_GROWL_VERSION = 1
_PACKET_TYPE_REGISTRATION = 0
_PACKET_TYPE_NOTIFICATION = 1


QUIET_MODE_INI='quiet_growl'
GROWL_CALLBACK_URL_INI='growl_url'

def pytest_addoption(parser):
    """Adds options to control growl notifications."""
    group = parser.getgroup('terminal reporting')
    group.addoption('--growl',
                    dest='growl',
                    default=True,
                    help='Enable Growl notifications.')
    parser.addini(QUIET_MODE_INI,
                  default=False,
                  help='Minimize notifications (only results).')
    parser.addini(GROWL_CALLBACK_URL_INI,
        default='',
        help='URL to open when clicking on single error notifications.'
    )


def pytest_sessionstart(session):
    if (session.config.option.growl
        and not session.config.getini(QUIET_MODE_INI)):
        send_growl(title="Session Begins At", message="%s" % time.strftime("%I:%M:%S %p"))


def pytest_terminal_summary(terminalreporter):
    if terminalreporter.config.option.growl:
        tr = terminalreporter
        quiet_mode = tr.config.getini(QUIET_MODE_INI)
        growl_callback_url = tr.config.getini(GROWL_CALLBACK_URL_INI)
        status = {}
        
        for key in tr.stats.keys():
            if key:  # There is an empty key for setup/teardown calls
                status[key] = len(tr.stats[key])
                
                for test_report in tr.stats[key]:
                    if key in ('failed', 'error'):
                        entry = test_report.longrepr.reprtraceback.reprentries[0]
                        callback_url = None
                        
                        if growl_callback_url:
                            fspath = '%s/%s' % (tr.curdir, entry.reprfileloc.path)
                            lineno = entry.reprfileloc.lineno
                            callback_url=growl_callback_url.format(path=fspath, lineno=lineno)
                            
                        send_growl(
                            title=key.title(),
                            message='\n'.join(entry.lines),
                            callback=callback_url
                        )
        
        message_to_send = ', '.join(
            ["%d %s " % (status[key], key.title()) for key in status]
        )
        
        if len(status) == 0:
            send_growl(title="Alert", message="No Tests Ran")
        
        send_growl(title="Tests Complete", message=message_to_send)
        
        if not quiet_mode:
            send_growl(title="Session Ended At", message="%s" % time.strftime("%I:%M:%S %p"))


class SignedStructStream(object):
    def __init__(self):
        super(SignedStructStream, self).__init__()
        self._stream = BytesIO()
        self._hash = md5()

    def writeBuffer(self, buff, sign=True):
        if sign:
            self._hash.update(buff)
        self._stream.write(buff)

    def sign(self):
        self.writeBuffer(self._hash.digest(), sign=False)

    def write(self, format, *data):
        packed = struct.pack(format, *data)
        self.writeBuffer(packed)

    def getvalue(self):
        return self._stream.getvalue()

    def gethash(self):
        return self._hash.digest()


def brp(application_name, notifications):
    returned = SignedStructStream()
    returned.write("b", _GROWL_VERSION)
    returned.write("b", _PACKET_TYPE_REGISTRATION)
    returned.write("!H", len(application_name))
    returned.write("bb", len(notifications), len(notifications))
    returned.writeBuffer(application_name.encode('utf-8'))
    for notification in notifications:
        returned.write("!H", len(notification))
        returned.writeBuffer(notification.encode('utf-8'))
    for i in range(len(notifications)):
        returned.write("b", i)
    returned.sign()
    return returned.getvalue()


def bnp(application_name, notification_name, title, message, priority, sticky):
    flags = (priority & 0x07) * 1
    returned = SignedStructStream()
    returned.write("!BBHHHHH", 1, 1, flags, len(notification_name), len(title), len(message), len(application_name),)
    for x in (notification_name, title, message, application_name):
        returned.writeBuffer(x.encode('utf-8'))
    returned.sign()
    return returned.getvalue()


def send_growl(message='', title='', callback=None, _socket=socket.socket, _bnp=bnp, _brp=brp):
    if 'gntp' in globals():
        gntp.notifier.mini(message, title=title, applicationName='pytest', noteType='Notification', callback=callback)
    else:
        s = _socket(socket.AF_INET, socket.SOCK_DGRAM)
        reg_packet = _brp(application_name="pytest", notifications=["Notification"])
        s.sendto(reg_packet, ("127.0.0.1", _GROWL_UDP_PORT))
        notification = _bnp(
            priority=4,
            message=message,
            title=title,
            notification_name="Notification",
            application_name="pytest",
            sticky=False)
        s.sendto(notification, ("127.0.0.1", _GROWL_UDP_PORT))
        s.close()


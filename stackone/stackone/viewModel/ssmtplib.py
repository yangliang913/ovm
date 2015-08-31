import smtplib
import socket
__all__ = ['SMTPSSLException', 'SMTP_SSL']
SSMTP_PORT = 465
class SMTPSSLException(smtplib.SMTPException):
	"""Base class for exceptions resulting from SSL negotiation."""
class SMTP_SSL(smtplib.SMTP):
	certfile = None
	keyfile = None
	def __init__(self, host='', port=0, local_hostname=None, keyfile=None, certfile=None):
		self.certfile = certfile
		self.keyfile = keyfile
		smtplib.SMTP.__init__(self, host, port, local_hostname)

	def connect(self, host='localhost', port=0):
		if not port and (host.find(':') == host.rfind(':')):
			i = host.rfind(':')
			if i >= 0:
				host, port = host[:i], host[i+1:]
				try: port = int(port)
				except ValueError:
					raise socket.error, "nonnumeric port"
		if not port: port = SSMTP_PORT
		if self.debuglevel > 0: print>>stderr, 'connect:', (host, port)
		msg = "getaddrinfo returns an empty list"
		self.sock = None
		for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
			af, socktype, proto, canonname, sa = res
			try:
				self.sock = socket.socket(af, socktype, proto)
				if self.debuglevel > 0: print>>stderr, 'connect:', (host, port)
				self.sock.connect(sa)
				# MB: Make the SSL connection.
				sslobj = socket.ssl(self.sock, self.keyfile, self.certfile)
			except socket.error, msg:
				if self.debuglevel > 0: 
					print>>stderr, 'connect fail:', (host, port)
				if self.sock:
					self.sock.close()
				self.sock = None
				continue
			break
		if not self.sock:
			raise socket.error, msg
		self.sock = smtplib.SSLFakeSocket(self.sock, sslobj)
		self.file = smtplib.SSLFakeFile(sslobj);

		(code, msg) = self.getreply()
		if self.debuglevel > 0: print>>stderr, "connect:", msg
		return (code, msg)

	def setkeyfile(self, keyfile):
		self.keyfile = keyfile

	def setcertfile(self, certfile):
		self.certfile = certfile

	def starttls(self):
		raise SMTPSSLException, 'Cannot perform StartTLS within SSL session.'




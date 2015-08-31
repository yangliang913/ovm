import sys
import types
class IPint():
	def __init__(self, data, ipversion=0, make_net=0):
		self.NoPrefixForSingleIp = 1
		self.WantPrefixLen = None
		netbits = 0
		prefixlen = -1
		if isinstance(data, (int, long)):
			self.ip = long(data)
			if ipversion == 0:
				if self.ip < 4294967296:
					ipversion = 4
				else:
					ipversion = 6
			if ipversion == 4:
				if self.ip > 4294967295:
					raise ValueError("IPv4 Addresses can't be larger than 0xffffffffffffffffffffffffffffffff: %x" % self.ip)
				prefixlen = 32
			else:
				if ipversion == 6:
					if self.ip:
						raise ValueError("IPv6 Addresses can't be larger than 0xffffffffffffffffffffffffffffffff: %x" % self.ip)
					prefixlen = 128
				else:
					raise ValueError('only IPv4 and IPv6 supported')
			self._ipversion = ipversion
			self._prefixlen = prefixlen
		else:
			if isinstance(data, IPint):
				self._ipversion = data._ipversion
				self._prefixlen = data._prefixlen
				self.ip = data.ip
			else:
				if isinstance(data, (str, unicode)):
					x = data.split('-')
					if len(x) == 2:
						ip,last = x
						self.ip,parsedVersion = parseAddress(ip)
						if parsedVersion != 4:
							raise ValueError('first-last notation only allowed for IPv4')
						last,lastversion = parseAddress(last)
						if lastversion != 4:
							raise ValueError('last address should be IPv4, too')
						if last < self.ip:
							raise ValueError('last address should be larger than first')
						size = last - self.ip
						netbits = _count1Bits(size)
						if IP('%s/%s' % (ip, 32 - netbits)).broadcast().int() != last:
							raise ValueError('the range %s is not on a network boundary.' % data)
					else:
						if len(x) == 1:
							x = data.split('/')
							if len(x) == 1:
								ip = x[0]
								prefixlen = -1
							else:
								if len(x) > 2:
									raise ValueError("only one '/' allowed in IP Address")
								else:
									ip,prefixlen = x
									if prefixlen.find('.') != -1:
										netmask,vers = parseAddress(prefixlen)
										if vers != 4:
											raise ValueError('netmask must be IPv4')
										prefixlen = _netmaskToPrefixlen(netmask)
						else:
							if len(x) > 2:
								raise ValueError("only one '-' allowed in IP Address")
							else:
								raise ValueError("can't parse")
					self.ip,parsedVersion = parseAddress(ip)
					if ipversion == 0:
						ipversion = parsedVersion
					if prefixlen == -1:
						if ipversion == 4:
							prefixlen = 32 - netbits
						else:
							if ipversion == 6:
								prefixlen = 128 - netbits
							else:
								raise ValueError('only IPv4 and IPv6 supported')
					self._ipversion = ipversion
					self._prefixlen = int(prefixlen)
					if make_net:
						self.ip = self.ip & _prefixlenToNetmask(self._prefixlen, self._ipversion)
					if not _checkNetaddrWorksWithPrefixlen(self.ip, self._prefixlen, self._ipversion):
						raise ValueError('%s has invalid prefix length (%s)' % (repr(self), self._prefixlen))
				else:
					raise TypeError('Unsupported data type: %s' % type(data))

	def int(self):
		return self.ip

	def version(self):
		return self._ipversion

	def prefixlen(self):
		return self._prefixlen

	def net(self):
		return self.int()

	def broadcast(self):
		return self.int() + self.len() - 1

	def _printPrefix(self, want):
		if self._ipversion == 4 and self._prefixlen == 32 or self._ipversion == 6 and self._prefixlen == 128:
			if self.NoPrefixForSingleIp:
				want = 0
		if want == None:
			want = self.WantPrefixLen
			if want == None:
				want = 1
		if want:
			if want == 2:
				netmask = self.netmask()
				if not isinstance(netmask, (int, long)):
					netmask = netmask.int()
				return '/%s' % intToIp(netmask, self._ipversion)
			if want == 3:
				return '-%s' % intToIp(self.ip + self.len() - 1, self._ipversion)
			return '/%d' % self._prefixlen
		else:
			return ''

	def strBin(self, wantprefixlen=None):
		if self._ipversion == 4:
			bits = 32
		else:
			if self._ipversion == 6:
				bits = 128
			else:
				raise ValueError('only IPv4 and IPv6 supported')
		if self.WantPrefixLen == None and wantprefixlen == None:
			wantprefixlen = 0
		ret = _intToBin(self.ip)
		return '0' * (bits - len(ret)) + ret + self._printPrefix(wantprefixlen)

	def strCompressed(self, wantprefixlen=None):
		if self.WantPrefixLen == None and wantprefixlen == None:
			wantprefixlen = 1
		if self._ipversion == 4:
			return self.strFullsize(wantprefixlen)
		if self.ip >> 32 == 65535:
			ipv4  = intToIp(self.ip & 4294967295, 4)
			text = '::ffff:' + ipv4 + self._printPrefix(wantprefixlen)
			return text
		hextets = [int(x, 16) for x in self.strFullsize(0).split(':')]
		followingzeros = [0] * 8
		for i in xrange(len(hextets)):
			followingzeros[i] = _countFollowingZeros(hextets[i:])
		compressionpos = followingzeros.index(max(followingzeros))
		if max(followingzeros) > 1:
			hextets = [x for x in self.strNormal(0).split(':')]
			while compressionpos < len(hextets) and hextets[compressionpos] == '0':
				del hextets[compressionpos]
			hextets.insert(compressionpos, '')
			if compressionpos + 1 >= len(hextets):
				hextets.append('')
			if compressionpos == 0:
				hextets = [''] + hextets
			return ':'.join(hextets) + self._printPrefix(wantprefixlen)
		else:
			return self.strNormal(0) + self._printPrefix(wantprefixlen)



	def strNormal(self, wantprefixlen=None):
		#[NODE: 54]
		if self.WantPrefixLen == None and wantprefixlen == None:
			wantprefixlen = 1
		if self._ipversion == 4:
			ret = self.strFullsize(0)
		elif self._ipversion == 6:
			ret = ':'.join([hex(x)[2:] for x in [int(x, 16) for x in self.strFullsize(0).split(':')]])
		else:
			raise ValueError('only IPv4 and IPv6 supported')
		return ret + self._printPrefix(wantprefixlen)


	def strFullsize(self, wantprefixlen=None):
		if self.WantPrefixLen == None and wantprefixlen == None:
			wantprefixlen = 1
		return intToIp(self.ip, self._ipversion).lower() + self._printPrefix(wantprefixlen)

	def strHex(self, wantprefixlen=None):
		if self.WantPrefixLen == None and wantprefixlen == None:
			wantprefixlen = 0
		x = hex(self.ip)
		if x[-1] == 'L':
			x = x[:-1]
		return x.lower() + self._printPrefix(wantprefixlen)

	def strDec(self, wantprefixlen=None):
		if self.WantPrefixLen == None and wantprefixlen == None:
			wantprefixlen = 0
		x = str(self.ip)
		if x[-1] == 'L':
			x = x[:-1]
		return x + self._printPrefix(wantprefixlen)

	def iptype(self):
		if self._ipversion == 4:
			iprange = IPv4ranges
		elif self._ipversion == 6:
			iprange = IPv6ranges
		else:
			raise ValueError('only IPv4 and IPv6 supported')
		bits = self.strBin()
		for i in xrange(len(bits), 0, -1):
			if bits[:i] in iprange:
				return iprange[bits[:i]]
		return 'unknown'

	def netmask(self):
		if self._ipversion == 4:
			locallen = 32 - self._prefixlen
		elif self._ipversion == 6:
			locallen = 128 - self._prefixlen
		else:
			raise ValueError('only IPv4 and IPv6 supported')
		return 2 ** self._prefixlen - 1 << locallen

	def strNetmask(self):
		if self._ipversion == 4:
			locallen = 32 - self._prefixlen
			return intToIp(2 ** self._prefixlen - 1 << locallen, 4)
		elif self._ipversion == 6:
			locallen = 128 - self._prefixlen
			return '/%d' % self._prefixlen
		raise ValueError('only IPv4 and IPv6 supported')

	def len(self):
		if self._ipversion == 4:
			locallen = 32 - self._prefixlen
		elif self._ipversion == 6:
			locallen = 128 - self._prefixlen
		else:
			raise ValueError('only IPv4 and IPv6 supported')
		return 2 ** locallen

	def __nonzero__(self):
		return True

	def __len__(self):
		return int(self.len())

	def __getitem__(self, key):
		if not isinstance(key, (int, long)):
			raise TypeError
		if key < 0:
			if abs(key) <= self.len():
				key = self.len() - abs(key)
			else:
				raise IndexError
		else:
			if key >= self.len():
				raise IndexError
		return self.ip + long(key)

	def __contains__(self, item):
		item = IP(item)
		if item.ip >= self.ip and item.ip < self.ip + self.len() - item.len() + 1:
			return True
		return False

	def overlaps(self, item):
		item = IP(item)
		if item.ip >= self.ip and item.ip < self.ip + self.len():
			return 1
		elif self.ip >= item.ip and self.ip < item.ip + item.len():
			return -1
		else:
			return 0

	def __str__(self):
		return self.strCompressed()

	def __repr__(self):
		return "IPint('%s')" % self.strCompressed(1)

	def __cmp__(self, other):
		if self._prefixlen < other.prefixlen():
			return other.prefixlen() - self._prefixlen
		if self._prefixlen > other.prefixlen():
			return other.prefixlen() - self._prefixlen
		if self.ip < other.ip:
			return -1
		if self.ip > other.ip:
			return 1
		if self._ipversion != other._ipversion:
			if self._ipversion < other._ipversion:
				return -1
			if self._ipversion > other._ipversion:
				return 1
			return 0
		else:
			return 0

	def __eq__(self, other):
		return self.__cmp__(other) == 0

	def __lt__(self, other):
		return self.__cmp__(other) < 0

	def __hash__(self):
		thehash = int(-1)
		ip = self.ip
		while ip > 0:
			thehash = thehash ^ ip & 2147483647
			ip = ip >> 32
		thehash = thehash ^ self._prefixlen
		return int(thehash)



class IP(IPint):
	def net(self):
		return IP(IPint.net(self), ipversion = self._ipversion)

	def broadcast(self):
		return IP(IPint.broadcast(self))

	def netmask(self):
		return IP(IPint.netmask(self), ipversion = self._ipversion)

	def _getIPv4Map(self):
		if self._ipversion != 6:
			return None
		if self.ip >> 32 != 65535:
			return None
		ipv4 = self.ip & 4294967295
		if self._prefixlen != 128:
			ipv4 = '%s/%s' % (ipv4, 32 - 128 - self._prefixlen)
		return IP(ipv4, 4)

	def reverseNames(self):
		if self._ipversion == 4:
			ret = []
			if self.len() < 2**8:
				for x in self:
					ret.append(x.reverseName())
			elif self.len() < 2**16:
				for i in xrange(0, self.len(), 2**8):
					ret.append(self[i].reverseName()[2:])
			elif self.len() < 2**24:
				for i in xrange(0, self.len(), 2**16):
					ret.append(self[i].reverseName()[4:])
			else:
				for i in xrange(0, self.len(), 2**24):
					ret.append(self[i].reverseName()[6:])
			return ret
		elif self._ipversion == 6:
			ipv4 = self._getIPv4Map()
			if ipv4 is not None:
				return ipv4.reverseNames()
			s = hex(self.ip)[2:].lower()
			if s[-1] == 'l':
				s = s[:-1]
			if self._prefixlen % 4 != 0:
				raise NotImplementedError("can't create IPv6 reverse names at sub nibble level")
			s = list(s)
			s.reverse()
			s = '.'.join(s)
			first_nibble_index = int(32 - self._prefixlen // 4) * 2
			return ['%s.ip6.arpa.' % s[first_nibble_index:]]
		else:
			raise ValueError('only IPv4 and IPv6 supported')

	def reverseName(self):
		if self._ipversion == 4:
			s = self.strFullsize(0)
			s = s.split('.')
			s.reverse()
			first_byte_index = int(4 - self._prefixlen // 8)
			if self._prefixlen % 8 != 0:
				nibblepart = '%s-%s' % (s[3 - self._prefixlen // 8], intToIp(self.ip + self.len() - 1, 4).split('.')[-1])
				if nibblepart[-1] == 'l':
					nibblepart = nibblepart[:-1]
				nibblepart += '.'
			else:
				nibblepart = ''
			s = '.'.join(s[first_byte_index:])
			return '%s%s.in-addr.arpa.' % (nibblepart, s)
		elif self._ipversion == 6:
			ipv4 = self._getIPv4Map()
			if ipv4 is not None:
				return ipv4.reverseName()
			s = hex(self.ip)[2:].lower()
			if s[-1] == 'l':
				s = s[:-1]
			if self._prefixlen % 4 != 0:
				nibblepart = '%s-%s' % (s[self._prefixlen:], hex(self.ip + self.len() - 1)[2:].lower())
				if nibblepart[-1] == 'l':
					nibblepart = nibblepart[:-1]
				nibblepart += '.'
			else:
				nibblepart = ''
			s = list(s)
			s.reverse()
			s = '.'.join(s)
			first_nibble_index = int(32 - self._prefixlen // 4) * 2
			return '%s%s.ip6.arpa.' % (nibblepart, s[first_nibble_index:])
		else:
			raise ValueError('only IPv4 and IPv6 supported')

	def make_net(self, netmask):
		if '/' in str(netmask):
			raise ValueError('invalid netmask (%s)' % netmask)
		return IP('%s/%s' % (self, netmask), True)

	def __getitem__(self, key):
		return IP(IPint.__getitem__(self, key))

	def __repr__(self):
		return "IP('%s')" % self.strCompressed(1)

	def __add__(self, other):
		if self.prefixlen() != other.prefixlen():
			raise ValueError('Only networks with the same prefixlen can be added.')
		if self.prefixlen() < 1:
			raise ValueError("Networks with a prefixlen longer than /1 can't be added.")
		if self.version() != other.version():
			raise ValueError('Only networks with the same IP version can be added.')
		if self > other:
			return other.__add__(self)
		else:
			ret = IP(self.int())
			ret._prefixlen = self.prefixlen() - 1
			return ret



#def _parseAddressIPv6(ipstr):
#	#[NODE: 0]
#	items = []
#	index = 0
#	fill_pos = None
#
#	#[NODE: 39]
#	text = ipstr[index:]
#	if text.startswith('::'):
#		text.startswith('::')
#		if fill_pos is not None:
#			raise ValueError("%r: Invalid IPv6 address: more than one '::'" % ipstr)
#		fill_pos = len(items)
#		index += 2
#		continue
#	else:
#		text.startswith('::')
#	pos = text.find(':')
#	if pos == 0:
#		raise ValueError('%r: Invalid IPv6 address' % ipstr)
#
#	#[NODE: 188]
#	items.append(text[:pos])
#	if text[pos:pos + 2] == '::':
#		index += pos
#	else:
#		index += pos + 1
#
#	#[NODE: 276]
#	raise ValueError('%r: Invalid IPv6 address' % ipstr)
#
#	#[NODE: 296]
#	continue
#
#	#[NODE: 300]
#	items.append(text)
#	break
#
#	#[NODE: 623]
#	item = int(item, 16)
#	if 0 <= item:
#		pass
#	else:
#		item
#	error = not 0 <= item
#
#	#[NODE: 672]
#	except ValueError:
#		error = True
#
#	#[NODE: 697]
#	if error:
#		error
#		raise ValueError('%r: Invalid IPv6 address: invalid hexlet %r' % (ipstr, item))
#	else:
#		error
#	value = (value << 16) + item
#	index += 1
#	return value
#
#	#[NODE: 320&326]
#	if items and '.' in items[-1]:
#		if fill_pos is not None and not fill_pos <= len(items) - 1:
#			not fill_pos <= len(items) - 1
#			raise ValueError("%r: Invalid IPv6 address: '::' after IPv4" % ipstr)
#		value = parseAddress(items[-1])[0]
#		items = items[:-1] + ['%04x' % (value >> 16), '%04x' % (value & 65535)]
#	else:
#		items
#	if fill_pos is not None:
#		diff = 8 - len(items)
#		if diff <= 0:
#			raise ValueError("%r: Invalid IPv6 address: '::' is not needed" % ipstr)
#		items = items[:fill_pos] + ['0'] * diff + items[fill_pos:]
#	if len(items) != 8:
#		raise ValueError('%r: Invalid IPv6 address: should have 8 hextets' % ipstr)
#	value = 0
#	index = 0
#	for item in items:
#		pass

def parseAddress(ipstr):
	if ipstr.startswith('0x'):
		ret = long(ipstr[2:], 16)
		if ret > 0xffffffffffffffffffffffffffffffffL:
			raise ValueError, "%r: IP Address can't be bigger than 2^128" % (ipstr)
		if ret < 0x100000000L:
			return (ret, 4)
		else:
			return (ret, 6)
			
	if ipstr.find(':') != -1:
		# assume IPv6
		if ipstr.find(':::') != -1:
			raise ValueError, "%r: IPv6 Address can't contain ':::'" % (ipstr)
		hextets = ipstr.split(':')
		if ipstr.find('.') != -1:
			# this might be a mixed address like '0:0:0:0:0:0:13.1.68.3'
			(v4, foo) = parseAddress(hextets[-1])
			assert foo == 4
			del(hextets[-1])
			hextets.append(hex(v4 >> 16)[2:-1])
			hextets.append(hex(v4 & 0xffff)[2:-1])
		if len(hextets) > 8:
			raise ValueError, "%r: IPv6 Address with more than 8 hexletts" % (ipstr)
		if len(hextets) < 8:
			if '' not in hextets:
				raise ValueError, "%r IPv6 Address with less than 8 hexletts and without '::'" % (ipstr)
			# catch :: at the beginning or end
			if hextets.index('') < len(hextets) - 1 and hextets[hextets.index('')+1] == '':
				hextets.remove('')
			# catch '::'
			if hextets.index('') < len(hextets) - 1 and hextets[hextets.index('')+1] == '':
				hextets.remove('')
			
			for foo in range(9-len(hextets)):
				hextets.insert(hextets.index(''), '0')
			hextets.remove('')
			if '' in hextets:
				raise ValueError, "%r IPv6 Address may contain '::' only once" % (ipstr)
		if '' in hextets:
			raise ValueError, "%r IPv6 Address may contain '::' only if it has less than 8 hextets" % (ipstr)
		num = ''
		for x in hextets:
			if len(x) < 4:
				x = ((4 - len(x)) * '0') + x
			if int(x, 16) < 0 or int(x, 16) > 0xffff: 
				raise ValueError, "%r: single hextet must be 0 <= hextet <= 0xffff which isn't true for %s" % (ipstr, x)
			num += x
		return (long(num, 16), 6)

	elif len(ipstr) == 32:
		# assume IPv6 in pure hexadecimal notation
		return (long(ipstr, 16), 6)
	
	elif  ipstr.find('.') != -1 or (len(ipstr) < 4 and int(ipstr) < 256):
		# assume IPv4  ('127' gets interpreted as '127.0.0.0')
		bytes = ipstr.split('.')
		if len(bytes) > 4:
			raise ValueError, "IPv4 Address with more than 4 bytes"
		bytes += ['0'] * (4 - len(bytes))
		bytes = [long(x) for x in bytes]
		for x in bytes:
			if x > 255 or x < 0:
				raise ValueError, "%r: single byte must be 0 <= byte < 256" % (ipstr)
		return ((bytes[0] << 24) + (bytes[1] << 16) + (bytes[2] << 8) + bytes[3], 4)

	else:
		# we try to interprete it as a decimal digit -
		# this ony works for numbers > 255 ... others
		# will be interpreted as IPv4 first byte
		ret = long(ipstr)
		if ret > 0xffffffffffffffffffffffffffffffffL:
			raise ValueError, "IP Address cant be bigger than 2^128"
		if ret <= 0xffffffffL:
			return (ret, 4)
		else:
			return (ret, 6)



def intToIp(ip, version):
	ip = long(ip)
	if ip < 0:
		raise ValueError("IPs can't be negative: %d" % ip)
	ret = ''
	if version == 4:
		if ip > 4294967295:
			raise ValueError("IPv4 Addresses can't be larger than 0xffffffff: %s" % hex(ip))
		for l in xrange(4):
			ret = str(ip & 255) + '.' + ret
			ip = ip >> 8
		ret = ret[:-1]
	else:
		if version == 6:
			if ip:
				raise ValueError("IPv6 Addresses can't be larger than 0xffffffffffffffffffffffffffffffff: %s" % hex(ip))
			if sys.hexversion >= 50331648:
				l = hex(ip)[2:]
			else:
				l = hex(ip)[2:-1]
			l = l.zfill(32)
			for x in xrange(1, 33):
				ret = l[-x] + ret
				if x % 4 == 0:
					ret = ':' + ret
			ret = ret[1:]
		else:
			raise ValueError('only IPv4 and IPv6 supported')
	return ret

def _ipVersionToLen(version):
	if version == 4:
		return 32
	if version == 6:
		return 128
	raise ValueError('only IPv4 and IPv6 supported')

def _countFollowingZeros(l):
	if len(l) == 0:
		return 0
	if l[0] != 0:
		return 0
	else:
		return 1 + _countFollowingZeros(l[1:])

def _intToBin(val):
	if val < 0:
		raise ValueError('Only positive values allowed')
	s = hex(val).lower()
	ret = ''
	if s[-1] == 'l':
		s = s[:-1]
	for x in s[2:]:
		ret += _BitTable[x]
	while ret[0] == '0' and len(ret) > 1:
		ret = ret[1:]
	return ret

def _count1Bits(num):
	ret = 0
	while num > 0:
		num = num >> 1
		ret += 1
	return ret

def _count0Bits(num):
	num = long(num)
	if num < 0:
		raise ValueError, "Only positive Numbers please: %s" % (num)
	ret = 0
	while num > 0:
		if num & 1 == 1:
			break
		num = num >> 1
		ret += 1
	return ret 

def _checkPrefix(ip, prefixlen, version):
	bits = _ipVersionToLen(version)
	if prefixlen < 0 or prefixlen > bits:
		return None
	if ip == 0:
		zbits = bits + 1
	else:
		zbits = _count0Bits(ip)
	if zbits < bits - prefixlen:
		return 0
	else:
		return 1

def _checkNetmask(netmask, masklen):
	num = long(netmask)
	bits = masklen
	while num & 1 == 0 and bits != 0:
		num = num >> 1
		bits -= 1
		if bits == 0:
			break
	while bits > 0:
		if num & 1 == 0:
			raise ValueError("Netmask %s can't be expressed as an prefix." % hex(netmask))
		num = num >> 1
		bits -= 1

def _checkNetaddrWorksWithPrefixlen(net, prefixlen, version):
	return net & _prefixlenToNetmask(prefixlen, version) == net

def _netmaskToPrefixlen(netmask):
	netlen = _count0Bits(netmask)
	masklen = _count1Bits(netmask)
	_checkNetmask(netmask, masklen)
	return masklen - netlen

def _prefixlenToNetmask(prefixlen, version):
	if prefixlen == 0:
		return 0
	elif prefixlen < 0:
		raise ValueError('Prefixlen must be > 0')
	return (2 << prefixlen - 1) - 1 << _ipVersionToLen(version) - prefixlen


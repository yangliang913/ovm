import Basic
from xml.dom import minidom
class ApplianceEntryVO():
	def __init__(self, xml_string):
		self.image_store = Basic.getImageStore()
		self.xml_string = xml_string
		self.xml_dom = minidom.parseString(self.xml_string)

	def entry_map(self):
		nodeList = self.xml_dom.getElementsByTagName('Appliance')
		appliance_entry = {}
		if nodeList._get_length() > 0L:
			xmlNode = nodeList.item(0L)
			appliance_entry['PAE'] = xmlNode.getAttribute('PAE')
			appliance_entry['arch'] = xmlNode.getAttribute('arch')
			appliance_entry['archive'] = xmlNode.getAttribute('archive')
			appliance_entry['compressed'] = xmlNode.getAttribute('compressed')
			appliance_entry['description'] = xmlNode.getAttribute('description')
			appliance_entry['filename'] = xmlNode.getAttribute('filename')
			appliance_entry['href'] = xmlNode.getAttribute('href')
			appliance_entry['id'] = xmlNode.getAttribute('id')
			appliance_entry['installed_size'] = xmlNode.getAttribute('installed_size')
			appliance_entry['is_hvm'] = xmlNode.getAttribute('is_hvm')
			appliance_entry['link'] = xmlNode.getAttribute('link')
			appliance_entry['platform'] = xmlNode.getAttribute('platform')
			appliance_entry['popularity_score'] = xmlNode.getAttribute('popularity_score')
			appliance_entry['provider'] = xmlNode.getAttribute('provider')
			appliance_entry['provider_id'] = xmlNode.getAttribute('provider_id')
			appliance_entry['provider_logo_url'] = xmlNode.getAttribute('provider_logo_url')
			appliance_entry['provider_url'] = xmlNode.getAttribute('provider_url')
			appliance_entry['short_description'] = xmlNode.getAttribute('short_description')
			appliance_entry['size'] = xmlNode.getAttribute('size')
			appliance_entry['title'] = xmlNode.getAttribute('title')
			appliance_entry['type'] = xmlNode.getAttribute('type')
			appliance_entry['updated'] = xmlNode.getAttribute('updated')
		import pprint
		print 'appliance_entry in parsing',
		pprint.pprint(appliance_entry)
		return appliance_entry



class ServiceInfo():
	def __init__(self, return_code, svc_name):
		self.return_code = return_code
		self.svc_name = svc_name

	def toXml(self, doc):
		xmlNode = doc.createElement(self.svc_name)
		xmlNode.setAttribute('returnCode', str(self.return_code))
		return xmlNode




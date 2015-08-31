class ImageInfoVO():
    def __init__(self, image):
        self.image = image

    def toXml(self, xml):
        image_info_xml = xml.createElement('ImageInfo')
        image_info_xml.setAttribute('name', self.image.get_name())
        image_info_xml.setAttribute('id', self.image.get_id())
        image_info_xml.setAttribute('platform', self.image.get_platform())
        image_info_xml.setAttribute('location', self.image.get_location())
        return image_info_xml



class ImageGroupInfoVO():
    def __init__(self, image_group):
        self.image_group = image_group

    def toXml(self, xml):
        image_group_xml = xml.createElement('ImageInfo')
        image_group_xml.setAttribute('name', self.image_group.get_name())
        image_group_xml.setAttribute('id', self.image_group.get_id())
        return image_group_xml




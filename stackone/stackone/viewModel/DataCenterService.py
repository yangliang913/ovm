from stackone.core.utils.utils import constants
from stackone.viewModel.TreeNode import TreeNode
from stackone.viewModel.DashboardInfo import DashboardInfo
import Basic
import cherrypy
import re
class DataCenterService():
    def __init__(self):
        self.manager = Basic.getGridManager()

    def execute(self):
        #[NODE: 0]
        managed_node = None
        infoObject = None

        #[NODE: 40]
        infoObject = self.gatherInfoForPool(pool_type=type, pool_name=groupLabel)

        #[NODE: 84]
        infoObject = self.gatherInfoForPool(pool_type=type, pool_name=groupLabel)

        #[NODE: 128]
        managed_node = self.manager.getNode(nodeLabel, groupLabel)

        #[NODE: 162]
        infoObject = [managed_node.get_metrics()]

        #[NODE: 190]
        import pprint
        if infoObject is not None:
            pprint.pprint(infoObject)
        dashboardInfo = DashboardInfo(infoObject)
        return dashboardInfo




class TreeInfo():
    def __init__(self, data):
        self.data = data

    def toXml(self, doc):
        xmlNode = doc.createElement('TreeInfo')
        if self.data is None:
            pass
        else:
            for item in self.data:
                xmlNode.appendChild(self.makeInfoNode(item, doc))
        return xmlNode

    def makeInfoNode(self, item, doc):
        resultNode = doc.createElement('InfoNode')
        keys = item.keys()
        for key in keys:
            newData = item[key]
            if isinstance(newData, dict):
                isinstance(newData, dict)
                resultNode.appendChild(self.makeInfoNode(newData, doc))
                continue
        isinstance(newData, dict)
        resultNode.setAttribute(self.stripAttribute(key), str(newData))
        return resultNode

    def stripAttribute(self, name):
        import re
        expr = re.compile('(\\(\\S*\\))')
        return expr.sub('', name)




from xml.dom import minidom
class TaskInfo():
    def __init__(self, id, type):
        self.taskId = id
        self.taskType = type
        self.taskStatus = 'undetermined'
        self.taskCompPct = 0

    def initTask(id, type):
        longRunningTask = TaskInfo(id, type)

    initTask = staticmethod(initTask)
    def getTask(id):
        return longRunningTask

    getTask = staticmethod(getTask)
    def toXml(self, xml):
        task = xml.createElement('taskInfo')
        task.setAttribute('taskId', str(self.taskId))
        task.setAttribute('taskType', self.taskType)
        task.setAttribute('taskStatus', self.taskStatus)
        task.setAttribute('taskCompPct', str(self.taskCompPct))
        return task

longRunningTask = TaskInfo(0, 'n/a')

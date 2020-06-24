#---------------------------------------
#   Import Libraries
#---------------------------------------
import clr, System, json, codecs, os, re

for asm in System.AppDomain.CurrentDomain.GetAssemblies(): 
    if "AnkhBotR2" in str(asm):
        clr.AddReference(asm)
        import AnkhBotR2
        break

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = "Queue Extensions"
Website = "twitch.tv/encryptedthoughts"
Description = "Extends existing streamlabs queue functionality."
Creator = "EncryptedThoughts"
Version = "1.0.0"

# ---------------------------------------
#	Set Variables
# ---------------------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMe = os.path.join(os.path.dirname(__file__), "README.md")
ScriptSettings = None
Queue = None

# ---------------------------------------
#	Script Classes
# ---------------------------------------
class Settings(object):
    def __init__(self, SettingsFile=None):
        if SettingsFile and os.path.isfile(SettingsFile):
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        else:
            self.EnableDebug = True

    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

    def Save(self, SettingsFile):
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(SettingsFile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------
def Init():
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)
    ScriptSettings.Save(SettingsFile)

    global Queue
    Queue = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.Queue

    return

# ---------------------------------------
# Chatbot Save Settings Function
# ---------------------------------------
def ReloadSettings(jsondata):
    ScriptSettings.Reload(jsondata)
    return

def Execute(data):
    ChangeQueueStatus()
    UpdateQueue()
    return

def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):

    regex = "\$onebasedqpos\(.*\)" # $onebasedqpos(string)
    item = re.search(regex, parseString)
    if item is not None:
        username = item.group().strip()[14:][:-1]
        notFound = True
        for entry in Queue.Queue:
            if username == entry.User.Name:
                parseString = parseString.replace(item.group(), str(entry.Id + 1))
                if ScriptSettings.EnableDebug:
                    Parent.Log(ScriptName, parseString)
                notFound = False
                break;

        if notFound is True:
            parseString = "User not found in queue"

    return parseString

def UpdateQueue():

    payload = {}

    for entry in Queue.Queue:
        payload[str(entry.Id)] = {
           "note": entry.Note,
           "time": str(entry.Time),
           "username": entry.User.Name,
           "userid": entry.UserId
        }

    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, str(payload))

    Parent.BroadcastWsEvent("EVENT_QUEUE_UPDATE", json.dumps(payload))
    return

def ChangeQueueStatus():

    status = "Closed"
    if Queue.Started:
        status = "Open"

    payload = { "status": status }
    Parent.BroadcastWsEvent("EVENT_QUEUE_STATUS", json.dumps(payload))
    return

# ---------------------------------------
# Script UI Button Functions
# ---------------------------------------
def OpenReadMe():
    os.startfile(ReadMeFile)
    return

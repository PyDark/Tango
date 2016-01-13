import re


__author__ = "Frowdo"
__description__ = "Emulates Chatango's obfuscated JavaScript code"

# Populate this python data structure if you know how to inspect the WebSocket Headers via Google Chromes Developer tools.
# Otherwise, leave it empty.
BookMarks = {
    #"nba-stream": 76,
}


# Part of Chatango's javascript obfuscation code
TsWeights = [
    ['5', 75], ['6', 75], ['7', 75], ['8', 75],
    ['16', 75], ['17', 75], ['18', 75], ['9', 95],
    ['11', 95], ['12', 95], ['13', 95], ['14', 95],
    ['15', 95], ['19', 110], ['23', 110], ['24', 110],
    ['25', 110], ['26', 110], ['28', 104], ['29', 104],
    ['30', 104], ['31', 104], ['32', 104], ['33', 104],
    ['35', 101], ['36', 101], ['37', 101], ['38', 101],
    ['39', 101], ['40', 101], ['41', 101], ['42', 101],
    ['43', 101], ['44', 101], ['45', 101], ['46', 101],
    ['47', 101], ['48', 101], ['49', 101], ['50', 101],
    ['52', 110], ['53', 110], ['55', 110], ['57', 110],
    ['58', 110], ['59', 110], ['60', 110], ['61', 110],
    ['62', 110], ['63', 110], ['64', 110], ['65', 110],
    ['66', 110], ['68', 95], ['71', 116], ['72', 116],
    ['73', 116], ['74', 116], ['75', 116], ['76', 116],
    ['77', 116], ['78', 116], ['79', 116], ['80', 116],
    ['81', 116], ['82', 116], ['83', 116], ['84', 116],
]


def get_server_id(website):
    """Return the correct Chatango WebSocket server hostname (address) for the specified website.
    """

    hostname = get_chatroom_name(website)
    sn = 0
    if BookMarks.has_key(hostname):
        sn = BookMarks.get(hostname)
    if sn == 0:
        name = re.sub("[^0-9a-z]", "q", hostname.lower())
        fnv = float(int(name[0:min(5, len(name))], 36))
        lnv = name[6: (6 + min(3, len(name) - 5))]
        if (lnv):
            lnv = float(int(lnv, 36))
            lnv = max(lnv, 1000)
        else:
            lnv = 1000
        num = (fnv % lnv) / lnv
        maxnum = sum(map(lambda x: x[1], TsWeights))
        cumfreq = 0
        for wgt in TsWeights:
            cumfreq += float(wgt[1]) / maxnum
            if (num <= cumfreq):
                sn = int(wgt[0])
                break
    return "s" + str(sn) + ".chatango.com"



def get_chatroom_name(website):
    """Returns a website URLs subdoman. I.E.: http://nba-stream.chatango.com becomes 'nba-stream'.
    """

    splitted = website.split("//")[1]
    return splitted.split(".")[0]
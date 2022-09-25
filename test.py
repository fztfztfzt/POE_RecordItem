from ast import Dict
from msilib import Table
import string
import pyautogui
import pyperclip
import time
import keyboard
import re
import json
import codecs 
import configparser
import threading
from tkinter import *
NeedSaveClass={
    "异界地图":True,
    "可堆叠通货":True,
    "精华":True,
    "命运卡":True,
    "地图碎片":True,
    "回忆":True,
    "辅助技能宝石":True,
    "主动技能宝石":True,
    "珠宝":True,
    "裂隙之石":True,
    "圣甲虫":True,
    "催化剂":True,
    "圣油":True,
}
Config = {

}
breakFlag = False
def LoadConfig():
    global Config
    file = 'config.ini'
    con = configparser.ConfigParser()
    con.read(file, encoding='utf-8')
    items = con.items('config')
    Config = dict(items)

AllItemInfo = {}
def InitSystem():
    global AllItemInfo
    print(pyautogui.size())
    print(pyautogui.position())
    LoadConfig()
    with codecs.open("record.json","r",encoding="utf-8") as f:
        AllItemInfo = json.load(f)
    if "count" not in AllItemInfo:
        AllItemInfo["count"] = 0

def ProcessPaste(s:str):
    if s == "": 
        return
    match =re.match("物品类别: (.*?)\r\n.*稀 有 度: (.*?)\r\n(.*?)\r\n----.*",s,re.S)
    item = {}
    item["name"] = re.sub("\[.*?\]","",match.group(3))
    if match.group(2) == "传奇" and "\n" in item["name"]:
        match = re.match("(.*?)\r\n(.*)",item["name"])
        item["name"] = match.group(1)
    elif "\n" in item["name"]:
        match = re.match("(.*?)\r\n(.*)",item["name"])
        item["name"] = match.group(2)

    if "圣甲虫" in item["name"]:
        item["class"] = "圣甲虫"
    elif "精华" in item["name"]:
        item["class"] = "精华"
    elif "圣油" in item["name"]:
        item["class"] = "圣油"
    elif "催化剂" in item["name"]:
        item["class"] = "催化剂"
    else :
        item["class"] = match.group(1)
    match =re.match(".*堆叠数量: (\d+) / (\d+)",s,re.S)
    if match != None:
        item["count"] = int(match.group(1))
        item["maxCount"] = int(match.group(2))
    return item

def AddItem(item):
    if item["class"] not in NeedSaveClass:
        return
    name = item["name"].encode("utf-8").decode("utf-8")
    count = 1
    if "count" in item:
        count = item["count"]
    inMap = AllItemInfo
    if "class" in item:
        if item["class"] not in AllItemInfo:
            AllItemInfo[item["class"]] = {}
        inMap = AllItemInfo[item["class"]]
    if name in inMap:
        inMap[name] += count
    else :
        inMap[name] = count

def Run():
    global breakFlag
    startX = float(Config["startx"])
    startY = float(Config["starty"])
    cellSize = float(Config["cellsize"])
    AllItemInfo["count"] += 1
    pyautogui.PAUSE =float(Config["movespeed"])
    pyautogui.keyDown('ctrl') 
    pyperclip.copy("")
    # pyautogui.moveTo(1739,810)
    for y in range(5):
        if breakFlag:
            break
        for x in range(12):
            if breakFlag:
                break
            if x== 0 and y == 0:
                continue
            pyautogui.moveTo(startX + x * cellSize,startY + y * cellSize)
            pyautogui.press('c')
            pyautogui.click()
            clipStr = pyperclip.paste()
            if clipStr == "":
                continue
            item = ProcessPaste(clipStr)
            pyperclip.copy("")
            # pyautogui.alert(text=str(item),title="info",button='OK')
            AddItem(item)

    with codecs.open("record.json","w",encoding="utf-8") as f:
        json.dump(AllItemInfo,f,ensure_ascii=False,indent=4)
    pyautogui.keyUp('ctrl') 

def BreakRun():
    global breakFlag
    breakFlag = not breakFlag

def ListenRun():
    while True:
        keyboard.add_hotkey(Config["hotkey"],Run)
        keyboard.wait()
        
def ListenBreakRun():
    keyboard.add_hotkey(Config["breakkey"],BreakRun)
    keyboard.wait()

def Start():
    global breakFlag
    breakFlag = False
    InitSystem()
    threading.Thread(target=ListenRun).start()


Alpha = 0.7
Start()
root=Tk()
root.wm_attributes('-topmost',1) 
root.attributes('-alpha',Alpha)
root.title("信息显示")   
root.geometry('220x500+10+10')
sb = Scrollbar(root)
sb.pack(side=RIGHT,fill=Y) 
listb = Listbox(root,yscrollcommand=sb.set)
def RefreshList():
    listb.delete(0,END)
    for key in AllItemInfo:        
        if key in Config["showclass"]:
            for key2 in AllItemInfo[key]:
                listb.insert(0,key2 + ":" + str(AllItemInfo[key][key2]))
        elif isinstance(AllItemInfo[key],dict):
            for key2 in AllItemInfo[key]:
                if key2 in Config["showitems"]:
                    listb.insert(0,key2 + ":" + str(AllItemInfo[key][key2]))

RefreshList()
listb.pack(side=LEFT,fill=BOTH) 



listb.pack(side=LEFT,fill=BOTH) 
sb.config(command=listb.yview)

bt = Button(root, text="刷新", bg="lightblue", width=155,command=RefreshList)
bt.pack()

def RefreshAlpha(v):
    root.attributes('-alpha',v)
Scale(root,label='透明度',
      from_=0.2,to=1,
      resolution=0.1,show=0,
      orient = HORIZONTAL,
      variable=Alpha,command=RefreshAlpha
      ).pack()
root.mainloop()
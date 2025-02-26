import tkinter as tk
from tkinter import filedialog
import wget, os, json, shutil, zipfile, string
from colorama import Fore, Style, init
init(autoreset=True)

user = os.getlogin()

drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

print(Fore.BLUE + "Searching for viable curseforge installations.")

curseforgePaths = []
for drive in drives:
    path = f"{drive}Users\{user}\curseforge\minecraft\Instances"
    if os.path.exists(path):
        print(Fore.GREEN + f"Found viable curseforge path! '{path}'")
        curseforgePaths.append(path)
    else:
        print(Fore.YELLOW + f"No viable curseforge path found on drive {drive}")

print(Fore.BLUE + "Searching for viable curseforge instances.")

curseforgeInstances = {}
for path in curseforgePaths:
    for instance in os.listdir(path):
        curseforgeInstances[f"CurseForge: {instance}"] = f"{path}\{instance}/mods".replace("\\", "/")

if curseforgeInstances != []:
    print(Fore.GREEN + "curseforge instances found, " + " ".join(curseforgeInstances))
else:
    print(Fore.YELLOW + "No curseforge instances found")

win = tk.Tk()
win.geometry("250x250")
win.title("Modpack Downloader")

config = {}
with open("config.json", "r") as configFile:
    config = json.load(configFile)

def downloadMods():

    if config["path"] != "":
        if config["modpack"] != "":
            for filename in os.listdir(config["path"]):
                file_path = os.path.join(config["path"], filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            wget.download(config["mirror_url"]+config["modpack_aliases"][config["modpack"]], config["path"])
            
            with zipfile.ZipFile(config["path"]+"/"+config["modpack_aliases"][config["modpack"]], 'r') as zip:
                zip.extractall(config["path"])

            os.unlink(config["path"]+"/"+config["modpack_aliases"][config["modpack"]])

            outputDialog.config(text="Modpack download successful", fg="green")
        else:
            outputDialog.config(text="Please select a modpack", fg="red")
    else:
        outputDialog.config(text="Please set a mods folder", fg="red")

def updateDownloadDirectory():
    config["path"]  = filedialog.askdirectory()

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)

    if config["path"] != "":
        if not config["path"] in curseforgeInstances.values():
            instanceSelector.destroy()
    
    outputDialog.config(text="Config update successful", fg="green")

def changeServer(value):
    config["modpack"] = value

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)

def selectDownloadDirectory(value):
    config["path"] = curseforgeInstances[value]

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)
    
    outputDialog.config(text="Config update successful", fg="green")

def resetConfig():
    config["path"] = ""
    config["modpack"] = ""

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)

    if config["path"] == "":
        if curseforgeInstances == []:
            selectedInstance.set("No instances available")
        else:
            selectedInstance.set("Select a Minecraft instance")
    else:
        if config["path"] in curseforgeInstances.values():
            selectedInstance.set(list(curseforgeInstances.keys())[list(curseforgeInstances.values()).index(config["path"])])

    if config["modpack"] == "":
        selectedServer.set("Select a server")
    else:
        selectedServer.set(config["modpack"])

selectedServer = tk.StringVar()
if config["modpack"] == "":
    selectedServer.set("Select a server")
else:
    selectedServer.set(config["modpack"])

modpacks = config["modpack_aliases"].keys()

serverSelector = tk.OptionMenu(win, selectedServer, *modpacks, command=changeServer)
serverSelector.pack()

downloadButton = tk.Button(win, text="Download Mods", command=downloadMods)
downloadButton.pack()

updateDirectoryButton = tk.Button(win, text="Set Custom Mods Folder", command=updateDownloadDirectory)
updateDirectoryButton.pack()

selectedInstance = tk.StringVar()
if config["path"] == "":
    if curseforgeInstances == []:
        selectedInstance.set("No instances available")
    else:
        selectedInstance.set("Select a Minecraft instance")
else:
    if config["path"] in curseforgeInstances.values():
        selectedInstance.set(list(curseforgeInstances.keys())[list(curseforgeInstances.values()).index(config["path"])])

instanceSelector = tk.OptionMenu(win, selectedInstance, *curseforgeInstances.keys(), command=selectDownloadDirectory)

if curseforgeInstances != []:
    if config["path"] == "" or config["path"] in curseforgeInstances.values():
        instanceSelector.pack()

resetConfigButton = tk.Button(win, text="Reset Config", command=resetConfig)
resetConfigButton.pack()

outputDialog = tk.Label(win, text="", fg="gray")
outputDialog.pack()

win.mainloop()
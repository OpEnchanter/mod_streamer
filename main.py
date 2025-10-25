import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import wget, os, json, shutil, zipfile, string, configparser, subprocess, sys
from colorama import Fore, Style, init
from ttkthemes import ThemedStyle
import requests
init(autoreset=True)

config = {}
with open("config.json", "r+") as configFile:
    config = json.load(configFile)

# Update Config
print(Fore.BLUE + "Updating Config")
try:
    downloadedConfig = requests.get(config["mirror_url"]+"/modm-api/updateConfig").json()

    for updatedItm in downloadedConfig.keys():
        config[updatedItm] = downloadedConfig[updatedItm]

    with open("config.json", "w") as f:
        json.dump(config, f)

    print(Fore.GREEN + "Updated Config!")
except:
    print(Fore.YELLOW + "Could not download latest config")

# Check for update

user = os.getlogin()

drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

launcherInstances = {}

# Find prism launcher instances
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

for path in curseforgePaths:
    for instance in os.listdir(path):
        launcherInstances[f"CurseForge: {instance}"] = f"{path}\{instance}/mods".replace("\\", "/")

# Find prism launcher instances
print(Fore.BLUE + "Searching for viable prism installations.")

prismPaths = []
for drive in drives:
    path = f"{drive}Users\{user}\AppData\Roaming\PrismLauncher\instances"
    if os.path.exists(path):
        print(Fore.GREEN + f"Found viable prism path! '{path}'")
        prismPaths.append(path)
    else:
        print(Fore.YELLOW + f"No viable prism path found on drive {drive}")

print(Fore.BLUE + "Searching for viable prism instances.")

for path in prismPaths:
    for instance in os.listdir(path):
        if not os.path.isfile(f"{path}\{instance}"):
            if "instance.cfg" in os.listdir(f"{path}\{instance}"):
                try:
                    instanceConfig = configparser.ConfigParser()
                    with open(f"{path}\{instance}/instance.cfg") as f:
                        configText = "[settings]\n"+f.read()
                    instanceConfig.read_string(configText)
                    instanceName = instanceConfig["settings"]["name"]
                    launcherInstances[f"Prism: {instanceName}"] = f"{path}\{instance}/.minecraft/mods".replace("\\", "/")
                except:
                    print(Fore.RED + "Failed to read Prism Launcher instance config file (This message does not indicate any fatal error do not report this to the program's developer)")

# Find modrinth instances
print(Fore.BLUE + "Searching for viable modrinth installations.")

modrinthPaths = []
for drive in drives:
    path = f"{drive}Users\{user}\AppData\Roaming\com.modrinth.theseus\profiles"
    if os.path.exists(path):
        print(Fore.GREEN + f"Found viable modrinth path! '{path}'")
        modrinthPaths.append(path)
    else:
        print(Fore.YELLOW + f"No viable modrinth path found on drive {drive}")

print(Fore.BLUE + "Searching for viable modrinth instances.")

for path in modrinthPaths:
    for instance in os.listdir(path):
        if not os.path.isfile(f"{path}\{instance}"):
            if "profile.json" in os.listdir(f"{path}\{instance}"):
                try:
                    with open(f"{path}\{instance}/profile.json") as cfg:
                        instanceConfig = json.load(cfg)
                    instanceName = instanceConfig["metadata"]["name"]
                    launcherInstances[f"Modrinth: {instanceName}"] = f"{path}\{instance}/mods".replace("\\", "/")
                except:
                    print(Fore.RED + "Failed to read Modrinth Launcher instance config file (This message does not indicate any fatal error do not report this to the program's developer)")

print(Fore.BLUE + "Searching for viable Minecraft Launcher installations.")

minecraftLauncherPaths = []
for drive in drives:
    path = f"{drive}Users\{user}\AppData\Roaming\.minecraft\mods"
    if os.path.exists(path):
        print(Fore.GREEN + f"Found viable Minecraft Launcher path! '{path}'")
        minecraftLauncherPaths.append(path)
    else:
        print(Fore.YELLOW + f"No viable Minecraft Launcher path found on drive {drive}")

for path in minecraftLauncherPaths:
    launcherInstances["Minecraft Launcher"] = path.replace("\\", "/")

if launcherInstances != {}:
    print(Fore.GREEN + "Game instances found: " + ", ".join(launcherInstances))
else:
    print(Fore.YELLOW + "No game instances found")

instanceOptions = []
for instance in launcherInstances.keys():
    instanceOptions.append(instance)
if instanceOptions == []:
    instanceOptions.append(" ")

win = tk.Tk()
win.geometry("250x250")
win.title("Mod Manager")

def update():
    config["app_version"] = int(requests.get(config["mirror_url"]+"/modm-api/version").json())
    with open("config.json", "w") as f:
        json.dump(config, f)
    wget.download(config["mirror_url"] + "/modm-api/downloadApp", "main.exe.new")
    subprocess.Popen(["start", "cmd", "/k", "updater.exe"], shell=True)
    sys.exit()


try:
    latestVer = int(requests.get(config["mirror_url"]+"/modm-api/version").json())
    if (config["app_version"] < latestVer):
        updateWin = tk.Toplevel(win)
        updateWin.title("Update Available")
        updateWin.geometry("150x150")

        updateText = ttk.Label(updateWin, text="Update Available", foreground="green")

        updateText.pack()

        updateButton = ttk.Button(updateWin, text="Download Update", command=update)
        updateButton.pack()
    else:
        print(Fore.GREEN + "App up to date!")
except Exception as e:
    print(Fore.YELLOW + "Could not check for app update")
    print(e)

style = ThemedStyle(win)
style.theme_use("arc")

def downloadMods():

    if config["path"] != "":
        if config["modpack"] != "":
            for filename in os.listdir(config["path"]):
                file_path = os.path.join(config["path"], filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            wget.download(config["mirror_url"]+"/"+config["modpack_aliases"][config["modpack"]]["downloadPath"], config["path"])
            
            with zipfile.ZipFile(config["path"]+"/"+config["modpack_aliases"][config["modpack"]]["filename"], 'r') as zip:
                zip.extractall(config["path"])

            os.unlink(config["path"]+"/"+config["modpack_aliases"][config["modpack"]]["filename"])

            outputDialog.config(text="Modpack download successful", foreground="green")
        else:
            outputDialog.config(text="Please select a modpack", foreground="red")
    else:
        outputDialog.config(text="Please set a mods folder", foreground="red")

def updateDownloadDirectory():
    config["path"]  = filedialog.askdirectory()

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)

    if config["path"] != "":
        if not config["path"] in launcherInstances.values():
            instanceSelector.destroy()
    
    outputDialog.config(text="Config update successful", foreground="green")

def changeModpack(args):
    config["modpack"] = modpackSelector.get()

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)

def selectDownloadDirectory(args):
    config["path"] = launcherInstances[instanceSelector.get()]

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)
    
    outputDialog.config(text="Config update successful", foreground="green")

def resetConfig():
    config["path"] = ""
    config["modpack"] = ""

    with open("config.json", "w") as configFile:
        json.dump(config, configFile)

    if config["path"] == "":
        if launcherInstances == []:
            instanceSelector.set("No instances available")
        else:
            instanceSelector.set("Select a Minecraft Instance")
    else:
        if config["path"] in launcherInstances.values():
            instanceSelector.set(list(launcherInstances.keys())[list(launcherInstances.values()).index(config["path"])])

    if config["modpack"] == "":
        modpackSelector.set("Select a Modpack")
    else:
        modpackSelector.set(config["modpack"])

modpacks = list(config["modpack_aliases"].keys())

modpackSelector = ttk.Combobox(win, values=modpacks, state="readonly")
modpackSelector.bind("<<ComboboxSelected>>", changeModpack)
if config["modpack"] == "":
    modpackSelector.set("Select a Modpack")
else:
    modpackSelector.set(config["modpack"])
modpackSelector.pack(pady=2)

downloadButton = ttk.Button(win, text="Download Mods", command=downloadMods)
downloadButton.pack(pady=2)

updateDirectoryButton = ttk.Button(win, text="Set Custom Mods Folder", command=updateDownloadDirectory)
updateDirectoryButton.pack(pady=2)

instanceSelector = ttk.Combobox(win, values=instanceOptions, state="readonly")
instanceSelector.bind("<<ComboboxSelected>>", selectDownloadDirectory)

if config["path"] == "":
    if launcherInstances == {}:
        instanceSelector.set("No instances available")
    else:
        instanceSelector.set("Select a Minecraft Instance")
else:
    if config["path"] in launcherInstances.values():
        instanceSelector.set(list(launcherInstances.keys())[list(launcherInstances.values()).index(config["path"])])

if launcherInstances != {}:
    if config["path"] == "" or config["path"] in launcherInstances.values():
        instanceSelector.pack()

resetConfigButton = ttk.Button(win, text="Reset Config", command=resetConfig)
resetConfigButton.pack(pady=2)

outputDialog = ttk.Label(win, text="", foreground="grey")
outputDialog.pack(pady=2)

win.mainloop()
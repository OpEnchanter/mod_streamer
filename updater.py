import os, sys, time

time.sleep(1)

os.unlink("./main.exe")
time.sleep(0.5)
os.rename("./main.exe.new", "main.exe")

sys.exit()
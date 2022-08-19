# Install the following packages by running the commands:
# pynput:
# pip install pynput

import time
import os
import json
import csv
import math
from pynput import keyboard 

mode = "main"
name = ""
data = {}
overAllData = {}
measurementIsRunning = False

def printWithMode(text, newLine=True):
  global mode, data, measurementIsRunning
  if (len(mode) <= 4):
    space = "\t\t"
  else:
    space = "\t"
  if (newLine == True):
    newLine = "\n"
  else:
    newLine = ""
  if (mode == "record"):
    if (measurementIsRunning == True):
      status = ", running"
    else:
      status = ", paused"
  else:
    status = ""
  print(newLine + "[" + mode + status + "]" + space + text)
  if (mode == "record"):
    data["log"].append(
      "[" + mode + status + "]" + space + text
    )
    

def printHelp():
  print(" ")
  print("-------------------------------------------------------------")
  print("MOUSE TRACKER")
  print(" ")
  print("commands in 'main'-mode:")
  print("h\t\tprints help information")
  print("n\t\tcreate a new data entry (main -> create)")
  print("l\t\tlist all saved results")
  print("s\t\tsave all results to a csv-file")
  print("q\t\texit this application")
  print(" ")
  print("commands in 'create'-mode:")
  print("ENTER\t\tconfirm data entry name (create -> record)")
  print("ESC\t\tswitch back to 'main'-mode (create -> main)")
  print(" ")
  print("commands in 'record'-mode:")
  print("SPACE\t\tstart / pause the measurement")
  print("LEFT\t\tadd time to left object")
  print("RIGHT\t\tadd time to right object")
  print("ESC\t\tsave and switch back to 'main'-mode (record -> main)")
  print("-------------------------------------------------------------")
  print(" ")
  
def listAllResults():
  global overAllData
  print(" ")
  print("-------------------------------------------------------------")
  for key in overAllData.keys():
    print(
      key + "\t" + 
      overAllData[key]["name"] + "\t" +
      "left: " + "{:.3f}".format(overAllData[key]["leftOverallTime"]) + "s" + "\t" +
      "right: " + "{:.3f}".format(overAllData[key]["rightOverallTime"]) + "s" + "\t" +
      "total: " + "{:.3f}".format(overAllData[key]["overallTime"]) + "s" + "\t" +
      "measurement timespan: " + formatSecondsToMinutes(overAllData[key]["measurementOverallTime"])
    )
  print("-------------------------------------------------------------")
  print(" ")
  
def saveResultsToCsv():
  global overAllData
  printWithMode("Saving results to a csv-file ...")
  try:
    with open("./data.csv", "w", encoding="UTF8") as f:
      writer = csv.writer(f, delimiter=";")
      writer.writerow(["name", "left", "right", "total", "measurement timespan"])
      for key in overAllData.keys():
        writer.writerow([
          overAllData[key]["name"],
          str(overAllData[key]["leftOverallTime"]).replace('.', ','),
          str(overAllData[key]["rightOverallTime"]).replace('.', ','),
          str(overAllData[key]["overallTime"]).replace('.', ','),
          formatSecondsToMinutes(overAllData[key]["measurementOverallTime"])
        ])
    printWithMode("Results saved to a csv-file.", newLine=False)
  except:
    printWithMode("An error occured while saving results to a csv-file ...", newLine=False)
  
def formatSecondsToMinutes(seconds):
  minutes = math.floor(seconds / 60)
  seconds = round(seconds - minutes * 60)
  return str(minutes) + "min " + str(seconds) + "s"

def calculateMeasurementTimespan():
  global data
  measurementTimespan = 0
  for timeEntries in data["measurementStartTime"]:
    if (len(timeEntries) == 1):
      measurementTimespan = measurementTimespan + (time.time() - timeEntries[0])
    elif (len(timeEntries) == 2):
      measurementTimespan = measurementTimespan + (timeEntries[1] - timeEntries[0])
    else:
      print("ERROR timespan calculation")
  data["measurementOverallTime"] = measurementTimespan
  
def checkOverallTime():
  global data
  leftOverallTime = 0 
  for timestamps in data["left"]:
    if (len(timestamps) != 2):
      continue
    else:
      leftOverallTime = leftOverallTime + (timestamps[1] - timestamps[0])
  rightOverallTime = 0 
  for timestamps in data["right"]:
    if (len(timestamps) != 2):
      continue
    else:
      rightOverallTime = rightOverallTime + (timestamps[1] - timestamps[0])
  overallTime = leftOverallTime + rightOverallTime
  data["leftOverallTime"] = leftOverallTime
  data["rightOverallTime"] = rightOverallTime
  data["overallTime"] = overallTime
  calculateMeasurementTimespan()
  if (overallTime >= 20):
    done = "\t<--- DONE\a"
  else:
    done = ""
  printWithMode("left: " + "{:.3f}".format(leftOverallTime) + "s" +
                "\tright: " + "{:.3f}".format(rightOverallTime) + "s" +
                "\ttotal: " + "{:.3f}".format(overallTime) + "s" + done + 
                "\t(measurement timespan: " + formatSecondsToMinutes(data["measurementOverallTime"]) + ")",
                newLine=False)
  
def on_press(key):
  global mode, name, data, overAllData, measurementIsRunning
  # main
  if ((mode == "main") and (key == keyboard.KeyCode.from_char("h"))):
    printHelp()
  elif ((mode == "main") and (key == keyboard.KeyCode.from_char("n"))):
    mode = "create"
    name = ""
    printWithMode("Please enter the name of the new data entry and press ENTER:\n")
  elif ((mode == "main") and (key == keyboard.KeyCode.from_char("l"))):
    listAllResults()
  elif ((mode == "main") and (key == keyboard.KeyCode.from_char("s"))):
    saveResultsToCsv()
  elif ((mode == "main") and (key == keyboard.KeyCode.from_char("q"))):
    printWithMode("Terminating the application ...")
    return False
  # create
  elif ((mode == "create") and (key == keyboard.Key.esc)):
    mode = "main"
    printWithMode("Switching back to main-menu ...")
  elif ((mode == "create") and (key == keyboard.Key.enter)):
    if (len(name) == 0):
      printWithMode("Please enter a data entry name!")
    else:
      printWithMode("Creating new data-entry '" + name + "'...")
      data = {
        "name": name,
        "left": [],
        "right": [],
        "leftIsPressed": False,
        "rightIsPressed": False,
        "leftOverallTime": 0,
        "rightOverallTime": 0,
        "overallTime": 0,
        "measurementStartTime": [],
        "measurementOverallTime": 0,
        "log": []
      }
      mode = "record"
      measurementIsRunning = False
      printWithMode("Switching to record-mode ...", newLine=False)
  elif (mode == "create"):
    try:
      name = name + key.char
    except AttributeError:
      pass
  # record
  elif ((mode == "record") and (key == keyboard.Key.space)):
    if ((data["leftIsPressed"] == True) or (data["rightIsPressed"] == True)):
      printWithMode("ERROR: Can't pause / start while LEFT or RIGHT is pressed.")
    else:
      measurementIsRunning = not(measurementIsRunning)
      if (measurementIsRunning == True):
        printWithMode("Measurement started.", newLine=False)
        data["measurementStartTime"].append([time.time()])
      else:
        printWithMode("Measurement paused.", newLine=False)
        data["measurementStartTime"][-1].append(time.time())
  elif ((mode == "record") and (key == keyboard.Key.left)):
    if (measurementIsRunning == False):
      printWithMode("MEASUREMENT IS PAUSED!", newLine=False)
    else:
      if (data["leftIsPressed"] == False):
        data["leftIsPressed"] = True
        data["left"].append([time.time()])
  elif ((mode == "record") and (key == keyboard.Key.right)):
    if (measurementIsRunning == False):
      printWithMode("MEASUREMENT IS PAUSED!", newLine=False)
    else:
      if (data["rightIsPressed"] == False):
        data["rightIsPressed"] = True
        data["right"].append([time.time()])
  elif ((mode == "record") and (key == keyboard.Key.esc)):
    if ((data["leftIsPressed"] == True) or (data["rightIsPressed"] == True)):
      printWithMode("ERROR: Can't stop measurement while LEFT or RIGHT is pressed.")
    else:
      calculateMeasurementTimespan()
      printWithMode("Saving results ...")
      filename = data["name"] + "_" + str(round(time.time()))
      overAllData[filename] = data
      with open("./data.json", "w") as f:
        json.dump(overAllData, f, indent=4)
      if not(os.path.exists("./log")):
        os.makedirs("./log")
      with open("./log/" + filename + ".txt", "w") as f:
        for line in data["log"]:
            f.write(line)
            f.write('\n')
      mode = "main"
      printWithMode("Saved results to './log/" + filename + ".txt'.", newLine=False)
      printWithMode("Switching back to main-menu ...", newLine=False)

def on_release(key):
  global mode, data
  if ((mode == "record") and (key == keyboard.Key.left)):
    if (data["leftIsPressed"] == True):
      data["leftIsPressed"] = False
      data["left"][-1].append(time.time())
      checkOverallTime()
  elif ((mode == "record") and (key == keyboard.Key.right)):
    if (data["rightIsPressed"] == True):
      data["rightIsPressed"] = False
      data["right"][-1].append(time.time())
      checkOverallTime()

def main():
  global overAllData
  # Load existing data.
  if (os.path.exists("./data.json")):
    # Data already exist.
    with open("./data.json") as f:
      overAllData = json.load(f)
  # Print the help text.
  printHelp()
  # Start the keyboard-listener.
  printWithMode("Starting keyboard-listener ...")
  with keyboard.Listener(
      on_press=on_press,
      on_release=on_release) as listener:
    listener.join()

if __name__ == "__main__":
  main()
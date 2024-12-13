#Atompunk78's BeamNG Track Generator
#Licenced under the CC BY-NC-SA 4.0 (see licence.txt for more info)
version = "1.11"

from random import randint, choice
import json
import sys
import os
import math

fileStart = """
{
  "author": "Atompunk78's Track Generator ?5",
  "connected": false,
  "date": "0",
  "defaultLaps": 1,
  "difficulty": 0,
  "environment": {
    "fog": 0.0005,
    "tod": {
      "azimuthOverride": 1,
      "dayLength": 0,
      "dayScale": 0,
      "nightScale": 0,
      "startTime": 0,
      "time": 0
    }
  },
  "length": 0,
  "level": "smallgrid",
  "materials": [],
  "reversible": true,
  "subPieces": [
    [
      {
        "bank": {
          "interpolation": "smoothSlope",
          "value": 0
        },
        "height": {
          "interpolation": "smoothSlope",
          "value": 0
        },
        "piece": "init",
        "width": {
          "interpolation": "smoothSlope",
          "value": ?4
        }
      },
      {
        "centerMesh": "?1",
        "leftMesh": "?2",
        "rightMesh": "?3",
        "length": 2,
        "piece": "freeForward"
      },
"""

fileEnd = """
      {
        "centerMesh": "?1",
        "leftMesh": "?2",
        "rightMesh": "?3",
        "length": 2,
        "piece": "freeForward"
      }
    ]
  ],
  "subTrackPositions": [
    {
      "hdg": 0,
      "x": 0,
      "y": 0,
      "z": ?4
    }
  ],
  "version": "1.1"
}
""" #the version just above represents the track editor version, not that of this program

currentFileString = ""
currentHeight = 0
currentLength = 0
currentPosition = [0, 0, 0]
currentHeading = 0 #degrees

try:
    with open("config.json", "r") as file:
        parameters = json.load(file)
except:
    print("\nThe config file cannot be read. If this issue persists, redownload the file.\n")
    sys.exit(1)

def findBeamNGVersion():
    n = 10
    found = False
    while not found:
        parameters["savePath"] = parameters["savePath"].replace("0."+str(n-1), "0."+str(n))
        if parameters["showDebugMessages"]:
            print("Trying for BeamNG version 0."+str(n))
        if os.path.exists(parameters["savePath"]):
            found = True
        n += 1
        if n >= 100:
            print("The path to BeamNG could not be found, you will have to manually enter the path to the trackEditor folder into the config file.")
            sys.exit(1)

if parameters["savePath"] == "AUTODETECT":
    print("Automatically detecting file path to BeamNG...")
    parameters["savePath"] = os.path.expanduser("~").replace("\\", "/") #just in case the backslashes cause issues
    if os.path.exists(parameters["savePath"]):
        parameters["savePath"] += "/AppData/Local/BeamNG.drive/0.34/trackEditor"
        if not os.path.exists(parameters["savePath"]):
            print("Path could not be found, retrying for new BeamNG versions...")
            findBeamNGVersion()
    else:
        print("Home directory could not be found, you will have to manually enter the path to the trackEditor folder into the config file.")
        sys.exit(1)
    with open("config.json", "w") as file:
        json.dump(parameters, file, indent=4)
        print("Path found and updated")

try:
    with open(f"Presets/{parameters['trackType']}.json", "r") as file:
        parameters |= json.load(file)
except FileNotFoundError:
    print(f"\nThe preset {parameters['trackType']}.json cannot be found.\n")
    sys.exit(1)
except:
    print(f"\nThe preset cannot be read. Fix any syntax errors, and if this issue persists, redownload the file.\n")
    sys.exit(1)

fileName = parameters["savePath"] + "/" + parameters["trackName"]

fileStart = fileStart.replace("?1", parameters["centreMeshType"]).replace("?2", parameters["leftMeshType"]).replace("?3", parameters["rightMeshType"]).replace("?4", str(parameters["trackWidth"])).replace("?5", "v"+version)
fileEnd = fileEnd.replace("?1", parameters["centreMeshType"]).replace("?2", parameters["leftMeshType"]).replace("?3", parameters["rightMeshType"]).replace("?4", str(parameters["startHeight"]))

positions = [(0, 0, parameters["startHeight"])]
print()

def segments_intersect(p1, p2, p3, p4): #this function is primarily written by ChatGPT; comments have been removed, for documentation check under the fridge
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    x4, y4 = p4[0], p4[1]

    def orientation(ax, ay, bx, by, cx, cy):
        val = (by - ay) * (cx - bx) - (bx - ax) * (cy - by)
        if val > 0:
            return 1
        elif val < 0:
            return 2
        return 0

    def on_segment(ax, ay, bx, by, cx, cy):
        return min(ax,bx) <= cx <= max(ax,bx) and min(ay,by) <= cy <= max(ay,by)
    
    o1 = orientation(x1, y1, x2, y2, x3, y3)
    o2 = orientation(x1, y1, x2, y2, x4, y4)
    o3 = orientation(x3, y3, x4, y4, x1, y1)
    o4 = orientation(x3, y3, x4, y4, x2, y2)

    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and on_segment(x1, y1, x2, y2, x3, y3):
        return True
    if o2 == 0 and on_segment(x1, y1, x2, y2, x4, y4):
        return True
    if o3 == 0 and on_segment(x3, y3, x4, y4, x1, y1):
        return True
    if o4 == 0 and on_segment(x3, y3, x4, y4, x2, y2):
        return True
    return False

def check_overlaps():
    for i in range(len(positions)-1):
        for j in range(i+3, len(positions)-1):
            p1 = positions[i]
            p2 = positions[i+1]
            p3 = positions[j]
            p4 = positions[j+1]

            if segments_intersect(p1, p2, p3, p4):
                z_avg_seg1 = (p1[2] + p2[2]) / 2.0
                z_avg_seg2 = (p3[2] + p4[2]) / 2.0
                if abs(z_avg_seg1 - z_avg_seg2) < 12:
                    return False
    return True

def UpdatePositions(height, length, radius=None, direction=None): #also primarily ChatGPT; o1 is so powerful
    global positions, currentHeading
    x_start, y_start, _ = positions[-1]

    if radius is None:
        # Straight segment subdivision
        step = 4
        steps = int(math.ceil(length / step))
        for s in range(1, steps+1):
            dist = s * step
            if dist > length:
                dist = length
            nx = x_start + dist * math.sin(math.radians(currentHeading))
            ny = y_start + dist * math.cos(math.radians(currentHeading))
            nz = height
            positions.append((nx, ny, nz))
    else:
        # Curved segment subdivision
        angle_delta = -length * direction
        increment = 10 if abs(angle_delta) >= 5 else angle_delta
        scaled_radius = radius * 4
        center_angle = currentHeading - 90 * direction
        cx = x_start + scaled_radius * math.sin(math.radians(center_angle))
        cy = y_start + scaled_radius * math.cos(math.radians(center_angle))
        dx = x_start - cx
        dy = y_start - cy
        theta_start = math.degrees(math.atan2(dx, dy))

        total_steps = int(abs(angle_delta) / increment)
        sign = 1 if angle_delta > 0 else -1

        current_angle = theta_start
        for s in range(1, total_steps+1):
            a = current_angle + increment * sign
            # check if we overshoot the final angle
            final_angle = theta_start + angle_delta
            if sign > 0 and a > final_angle:
                a = final_angle
            elif sign < 0 and a < final_angle:
                a = final_angle
            nx = cx + scaled_radius * math.sin(math.radians(a))
            ny = cy + scaled_radius * math.cos(math.radians(a))
            nz = height
            positions.append((nx, ny, nz))
            current_angle = a

        currentHeading = (currentHeading + angle_delta) % 360
        #print("UpdatePositions called with length:", length, "radius:", radius, "direction:", direction)


def addPiece():
    global currentHeight
    global currentLength
    global positions
    randomNumber = choice(parameters["tileTypeDist"])

    if randomNumber == 1: #short straight
        length = randint(parameters["shortStraightLengthMin"], parameters["shortStraightLengthMax"])
        currentHeight += choice(parameters["shortStraightHeightDist"])
        newPiece = f"""
      [
        "centerMesh": \"{parameters['centreMeshType']}\",
        "leftMesh": \"{parameters['leftMeshType']}\",
        "rightMesh": \"{parameters['rightMeshType']}\",
        "length": {length},
        "piece": "freeForward"?
      ],"""
        if choice(parameters["shortStraightHeightChanceDist"]) == 1: #only sometimes update height
            newPiece = newPiece.replace("?",f""",
        "height": [
          "interpolation": "smoothSlope",
          "value": {currentHeight}
        ]""")
        currentLength += length * 4
        UpdatePositions(currentHeight, length)
        
    elif randomNumber == 2: #long straight
        length = randint(parameters["longStraightLengthMin"], parameters["longStraightLengthMax"])
        currentHeight += choice(parameters["longStraightHeightDist"])
        newPiece = f"""
      [
        "centerMesh": \"{parameters['centreMeshType']}\",
        "leftMesh": \"{parameters['leftMeshType']}\",
        "rightMesh": \"{parameters['rightMeshType']}\",
        "length": {length},
        "piece": "freeForward"?
      ],"""
        if choice(parameters["longStraightHeightChanceDist"]) == 1:
            newPiece = newPiece.replace("?",f""",
        "height": [
          "interpolation": "smoothSlope",
          "value": {currentHeight}
        ]""")
        currentLength += length * 4
        UpdatePositions(currentHeight, length)
        
    elif randomNumber == 3: #short turn
        direction = choice([-1,1])
        length = randint(parameters["shortTurnLengthMin1"], parameters["shortTurnLengthMax1"]) + randint(parameters["shortTurnLengthMin2"], parameters["shortTurnLengthMax2"])
        radius = randint(parameters["shortTurnRadiusMin1"], parameters["shortTurnRadiusMax1"]) + randint(parameters["shortTurnRadiusMin2"], parameters["shortTurnRadiusMax2"])
        currentHeight += choice(parameters["shortTurnHeightDist"])
        newPiece = f"""
      [
        "centerMesh": \"{parameters['centreMeshType']}\",
        "leftMesh": \"{parameters['leftMeshType']}\",
        "rightMesh": \"{parameters['rightMeshType']}\",
        "direction": {direction},
        "length": {length},
        "piece": "freeCurve",
        "radius": {radius}?
      ],"""
        if choice(parameters["shortTurnHeightChanceDist"]) == 1:
            newPiece = newPiece.replace("?",f""",
        "height": [
          "interpolation": "smoothSlope",
          "value": {currentHeight}
        ]""")
        currentLength += 2 * math.pi * (radius * 4) * (length / 360)
        UpdatePositions(currentHeight, length, radius, direction)
        
    elif randomNumber == 4: #long turn
        direction = choice([-1,1])
        length = randint(parameters["longTurnLengthMin1"], parameters["longTurnLengthMax1"]) + randint(parameters["longTurnLengthMin2"], parameters["longTurnLengthMax2"])
        radius = randint(parameters["longTurnRadiusMin1"], parameters["longTurnRadiusMax1"]) + randint(parameters["longTurnRadiusMin2"], parameters["longTurnRadiusMax2"])
        if radius <= parameters["longTurnRadiusMax1"]: #stops too long and gentle corners somewhat
            length += randint(parameters["longTurnLengthMin2"], parameters["longTurnLengthMax2"])
        currentHeight += choice(parameters["longTurnHeightDist"])
        newPiece = f"""
      [
        "centerMesh": \"{parameters['centreMeshType']}\",
        "leftMesh": \"{parameters['leftMeshType']}\",
        "rightMesh": \"{parameters['rightMeshType']}\",
        "direction": {direction},
        "length": {length},
        "piece": "freeCurve",
        "radius": {radius}?
      ],"""
        if choice(parameters["longTurnHeightChanceDist"]) == 1:
            newPiece = newPiece.replace("?",f""",
        "height": [
          "interpolation": "smoothSlope",
          "value": {currentHeight}
        ]""")
        currentLength += 2 * math.pi * (radius * 4) * (length / 360)
        UpdatePositions(currentHeight, length, radius, direction)

    return newPiece.replace("[","{").replace("]","}").replace("?","")


from time import sleep
acceptableTrack = False
count = 0
while not acceptableTrack: #makes sure track doesn't go below 0 height or, if enabled, overlap itself
    acceptableTrack = True
    currentFileString = ""
    currentHeight = 0
    currentLength = 0
    positions = [(0, 0, parameters["startHeight"])]
    currentHeading = 0
    stuckNumber = 0

    while currentLength < parameters["totalLength"]:
      if acceptableTrack:
          if parameters["startHeight"] + currentHeight > 0:
              currentFileString += addPiece()
          else:
              acceptableTrack = False
              currentLength = parameters["totalLength"]

    if acceptableTrack and parameters["checkForOverlap"]:
        acceptableTrack = check_overlaps()

    if not acceptableTrack and parameters["showDebugMessages"]:
      print("Track layout invalid, regenerating track...")
    count += 1
    if count > 25:
        print("\nMaximum retries reached, exiting program. If this keeps happening, lower the maximum length or disable checkForOverlap.\n")
        sys.exit(1)

currentFileString = fileStart + currentFileString + fileEnd

if not parameters["overwriteTracks"]:
  with open("data.txt", "r+") as file:
      try:
        data = eval(file.read())
      except:
          data = []
      existingFile = False
      for name in data:
          if fileName == name[0]:
              existingFile = True
              dataLocation = data.index(name)
      if existingFile:
          data[dataLocation][1] += 1
          saveName = fileName.replace(".json","") + "_" + str(data[dataLocation][1])
      else:
          data.append([fileName, 1])
          saveName = fileName.replace(".json","") + "_1"
      saveName += ".json"
  
  with open("data.txt", "w") as file:
      file.write(str(data))
else:
    saveName = fileName

with open(saveName, "w") as file:
    file.write(currentFileString)

print(f"Track successfully generated and saved to {saveName}\n")

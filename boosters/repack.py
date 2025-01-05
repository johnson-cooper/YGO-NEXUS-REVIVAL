import os
import math

inputPacFile = "rom_work/data/Data_arc_pac/bin2.pac"
directory = "rom_work/data/Data_arc_pac/bin2/"

with open(inputPacFile, "rb") as inputFile:
    bytE = inputFile.read()

header = 0
fileNamesBeginning = 0
fileNames = 0
fileDataBeginningAddress = 0
third = 0
lineBreakBytes = [0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18]
tableOfFileNames = []
tableOfFiles = []

for i in range(0, len(bytE)):
    if ((i / 2) == (math.floor(i / 2))):
        if (bytE[i] & 0xFF == 0xFF) and (bytE[i + 1] & 0xFF == 0xFF):
            j = i - (i % 16)
            header = bytE[0:j]
            fileNamesBeginning = j
            break

for i in range(fileNamesBeginning, len(bytE)):
    if ((i % 16) == (fileNamesBeginning % 16)):
        currentLine = bytE[i:(i + 8)]
        if (int.from_bytes(currentLine, "little") == 0):
            fileNames = bytE[fileNamesBeginning:i]
            third = i
            break

for i in range(third, len(bytE)):
    if ((i % 16) == (third % 16)):
        currentLine = bytE[i:(i + 8)]
        if (int.from_bytes(currentLine, "little") != 0):
            fileDataBeginningAddress = i
            break

beginningOfWord = 0
check = 0
for i in range(0, len(header)):
    if (check == 1):
        check = 0
    else:
        currentByte = header[i]
        for j in range(15):
            if (currentByte == lineBreakBytes[j]):
                tableOfFileNames.append(header[beginningOfWord:i])
                beginningOfWord = i + 2
                check = 1

finalCharacter = len(header) - 1
while (header[finalCharacter - 3] & 0xFF == 0x00):
    finalCharacter = finalCharacter - 1
tableOfFileNames.append(header[beginningOfWord:finalCharacter])

temp = tableOfFileNames.copy()
for k in temp:
    checkP = 0
    for j in range(len(k)):
        if (k[j] == 46):
            checkP = 1

    if (checkP != 1):
        while (tableOfFileNames.count(k) > 0):
            tableOfFileNames.remove(k)

for i in range(8, len(fileNames)):
    if ((i % 8) == 0) and ((i + 8) <= len(fileNames)):
        byteSlice = fileNames[i:(i + 8)]
        fileSize = int.from_bytes(byteSlice[4:8], "little")
        if (fileSize != 0):
            address = int.from_bytes(byteSlice[0:4], "little")
            theFile = {"size": fileSize, "address": fileDataBeginningAddress + address, "after": -1}
            if ((i + 16) <= len(fileNames)) and (int.from_bytes(fileNames[(i + 12):(i + 16)], "little") == 0):
                theFile["after"] = (int.from_bytes(fileNames[(i + 8):(i + 16)], "little"))
            tableOfFiles.append(theFile)

if len(tableOfFileNames) != len(tableOfFiles):
    print("Error! " + str(len(tableOfFileNames)) + " file names but " + str(len(tableOfFiles)) + " files!")
    exit()

outputPacFile = "bin2.pac"
with open(outputPacFile, "wb") as newPac:
    newPac.write(bytE[0:fileNamesBeginning])
    newPac.write(fileNames[0:8])

    newAddress = tableOfFiles[0]["address"] - fileDataBeginningAddress
    totalSizeDiff = 0
    for i in range(0, len(tableOfFileNames)):
        cleanedFileName = tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
        with open(os.path.join(directory, cleanedFileName), "rb") as openSesame:
            currentFile = openSesame.read()

            newPac.write(newAddress.to_bytes(4, "little"))
            newPac.write(len(currentFile).to_bytes(4, "little"))

            if tableOfFiles[i]["after"] != -1:
                newPac.write(tableOfFiles[i]["after"].to_bytes(8, "little"))

            totalSizeDiff += (len(currentFile) - tableOfFiles[i]["size"])
            if (i + 1 < len(tableOfFiles)):
                newAddress = tableOfFiles[i + 1]["address"] - fileDataBeginningAddress + totalSizeDiff

    endBit = len(fileNames) - (len(fileNames) % 8)
    if endBit < len(fileNames):
        newPac.write(fileNames[endBit:len(fileNames)])
    newPac.write(bytE[third:fileDataBeginningAddress])

    for i in range(0, len(tableOfFileNames)):
        cleanedFileName = tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
        with open(os.path.join(directory, cleanedFileName), "rb") as openSesame:
            currentFile = openSesame.read()
            if i > 0:
                newPac.write(bytE[(tableOfFiles[i - 1]["address"] + tableOfFiles[i - 1]["size"]):tableOfFiles[i]["address"]])
            newPac.write(currentFile)

    lastFile = tableOfFiles[-1]
    newPac.write(bytE[(lastFile["address"] + lastFile["size"]):len(bytE)])

import os
import math

# Hardcoded paths
inputPacFile = "rom_work/data/Data_arc_pac/bin2.pac"
directory = "rom_work/data/Data_arc_pac/bin2/"

# Reading the original .pac file
with open(inputPacFile, "rb") as inputFile:
    bytE = inputFile.read()

# Extracting header and file name data from the original .pac
fileNamesBeginning = 0
fileNames = 0
fileDataBeginningAddress = 0

for i in range(0, len(bytE)):
    if ((i / 2) == (math.floor(i / 2))):
        if (bytE[i] & 0xFF == 0xFF) and (bytE[i + 1] & 0xFF == 0xFF):
            j = i - (i % 16)
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

# Repack using the files from the directory
# Gather files from the directory
newFiles = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.bin'):  # Assuming files are .bin
            filePath = os.path.join(root, file)
            newFiles.append(filePath)

# Rebuild the .pac file
outputPacFile = "repackedOutput.pac"
with open(outputPacFile, "wb") as newPac:
    # Write the original header and part of the fileNames
    newPac.write(bytE[0:fileNamesBeginning])
    newPac.write(fileNames[0:8])

    # Create new address and size information
    newAddress = fileDataBeginningAddress
    for i, filePath in enumerate(newFiles):
        with open(filePath, "rb") as openSesame:
            currentFile = openSesame.read()
            fileSize = len(currentFile)
            newPac.write(newAddress.to_bytes(4, "little"))  # Address of file
            newPac.write(fileSize.to_bytes(4, "little"))  # Size of file
            
            # No 'after' info in this case, but you can add if necessary
            newPac.write((0).to_bytes(8, "little"))  # Placeholder for 'after'

            newAddress += fileSize
    
    # Write the remaining bytes (handle padding if necessary)
    endBit = len(fileNames) - (len(fileNames) % 8)
    if (endBit < len(fileNames)):
        newPac.write(fileNames[endBit:(len(fileNames))])
    
    # Write the new files to the packed file
    for filePath in newFiles:
        with open(filePath, "rb") as openSesame:
            currentFile = openSesame.read()
            newPac.write(currentFile)

print(f"Repacking completed. Output saved as {outputPacFile}.")
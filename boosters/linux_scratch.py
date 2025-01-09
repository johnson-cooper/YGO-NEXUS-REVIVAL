import os
import subprocess
import math

# Read binary file
def read_binary(file_path):
   
    with open(file_path, "rb") as file:
        return bytearray(file.read())

# Write binary file
def write_binary(file_path, data):
   
    with open(file_path, "wb") as file:
        file.write(data)


import math
import os

class PacProcessor:  
    def __init__(self, file):
        self.inputFile = file
        handle = open(self.inputFile, 'rb')
        self.bytE = handle.read()
        handle.close()

    def unpack(self, out_path):
        self.header = 0
        self.fileNamesBeginning = 0
        self.fileNames = 0
        self.fileDataBeginningAddress = 0
        self.third = 0
        lineBreakBytes = [ 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18 ]
        self.tableOfFileNames = []
        self.tableOfFiles = []
        for i in range(0, len(self.bytE)):
        	if ((i / 2) == (math.floor(i / 2))):
        		if (self.bytE[i] & 0xFF == 0xFF) and (self.bytE[i + 1] & 0xFF == 0xFF):
        			j = i - (i % 16)
        			self.header = self.bytE[0:j]
        			self.fileNamesBeginning = j
        			break

        for i in range(self.fileNamesBeginning, len(self.bytE)):
        	if ((i % 16) == (self.fileNamesBeginning % 16)):
        		currentLine = self.bytE[i:(i + 8)]
        		if (int.from_bytes(currentLine, "little") == 0):
        			self.fileNames = self.bytE[self.fileNamesBeginning:i]
        			self.third = i
        			break

        for i in range(self.third, len(self.bytE)):
        	if ((i % 16) == (self.third % 16)):
        		currentLine = self.bytE[i:(i + 8)]
        		if (int.from_bytes(currentLine, "little") != 0):
        			self.fileDataBeginningAddress = i
        			break

        beginningOfWord = 0
        check = 0
        for i in range(0, len(self.header)):
            if (check == 1):
                check = 0
            else:
                currentByte = self.header[i]
                for j in range(15):
                    if (currentByte == lineBreakBytes[j]):
                        self.tableOfFileNames.insert(10000, self.header[beginningOfWord:i])
                        beginningOfWord = i + 2
                        check = 1

        finalCharacter = len(self.header) - 1
        while (self.header[finalCharacter - 3] & 0xFF == 0x00):
            finalCharacter = finalCharacter - 1
        self.tableOfFileNames.insert(10000, self.header[beginningOfWord:finalCharacter])

        temp = self.tableOfFileNames.copy()
        for k in temp:
            checkP = 0
            for j in range(len(k)):
                if (k[j] == 46):
                    checkP = 1

            if (checkP != 1):
                while (self.tableOfFileNames.count(k) > 0):
                    self.tableOfFileNames.remove(k)

        for i in range(8, len(self.fileNames)):
            if ((i % 8) == 0) and ((i + 8) <= len(self.fileNames)):
                byteSlice = self.fileNames[i:(i + 8)]
                fileSize = int.from_bytes(byteSlice[4:8], "little")
                if (fileSize != 0):
                    address = int.from_bytes(byteSlice[0:4], "little")
                    theFile = { "size": fileSize, "address": self.fileDataBeginningAddress + address, "after": -1 }
                    if ((i + 16) <= len(self.fileNames)) and (int.from_bytes(self.fileNames[(i + 12):(i + 16)], "little") == 0):
                        theFile["after"] = (int.from_bytes(self.fileNames[(i + 8):(i + 16)], "little"))
                    self.tableOfFiles.insert(10000, theFile)

        if (len(self.tableOfFileNames) != len(self.tableOfFiles)):
            print("Error! " + str(len(self.tableOfFileNames)) + " file names but " + str(len(self.tableOfFiles)) + " files!")
            raise ValueError
        self.out_path = out_path
        if os.path.exists(self.out_path):
             import shutil
             shutil.rmtree(self.out_path)
        os.makedirs(self.out_path, exist_ok=True)
        for i in range(0, len(self.tableOfFileNames)):
            cleanedFileName = self.tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
            currentFile = self.tableOfFiles[i]
            thisFrom = currentFile["address"]
            thisTo = currentFile["address"] + currentFile["size"]
            newFilePath = os.path.join(self.out_path, cleanedFileName)
            newFile = open(newFilePath, "wb")
            newFile.write(self.bytE[thisFrom:thisTo])
            newFile.close()

    def pack(self):
        if os.path.exists(self.inputFile):
             os.remove(self.inputFile)
        newPac = open(self.inputFile, "wb")
        newPac.close()
        newPac = open(self.inputFile, "ab")
        newPac.write(self.bytE[0:self.fileNamesBeginning])
        newPac.write(self.fileNames[0:8])
        newAddress = self.tableOfFiles[0]["address"] - self.fileDataBeginningAddress
        totalSizeDiff = 0
        for i in range(0, len(self.tableOfFileNames)):                
            cleanedFileName = self.tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
            openSesame = open(os.path.join(self.out_path, cleanedFileName), "rb")
            currentFile = openSesame.read()
            newPac.write(newAddress.to_bytes(4, "little"))
            newPac.write(len(currentFile).to_bytes(4, "little"))
            if (self.tableOfFiles[i]["after"] != -1):
                newPac.write(self.tableOfFiles[i]["after"].to_bytes(8, "little"))
            totalSizeDiff = totalSizeDiff + (len(currentFile) - self.tableOfFiles[i]["size"])
            if (i + 1 < len(self.tableOfFiles)):
                newAddress = self.tableOfFiles[i + 1]["address"] - self.fileDataBeginningAddress + totalSizeDiff
            openSesame.close()

            endBit = len(self.fileNames) - (len(self.fileNames) % 8)
            if (endBit < len(self.fileNames)):
                newPac.write(self.fileNames[endBit:(len(self.fileNames))])
            newPac.write(self.bytE[self.third:self.fileDataBeginningAddress])

            for i in range(0, len(self.tableOfFileNames)):
                cleanedFileName = self.tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
                openSesame = open(os.path.join(self.out_path, cleanedFileName), "rb")
                currentFile = openSesame.read()
                if (i > 0):
                    newPac.write(self.bytE[(self.tableOfFiles[i - 1]["address"] + self.tableOfFiles[i - 1]["size"]):self.tableOfFiles[i]["address"]])
                newPac.write(currentFile)
                openSesame.close()

            lastFile = self.tableOfFiles[len(self.tableOfFiles) - 1]
            newPac.write(self.bytE[(lastFile["address"] + lastFile["size"]):len(self.bytE)])
        newPac.close()


class ROMProcessor:
    def __init__(self, ndstool_path, rom_file, work_dir):
        self.ndstool_path = ndstool_path
        self.rom_file = rom_file
        self.work_dir = work_dir
        rom_work_dir = os.path.join('work_dir', 'unpacked')
        os.makedirs(rom_work_dir, exist_ok=True)
        self.rom_work_dir = rom_work_dir    

    def unpack_rom(self):
        print(f"Unpacking ROM file: {self.rom_file}...")
        subprocess.run(
            [self.ndstool_path, 
            "-x", self.rom_file, 
            "-9", os.path.join(self.rom_work_dir, "arm9.bin"),
            "-7", os.path.join(self.rom_work_dir, "arm7.bin"), 
            "-y9", os.path.join(self.rom_work_dir, "y9.bin"),
            "-y7", os.path.join(self.rom_work_dir, "y7.bin"),
            "-d", os.path.join(self.rom_work_dir, "data"),
            "-y", os.path.join(self.rom_work_dir, "overlay"),
            "-t", os.path.join(self.rom_work_dir, "banner.bin"),
            "-h", os.path.join(self.rom_work_dir, "header.bin"),
        ], check=True)
        print("ROM unpacked successfully.")

    def pack_rom(self, rom_file=None):
        if rom_file is None:
            rom_file = os.path.join(self.work_dir, 'romhack.nds')
        print(f"Packing ROM file: {rom_file}...")
        subprocess.run(
            [self.ndstool_path, 
            "-c", rom_file, 
            "-9", os.path.join(self.rom_work_dir, "arm9.bin"),
            "-7", os.path.join(self.rom_work_dir, "arm7.bin"), 
            "-y9", os.path.join(self.rom_work_dir, "y9.bin"),
            "-y7", os.path.join(self.rom_work_dir, "y7.bin"),
            "-d", os.path.join(self.rom_work_dir, "data"),
            "-y", os.path.join(self.rom_work_dir, "overlay"),
            "-t", os.path.join(self.rom_work_dir, "banner.bin"),
            "-h", os.path.join(self.rom_work_dir, "header.bin"),
        ], check=True)
        print("ROM unpacked successfully.")

def run():
    from boosters.script import ROMProcessor as RP, PacProcessor as PP
    import shutil
    handle = RP('ndstool', 'rom.nds', 'rom_work')
    handle.unpack_rom()
    pac = PP(file='./work_dir/unpacked/data/Data_arc_pac/deck.pac')
    pac.unpack(out_path='here')
    # Overwrite moja.dek with tomato.dek (as a test...)
    shutil.copyfile('./here/wcs002_tomabo.ydc', './here/Pwcs001_moja.ydc')
    pac.pack()
    handle.pack_rom(rom_file='my_rom.nds')

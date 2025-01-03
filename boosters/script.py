import os
import json
import subprocess
import math


class ROMProcessor:
    def __init__(self, ndstool_path, rom_file, work_dir, pac_file, pack_file, config_file, output_file):
        self.ndstool_path = ndstool_path
        self.rom_file = rom_file
        self.work_dir = work_dir
        self.pac_file = pac_file
        self.pack_file = pack_file
        self.config_file = config_file
        self.output_file = output_file

    # Load pack-to-card mapping
    def load_pack_mapping(self):
        print(f"Loading pack-to-card mapping from {self.config_file}...")
        with open(self.config_file, "r") as file:
            mapping = json.load(file)
        print(f"Loaded {len(mapping)} packs from the mapping.")
        return mapping

    # Read binary file
    def read_binary(self, file_path):
        print(f"Reading binary file: {file_path}...")
        with open(file_path, "rb") as file:
            return bytearray(file.read())

    # Write binary file
    def write_binary(self, file_path, data):
        print(f"Writing binary data to: {file_path}...")
        with open(file_path, "wb") as file:
            file.write(data)

    # Unpack ROM
    def unpack_rom(self):
        print(f"Unpacking ROM file: {self.rom_file}...")
        subprocess.run([self.ndstool_path, "-x", self.rom_file, "-9", os.path.join(self.work_dir, "arm9.bin"),
                        "-7", os.path.join(self.work_dir, "arm7.bin"), "-y9", os.path.join(self.work_dir, "y9.bin"),
                        "-y7", os.path.join(self.work_dir, "y7.bin"), "-d", os.path.join(self.work_dir, "data"),
                        "-y", os.path.join(self.work_dir, "overlay")], check=True)
        print("ROM unpacked successfully.")

        pac_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin2.pac")
        unpack_dir = os.path.join(self.work_dir, "data/Data_arc_pac/bin2")

        print(f"Unpacking the .pac file: {pac_file}...")

        if not os.path.exists(pac_file):
            print(f"Error: {pac_file} not found!")
            return

        self.unpack_pac_file(pac_file, unpack_dir)

    # Function to unpack .pac file
    def unpack_pac_file(self, pac_file, unpack_dir):
        try:
            print("Unpacking PAC file...")
            pac_data = self.read_binary(pac_file)

            # Process PAC file
            header = 0
            fileNamesBeginning = 0
            fileNames = 0
            fileDataBeginningAddress = 0
            third = 0
            lineBreakBytes = [0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18]
            tableOfFileNames = []
            tableOfFiles = []

            for i in range(0, len(pac_data)):
                if ((i / 2) == (math.floor(i / 2))):
                    if (pac_data[i] & 0xFF == 0xFF) and (pac_data[i + 1] & 0xFF == 0xFF):
                        j = i - (i % 16)
                        header = pac_data[0:j]
                        fileNamesBeginning = j
                        break

            for i in range(fileNamesBeginning, len(pac_data)):
                if ((i % 16) == (fileNamesBeginning % 16)):
                    currentLine = pac_data[i:(i + 8)]
                    if (int.from_bytes(currentLine, "little") == 0):
                        fileNames = pac_data[fileNamesBeginning:i]
                        third = i
                        break

            for i in range(third, len(pac_data)):
                if ((i % 16) == (third % 16)):
                    currentLine = pac_data[i:(i + 8)]
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
                            tableOfFileNames.insert(10000, header[beginningOfWord:i])
                            beginningOfWord = i + 2
                            check = 1

            finalCharacter = len(header) - 1
            while (header[finalCharacter - 3] & 0xFF == 0x00):
                finalCharacter = finalCharacter - 1
            tableOfFileNames.insert(10000, header[beginningOfWord:finalCharacter])

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
                        theFile = { "size": fileSize, "address": fileDataBeginningAddress + address, "after": -1 }
                        if ((i + 16) <= len(fileNames)) and (int.from_bytes(fileNames[(i + 12):(i + 16)], "little") == 0):
                            theFile["after"] = (int.from_bytes(fileNames[(i + 8):(i + 16)], "little"))
                        tableOfFiles.insert(10000, theFile)

            if len(tableOfFileNames) != len(tableOfFiles):
                print("Error! Number of file names and file entries mismatch!")
                return

            try:
                os.makedirs(unpack_dir, exist_ok=True)
                for i in range(len(tableOfFileNames)):
                    cleanedFileName = tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
                    currentFile = tableOfFiles[i]
                    thisFrom = currentFile["address"]
                    thisTo = currentFile["address"] + currentFile["size"]

                    with open(os.path.join(unpack_dir, cleanedFileName), "wb") as newFile:
                        newFile.write(pac_data[thisFrom:thisTo])

                print(f"PAC file unpacked successfully to {unpack_dir}.")
            except Exception as e:
                print(f"Error while unpacking PAC file: {e}")

        except Exception as e:
            print(f"Error unpacking the PAC file: {e}")

    # Read card packs from card_pack.bin, skipping any packs where pack ID or card ID equals 0
    def read_card_packs(self):
        print(f"Reading card packs from {self.pack_file}...")
        data = self.read_binary(self.pack_file)

        packs = []
        for i in range(0, len(data), 8):  # Assuming each pack has 8 bytes (4 for pack ID, 4 for card ID)
            if i + 8 <= len(data):
                pack_id = int.from_bytes(data[i:i + 4], "little")
                card_id = int.from_bytes(data[i + 4:i + 8], "little")

                if pack_id != 0 and card_id != 0:
                    packs.append((pack_id, card_id))

        return packs

    # Write card packs to a text file
    def write_packs_to_txt(self, packs):
        print(f"Writing card packs to {self.output_file}...")
        with open(self.output_file, "w") as file:
            for pack_id, card_id in packs:
                file.write(f"Pack ID: {pack_id}, Card ID: {card_id}\n")
        print(f"Packs and cards written to {self.output_file}.")

# Modify the card packs (replace all pack IDs)
    def modify_card_packs(self, packs):
        print(f"Modifying card packs in {self.pack_file}...")
        new_pack_id = 771751940  # New pack ID (decimal representation of 0x01000004)

        if packs:
            print(f"\nReplacing all pack IDs with {new_pack_id}...")
            for i in range(len(packs)):
                _, card_id = packs[i]  # Keep the original card ID
                packs[i] = (new_pack_id, card_id)  # Replace pack ID
            print(f"Updated packs: {packs}")
        else:
            print("No packs to modify!")

        return packs
    
     # After modifying packs, write them back to card_pack.bin
    def write_modified_packs_to_bin(self, packs):
        print(f"Writing modified card packs to {self.pack_file}...")
        with open(self.pack_file, "wb") as file:
            for pack_id, card_id in packs:
                file.write(pack_id.to_bytes(4, "little"))
                file.write(card_id.to_bytes(4, "little"))
        print(f"Modified packs written to {self.pack_file}.")

    # Repack the modified card packs into the original ROM
    def repack_rom(self):
        print(f"Repacking the ROM...")
        subprocess.run([self.ndstool_path, "-9", os.path.join(self.work_dir, "arm9.bin"),
                        "-7", os.path.join(self.work_dir, "arm7.bin"),
                        "-y9", os.path.join(self.work_dir, "y9.bin"),
                        "-y7", os.path.join(self.work_dir, "y7.bin"),
                        "-d", os.path.join(self.work_dir, "data"),
                        "-y", os.path.join(self.work_dir, "overlay"),
                        "-9", self.rom_file, "-7", self.rom_file])

        print("ROM repacked successfully!")


if __name__ == "__main__":
    # Set the paths as provided
    NDSTOOL_PATH = "ndstool.exe"
    ROM_FILE = "rom.nds"
    WORK_DIR = "rom_work"
    PAC_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2.pac")  # Path to the .pac file
    PACK_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2/card_pack.bin")  # Path to the card_pack.bin
    CONFIG_FILE = "pack_card_mapping.json"
    OUTPUT_FILE = "packs_and_cards.txt"  # Output text file path

    # Create the ROMProcessor instance and start processing
    processor = ROMProcessor(NDSTOOL_PATH, ROM_FILE, WORK_DIR, PAC_FILE, PACK_FILE, CONFIG_FILE, OUTPUT_FILE)

    processor.unpack_rom()
    pack_mapping = processor.load_pack_mapping()
    card_packs = processor.read_card_packs()
    modified_packs = processor.modify_card_packs(card_packs)
      # Write the modified packs back to the ROM file
    processor.write_modified_packs_to_bin(modified_packs)
    processor.write_packs_to_txt(modified_packs)
    processor.repack_rom()
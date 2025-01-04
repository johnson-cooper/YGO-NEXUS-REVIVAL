import os
import json
import subprocess
import math


class ROMProcessor:
    def __init__(self, ndstool_path, rom_file, work_dir, pac_file, pack_file, config_file, output_file, card_name_file, card_indx_file, modified_cardstxt, output_rom_file):
        self.ndstool_path = ndstool_path
        self.rom_file = rom_file
        self.work_dir = work_dir
        self.pac_file = pac_file
        self.pack_file = pack_file
        self.config_file = config_file
        self.output_file = output_file
        self.card_name_file = card_name_file
        self.card_indx_file = card_indx_file
        self.modified_cardstxt = modified_cardstxt 
        self.output_rom_file = output_rom_file

    def load_pack_mapping(self):
        print(f"Loading card_name_e.bin from {self.card_name_file}...")
        with open(self.card_name_file, "rb") as file:
            card_name_data = file.read()

        print(f"Loading card_indx_e.bin from {self.card_indx_file}...")
        with open(self.card_indx_file, "rb") as file:
            card_indx_data = file.read()

        konami_to_internal_id = {}
        entry_size = 8  # Each entry is 8 bytes in the card_indx_e.bin

        # Iterate through the card_indx_data
        for internal_id in range(0, len(card_indx_data), entry_size):
            # Fetch the name offset
            offsets = card_indx_data[internal_id:internal_id + entry_size]
            name_offset = int.from_bytes(offsets[:4], "little")

            # Fetch the name
            name_end = card_name_data.find(b"\x00", name_offset)  # Find null-terminator
            if name_end == -1:
                continue  # Skip if no null-terminator
            card_name = card_name_data[name_offset:name_end].decode("utf-8", errors="ignore").strip()

            konami_to_internal_id[card_name] = internal_id // entry_size

        print(f"Loaded {len(konami_to_internal_id)} Konami code to internal ID mappings.")
        return konami_to_internal_id

    # Read binary file
    def read_binary(self, file_path):
       
        with open(file_path, "rb") as file:
            return bytearray(file.read())

    # Write binary file
    def write_binary(self, file_path, data):
       
        with open(file_path, "wb") as file:
            file.write(data)

    def unpack_rom(self):
        print(f"Unpacking ROM file: {self.rom_file}...")
        subprocess.run([self.ndstool_path, "-x", self.rom_file, "-9", os.path.join(self.work_dir, "arm9.bin"),
                        "-7", os.path.join(self.work_dir, "arm7.bin"), "-y9", os.path.join(self.work_dir, "y9.bin"),
                        "-y7", os.path.join(self.work_dir, "y7.bin"), "-d", os.path.join(self.work_dir, "data"),
                        "-y", os.path.join(self.work_dir, "overlay")], check=True)
        print("ROM unpacked successfully.")

        # Define PAC files and their directories
        pac_file1 = os.path.join(self.work_dir, "data/Data_arc_pac/bin.pac")
        unpack_dir1 = os.path.join(self.work_dir, "data/Data_arc_pac/bin")

        pac_file2 = os.path.join(self.work_dir, "data/Data_arc_pac/bin2.pac")
        unpack_dir2 = os.path.join(self.work_dir, "data/Data_arc_pac/bin2")

        # Unpack both PAC files
        if os.path.exists(pac_file1):
            self.unpack_pac_file(pac_file1, unpack_dir1)
        else:
            print(f"Error: {pac_file1} not found!")

        if os.path.exists(pac_file2):
            self.unpack_pac_file(pac_file2, unpack_dir2)
        else:
            print(f"Error: {pac_file2} not found!")

    def unpack_pac_file(self, pac_file, unpack_dir):
        try:
            
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

            # Parse header
            for i in range(0, len(pac_data)):
                if ((i / 2) == (math.floor(i / 2))):
                    if (pac_data[i] & 0xFF == 0xFF) and (pac_data[i + 1] & 0xFF == 0xFF):
                        j = i - (i % 16)
                        header = pac_data[0:j]
                        fileNamesBeginning = j
                        break

            # Parse file names
            for i in range(fileNamesBeginning, len(pac_data)):
                if ((i % 16) == (fileNamesBeginning % 16)):
                    currentLine = pac_data[i:(i + 8)]
                    if (int.from_bytes(currentLine, "little") == 0):
                        fileNames = pac_data[fileNamesBeginning:i]
                        third = i
                        break

            # Parse file data
            for i in range(third, len(pac_data)):
                if ((i % 16) == (third % 16)):
                    currentLine = pac_data[i:(i + 8)]
                    if (int.from_bytes(currentLine, "little") != 0):
                        fileDataBeginningAddress = i
                        break

            # Process file names
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

            # Clean up file names
            temp = tableOfFileNames.copy()
            for k in temp:
                checkP = 0
                for j in range(len(k)):
                    if (k[j] == 46):
                        checkP = 1

                if (checkP != 1):
                    while (tableOfFileNames.count(k) > 0):
                        tableOfFileNames.remove(k)

            # Parse files and sizes
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

            # Create the unpack directory and write files
            try:
                os.makedirs(unpack_dir, exist_ok=True)
                for i in range(len(tableOfFileNames)):
                    cleanedFileName = tableOfFileNames[i].decode("utf-8").split("\x00", 1)[0]
                    currentFile = tableOfFiles[i]
                    thisFrom = currentFile["address"]
                    thisTo = currentFile["address"] + currentFile["size"]

                    with open(os.path.join(unpack_dir, cleanedFileName), "wb") as newFile:
                        newFile.write(pac_data[thisFrom:thisTo])

                print(f"PAC file unpacked successfully.")
            except Exception as e:
                print(f"Error while unpacking PAC file: {e}")

        except Exception as e:
            print(f"Error unpacking the PAC file: {e}")

    

    def read_card_packs(self):
        print(f"Reading card packs from {self.pack_file}...")
        data = self.read_binary(self.pack_file)

        packs = []
        total_packs = 0
        skipped_packs = 0

        # Debug: Total size of the binary data
        print(f"Total bytes read: {len(data)}")

        # Each entry is 8 bytes
        for internal_id in range(0, len(data), 8):
            pack_entry = data[internal_id:internal_id + 8]
            if len(pack_entry) < 8:
                continue  # Skip incomplete entries

            pack_id = pack_entry[3]  # 4th byte is the pack ID
            internal_id = internal_id // 8  # Calculate internal ID
            _, card_name = self.get_internal_card_id(internal_id)

            # Skip empty names
            if not card_name.strip():
                skipped_packs += 1
                continue

            packs.append((pack_id, internal_id, card_name))
            total_packs += 1

        print(f"Total packs processed: {total_packs}")
        print(f"Total skipped packs: {skipped_packs}")
        return packs
    
    def get_internal_card_id(self, card_id):
        card_name_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin2/card_name_e.bin")
        card_indx_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin2/card_indx_e.bin")

        card_names = self.read_binary(card_name_file)
        card_indexes = self.read_binary(card_indx_file)

        # Calculate the offset for the given card ID
        card_offset = card_id * 8  # Each entry is 8 bytes
        if card_offset + 8 > len(card_indexes):
            return card_id, "Unknown Card"

        offsets = card_indexes[card_offset:card_offset + 8]
        name_offset = int.from_bytes(offsets[:4], "little")

        # Fetch the name
        name_end = card_names.find(b"\x00", name_offset)  # Find null-terminator
        card_name = card_names[name_offset:name_end].decode("utf-8", errors="ignore").strip() if name_end != -1 else "Unknown Card"

        return card_id, card_name

    # Write card packs to a text file
    def write_packs_to_txt(self, packs):
        print(f"Writing card packs to {self.output_file}...")
        with open(self.output_file, "w") as file:
            for pack_id, internal_id, card_name in packs:
                file.write(f"Pack ID: {pack_id}, Internal ID: {internal_id}, Card Name: {card_name}\n")
        print(f"Packs and cards written to {self.output_file}.")




    def modify_card_packs(self, packs):
        print(f"Modifying card packs in {self.pack_file}...")

        # Define the internal IDs and their new pack IDs
        target_internal_id_1 = 759  # The internal ID for the first card
        target_internal_id_2 = 251  # The internal ID for the second card
        new_pack_id_1 = 2          # New pack ID for the card with internal ID 759
        new_pack_id_2 = 1          # New pack ID for the card with internal ID 251

        modified_packs = []  # List to store modified packs

        if packs:
            print(f"\nSwitching pack IDs for internal IDs {target_internal_id_1} and {target_internal_id_2}...")

            # Iterate over the packs and modify the necessary values
            for i in range(len(packs)):
                pack_id, internal_id, card_name = packs[i]  # Unpack all three values

                # Find the cards with internal ID 759 and 251
                if internal_id == target_internal_id_1:
                    # Fetch the pack data for internal ID 759 (target card)
                    pack_data_offset = 8 * internal_id  # Multiply internal ID by 8 to get the offset in the card_pack file
                    pack_data = self.read_binary(self.pack_file)[pack_data_offset:pack_data_offset + 8]
                    
                    # Update the pack ID of card with internal ID 759 to new_pack_id_1
                    pack_data[3] = new_pack_id_1  # Set the new pack_id at the 4th byte (index 3)
                    modified_packs.append((new_pack_id_1, internal_id, card_name))  # Preserve internal ID and card name

                elif internal_id == target_internal_id_2:
                    # Fetch the pack data for internal ID 251 (target card)
                    pack_data_offset = 8 * internal_id  # Multiply internal ID by 8 to get the offset in the card_pack file
                    pack_data = self.read_binary(self.pack_file)[pack_data_offset:pack_data_offset + 8]
                    
                    # Update the pack ID of card with internal ID 251 to new_pack_id_2
                    pack_data[3] = new_pack_id_2  # Set the new pack_id at the 4th byte (index 3)
                    modified_packs.append((new_pack_id_2, internal_id, card_name))  # Preserve internal ID and card name

            print(f"Pack IDs switched for internal IDs {target_internal_id_1} and {target_internal_id_2}.")

        else:
            print("No packs to modify!")

        return modified_packs
    

    def get_modified_card_name(self, new_card_id):
        card_name_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin2/card_name_e.bin")
        card_indx_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin2/card_indx_e.bin")

        card_names = self.read_binary(card_name_file)
        card_indexes = self.read_binary(card_indx_file)

        # Calculate the offset for the given internal ID
        card_offset = new_card_id * 8  # Assuming each entry is 8 bytes
        new_card_id = new_card_id  # Internal ID is used directly here

        # Find the card name and internal ID
        name_offset = int.from_bytes(card_indexes[card_offset:card_offset+4], "little")
        name_start = name_offset
        name_end = card_names.find(b"\x00", name_start)
        modified_card_name = card_names[name_start:name_end].decode("utf-8") if name_end != -1 else "Unknown Card"

        return modified_card_name

    
    def write_modified_packs_to_bin(self, modified_packs):
        print(f"Writing modified card packs to {self.pack_file}...")

        with open(self.pack_file, "r+b") as file:  # Open in read-write binary mode
            for new_pack_id, internal_id, card_name in modified_packs:
                # Ensure the new pack ID is within the byte range (0-255)
                if not (0 <= new_pack_id <= 255):
                    raise ValueError(f"Invalid pack ID: {new_pack_id}. It must be between 0 and 255.")

                # Calculate the offset for the current internal_id (8 bytes per entry)
                pack_data_offset = 8 * internal_id

                # Seek to the correct location in the file
                file.seek(pack_data_offset)

                # Read the current 8 bytes (the entire entry)
                pack_data = file.read(8)

                # Check the current data (debugging line)
                print(f"Current data at offset {pack_data_offset}: {pack_data.hex()}")

                # Modify the 4th byte (index 3) to the new pack ID
                pack_data = bytearray(pack_data)  # Convert to bytearray for mutability
                pack_data[3] = new_pack_id  # Update the pack ID byte

                # Check the modified data (debugging line)
                print(f"Modified data: {pack_data.hex()}")

                # Seek back to the correct position and write the modified 8 bytes
                file.seek(pack_data_offset)
                file.write(pack_data)

        print(f"Modified packs written to {self.pack_file}.")

    # Write modified card names to a text file
    def write_modified_cards_to_txt(self, modified_packs):
        print(f"Writing modified card names to {self.modified_cardstxt}...")

        # Open the file for writing
        with open(self.modified_cardstxt, "w") as file:
            for pack_id, internal_id, new_card_name in modified_packs:
                # Write the modified information to the text file
                file.write(f"Pack ID: {pack_id}, Internal ID: {internal_id}, Modified Card Name: {new_card_name}\n")

        print(f"Modified packs and cards written to {self.modified_cardstxt}.")
        




if __name__ == "__main__":
    # Set the paths as provided
    NDSTOOL_PATH = "ndstool.exe"
    ROM_FILE = "rom.nds"
    WORK_DIR = "rom_work"
    PAC_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2.pac")  # Path to the .pac file
    PACK_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2/card_pack.bin")  # Path to the card_pack.bin
    CONFIG_FILE = "pack_card_mapping.json"
    OUTPUT_FILE = "packs_and_cards.txt"  # Output text file path
    CARD_NAME_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2/card_name_e.bin")
    CARD_INDX_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2/card_indx_e.bin")
    MODIFIED_PACKSTXT = "modifiedpacks.txt"
    OUTPUT_ROM_FILE = "romhack.nds"
    

    # Create the ROMProcessor instance and start processing
    processor = ROMProcessor(NDSTOOL_PATH, ROM_FILE, WORK_DIR, PAC_FILE, PACK_FILE, CONFIG_FILE, OUTPUT_FILE, CARD_NAME_FILE, CARD_INDX_FILE, MODIFIED_PACKSTXT, OUTPUT_ROM_FILE)

    processor.unpack_rom()
    pack_mapping = processor.load_pack_mapping()
    packs = processor.read_card_packs()
    processor.write_packs_to_txt(packs)
    modified_packs = processor.modify_card_packs(packs)
    processor.write_modified_packs_to_bin(modified_packs)
    processor.write_modified_cards_to_txt(modified_packs)
    
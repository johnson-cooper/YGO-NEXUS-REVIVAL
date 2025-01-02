import os
import json
import subprocess
import math

# Paths
NDSTOOL_PATH = "ndstool.exe"
ROM_FILE = "rom.nds"
WORK_DIR = "rom_work"
PAC_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2.pac")  # Path to the .pac file
PACK_FILE = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2/card_pack.bin")  # Path to the card_pack.bin
CONFIG_FILE = "pack_card_mapping.json"
OUTPUT_FILE = "packs_and_cards.txt"  # Output text file path

# Load pack-to-card mapping
def load_pack_mapping(config_file):
    print(f"Loading pack-to-card mapping from {config_file}...")
    with open(config_file, "r") as file:
        mapping = json.load(file)
    print(f"Loaded {len(mapping)} packs from the mapping.")
    return mapping

# Read binary file
def read_binary(file_path):
    print(f"Reading binary file: {file_path}...")
    with open(file_path, "rb") as file:
        return bytearray(file.read())

# Write binary file
def write_binary(file_path, data):
    print(f"Writing binary data to: {file_path}...")
    with open(file_path, "wb") as file:
        file.write(data)

# Unpack ROM
def unpack_rom():
    print(f"Unpacking ROM file: {ROM_FILE}...")
    subprocess.run([NDSTOOL_PATH, "-x", ROM_FILE, "-9", os.path.join(WORK_DIR, "arm9.bin"),
                    "-7", os.path.join(WORK_DIR, "arm7.bin"), "-y9", os.path.join(WORK_DIR, "y9.bin"),
                    "-y7", os.path.join(WORK_DIR, "y7.bin"), "-d", os.path.join(WORK_DIR, "data"),
                    "-y", os.path.join(WORK_DIR, "overlay")], check=True)
    print("ROM unpacked successfully.")

    pac_file = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2.pac")
    unpack_dir = os.path.join(WORK_DIR, "data/Data_arc_pac/bin2")
    
    print(f"Unpacking the .pac file: {pac_file}...")

    # Check if the .pac file exists
    if not os.path.exists(pac_file):
        print(f"Error: {pac_file} not found!")
        return

    # Unpack the .pac file directly
    unpack_pac_file(pac_file, unpack_dir)

# Function to unpack .pac file (modified from your script)
def unpack_pac_file(pac_file, unpack_dir):
    try:
        print("Unpacking PAC file...")
        pac_data = read_binary(pac_file)

        # Process PAC file using similar logic as in your provided script
        header = 0
        fileNamesBeginning = 0
        fileNames = 0
        fileDataBeginningAddress = 0
        third = 0
        lineBreakBytes = [0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18]
        tableOfFileNames = []
        tableOfFiles = []

        # Implement the unpacking logic for the PAC file
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

        # Write the unpacked data to the directory
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
def read_card_packs(pack_file):
    print(f"Reading card packs from {pack_file}...")
    data = read_binary(pack_file)
    
    packs = []
    for i in range(0, len(data), 8):  # Assuming each pack has 8 bytes (4 for pack ID, 4 for card ID)
        if i + 8 <= len(data):
            pack_id = int.from_bytes(data[i:i + 4], "little")
            card_id = int.from_bytes(data[i + 4:i + 8], "little")
            
            # Skip packs where pack_id or card_id is 0
            if pack_id != 0 and card_id != 0:
                packs.append((pack_id, card_id))
    
    return packs

# Write card packs to a text file
def write_packs_to_txt(packs, output_file):
    print(f"Writing card packs to {output_file}...")
    with open(output_file, "w") as file:
        for pack_id, card_id in packs:
            file.write(f"Pack ID: {pack_id}, Card ID: {card_id}\n")
    print(f"Packs and cards written to {output_file}.")

# Modify the card packs (e.g., replacing cards in the first pack)
def modify_card_packs(pack_file, packs):
    print(f"Modifying card packs in {pack_file}...")
    blue_eyes_ultimate_id = 0x1112  # Blue-Eyes Ultimate Dragon ID in hex
    
    if packs:
        print("\nReplacing the first pack with Blue-Eyes Ultimate Dragon...")
        pack_id, _ = packs[0]  # Keep the original pack ID
        packs[0] = (pack_id, blue_eyes_ultimate_id)  # Replace card ID
    else:
        print("No packs found to modify.")
        return
    
    # Confirm and save changes
    confirm = input("\nDo you want to proceed with saving these changes? (Y/N): ")
    if confirm.lower() != 'y':
        print("Modification canceled.")
        return
    
    # Convert the modified packs back into binary format
    data = bytearray()
    for pack_id, card_id in packs:
        data.extend(pack_id.to_bytes(4, "little"))
        data.extend(card_id.to_bytes(4, "little"))

    write_binary(pack_file, data)
    print(f"Card packs modified and saved to {pack_file}.")

# Repack ROM after modification with size check
def repack_rom():
    # Step 1: Get the original ROM size
    original_size = os.path.getsize(ROM_FILE)
    
    print("Repacking ROM...")
    subprocess.run([NDSTOOL_PATH, "-c", ROM_FILE, "-9", os.path.join(WORK_DIR, "arm9.bin"),
                    "-7", os.path.join(WORK_DIR, "arm7.bin"), "-y9", os.path.join(WORK_DIR, "y9.bin"),
                    "-y7", os.path.join(WORK_DIR, "y7.bin"), "-d", os.path.join(WORK_DIR, "data"),
                    "-y", os.path.join(WORK_DIR, "overlay")], check=True)
    print("ROM repacked successfully.")
    
    # Step 2: Get the new ROM size and check if it matches the original
    new_size = os.path.getsize(ROM_FILE)
    if new_size > original_size:
        print(f"Warning: ROM size increased by {new_size - original_size} bytes")
        # Optionally, trim or adjust the ROM size
        with open(ROM_FILE, "rb+") as rom_file:
            rom_file.truncate(original_size)
        print("Extra bytes trimmed to match original ROM size.")
    elif new_size < original_size:
        print(f"Warning: ROM size decreased by {original_size - new_size} bytes")
        # Optionally, pad the ROM with zero bytes to match the original size
        with open(ROM_FILE, "ab") as rom_file:
            rom_file.write(b'\x00' * (original_size - new_size))
        print("ROM padded to match original ROM size.")

# Main function to orchestrate all tasks
def main():
    # Step 1: Unpack the ROM if needed
    unpack_rom()

    # Step 2: Read the card packs directly from the ROM (card_pack.bin)
    packs = read_card_packs(PACK_FILE)

    # Step 3: Write the packs and cards to a text file
    write_packs_to_txt(packs, OUTPUT_FILE)

    # Step 4: Modify the card packs
    modify_card_packs(PACK_FILE, packs)

    # Step 5: Repack the ROM after modification
    repack_rom()

if __name__ == "__main__":
    main()
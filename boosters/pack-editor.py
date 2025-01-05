import dearpygui.dearpygui as dpg
import re
import json
import os
import subprocess
import math

def unpack_rom(rom_file, ndstool_path, work_dir):
    print(f"Unpacking ROM file: {rom_file}...")
    subprocess.run([ndstool_path, "-x", rom_file, "-9", os.path.join(work_dir, "arm9.bin"),
                    "-7", os.path.join(work_dir, "arm7.bin"), "-y9", os.path.join(work_dir, "y9.bin"),
                    "-y7", os.path.join(work_dir, "y7.bin"), "-d", os.path.join(work_dir, "data"),
                    "-y", os.path.join(work_dir, "overlay")], check=True)
    print("ROM unpacked successfully.")

    # Define PAC files and their directories
    pac_file1 = os.path.join(work_dir, "data/Data_arc_pac/bin.pac")
    unpack_dir1 = os.path.join(work_dir, "data/Data_arc_pac/bin")

    pac_file2 = os.path.join(work_dir, "data/Data_arc_pac/bin2.pac")
    unpack_dir2 = os.path.join(work_dir, "data/Data_arc_pac/bin2")

    # Unpack both PAC files
    if os.path.exists(pac_file1):
        unpack_pac_file(pac_file1, unpack_dir1)
    else:
        print(f"Error: {pac_file1} not found!")

    if os.path.exists(pac_file2):
        unpack_pac_file(pac_file2, unpack_dir2)
    else:
        print(f"Error: {pac_file2} not found!")


def unpack_pac_file(pac_file, unpack_dir):
    try:
        pac_data = read_binary(pac_file)

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


def read_binary(pac_file):
    with open(pac_file, "rb") as f:
        return f.read()


# Dear PyGui button callback to start the unpacking
def on_unpack_button_click(sender, app_data):
    rom_file = "rom.nds"  # Change this to your actual ROM file path
    ndstool_path = "ndstool.exe"  # Change this to your actual ndstool executable path
    work_dir = "rom_work"  # Change this to your working directory
    os.makedirs(work_dir, exist_ok=True)
    unpack_rom(rom_file, ndstool_path, work_dir)



# Function to read the cards from the pack_and_cards.txt file
def read_cards_from_file(filename):
    cards = []
    with open(filename, 'r') as file:
        for line in file:
            match = re.match(r"Pack ID: (\d+), Internal ID: (\d+), Card Name: (.+)", line.strip())
            if match:
                pack_id = int(match.group(1))
                internal_id = int(match.group(2))
                card_name = match.group(3)
                cards.append((pack_id, internal_id, card_name))
    return cards

# Organize cards by Pack ID and count them
def organize_and_count_cards(cards):
    packs = {}
    counts = {}
    for card in cards:
        pack_id, internal_id, card_name = card
        if pack_id not in packs:
            packs[pack_id] = []
            counts[pack_id] = 0
        packs[pack_id].append(card)
        counts[pack_id] += 1
    return packs, counts

# Save changes to a temporary file
def save_to_temp_file(cards, temp_filename="temp_cards.txt"):
    with open(temp_filename, 'w') as file:
        for card in cards:
            file.write(f"Pack ID: {card[0]}, Internal ID: {card[1]}, Card Name: {card[2]}\n")

# Check for over-limit cards
# Function to check for over-limit cards and update the temporary file
# Function to check for over-limit and under-limit cards and update the temporary file
def update_temp_file_with_limits(original_counts, temp_filename="temp_cards.txt"):
    with open(temp_filename, 'r') as file:
        lines = file.readlines()
    
    pack_counts = {}
    updated_lines = []

    # Count cards per pack in the temporary file
    for line in lines:
        match = re.match(r"Pack ID: (\d+), Internal ID: (\d+), Card Name: (.+)", line.strip())
        if match:
            pack_id = int(match.group(1))
            if pack_id not in pack_counts:
                pack_counts[pack_id] = 0
            pack_counts[pack_id] += 1

    # Check for over-limit and under-limit, and mark the lines
    for line in lines:
        match = re.match(r"Pack ID: (\d+), Internal ID: (\d+), Card Name: (.+)", line.strip())
        if match:
            pack_id = int(match.group(1))
            original_limit = original_counts.get(pack_id, 0)
            if pack_counts[pack_id] > original_limit:
                updated_lines.append(f"{line.strip()} [OVER LIMIT]\n")
            elif pack_counts[pack_id] < original_limit:
                updated_lines.append(f"{line.strip()} [UNDER LIMIT]\n")
            else:
                updated_lines.append(line)

    # Write updated lines back to the temporary file
    with open(temp_filename, 'w') as file:
        file.writelines(updated_lines)

# Save the modified pack information to config.json
def save_config(temp_filename="temp_cards.txt", config_filename="config.json"):
    config_data = {"cards": []}
    with open(temp_filename, 'r') as file:
        for line in file:
            match = re.match(r"Pack ID: (\d+), Internal ID: (\d+), Card Name: (.+)", line.strip())
            if match:
                target_internal_id = int(match.group(2))
                new_pack_id = int(match.group(1))
                config_data["cards"].append({"target_internal_id": target_internal_id, "new_pack_id": new_pack_id})

    with open(config_filename, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)

    # Remove the temporary file after saving
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

def load_file_callback():
    save_to_temp_file(cards)  # Save initial data to temp file
    update_temp_file_with_limits(original_counts)  # Pass original_counts
    with open("temp_cards.txt", 'r') as file:
        content = file.read()
    dpg.set_value("card_text_editor", content)

# New function for "Save Project" that saves only the updated temporary file
def save_project_callback():
    # Write current text editor content to temp file
    content = dpg.get_value("card_text_editor")
    with open("temp_cards.txt", 'w') as file:
        file.write(content)
    
    # Update temp file with limits (adds "[OVER LIMIT]" where necessary)
    update_temp_file_with_limits(original_counts)  # Pass original_counts

    # Reload the updated temp file into the text editor
    with open("temp_cards.txt", 'r') as file:
        updated_content = file.read()
    dpg.set_value("card_text_editor", updated_content)

# Function to execute another Python script when PATCH ROM button is clicked
def patch_rom_callback():
    # Run the script.py
    subprocess.run(["python", "script.py"], check=True)
def rebuild_rom_callback():
    # Run the script.py
    subprocess.run(["python", "repack.py"], check=True)    

# Modified function for "Modify and Save to Config"
def modify_and_save_to_config_callback():
    # Ensure the temporary file is updated
    save_project_callback()

    # Save to config.json from the updated temporary file
    save_config()

# Initialize DearPyGui
dpg.create_context()

# Read cards from the text file
cards = read_cards_from_file('packs_and_cards.txt')

# Organize cards and get original counts
organized_cards, original_counts = organize_and_count_cards(cards)

# Create the main window
with dpg.window(label="Card Pack Modifier", tag="Card Pack Modifier", width=1280, height=720):
    # Button to load the file content
    dpg.add_button(label="Unpack ROM", callback=on_unpack_button_click)
    dpg.add_button(label="Load File", callback=load_file_callback)
    
    # Button to save only the temporary file updates (Save Project)
    dpg.add_button(label="Save Project", callback=save_project_callback)
    
    # Button to save both the updates and the config.json file
    dpg.add_button(label="Modify and Save Changes to Config", callback=modify_and_save_to_config_callback)
     # Button to patch the ROM by executing the script.py
    dpg.add_button(label="PATCH ROM", callback=patch_rom_callback)
    dpg.add_button(label="REBUILD BIN2.PAC", callback=rebuild_rom_callback)
    
    # Scrollable text editor to display the file content
    dpg.add_input_text(tag="card_text_editor", multiline=True, readonly=False, height=-1, width=-1)

# Create and set the viewport to be the primary window
dpg.create_viewport(title="Card Pack Modifier", width=1280, height=720)

# Set the primary window before starting the DearPyGui application
dpg.set_primary_window("Card Pack Modifier", True)

# Show the main window as the primary window
dpg.show_viewport()

# Start the DearPyGui application
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()
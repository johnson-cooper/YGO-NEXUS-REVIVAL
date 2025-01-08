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

# Save the modified pack information to config.json
# Save config function
# Save config function
# Save config function
def save_config(cards, config_filename="config.json"):
    config_data = {"cards": []}
    
    # Debug output to ensure cards are correctly formatted
    print("Cards to save:", cards)
    
    # Store the card data in the required format with integers
    for pack_id, internal_id in cards:
        config_data["cards"].append({
            "target_internal_id": int(internal_id),  # Convert to integer
            "new_pack_id": int(pack_id)  # Convert to integer
        })

    # Write the config data to config.json
    with open(config_filename, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)
    print(f"Config saved to {config_filename}!")

# Callback for processing the selected file
# Callback for processing the selected file
# Callback for processing the selected file
def callback(sender, app_data, user_data):
    selected_file = app_data["file_name"]
    
    # Check if a file is selected
    if selected_file:
        cards = []
        
        # Open and read the selected file
        with open(selected_file, 'r') as file:
            for line in file:
                # Debug output for each line read
                print("Processing line:", line.strip())
                
                # Parse the input format: Pack ID, , Internal ID, Card Name
                parts = line.strip().split(",")
                
                # Ensure the line is in the correct format
                if len(parts) == 4:  # Expecting 4 parts based on your format
                    # Extracting values and removing labels
                    pack_id = parts[0].replace("Pack ID: ", "").strip()
                    internal_id = parts[2].replace("Internal ID: ", "").strip()
                    
                    # Add to cards list
                    cards.append((pack_id, internal_id))
                else:
                    print(f"Skipping invalid line: {line.strip()}")

        # Debug output to verify the cards list
        print("Extracted cards:", cards)
        
        # Save the extracted card data to config.json
        save_config(cards)
        
        # Notify the user
        dpg.set_value("output_text", "Config saved successfully to config.json!")
        print("Config saved successfully!")
    else:
        dpg.set_value("output_text", "No file selected!")


# Function to execute another Python script when PATCH ROM button is clicked
def patch_rom_callback():
    # Run the script.py
    subprocess.run(["python", "script.py"], check=True)
def rebuild_rom_callback():
    # Run the script.py
    subprocess.run(["python", "repack.py"], check=True)  

def rebuild_name_callback(sender, app_data, user_data):
    # Retrieve input from the textbox
    input_text = dpg.get_value("arguments_input").strip()

    # Validate input format
    args = input_text.split(" ", 2)  # Split input into three parts (pack_id, new_name, new_description)
    if len(args) < 3:
        dpg.set_value("output_text", "Error: Missing arguments. Usage: <pack_id> <new_name> <new_description>")
        return

    try:
        pack_id = int(args[0])  # Ensure pack_id is an integer
        new_name = args[1]      # The second part is the new_name
        new_description = args[2]  # The third part is the new_description
    except ValueError:
        dpg.set_value("output_text", "Error: Pack ID must be an integer.")
        return

    try:
        # Run the script with arguments
        subprocess.run(["python", "pack-name.py", str(pack_id), new_name, new_description], check=True)
        print ("pack and description changed successfully")
    except subprocess.CalledProcessError as e:
        print ("error")
  

# Modified function for "Modify and Save to Config"
def modify_and_save_to_config_callback():
    # Ensure the temporary file is updated
    

    # Save to config.json from the updated temporary file
    save_config()

# Initialize DearPyGui
dpg.create_context()

# Create the main window
with dpg.window(label="Card Pack Modifier", tag="Card Pack Modifier", width=600, height=400):
    # Button to load the file content
    dpg.add_button(label="Unpack ROM", callback=on_unpack_button_click)
    dpg.add_button(label="Open Project (.txt)", callback=lambda: dpg.show_item("file_dialog_id"))  
    dpg.add_text("Output will be shown here:", tag="output_text") 
    # Button to save both the updates and the config.json file
     # Button to patch the ROM by executing the script.py
    dpg.add_button(label="PATCH ROM", callback=patch_rom_callback)
    dpg.add_button(label="REBUILD BIN2.PAC", callback=rebuild_rom_callback)
    dpg.add_input_text(label= "Edit Pack Names", tag="arguments_input", hint="Example: 42 NewPackName Description", width=400)
    dpg.add_button(label="Submit", callback=rebuild_name_callback)
# File dialog to select a .txt file
with dpg.file_dialog(directory_selector=False, show=False, callback=callback, id="file_dialog_id", width=600 ,height=400):
    dpg.add_file_extension(".txt", color=(255, 0, 0, 255))  # Only allow .txt files

    
# Create and set the viewport to be the primary window
dpg.create_viewport(title="Card Pack Modifier", width=800, height=600)

# Set the primary window before starting the DearPyGui application
dpg.set_primary_window("Card Pack Modifier", True)

# Show the main window as the primary window
dpg.show_viewport()

# Start the DearPyGui application
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()
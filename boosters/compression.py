import os
import math
import shutil
import subprocess

def read_binary(file_path):
    """Reads the binary data from a file."""
    with open(file_path, 'rb') as file:
        return file.read()

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

            print(f"PAC file unpacked successfully to {unpack_dir}.")
        except Exception as e:
            print(f"Error while unpacking PAC file: {e}")

    except Exception as e:
        print(f"Error unpacking the PAC file: {e}")

def compress_files(input_dir, temp_dir):
    try:
        # Path to dscemp executable
        dscemp_path = "DSDecmp.exe"

        # Check if dscemp exists
        if not os.path.exists(dscemp_path):
            print("Error: dscemp executable not found in the script directory.")
            return

        # Collect files from input directory
        files = []
        for root, dirs, files_in_dir in os.walk(input_dir):
            for file_name in files_in_dir:
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rb') as file:
                    files.append((file_name, file.read()))

        # Ensure the output directory exists
        os.makedirs(temp_dir, exist_ok=True)

        # Process and compress files
        for file_name, file_data in files:
            # Prepare the file path in the output directory (temp_dir)
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_data)

            # Run the compression command with lz11 using dscemp
            compressed_file_path = os.path.join(temp_dir, file_name)  # Output file without any extension change yet
            command = f"{dscemp_path} -c lz11 -ge {file_path} {compressed_file_path}"
            subprocess.run(command, shell=True)

        print(f"Compression completed for files in {input_dir}.")
        
        # After compression is finished, rename the files
        rename_compressed_files(temp_dir)

    except Exception as e:
        print(f"Error compressing files: {e}")

def rename_compressed_files(temp_dir):
    try:
        # Iterate through all files in the temp_dir
        for root, dirs, files in os.walk(temp_dir):
            for file_name in files:
                if file_name.endswith(".5bg.lz11"):
                    # Build the full file path
                    old_file_path = os.path.join(root, file_name)
                    # Replace the extension .5bg.lz11 with .lz5bg
                    new_file_path = old_file_path.replace(".5bg.lz11", ".lz5bg")
                    # Rename the file
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed {old_file_path} to {new_file_path}")

    except Exception as e:
        print(f"Error renaming files: {e}")



# Prompt the user for options
def main():
    action = input("Choose an action (unpack/compress/): ").strip().lower()
    packpac = "rom_work\data\Data_arc_pac\pack.pac"
    unpackdir = "rom_work\data\Data_arc_pac\pack"
    
    if action == 'unpack':
        pac_file = packpac
        unpack_dir = unpackdir
        unpack_pac_file(pac_file, unpack_dir)

    if action == 'compress':
        input_dir = input("Enter the folder to compress files inside ").strip()
        temp_dir = input("Enter output folder ").strip()
        
        # Call compress_files and perform compression
        compress_files(input_dir, temp_dir)
if __name__ == "__main__":
    main()
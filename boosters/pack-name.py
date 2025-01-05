import os
import sys
import subprocess
class PackNameManager:
    def __init__(self):
        self.work_dir = "rom_work"  # Hardcoded working directory
        self.pack_name_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin/pack_nameeng.bin")
        self.pack_index_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin/pack_indxeng.bin")
        self.output_file = "pack_names.txt"

    def read_binary(self, file_path):
        with open(file_path, "rb") as file:
            return file.read()

    def write_binary(self, file_path, data):
        with open(file_path, "wb") as file:
            file.write(data)
    
    def save_pack_names_to_file(self, pack_names):
        with open(self.output_file, "w", encoding="utf-8") as file:
            for pack_id, pack_name in pack_names:
                file.write(f"{pack_id}:{pack_name}\n")

        print(f"Pack names written to {self.output_file}")

    def get_pack_names(self):
        pack_names = []
        pack_names_data = self.read_binary(self.pack_name_file)
        pack_indexes = self.read_binary(self.pack_index_file)

        # Debug: Show total number of pack indexes
        print(f"Total bytes in pack indexes: {len(pack_indexes)}")
        print(f"Total bytes in pack names: {len(pack_names_data)}")

        for pack_id in range(0, len(pack_indexes), 8):
            pack_offset = pack_id  # Each pack ID is represented by an 8-byte entry
            if pack_offset + 8 > len(pack_indexes):
                break

            # Extract the name offset for the pack
            name_offset = int.from_bytes(pack_indexes[pack_offset:pack_offset + 4], "little")

            # Check for invalid or out-of-bounds offsets
            if name_offset >= len(pack_names_data):
                print(f"Invalid name offset for pack ID {pack_id // 8}: {name_offset}")
                pack_names.append((pack_id // 8, "Unknown Pack"))
                continue

            # Locate the null terminator to extract the full name
            name_end = pack_names_data.find(b"\x00", name_offset)
            if name_end == -1:
                print(f"No null terminator found for pack ID {pack_id // 8}, name offset {name_offset}")
                pack_name = "Unknown Pack"
            else:
                pack_name = pack_names_data[name_offset:name_end].decode("utf-8", errors="ignore").strip()

            pack_names.append((pack_id // 8, pack_name))

        return pack_names

    def modify_pack_name(self, pack_id, new_name):
        pack_names_data = bytearray(self.read_binary(self.pack_name_file))
        pack_indexes = bytearray(self.read_binary(self.pack_index_file))

        name_offset_position = pack_id * 8
        if name_offset_position + 8 > len(pack_indexes):
            print(f"Pack ID {pack_id} is invalid or out of range.")
            return False

        # Retrieve the name offset
        name_offset = int.from_bytes(pack_indexes[name_offset_position:name_offset_position + 4], "little")

        if name_offset >= len(pack_names_data):
            print(f"Invalid name offset for Pack ID {pack_id}.")
            return False

        # Encode new name and ensure it fits
        new_name_bytes = new_name.encode("utf-8") + b"\x00"
        if len(new_name_bytes) > len(pack_names_data) - name_offset:
            print(f"New name '{new_name}' is too long for Pack ID {pack_id}.")
            return False

        # Update the name in the binary data
        pack_names_data[name_offset:name_offset + len(new_name_bytes)] = new_name_bytes

        # Save updated binary data back to the file
        self.write_binary(self.pack_name_file, pack_names_data)
        print(f"Pack ID {pack_id} name successfully changed to '{new_name}'.")
        return True

    def run(self):
        # Step 1: Read pack names and save to a text file
        pack_names = self.get_pack_names()
        self.save_pack_names_to_file(pack_names)

    def rebuild_rom_callback(self):
        # Run the script.py
        subprocess.run(["python", "repack-name.py"], check=True)    

if __name__ == "__main__":
    
    

    if len(sys.argv) < 3:
        print("Usage: python modify_pack.py <pack_id> <new_name>")
        sys.exit(1)

    try:
        pack_id = int(sys.argv[1])
    except ValueError:
        print("Error: Pack ID must be an integer.")
        sys.exit(1)

    new_name = sys.argv[2]

    manager = PackNameManager()
    manager.run()
    manager.rebuild_rom_callback()
    if not manager.modify_pack_name(pack_id, new_name):
        print("Failed to modify the pack name.")

import os
import sys
import subprocess


class PackNameManager:
    def __init__(self):
        self.work_dir = "rom_work"  # Hardcoded working directory
        self.pack_name_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin/pack_nameeng.bin")
        self.pack_index_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin/pack_indxeng.bin")
        self.pack_desc_file = os.path.join(self.work_dir, "data/Data_arc_pac/bin/pack_desceng.bin")
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

        for pack_id in range(0, len(pack_indexes), 8):
            pack_offset = pack_id  # Each pack ID is represented by an 8-byte entry
            if pack_offset + 8 > len(pack_indexes):
                break

            name_offset = int.from_bytes(pack_indexes[pack_offset:pack_offset + 4], "little")
            if name_offset >= len(pack_names_data):
                pack_names.append((pack_id // 8, "Unknown Pack"))
                continue

            name_end = pack_names_data.find(b"\x00", name_offset)
            if name_end == -1:
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

        name_offset = int.from_bytes(pack_indexes[name_offset_position:name_offset_position + 4], "little")
        if name_offset >= len(pack_names_data):
            print(f"Invalid name offset for Pack ID {pack_id}.")
            return False

        # Ensure the new name fits within the allocated space
        name_end = pack_names_data.find(b'\x00', name_offset)
        if name_end == -1:
            name_end = len(pack_names_data)  # Assume end of file if no null terminator
        max_length = name_end - name_offset

        new_name_bytes = new_name.encode("utf-8") + b'\x00'
        if len(new_name_bytes) > max_length:
            print(f"New name '{new_name}' is too long for Pack ID {pack_id}. Max length: {max_length}")
            return False

        # Clear existing name data and write the new name
        pack_names_data[name_offset:name_offset + max_length] = b'\x00' * max_length  # Clear existing data
        pack_names_data[name_offset:name_offset + len(new_name_bytes)] = new_name_bytes
        self.write_binary(self.pack_name_file, pack_names_data)

        print(f"Pack ID {pack_id} name successfully changed to '{new_name}'.")
        return True

    def modify_pack_description(self, pack_id, new_description):
        pack_desc_data = bytearray(self.read_binary(self.pack_desc_file))
        pack_indexes = bytearray(self.read_binary(self.pack_index_file))

        desc_offset_position = pack_id * 8 + 4  # Description offset starts at byte 4
        if desc_offset_position + 8 > len(pack_indexes):
            print(f"Pack ID {pack_id} is invalid or out of range.")
            return False

        desc_offset = int.from_bytes(pack_indexes[desc_offset_position:desc_offset_position + 4], "little")
        if desc_offset >= len(pack_desc_data):
            print(f"Invalid description offset for Pack ID {pack_id}.")
            return False

        new_desc_bytes = new_description.encode("utf-8") + b"\x00"
        if len(new_desc_bytes) > len(pack_desc_data) - desc_offset:
            print(f"New description '{new_description}' is too long for Pack ID {pack_id}.")
            return False

        pack_desc_data[desc_offset:desc_offset + len(new_desc_bytes)] = new_desc_bytes
        self.write_binary(self.pack_desc_file, pack_desc_data)
        print(f"Pack ID {pack_id} description successfully changed to '{new_description}'.")
        return True

    def run(self):
        pack_names = self.get_pack_names()
        self.save_pack_names_to_file(pack_names)

    def rebuild_rom_callback(self):
        subprocess.run(["python", "repack-name.py"], check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv[1:]) % 3 != 0:
        print("Usage: python modify_pack.py <pack_id1> <new_name1> <new_description1> [<pack_id2> <new_name2> <new_description2> ...]")
        sys.exit(1)

    inputs = sys.argv[1:]
    manager = PackNameManager()
    manager.run()
    manager.rebuild_rom_callback()

    for i in range(0, len(inputs), 3):
        try:
            pack_id = int(inputs[i])
            new_name = inputs[i + 1]
            new_description = inputs[i + 2]

            if not manager.modify_pack_name(pack_id, new_name):
                print(f"Failed to modify the pack name for Pack ID {pack_id}.")
            if not manager.modify_pack_description(pack_id, new_description):
                print(f"Failed to modify the pack description for Pack ID {pack_id}.")
        except ValueError:
            print(f"Error: Pack ID '{inputs[i]}' must be an integer.")
            continue
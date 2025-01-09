import sys
import os

class CardPackModifier:
    def __init__(self, pack_file, work_dir):
        self.pack_file = pack_file
        self.work_dir = work_dir

    def read_binary(self, file_path):
        """Read a binary file and return its content as bytes."""
        with open(file_path, "rb") as file:
            return file.read()

    def write_binary(self, file_path, data):
        """Write modified data back to the binary file."""
        with open(file_path, "r+b") as file:
            file.write(data)

    def modify_rarity(self, internal_id, new_rarity_value):
        """Modify the rarity byte (second byte) in a card pack."""
        print(f"Modifying rarity for internal ID: {internal_id}...")

        # Read the binary data of the card pack
        data = self.read_binary(self.pack_file)

        # Calculate the offset for the given internal ID (each card pack entry is 8 bytes)
        pack_data_offset = internal_id * 8

        # Read the current pack data (8 bytes)
        pack_data = data[pack_data_offset:pack_data_offset + 8]

        # Check if we have enough data for this card
        if len(pack_data) < 8:
            print(f"Invalid data at offset {pack_data_offset}. Skipping this pack.")
            return

        # Convert the data to a mutable bytearray
        mutable_pack_data = bytearray(pack_data)

        # Modify the second byte (index 1) for rarity
        print(f"Current rarity (byte 2): {mutable_pack_data[0]}")  # Debug: show current rarity
        mutable_pack_data[0] = new_rarity_value  # Set the second byte (rarity)

        # Update the original data with the modified entry
        updated_data = (
            data[:pack_data_offset] + mutable_pack_data + data[pack_data_offset + 8:]
        )

        # Write the updated data back to the binary file
        self.write_binary(self.pack_file, updated_data)

        print(f"Rarity changed to {new_rarity_value} for internal ID {internal_id}.")

    def apply_rarity_changes(self, rarity_changes):
        """Apply multiple rarity changes based on the internal IDs and new rarity values."""
        for internal_id, new_rarity_value in rarity_changes:
            self.modify_rarity(internal_id, new_rarity_value)

# Example Usage
if __name__ == "__main__":
    # Example pack file and work directory
  
    work_dir = "rom_work"  # Adjust this path if needed
    pack_file = os.path.join(work_dir, "data/Data_arc_pac/bin2/card_pack.bin")  # Path to the card pack binary file

    # Check if command-line arguments are provided
    if len(sys.argv) < 3 or len(sys.argv) % 2 == 0:
        print("Usage: python modify_rarity.py <internal_id_1> <rarity_1> [<internal_id_2> <rarity_2> ...]")
        sys.exit(1)

    # Parse command-line arguments into a list of (internal_id, new_rarity_value) tuples
    rarity_changes = []
    for i in range(1, len(sys.argv), 2):
        try:
            internal_id = int(sys.argv[i])
            new_rarity_value = int(sys.argv[i + 1])
            rarity_changes.append((internal_id, new_rarity_value))
        except ValueError:
            print(f"Invalid argument pair: {sys.argv[i]} {sys.argv[i + 1]}")
            sys.exit(1)

    # Instantiate the modifier class
    modifier = CardPackModifier(pack_file, work_dir)

    # Apply the rarity changes
    modifier.apply_rarity_changes(rarity_changes)
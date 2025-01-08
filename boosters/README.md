# Nexus Revival Pack Editor

The Nexus Revival Pack Editor allows you to edit booster packs from the game "Over the Nexus 2011." Follow the steps below to get started.

## Prerequisites

Ensure the ROM file is named `rom.nds` and is placed in the same directory as the editor.

### Python Users

1. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Non-Python Users

1. Download the ZIP file from this repository.
2. Open `!pack-editor.bat` to run the editor with embeddable Python.

## Important Notes

- To prevent crashing the ROM, ensure you only replace the pack ID.
- The overall goal is to edit `card_pack.bin` and other BIN files that affect booster packs.
- Use the editor for a streamlined process. Once you've patched the ROM and saved pack names, use Tinke to reinsert `bin.pac` and `bin2.pac` back into the original ROM.

## Program Buttons

The program has five main buttons:

1. **Unpack ROM**: Unpacks the ROM, `bin2.pac`, and `bin.pac` to the `rom_work` folder in the same directory.
2. **Open Project**: Opens a text file that will be saved to `config.json`. This is required to make changes. Use `pack_and_cards` as a template starter project for the repository; it only accepts TXT files.
3. **Patch ROM**: Patches the `card_pack.bin` file inside `bin2.pac` folder.
4. **Rebuild bin2.pac**: Rebuilds `bin2.pac` for reinsertion back into the ROM with Tinke.
5. **Edit Pack Names**: Usage: 
    ```sh
    packid "new pack name" "this is a description"
    ```
    to edit pack names and their descriptions.

## Conclusion

By following these steps, you'll be able to customize booster packs in "Over the Nexus 2011" seamlessly. Enjoy your editing!


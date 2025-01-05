# ROM Editor README

## Overview

This ROM editor allows you to modify and patch a ROM file by following a series of steps. The editor has 5 buttons that must be pressed in a specific order to ensure the correct changes are made and applied. Follow the instructions below to guide you through each step.

## Button Overview and Order

The editor operates in a sequential process. Each button corresponds to a step in the editing and patching workflow. Below is an explanation of each button and its function:

### 1. **Unpack ROM**
   - **Purpose**: This button unpacks the necessary files from the ROM for editing.
   - **How to Use**: 
     - Click this button to extract the necessary files from the ROM. These files will be used in later steps to load, modify, and patch the ROM.
     - This step is essential as it prepares the ROM for modifications.

### 2. **Load File**
   - **Purpose**: This button loads the original packs and their cards into the GUI.
   - **How to Use**:
     - After unpacking the ROM, click this button to load the extracted files and their card data into the editor.
     - This step is important to ensure that the data you wish to edit is available in the editor.

### 3. **Save Project**
   - **Purpose**: This button saves your current progress and ensures changes can be made to the ROM.
   - **How to Use**:
     - After loading the files, click this button to save your current project.
     - This step is necessary before making any modifications to the ROM, as it stores the data you will later modify.

### 4. **Modify and Save Changes to Config**
   - **Purpose**: This button saves the changes to a configuration file, which will be used later to patch the ROM.
   - **How to Use**:
     - Make the changes you want to the ROM data (e.g., modifying cards, packs, etc.).
     - Once you're done, click this button to save those changes to a configuration file. This file will act as the "blueprint" for patching the ROM in the next step.
     - **Important**: Without this step, the changes you make will not be saved for patching.

### 5. **Patch ROM**
   - **Purpose**: This button runs the script to patch the ROM with the values from the configuration file.
   - **How to Use**:
     - After saving the changes to the config file, click this button to apply the changes and patch the ROM.
     - The patching process will modify the ROM according to the saved configuration, resulting in an updated ROM file with the modifications you made.

## Step-by-Step Guide

1. **Unpack ROM**: Click the **Unpack ROM** button to extract necessary files from the ROM. This will prepare the ROM for editing.
2. **Load File**: After unpacking the ROM, click the **Load File** button to load the extracted files and their data into the editor.
3. **Save Project**: Once the files are loaded, click the **Save Project** button to save the project. This step is required before you can modify the ROM.
4. **Modify and Save Changes to Config**: After saving the project, modify the data as needed (e.g., change cards, packs, etc.), then click **Modify and Save Changes to Config** to save your changes.
5. **Patch ROM**: Finally, click the **Patch ROM** button to apply your modifications to the ROM, creating a modified version of the original.

## Notes

- It is important to follow the order of these steps, as skipping any step may cause errors or result in lost changes.
- Ensure that all paths (ROM file, working directory, etc.) are set correctly before starting the process.
- Save your work frequently, especially after major changes to avoid losing your progress.
# Tellius-Unit-Model-Ports
Modify Fire Emblem 9 &amp; 10 assets to transfer unit models and animations between the games. 

### Install / Build:
- For Windows 11 users:
	- Released version for Windows 11 should require no dependencies.
 	- Download the zip folder from the [Releases](https://github.com/ltra043/Tellius-Unit-Model-Ports/releases).
  	- Unzip the folder and run the exe file.
- For other OS: the python script, requirements, and necessary files have been provided.
	- Written in Python 3.13. May be compatible with versions 3.10+. 
	- Download the 'fe10-to-fe9' folder.
 	- Install the requirements listed in requirements.txt.
  		- Open your terminal. Change your directory to the 'fe10-to-fe9' folder.
    	- Optional: create and activate a virtual environment
     	- Run the instruction: `pip install -r requirements.txt`
  	- Run the program from the python script or build an executable for your OS. 

### General Info:
- Use to transfer ymu assets from FE10 to FE9
- The files '10-to-9-ymu.exe' ('10-to-9-ymu.py' for non-windows users), '10-to-9-ymu.ui', and 'FE10-AnimData.txt' must be kept together in a single directory.
- Do not rename '10-to-9-ymu.ui' or 'FE10-AnimData.txt'

### Other Resources:
- Dolphin Emulator
- [Paragon](https://github.com/thane98/paragon) by thane98
- [Lumina](https://github.com/thane98/lumina) by thane98
- [FE10AnimData Editor](https://docs.google.com/spreadsheets/d/1pxpptW_rRY9hspODIw7zljYLYZYSH3R9QRNiI0DVHFA/edit?usp=sharing) (data provided by LordMewtwo73)
- [FE8Anim Editor](https://drive.google.com/drive/folders/1BDKiTbtlx_h9jmkNpxF4xa3EeEyoQefh?usp=sharing)

### Directions:
#### Initial preparation
1. Extract disc files from FE10.
2. Locate 'pack.cmp' in the ymu subfolder holding the files you want to transfer. Process 'pack.cmp' using Lumina to generate a folder named 'pack'.

#### Process files in the app
1. Run '10-to-9-ymu.exe'
2. On the Start Page, choose the input path. It should be the ymu subfolder holding the files you want to transfer.
3. Set the output path to your desired location.
4. Press Next to confirm your selections. A warning message will appear if either path is considered invalid.
5. If your input path is a vanilla folder name, the associated FE10AnimData should load automatically. Use the dropdown menu to select other vanilla options. Otherwise, select the option to manually type in the AnimData (found in FE10Anim.cms, Paragon - Animations, or FE10AnimData Editor)
6. Click 'Load / Refresh Table' above the table to view what the source and destination files will be named. This step can be safely skipped.
7. Click 'Port Files' below the table to generate the modified files. File changes include changing the overall format to match the destination game, making unused weapons invisible, and updating pointers.
	- Not included: updating damage timing on brave attacks (atk2_*.ga) and ensuring projectile weapons are visible only when in the unit's hand.
	- The involved animations will still be functional. If desired, these can be fixed with manual hex editing.
8. Click 'Return to Start' to port another model or close the application.

#### File organization
1. Process the output 'pack' folder using Lumina to generate a file named 'pack.cmp'.
2. Rename texture files to the format 'tex_#.tpl'. Texture files can stay in the 'ymu/model*/' folder.
3. If needed, update 'FE8Anim.bin'.
4. Use your preferred method to add the new ymu folder(s) to FE9.



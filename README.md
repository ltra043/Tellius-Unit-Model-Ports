# Tellius-Unit-Model-Ports
Modify Fire Emblem 9 &amp; 10 assets to transfer unit map models and animations between the games. 

### Install / Build:
- For Windows 11 users:
	- Released version for Windows 11 should require no dependencies.
 	- Download a zip folder from the [Releases](https://github.com/ltra043/Tellius-Unit-Model-Ports/releases).
  		- Choose between a windowed version with no terminal and a version with a terminal.
    	- There are no commands or inputs accepted in the terminal, but info is printed there that may be useful to view.
  	- Unzip the folder and run the exe file.
- For other OS: the python script, requirements, and necessary files have been provided.
	- Written in Python 3.13. Untested with older versions; may be compatible with versions 3.10+. 
	- Download the 'fe10-to-fe9' folder.
 	- Install the requirements listed in requirements.txt.
  		- Open your terminal. Change your directory to the 'fe10-to-fe9' folder.
    	- Optional: create and activate a virtual environment
     	- Run the instruction: `pip install -r requirements.txt`
  	- Run the program from the python script or build an executable for your OS. 

### General Info:
- Use to transfer ymu assets from FE10 to FE9
- The file '10-to-9-ymu.exe' and 'assets' folder must be kept together in a single directory.
	- For those using the python script '10-to-9-ymu.py' and folders 'assets' and 'modules' must be kept together in a single directory. 
- Do not rename 'assets' or any files inside it ('10-to-9-ymu.ui' or 'FE10-AnimData.txt')
	- For those using the python script, additionally do not rename the 'modules' folder or any files inside it.

### Other Resources:
- Dolphin Emulator
- [Paragon](https://github.com/thane98/paragon) by thane98
- [Lumina](https://github.com/thane98/lumina) by thane98
- [FE10AnimData Editor](https://docs.google.com/spreadsheets/d/1pxpptW_rRY9hspODIw7zljYLYZYSH3R9QRNiI0DVHFA/edit?usp=sharing) (data provided by LordMewtwo73)
- [FE8Anim Editor](https://drive.google.com/drive/folders/1BDKiTbtlx_h9jmkNpxF4xa3EeEyoQefh?usp=sharing)
- [skeleton.g viewer](https://docs.google.com/spreadsheets/d/1zbN7nSeyl0lY_XA7-t0zFUdaRjoDEF3c_laifMrM5Pc/edit?gid=1433193727#gid=1433193727&range=A1)
- [Detailed guide](https://docs.google.com/document/d/1ue4MTJ-L5mxt4ahNEV5HmpHVj0hPOC_9L4fgOrATIOM/edit?usp=sharing): includes notes on animation file format, what changes are needed when porting animations, and a visual guide for the app

### Directions:
#### Initial preparation
1. Extract disc files from FE10.
2. Locate 'pack.cmp' in the ymu subfolder holding the files you want to transfer. Decompress 'pack.cmp' using Lumina to extract it to a folder named 'pack'.

#### Process files in the app
1. Run '10-to-9-ymu.exe'
2. On the Start Page, choose the input path. It should be the ymu subfolder holding the files you want to transfer.
3. Set the output path to your desired location.
4. Choose to delete some (animations only), all, or none of the files currently in the output folder. It is recommended to delete some or all files if the output folder is not empty.
5. Press Next to confirm your selections. A warning message will appear if either path is considered invalid.
6. If your input path is a vanilla folder name, the associated FE10AnimData should load automatically.
	- Use the dropdown menu to select other vanilla options.
 	- Otherwise, select the option to manually type in the AnimData (found in FE10Anim.cms, Paragon - Animations, or FE10AnimData Editor)
7. Choose a source animation for the FE9 wait animation. FE10 has two options: wait (healthy) and twait (damaged/tired).
8. Choose 'yes' or 'no' to tell if the source model uses knives or staves. Some animations will be renamed if the answer is 'yes'.
9. Click 'Load / Refresh Table' above the table to view what the source and destination files will be named. This step can be safely skipped.
10. Click 'Port Files' below the table to generate the modified files. File changes include changing the overall format to match the destination game, making unused weapons invisible, and updating pointers.
	- Now included (release v1.1.0): updating damage timing on brave attacks (atk2_*.ga) and ensuring projectile weapons are visible only when in the unit's hand.
11. Click 'Return to Start' to port another model or close the application.

#### File organization
1. Process the output 'pack' folder using Lumina to generate a file named 'pack.cmp'.
2. If needed, update 'FE8Anim.bin'.
3. Use your preferred method to add the new ymu folder(s) to FE9.
4. View 'change_log.txt' in the 'Notes & Other Materials' folder in the output directory.

#### Known Issues
1. Unused weapons may appear at the start/end of some animations. This is not consistent across different models and animations.
	- This can sometimes be fixed by rearranging the row order in the Skeleton Table of animation files.

#### Other Notes:
1. As of v1.1.0, disabled data for bone visibility modification is added to every animation file. This can be referenced to hex edit further changes to animations. 
	- See detailed guide in Other Resources at the top for more information.

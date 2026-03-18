import math
import shutil
from PyQt6.QtWidgets import (QTableWidgetItem, QMessageBox)

from modules import start
from modules.config import *

# port.toggle((self)      return: None
def toggle(self):
    print(f'\nRunning port.toggle() ...')
    if self.radio_comboBox_1.isChecked():
        print(f'comboBox selected')
        self.textEdit_anim_data_1.setReadOnly(True)
        self.comboBox_1.setEnabled(True)
        fill_anim_data_1(self)
    elif self.radio_textBox_1.isChecked():
        print(f'textBox selected')
        self.textEdit_anim_data_1.setReadOnly(False)
        self.comboBox_1.setEnabled(False)


# port.fill_anim_data_1(self)      return: None
def fill_anim_data_1(self):
    print(f'\nRunning port.fill_anim_data_1() ...')
    model = self.comboBox_1.currentText()
    if model == 'Select Model':
        self.textEdit_anim_data_1.setText('Select your FE10 source model from the dropdown '
                                          'list.\n\nAlternatively, input AnimData in this '
                                          'textbox.')
    else:
        anim_data = ANIM_DATA_DICT[model]
        print(f'model: {model}')
        print(anim_data)
        self.textEdit_anim_data_1.setText(str(anim_data))


# port.load_table_1(self)      return True | False, rename_dict
def load_table_1(self):
    """ Load source and dest file names and fill table
    - Generate list of bytes from AnimData input
    - Read AnimData to determine the weapon type for each animation ile
    - Write dictionary matching each key (source file) to a value (renamed file)
    - Write list for source files that need to be duplicated
        - Source file is used for multiple weapons (usually None and another weapon)
        - Format is a list of 2-length lists.
            - The first item of the sub-list is the renamed file in the output directory
            - Last item of sub-list is the name the file should be duplicated and renamed to
    - Check that files expected according AnimData exist in the input directory
    - Fill the table with source and destination file names

    :return: tuple (bool, rename_dict)
        bool: true of false if data was loaded (data not loaded if AnimData is incorrect size)
        rename_dict = {src_file: dest_file, ...}
        dupe_src_anim_data = [[renamed file which will be duplicated, ...]
        dupe_dest_anim_data = [destination duplicated file], ...]
    """
    print(f'\nRunning port.load_table_1() ...')

    '''Local Variables'''
    wp_nums = []
    rename_dict = {}
    rename_status = False
    anim_data = self.textEdit_anim_data_1.toPlainText()

    '''Check for correct  AnimData size'''
    if len(anim_data) / 2 == 440:
        anim_data = anim_data[16:440 * 2]
        print(f'anim_data: {anim_data}, len = {len(anim_data) / 2}')
    elif len(anim_data) / 2 != 432:
        QMessageBox.warning(self, "Warning", f'Incorrect AnimData size')
        return False, rename_dict
    for count in range(432):
        byte = anim_data[count * 2:count * 2 + 2]
        byte_int = int(byte, 16)
        wp_nums.append(byte_int)

    # print(f'anim_data_dict_int:\n{anim_data_dict_int}\n')
    print(f'wp_nums: {wp_nums}\nlen = {len(wp_nums)}')

    '''Make list of source/dest file names '''
    for count, wp_num in enumerate(wp_nums):
        if wp_num != 0:
            wp_str_index = math.floor(count / 48)
            wp_str = WP_ALL_STRINGS[wp_str_index]  # determine weapon type

            motion_index = count % 48
            src_motion = MOTIONS_ALL_10[motion_index]  # determine src anim motion
            # print(f'SRC: {src_motion}_{wp_num}')

            '''Determine fe9 destination motion'''
            dest_motion = 'no_dest'
            if src_motion == 'wait':
                if self.radio_wait_1.isChecked():
                    rename_status = True
                    dest_motion = 'wait'
                else:
                    rename_status = False
            elif src_motion == 'twait':
                if self.radio_twait_1.isChecked():
                    rename_status = True
                    dest_motion = 'wait'
                else:
                    rename_status = False
            elif src_motion in MOTIONS_10_TO_9:
                rename_status = True
                index = MOTIONS_10_TO_9.index(src_motion)
                dest_motion = MOTIONS_ALL_9[index]
            elif src_motion in MOTIONS_10_EVT:
                rename_status = True
                dest_motion = src_motion

            if rename_status:  # Ignores files with no equivalent FE9 animation
                src_file = f'{src_motion}_{wp_num}.ga'
                dest_file = f'{dest_motion}_{wp_str}.ga'
                if src_file not in list(rename_dict.keys()):
                    '''Check if source file is used for multiple weapon animations'''
                    rename_dict[src_file] = [dest_file]
                else:
                    rename_dict[src_file].append(dest_file)

                if src_motion == 'atk':
                    dest_file = f'atk2_{wp_str}.ga'
                    rename_dict[src_file].append(dest_file)
        rename_status = False
    return True, rename_dict


# port.fill_table_1(self, rename_dict)      return: path_dict
                                            # path_dict.keys() = src_paths, dest_paths
def fill_table_1(self, rename_dict: dict):
    """
    - Evaluate the lists of source and destination files from load_table_1.
    - Determine if source files exist in the input directory and match to a destination file.
    - Distinguish between files for which the program should read and write an edited version
    of the source file, and which can be duplicated later to avoid repeating the same work.

    :param self:
    :param rename_dict: dictionary of FE10 to FE9 renamed anims generated in load_table_1
    :return: path_dict
                - dictionary of source and destination paths
                - keys = src_paths, dest_paths, dupe_src_paths, dupe_dest_paths
                - src_path file's data will be edited and written to the dest_path
    """
    directory_dict = start.directory(self)
    print('\nRunning port.fill_table_1() ...')
    input_dir, output_dir, input_pack, output_pack = list(directory_dict.values())
    input_files = []
    input_paths2 = []  # Different from input_paths[]; these paths have been verified

    # noinspection PyGlobalUndefined
    global SRC_FILES, DEST_FILES, STANDARD_SRC_FILES
    SRC_FILES = []
    DEST_FILES = []
    STANDARD_SRC_FILES = []
    src_paths = []
    dest_paths = []
    wp_dict = {}

    '''List of all animation file paths in input directory and pack'''
    input_paths = [
        [file for file in input_dir.iterdir() if file.suffix == '.ga'],
        [file for file in input_pack.iterdir() if file.suffix == '.ga']
    ]
    input_paths = [path for sublist in input_paths for path in sublist]

    ''' Check if file name is in the proper format 'motion_#.ga' or 'prefix_motion_#.ga'''
    for path in input_paths:
        src_format = True
        src_name = path.stem
        src_file = path.name
        if len(src_name.split('_')) == 2:
            src_motion, wp_num = src_name.split('_')
            standard_src_file = src_file
        elif len(src_name.split('_')) == 3:
            prefix, src_motion, wp_num = src_name.split('_')
            standard_src_file = f'{src_motion}_{wp_num}.ga'
        else:
            src_motion = "N/A"
            wp_num = "N/A"
            standard_src_file = "N/A"
            src_format = False
        if src_motion.lower() in MOTIONS_ALL_10 and wp_num.isdecimal() and len(wp_num) == 1:
            input_files.append(src_file)
            STANDARD_SRC_FILES.append(standard_src_file)
            input_paths2.append(path)
        else:
            src_format = False
        # print(f'src_motion: {src_motion}, wp_num: {wp_num}, status: {src_format}')

    if not src_format:
        QMessageBox.warning(self, "Warning",
                            f'Some animation file names are in a non-standard format.'
                            f'These files will be skipped over. If you wish to include these '
                            f'files, change their names to match the format: motion_#.ga '
                            f'and refresh the table.\n\n'
                            f'The issue may be:\n'
                            f'- Motion name does not exist in vanilla FE10\n'
                            f'- Animation weapon # after "_" is not a single digit number\n'
                            f'- Animation name contains more than 2 "_" characters* (See '
                            f'Note)\n\n '
                            f'Note: Standard names include 1 underscore, but this program '
                            f'allows for a prefix and 1 additional underscore to be added to '
                            f'the start of the name for organization purposes\n'
                            )
    src_files_sorted = []
    dest_files_sorted = []
    dest_files_rename = []
    if len(STANDARD_SRC_FILES) > 0:
        for standard_src_file in [f for f in STANDARD_SRC_FILES
                                  if f in list(rename_dict.keys())]:
            src_index = STANDARD_SRC_FILES.index(standard_src_file)
            src_occurrence = len(rename_dict[standard_src_file])
            src_file = input_files[src_index]
            src_path = input_paths2[src_index]
            SRC_FILES.extend([src_file] * src_occurrence)
            src_paths.extend([src_path] * src_occurrence)

            for dest_file in rename_dict[standard_src_file]:
                if src_path.parent.name == 'pack':
                    dest_path = output_pack.joinpath(dest_file)
                else:
                    dest_path = output_dir.joinpath(dest_file)
                DEST_FILES.append(dest_file)
                dest_paths.append(dest_path)

        '''Sort files by src_file A_Z, maintaining matching order'''
        src_files_sorted = list(enumerate(SRC_FILES))
        src_files_sorted.sort(key=lambda x: x[1])

        for index, src_file in src_files_sorted:
            dest_file = DEST_FILES[index]
            dest_files_sorted.append(dest_file)
            print(f'index: {index}, SRC: {src_file}, DEST: {dest_file}')
        src_files_sorted = [x[1] for x in src_files_sorted]

    input_dir, _, _, _ = list(directory_dict.values())
    model = input_dir.name
    is_mist_or_elincia = False
    if model in ['cleric', 'cleric2', 'erincia_p']:
        is_mist_or_elincia = True
    for file in dest_files_sorted:
        rename_file = file
        if self.radio_knife_yes.isChecked():
            motion, wp_str = file[:-3].split('_')
            if wp_str == 'RD':
                rename_file = f'UNUSED-{file}'
                if motion == 'rod' and 'rod_N.ga' not in dest_files_sorted:
                    rename_file = f'{motion}_N.ga'
                elif motion in ['atk1', 'atk2', 'crit']:
                    rename_file = f'{motion}_N.ga'
            elif wp_str == 'SW' and not is_mist_or_elincia:
                rename_file = f'UNUSED-{file}'
                if motion in ['atk1', 'atk2', 'crit']:
                    rename_file = f'{motion}_N.ga'
        dest_files_rename.append(rename_file)
    table_other_files = copy_other(self, wp_dict, False)
    other_srcs, other_dests = list(table_other_files.values())
    other_files_sorted = []
    for index, other_dest in enumerate(other_dests):
        stem, suffix = other_dest.split('.')
        other_src = other_srcs[index]
        sort_list = [other_src, other_dest, suffix]
        other_files_sorted.append(sort_list)
    other_files_sorted.sort(key=lambda x: x[1])
    other_files_sorted.sort(key=lambda x: x[2])
    for file in other_files_sorted:
        src_files_sorted.append(file[0])
        dest_files_rename.append(file[1])

    '''Fill Table with src and dest file names'''
    row_count = len(src_files_sorted)
    self.tableW_1.clearContents()
    self.tableW_1.setRowCount(row_count)
    for row, file in enumerate(src_files_sorted):
        item = QTableWidgetItem(file)
        self.tableW_1.setItem(row, 0, item)
    for row, file in enumerate(dest_files_rename):
        item = QTableWidgetItem(file)
        self.tableW_1.setItem(row, 1, item)
    self.tableW_1.setColumnWidth(0, 143)
    self.tableW_1.setColumnWidth(1, 143)
    path_dict = {'src_paths': src_paths, 'dest_paths': dest_paths}
    return path_dict

# port.copy_anim(input_pack)        return: None
def copy_anim(src_paths, dest_paths, input_pack):
    """ Copy and modify all .ga anim files from src_paths
        1. Read model's skeleton.g file and look for up to 8 possible displayed weapons.
        2. Sort files according to the number and type of pointers at the end of the file.
        3. Hex edit all files contain footer section 2. See port.hex_edit() for more info
        4. Add model's weapons to a list (from skeleton and from collective footer 2 data)
        5. Hex edit files without footer section 2. #!!! Test set col 2 to 00 instead of 08
    :param src_paths: list of source paths of animation files from the source model
    :param dest_paths: list of destination paths for edited animation files
    :param input_pack: path of the pack folder in the input directory
    :return: None
    """
    '''Look for visible weapons in skeleton.g'''
    wp_dict = count_skeleton_wp(input_pack)
    print(f'wp_dict: {wp_dict}')

    print(f'\nRunning port.copy_anim() ...')
    for count, src_path in enumerate(src_paths):
        dest_path = dest_paths[count]
        hex_edit(src_path, dest_path, wp_dict)

    return wp_dict


# port.copy_other(self, wp_dict: dict)         return: table_other_files: dict
def copy_other(self, wp_dict: dict, copy_status: bool):
    """Copy non-animation files and write a changelog.

    :param self:
    :param wp_dict: dictionary tracking weapons and bone ID from the model skeleton
    :param copy_status: bool
        True if actually copying files
        False if only generating list of file names, but not yet copying files (for filling table)
    :return: table_other_files: dict
        dictionary of src/dest file names for non-animation copied files
        keys = 'src', 'dest'
        values are strings
    """
    directory_dict = start.directory(self)
    print(f'\nRunning port.copy_other(copy_status={copy_status}) ...')

    input_dir, output_dir, input_pack, output_pack = list(directory_dict.values())
    wp_dict_values = list(wp_dict.values())
    wp_dict_keys = list(wp_dict.keys())
    tpl_srcs = []
    tpl_dests = []
    table_other_files = {'src': [], 'dest': []}

    '''List of non-animation files in the source directory'''
    other_paths = [path for path in input_dir.iterdir()
                       if path.suffix != '.ga' and path.stem != 'pack']
    other_paths = other_paths + [path for path in input_pack.iterdir()
                                         if path.suffix != '.ga']

    '''Copy non-animation files from input directory to output directory.'''
    tex_num = 0
    for src_path in other_paths:
        if src_path.suffix == '.tpl':
            src_stem = src_path.stem
            if src_path.stem not in tpl_srcs:
                dest_name = f'tex_{tex_num}.tpl'
                tpl_srcs.append(src_stem)
                tpl_dests.append(dest_name[0:len(dest_name) - 4])
                tex_num += 1
            else:
                index = tpl_srcs.index(src_stem)
                dest_name = f'{tpl_dests[index]}.tpl'
            dest_path = output_dir.joinpath(dest_name)
        elif src_path.parent.name == 'pack':
            dest_path = output_pack.joinpath(src_path.name)
        else:
            dest_path = output_dir.joinpath(src_path.name)

        if len(other_paths) > 0:
            if dest_path.name not in table_other_files['dest']:
                table_other_files['src'].append(src_path.name)
                table_other_files['dest'].append(dest_path.name)
            if copy_status:
                shutil.copy(src_path, dest_path)
                print(f'{src_path.name}:\nSRC: {src_path}\nDEST: {dest_path}\n')

    '''Write changelog (texture names and bone ID)'''
    if copy_status:
        notes_dir = output_dir.joinpath('Notes & Other Materials')
        if not notes_dir.exists():
            Path.mkdir(notes_dir)
        change_log = notes_dir.joinpath('change_log.txt')

        with open(change_log, "w") as file:
            file.write(f'FE10 {self.label_src_1.text()}\n')
            if len(tpl_srcs) != 0:
                file.write(f'\nTexture Name Changes\n')
                file.write('\tFE10 texture.tpl\t>\tFE9 texture.tpl\n')
                for count, tpl_src in enumerate(tpl_srcs):
                    src_len = len(tpl_srcs[count])
                    if src_len >= 12:
                        file.write(f'\t{tpl_srcs[count]}\t\t>\t{tpl_dests[count]}\n')
                    elif src_len >= 8:
                        file.write(f'\t{tpl_srcs[count]}\t\t\t>\t{tpl_dests[count]}\n')
                    elif src_len >= 4:
                        file.write(f'\t{tpl_srcs[count]}\t\t\t\t>\t{tpl_dests[count]}\n')
                    else:
                        file.write(f'\t{tpl_srcs[count]}\t\t\t\t\t>\t{tpl_dests[count]}\n')
            file.write(f'\nWeapon & Bone ID (for hex editing)\n')
            for count, wp_str in enumerate(wp_dict_keys):
                bone_ID = hex(wp_dict_values[count])
                bone_ID = f'0x{bone_ID[2:].zfill(2)}'
                file.write(f'\t{wp_str[1:3]}: {bone_ID}\n')
    return table_other_files


# port.read_hex(src_path: Path, wp_dict: dict, dest_stem: str)     return data_dict
def read_hex(src_path: Path, wp_dict: dict, dest_stem: str):
    """ Read the fe10 source file and modify to follow fe9 format
    - Read and store each section of the source file in data_dict.
    - Add invisibility data (partial and full) to all files. It is disabled by default
    unless used by Footer Data 2 modifications. This can be referenced if you need to
    further hex edit the animation.
    - Modify Footer Data 2 (controls weapon invisibility) and incorporate in table, meta,
    and frame data.
    - Remove bones found in Footer 2 from the original table data. These can sometimes cause
    visual glitches. They are saved in a disabled section between the table and metadata.

    :param src_path:
    :param wp_dict: dictionary tracking weapons and bone ID from the model skeleton
    :param dest_stem:
    :return: data_dict: dictionary of modified data bytes of the animation file.
            data_dict.keys() = ('file_info', 'table_data_edit', 'fd2_table_bytes',
            'disable_table_bytes', 'meta_data' meta_data, 'fd2_meta_bytes', 'frame_data',
            'fd2_frame_bytes', 'ftr_ptr_1' , 'ftr_data_1')
    """
    # print('Running port.read_hex() ...')
    print(f'Reading hex for {src_path.name} ...')
    data_dict = {}
    motion, wp_str = dest_stem.split('_')
    with open(Path(src_path), "rb") as SOURCE:
        '''Find & Store File Pointers'''
        data = SOURCE.read()
        total_size = len(data)
        hdr_ptr = data[0:4]
        meta_ptr = int.from_bytes(data[36:40], "big")
        frame_ptr = int.from_bytes(data[44:48], "big")
        first_frame = int.from_bytes(data[20:24], "big")
        last_frame = int.from_bytes(data[24:28], "big")
        row_count = int.from_bytes(data[31:32], "big")
        table_size = row_count * 16

        '''Store source data'''
        SOURCE.seek(0)
        file_info = SOURCE.read(48)
        table_data = SOURCE.read(row_count * 16)
        meta_data = SOURCE.read(frame_ptr - meta_ptr)
        file_info = bytearray(file_info)
        file_info[8] = 0

        '''Create dictionary'''
        data_dict['file_info'] = file_info
        data_dict['table_data_edit'] = table_data
        data_dict['fd2_table_bytes'] = bytearray([])
        data_dict['disable_table_bytes'] = bytearray([])
        data_dict['meta_data'] = meta_data
        data_dict['fd2_meta_bytes'] = bytearray([])
        data_dict['frame_data'] = bytearray([])
        data_dict['fd2_frame_bytes'] = bytearray([])
        data_dict['ftr_ptr_1'] = bytearray([])
        data_dict['ftr_data_1'] = bytearray([])
        ftr_data_1 = bytearray([])

        ''''Read and store data if source has no footer data'''
        hdr_ptr = int.from_bytes(hdr_ptr, "big")
        ftr_type = -1
        if hdr_ptr == 0:
            ftr_type = 0
            frame_data = SOURCE.read()
            data_dict['frame_data'] = frame_data

        '''Determine variables for adding new table data'''
        SOURCE.seek(48 + row_count * 16 - 5)
        last_meta = int.from_bytes(SOURCE.read(1), "big")
        next_meta = last_meta + int.from_bytes(SOURCE.read(4), "big")
        # print(f'last_meta: int = {last_meta}, next_meta: int = {next_meta}')

        '''Determine variables for adding new meta data'''
        SOURCE.seek(meta_ptr + next_meta * 12 - 5)
        last_frame_count = int.from_bytes(SOURCE.read(1), "big")
        last_frame_start = int.from_bytes(SOURCE.read(4), "big")
        next_frame_start = last_frame_start + last_frame_count
        next_frame_start = hex(next_frame_start)
        next_frame_start = bytes.fromhex(next_frame_start[2:].zfill(8))

        '''Store data if only Footer Data 1 is present'''
        ftr_ID = -1  # no footer data if ftr_type == 0
        if ftr_type != 0:
            SOURCE.seek(hdr_ptr)
            ftr_ID = int.from_bytes(SOURCE.read(4), "big")
        if ftr_ID == 5:
            ftr_type = 1
            ftr_ptr_1_bytes = SOURCE.read(4)
            file_info[0:4] = ftr_ptr_1_bytes
            ftr_ptr_1 = int.from_bytes(ftr_ptr_1_bytes, "big")

            data = bytearray(data)
            frame_data = data[frame_ptr:ftr_ptr_1]
            ftr_data_1 = data[ftr_ptr_1:hdr_ptr]
            ftr_ptr_1: int = ftr_ptr_1 + 40
            ftr_ptr_1: bytes = bytes.fromhex(hex(ftr_ptr_1)[2:].zfill(8))

        # Determine if Footer Data 2 is present
        elif ftr_ID == 0:
            ftr_ptr_2 = SOURCE.read(4)
            ftr_ptr_2 = int.from_bytes(ftr_ptr_2, "big")
            ftr_ptr_3 = SOURCE.read(4)
            ftr_ptr_3 = int.from_bytes(ftr_ptr_3, "big")

            if ftr_ptr_3 == 0:  # only Footer Data 2 is present (no Footer Data 1)
                ftr_type = 2
                ftr_2_size = hdr_ptr - ftr_ptr_2
                frame_data = data[frame_ptr:ftr_ptr_2]
            else:       # Both Footer Data 1 and Footer Data 2 present
                ftr_type = 3
                ftr_2_size = ftr_ptr_3 - ftr_ptr_2
                SOURCE.seek(hdr_ptr - 8)
                ftr_ptr_1_bytes = SOURCE.read(4)
                ftr_ptr_1 = int.from_bytes(ftr_ptr_1_bytes, "big")
                SOURCE.seek(ftr_ptr_1)
                ftr_data_1 = data[ftr_ptr_1:ftr_ptr_2]
                frame_data = data[frame_ptr:ftr_ptr_1]
            SOURCE.seek(ftr_ptr_2)
            ftr_data_2 = SOURCE.read(ftr_2_size)

    '''Make dictionaries for making a bone invisible
            - Add a default, disabled version of each duration type of invisibility for 
            reference if further hex editing is needed'''
    hide_full = {'bone': [255], 'frame': [0]}
    hide_part: dict[str, list[int] | list[list[int]]] = {'bone': [255], 'frame': [[50, 51, 100, 101]],
                 'visibility': [[64, 0, 0,64]]}

    '''Save Footer Data 2 entries individually'''
    wp_bones_id = list(wp_dict.values())
    wp_bones_str = list(wp_dict.keys())
    dest_wp = wp_str.lower()
    if ftr_type >= 2:
        entry_indexes = []
        ftr_2_entries = []
        ftr_2_num = ftr_data_2[0:2]
        ftr_2_num = int.from_bytes(ftr_2_num, "big")
        for entry in range(ftr_2_num):
            addr_index = 8 + entry * 2
            entry_index = int.from_bytes(ftr_data_2[addr_index:addr_index + 2], "big")
            entry_indexes.append(entry_index)
        # print(f'entry_indexes: {entry_indexes}')

        for entry, entry_start in enumerate(entry_indexes):
            try:
                ftr_2_entry = ftr_data_2[entry_start:entry_indexes[entry + 1]]
                ftr_2_entries.append(ftr_2_entry)
            except IndexError:
                ftr_2_entry = ftr_data_2[entry_start:]
                ftr_2_entries.append(ftr_2_entry)

        '''Determine if bone is hidden for part or all of animation'''
        for entry in ftr_2_entries:
            frames_part = []
            visibility_part = []
            if entry[1] == 1:
                hide_full['bone'].append(entry[3])
                hide_full['frame'].append(entry[5])
            else:
                hide_part['bone'].append(entry[3])
                for r in range(entry[1]):
                    frames_part.append(entry[5 + r * 4])
                    if entry[7 + r * 4] == 1:
                        visibility_part.append(64)
                    else:
                        visibility_part.append(entry[7 + r * 4])
                hide_part['frame'].append(frames_part)
                hide_part['visibility'].append(visibility_part)
    else:  # ftr_type = 0 or 1
        for count, bone in enumerate(wp_bones_id):
            skel_wp = wp_bones_str[count]
            if skel_wp != f'_{dest_wp}_':
                hide_full['bone'].append(bone)
                hide_full['frame'].append(0)
    print(f'hide_full: {hide_full}')
    print(f'hide_part: {hide_part}')

    '''Modify Footer Data 2 for bones hidden for all of the animation'''
    fd2_table_bytes = bytearray([])
    disable_table_bytes = bytearray([])
    disable_table_bytes.extend(bytearray([0] * 32))
    fd2_meta_bytes = bytearray([])
    fd2_frame_bytes = []
    hide_bones_full = hide_full['bone']
    hide_bones_part = hide_part['bone']
    frames_all: list[list] = hide_part['frame']
    vis_values_all: list[list] = hide_part['visibility']

    disable_table_bytes.extend(
        bytearray([0, 0, 0, 255, 0, 0, 0, 8, 0, 0, 0, next_meta, 0, 0, 0, 3]))
    for bone in hide_bones_full:
        if bone != 255:
            fd2_table_bytes.extend(
                bytearray([0, 0, 0, bone, 0, 0, 0, 8, 0, 0, 0, next_meta, 0, 0, 0, 3]))
    for r in range(3):
        fd2_meta_bytes += (bytearray([0, r, 15, 0, 0, 0, 0, 1]) + next_frame_start)
    fd2_frame_bytes.extend([0, 0, 0, 0])

    '''Modify Footer Data 2 for bones hidden for part of the animation'''
    next_meta += 3
    next_frame_int = int.from_bytes(next_frame_start, "big") + 1
    for count, bone in enumerate(hide_bones_part):
        if bone == 255:
            disable_table_bytes.extend(
                bytearray([0, 0, 0, bone, 0, 0, 0, 40, 0, 0, 0, next_meta, 0, 0, 0, 3]))
            next_meta += 3
            next_frame_mod = 0
        else:
            fd2_table_bytes.extend(
                bytearray([0, 0, 0, bone, 0, 0, 0, 40, 0, 0, 0, next_meta, 0, 0, 0, 3]))
            next_frame_mod = 4
        next_frame_addr = next_frame_int + next_frame_mod
        next_frame_addr = bytes.fromhex(hex(next_frame_addr)[2:].zfill(8))
        for r in range(3):
            fd2_meta_bytes.extend(bytearray([0, r, 14, 0, 0, last_frame, 0, 4]))
            fd2_meta_bytes.extend(next_frame_addr)
        frames = frames_all[count]
        vis_values = vis_values_all[count]
        for count_f, frame in enumerate(frames):
            fd2_frame_bytes.extend([0, frame, vis_values[count_f], 0])
        # print(f'count {count} complete')
    fd2_frame_bytes = bytearray(fd2_frame_bytes)

    '''Filter fully hidden bones from table_data'''
    table_data_edit = []
    remove_bones = []
    for count, bone in enumerate(wp_bones_id):
        motions = ['atk', 'atk2', 'magic1', 'magic2', 'crit']
        if motion not in motions:
            # if bone not in hide_bones_full + hide_bones_part:
            if bone in hide_bones_full + hide_bones_part:
                # print(f'bone: {bone}')
                remove_bones.append(bone)

    for row in range(row_count):
        row_data = table_data[row * 16:(row + 1) * 16]
        table_bone = row_data[3]
        if int(table_bone) in hide_bones_full + hide_bones_part + remove_bones:
            print(f'bone {table_bone} in table row {hex(row)} is fully hidden in Footer Data 2')
            disable_table_bytes.extend(row_data)
        else:
            table_data_edit.extend(row_data)

    print(f'fd2_table_bytes: {fd2_table_bytes}')
    table_data_edit = bytearray(table_data_edit)

    meta_ptr = len(file_info + table_data_edit + fd2_table_bytes + disable_table_bytes)
    frame_ptr = meta_ptr + len(meta_data + fd2_meta_bytes)
    table_rows = int(len(table_data_edit + fd2_table_bytes) / 16)
    file_info = bytearray(file_info)

    if ftr_type == 3 or ftr_type == 1:
        hdr_ptr = frame_ptr + len(frame_data + fd2_frame_bytes)
        ftr_ptr_1_int = hdr_ptr + 40
        ftr_ptr_1: bytes = bytes.fromhex(hex(ftr_ptr_1_int)[2:].zfill(8))
    elif ftr_type == 0 or ftr_type == 2:
        hdr_ptr = 0
        ftr_ptr_1: bytearray = bytearray([])

    '''Modify Footer Data 1 for atk1, atk2, crit, magic1, and magic2'''
    motions = ['atk1', 'atk2', 'crit', 'magic1', 'magic2']
    if motion in motions and len(ftr_data_1) > 1:
        entry_num = ftr_data_1[1]
        addresses = []
        ftr_data_1 = bytearray(ftr_data_1)
        for count in range(entry_num):
            address = ftr_data_1[9 + 2 * count]
            addresses.append(address)
        for address in addresses:
            ftr_data_1[address + 3] = 1

    '''Update Pointers & File Info'''
    hdr_ptr = bytes.fromhex(hex(hdr_ptr)[2:].zfill(8))
    meta_ptr = bytes.fromhex(hex(meta_ptr)[2:].zfill(8))
    frame_ptr = bytes.fromhex(hex(frame_ptr)[2:].zfill(8))
    table_rows = bytes.fromhex(hex(table_rows)[2:].zfill(8))

    file_info[0:4] = hdr_ptr
    file_info[8] = 0
    file_info[28:32] = table_rows
    file_info[36:40] = meta_ptr
    file_info[44:48] = frame_ptr

    data_dict['file_info'] = file_info
    data_dict['table_data_edit'] = table_data_edit
    data_dict['fd2_table_bytes'] = fd2_table_bytes
    data_dict['disable_table_bytes'] = disable_table_bytes
    data_dict['meta_data'] = meta_data
    data_dict['fd2_meta_bytes'] = fd2_meta_bytes
    data_dict['frame_data'] = frame_data
    data_dict['fd2_frame_bytes'] = fd2_frame_bytes
    data_dict['ftr_ptr_1'] = ftr_ptr_1
    data_dict['ftr_data_1'] = ftr_data_1

    return data_dict, ftr_type


# port.write_hex(dest_path: Path, data_dict: dict, ftr_type: int)        return None
def write_hex(dest_path: Path, data_dict: dict, ftr_type: int):
    """ Write the modified data to new animation files

    :param dest_path:
    :param data_dict: dictionary of modified data, stored by section
    :param ftr_type: 0, 1, 2, or 3
        0: No Footer Data in source file
        1: Only Footer Data 1 in source file
        2: Only Footer Data 2 in source file
        3: Both Footer Data 1 & 2 in source file
    :return: None
    """
    # print('Running port.write_hex() ...')
    with open(Path(dest_path), "wb+") as DEST:
        print(f'Writing {dest_path.name}...')
        data_values = list(data_dict.values())
        # data_keys = list(data_dict.keys())

        for count, data in enumerate(data_values):
            # data_section = data_keys[count]
            # print(f'writing {data_section} ...')
            if count <= len(data_values)-2:
                DEST.write(data)    #write file_info, table, metadata, frame data, ftr_ptr_1
            elif ftr_type == 1 or ftr_type == 3:   # write 00 buffer and footer data 1
                DEST.write(bytearray([0] * 36))
                DEST.write(data)


# port.count_skeleton_wp(input_pack)        return: wp_dict
def count_skeleton_wp(input_pack):
    """ Determine bone ID for all weapons in the skeleton file
        - Store weapon (key) and bone ID (value) in wp_dict
    :param input_pack:
    :return: wp_dict
    """
    print('\nRunning port.count_skeleton_wp() ...')
    with (open(input_pack.joinpath('skeleton.g'), 'rb') as skeleton):
        data = skeleton.read()
        total_size = len(data)

        skeleton.seek(4)
        str_pool_ptr = skeleton.read(4)
        str_pool_ptr = int.from_bytes(str_pool_ptr, "big")
        skeleton.seek(str_pool_ptr)
        str_pool_bytes = skeleton.read(total_size - str_pool_ptr)
        str_pool_split = str_pool_bytes.split(b'\x00')
        str_pool_decode = [s.decode('utf-8') for s in str_pool_split if s]
        print(f'decoded_strings: {str_pool_decode}')

        wp_dict = {}
        for wp_str in ['_ar_', '_sw_', '_sp_', '_ja_', '_ax_', '_ha_', '_bw_', '_rd_', '_bg_']:
            if wp_str in str_pool_decode:
                wp_dict[wp_str] = str_pool_decode.index(wp_str) - 1
    return wp_dict


# port.hex_edit(src_path: Path, dest_path: Path, wp_dict: dict)         # return: None
def hex_edit(src_path: Path, dest_path: Path, wp_dict: dict):
    """ Read, modify, and write animation file

    :param src_path:
    :param dest_path:
    :param wp_dict:
    :return:
    """
    print(f'\nRunning port.hex_edit() for {src_path.name} ...')
    dest_name = dest_path.name
    dest_stem = dest_path.stem
    print(f'SRC: {src_path.name}, DEST: {dest_name}')

    data_dict, ftr_type = read_hex(src_path, wp_dict, dest_stem)
    write_hex(dest_path, data_dict, ftr_type)


# port.rename_no_wp(self)                   # return None
def rename_no_wp(directory_dict):
    """ Rename staff and knife animations
    Rename attack or rod animations with knife (SW) or staff (RD) equipped.
    - Must filter out Mist and Elincia (SW) animations
    - Some models have two rod animations using (N) and (RD). Do not rename if the model already
    has a rod_N animation.
    - Rename all remaining (RD) animations to lowercase (rd) as a reminder that these are not
    usable unless renamed to use a valid FE9 weapon string.
    - Experiment with using the staff animations instead of (N)

    :param directory_dict: dictionary of input/output directory paths
           directory_dict.keys() = ['input_dir', 'output_dir', 'input_pack', 'output_pack']
    :return: None
    """
    print(f'\nRunning port.rename_no_wp() ...')
    renamed_files = {'src': [], 'dest': []}
    '''Flag if model is Mist or Elincia. This is used to rename some SW/RD anims'''
    input_dir, output_dir, _, output_pack = list(directory_dict.values())
    model = input_dir.name
    is_mist_or_elincia = False
    if model in ['cleric', 'cleric2', 'erincia_p']:
        is_mist_or_elincia = True

    files = [f for f in output_dir.iterdir() if f.suffix == '.ga']
    files_pack = [f for f in output_pack.iterdir() if f.suffix == '.ga']
    files.extend(files_pack)
    stems = [f.stem for f in files]
    for file in files:
        stem = file.stem
        print(f'stem: {stem}')
        motion, wp_str = stem.split('_')
        rename_status = False
        dest_dir = file.parent
        dest_path = dest_dir.joinpath(f'{motion}_N.ga')

        if wp_str == 'RD':
            rename_status = True
            if motion == 'rod' and 'rod_N' in stems:
                dest_path = dest_dir.joinpath(f'UNUSED-{stem}.ga')
            elif motion not in ['atk1', 'atk2', 'crit']:
                dest_path = dest_dir.joinpath(f'UNUSED-{stem}.ga')
        elif wp_str == 'SW' and not is_mist_or_elincia:
            rename_status = True
            if motion not in ['atk1', 'atk2', 'crit']:
                dest_path = dest_dir.joinpath(f'UNUSED-{stem}.ga')
        if rename_status:
            if dest_path.stem in stems and dest_path.stem != stem:
                dest_path.unlink()
                stems.remove(dest_path.stem)
            file.rename(dest_path)
            renamed_files['src'].append(stem)
            renamed_files['dest'].append(dest_path.stem)
    

    if len(renamed_files['src']) > 0:
        change_log = output_dir.joinpath('Notes & Other Materials')
        change_log = change_log.joinpath('change_log.txt')
        with open (change_log, 'a') as f:
            f.write(f'\nRenamed Knife (SW) or Rod (RD) Animations:\n')
            for count, src_stem in enumerate(renamed_files['src']):
                src_len = len(src_stem)
                if src_len >= 8:
                    f.write(f"{src_stem}\t>\t{renamed_files['dest'][count]}\n")
                else:
                    f.write(f"{src_stem}\t\t>\t{renamed_files['dest'][count]}\n")

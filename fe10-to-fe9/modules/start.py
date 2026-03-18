from pathlib import Path
from PyQt6.QtWidgets import (QFileDialog)

# start.select_input(self)      return: None
def select_input(self):
    print(f'\nRunning start.select_input() ...')
    self.directory = QFileDialog.getExistingDirectory(None, "Select Input Directory")
    if self.directory:
        # If a folder was selected (not cancelled), update lineEdit to selected directory
        input_dir = Path(self.directory)
        self.lineEdit_input_0.setText(str(input_dir))
    else:
        # If a folder selection was cancelled, use the last input
        last_input = self.lineEdit_input_0.text()
        print(f'No selection was made. Reusing the last input:\n{last_input}')
        print('')
        self.lineEdit_input_0.setText(last_input)


# start.select_output(self)      return: None
def select_output(self):
    print(f'\nRunning start.select_output() ...')
    self.directory = QFileDialog.getExistingDirectory(None, "Select Output Directory")
    if self.directory:
        # If a folder was selected (not cancelled), update lineEdit to selected directory
        output_dir = Path(self.directory)
        self.lineEdit_output_0.setText(str(output_dir))
    else:
        # If a folder selection was cancelled, use the last output
        last_output = self.lineEdit_output_0.text()
        print('No selection was made. Reusing the last input ' + last_output)
        print('')
        self.lineEdit_output_0.setText(last_output)


# start.directory(self)     return: directory_dict
                            # keys = ['input_dir', 'output_dir', 'input_pack', 'output_pack']
def directory(self):
    print(f'\nRunning start.directory() ...')
    input_dir = Path(self.lineEdit_input_0.text())
    output_dir = Path(self.lineEdit_output_0.text())
    input_pack = input_dir.joinpath('pack')
    output_pack = output_dir.joinpath('pack')

    try:
        if not output_dir.exists():
            output_dir.mkdir()
        if not output_pack.exists():
            output_pack.mkdir()
    except FileNotFoundError:
        return None

    directory_dict = {'input_dir': input_dir, 'output_dir': output_dir,
                      'input_pack': input_pack, 'output_pack': output_pack}
    return directory_dict
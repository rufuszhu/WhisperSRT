import glob
import os


class Rename:
    def __init__(self, args):
        self.args = args
        self.rename()

    def rename(self):
        for folder in self.args.inputs:
            for filepath in glob.glob(os.path.join(folder, "**/*."+self.args.suffix), recursive=True):
                print(filepath)
                os.rename(filepath, os.path.splitext(filepath)[0]+"."+self.args.new_suffix)


import os
import glob
from srtranslator import SrtFile
from srtranslator.translators.deepl_api import DeeplApi


class Translate:
    def __init__(self, args):
        self.args = args

    def run(self):
        translator = DeeplApi(api_key=os.environ.get("DEEPL_API_KEY"))
        for input in self.args.inputs:
            for filepath in glob.glob(os.path.join(input, "**/*.srt"), recursive=True):
                srt = SrtFile(filepath)
                # rename filepath to a new extension
                os.rename(filepath, os.path.splitext(filepath)[0] + "." + self.args.lang)
                srt.translate(translator, self.args.lang, self.args.dest)
                srt.wrap_lines()
                srt.save(f"{os.path.splitext(filepath)[0]}.srt")
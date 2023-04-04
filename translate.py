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
                os.rename(filepath, os.path.splitext(filepath)[0] + ".jp")
                srt.translate(translator, "ja", "zh")
                srt.wrap_lines()
                srt.save(f"{os.path.splitext(filepath)[0]}.srt")

            # for root, dirs, files in os.walk(input):
            #     for file in files:
            #         if not utils.is_srt(file):
            #             continue
            #         logging.info(f"translating {file}")
            #         with open(os.path.join(root, file), encoding='utf8') as f:
            #             subs = srt.parse(f.read())
            #
            #         newSubs = []
            #         for sub in subs:
            #             translated = google_translate_text("zh-cn", sub.content)
            #             newSubs.append(srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=translated))
            #
            #         with open("translated.srt", "wb") as f:
            #                 f.write(srt.compose(newSubs).encode(self.args.encoding, "replace"))


def google_translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    # print(u"Text: {}".format(result["input"]))
    # print(u"Translation: {}".format(result["translatedText"]))
    # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result["translatedText"]

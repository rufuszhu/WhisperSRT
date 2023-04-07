import datetime
import glob
import logging
import os
import time

import srt
import torch
import whisper
from srtranslator import SrtFile
from srtranslator.translators.deepl_api import DeeplApi

from tqdm import tqdm

from . import utils


def process(whisper_model, audio, seg, lang, prompt):
    r = whisper_model.transcribe(
        audio[int(seg["start"]): int(seg["end"])],
        task="transcribe",
        language=lang,
        initial_prompt=prompt,
    )
    r["origin_timestamp"] = seg
    return r


class Transcribe:
    def __init__(self, args):
        self.args = args
        self.sampling_rate = 16000
        self.whisper_model = None
        self.vad_model = None
        self.detect_speech = None
        self.translator = DeeplApi(api_key=os.environ.get("DEEPL_API_KEY"))

    def run(self):
        for input in self.args.inputs:
            if os.path.isdir(input):
                for filepath in glob.glob(os.path.join(input, "**/*"), recursive=True):
                    if utils.is_video(filepath):
                        self.transcribe_file(filepath)
            else:
                self.transcribe_file(input)

    def transcribe_file(self, file):
        logging.info(f"Transcribing {file}")
        name, _ = os.path.splitext(file)
        if utils.check_exists(name + ".srt", False):
            return

        audio = whisper.load_audio(file, sr=self.sampling_rate)
        if (
                self.args.vad == "1"
                or self.args.vad == "auto"
                and not name.endswith("_cut")
        ):
            speech_timestamps = self._detect_voice_activity(audio)
        else:
            speech_timestamps = [{"start": 0, "end": len(audio)}]
        transcribe_results = self._transcribe(audio, speech_timestamps)

        output = name + ".srt"
        self._save_srt(output, transcribe_results)
        self.translate(output)

        logging.info(f"Transcribed {file} to {output}")

    def translate(self, filepath):
        srt = SrtFile(filepath)
        # rename filepath to a new extension
        os.rename(filepath, os.path.splitext(filepath)[0] + "." + self.args.lang)
        srt.translate(self.translator, self.args.lang, self.args.dest)
        srt.wrap_lines()
        srt.save(f"{os.path.splitext(filepath)[0]}.srt")

    def _detect_voice_activity(self, audio):
        """Detect segments that have voice activities"""
        tic = time.time()
        if self.vad_model is None or self.detect_speech is None:
            # torch load limit https://github.com/pytorch/vision/issues/4156
            torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
            self.vad_model, funcs = torch.hub.load(
                repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True
            )

            self.detect_speech = funcs[0]

        speeches = self.detect_speech(
            audio, self.vad_model, sampling_rate=self.sampling_rate
        )

        # Remove too short segments
        speeches = utils.remove_short_segments(speeches, 1.0 * self.sampling_rate)

        # Expand to avoid to tight cut. You can tune the pad length
        speeches = utils.expand_segments(
            speeches, 0.2 * self.sampling_rate, 0.0 * self.sampling_rate, audio.shape[0]
        )

        # Merge very closed segments
        speeches = utils.merge_adjacent_segments(speeches, 0.5 * self.sampling_rate)

        logging.info(f"Done voice activity detection in {time.time() - tic:.1f} sec")
        return speeches if len(speeches) > 1 else [{"start": 0, "end": len(audio)}]

    def _transcribe(self, audio, speech_timestamps):
        tic = time.time()
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model(
                "large-v2", self.args.device
            )

        res = []
        if self.args.device == "cpu" and len(speech_timestamps) > 1:
            logging.info(f"Using multiprocessing to transcribe")
            from multiprocessing import Pool

            pbar = tqdm(total=len(speech_timestamps))

            pool = Pool(processes=4)
            # TODO, a better way is merging these segments into a single one, so whisper can get more context
            for seg in speech_timestamps:
                res.append(
                    pool.apply_async(
                        process,
                        (
                            self.whisper_model,
                            audio,
                            seg,
                            self.args.lang,
                            self.args.prompt,
                        ),
                        callback=lambda x: pbar.update(),
                    )
                )
            pool.close()
            pool.join()
            pbar.close()
            logging.info(f"Done transcription in {time.time() - tic:.1f} sec")
            return [i.get() for i in res]
        else:
            for seg in (
                    speech_timestamps
                    if len(speech_timestamps) == 1
                    else tqdm(speech_timestamps)
            ):
                r = self.whisper_model.transcribe(
                    audio[int(seg["start"]): int(seg["end"])],
                    task="transcribe",
                    language=self.args.lang,
                    initial_prompt=self.args.prompt,
                    verbose=False if len(speech_timestamps) == 1 else None,
                )
                r["origin_timestamp"] = seg
                res.append(r)
            logging.info(f"Done transcription in {time.time() - tic:.1f} sec")
            return res

    def _save_srt(self, output, transcribe_results):
        subs = []

        # whisper sometimes generate traditional chinese, explicitly convert
        # cc = opencc.OpenCC("t2s")

        def _add_sub(start, end, text):
            subs.append(
                srt.Subtitle(
                    index=0,
                    start=datetime.timedelta(seconds=start),
                    end=datetime.timedelta(seconds=end),
                    # content=cc.convert(text.strip()),
                    content=text.strip(),
                )
            )

        prev_end = 0
        for r in transcribe_results:
            origin = r["origin_timestamp"]
            for s in r["segments"]:
                start = s["start"] + origin["start"] / self.sampling_rate
                end = min(
                    s["end"] + origin["start"] / self.sampling_rate,
                    origin["end"] / self.sampling_rate,
                )
                if start > end:
                    continue
                # mark any empty segment that is not very short
                # if start > prev_end + 1.0:
                #     _add_sub(prev_end, start, "< No Speech >")
                _add_sub(start, end, s["text"])
                prev_end = end

        with open(output, "wb") as f:
            f.write(srt.compose(subs).encode(self.args.encoding, "replace"))

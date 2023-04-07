import argparse
import logging
import torch

def main():
    parser = argparse.ArgumentParser(
        description="Generate subtitles for audio/video files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    logging.basicConfig(
        format="[WhisperSRT:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s"
    )
    logging.getLogger().setLevel(logging.INFO)

    parser.add_argument("inputs", type=str, nargs="+", help="Inputs folder name")
    parser.add_argument(
        "-t",
        "--transcribe",
        help="Transcribe videos/audio into subtitles",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-tr",
        "--translate",
        help="Translate existing srt files into other languages",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-r",
        "--rename",
        help="rename file extension",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        choices=["cpu", "cuda"],
        help="Force to CPU or GPU for transcribing. In default automatically use GPU if available.",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="",
        help="The original language of the video/audio/srt, blank for auto detect"
    )
    parser.add_argument(
        "--dest", type=str, default="zh", help="Output language or the srt file"
    )
    parser.add_argument(
        "--encoding", type=str, default="utf-8", help="Document encoding format"
    )
    parser.add_argument(
        "--vad", help="If or not use VAD", choices=["1", "0", "auto"], default="auto"
    )
    parser.add_argument(
        "--prompt", type=str, default="", help="initial prompt feed into whisper"
    )
    parser.add_argument("--suffix", type=str, default="", help="original file suffix to rename")
    parser.add_argument("--new_suffix", type=str, default="", help="new suffix to change to")
    args = parser.parse_args()

    if args.transcribe:
        from .transcribe import Transcribe

        Transcribe(args).run()
    elif args.translate:
        from .translate import Translate

        Translate(args).run()
    elif args.rename:
        from .rename import Rename

        Rename(args)
    else:
        logging.warn("No action, use -t")


if __name__ == '__main__':
    main()

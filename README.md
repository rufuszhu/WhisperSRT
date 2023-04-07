## WhisperSRT
- Use [OpenAi Whisper](https://github.com/openai/whisper) to generate subtitles for videos, and use [deepL](https://www.deepl.com/translator) to translate them.
- Use [Silero VAD](https://github.com/snakers4/silero-vad) to detect voice activity to accelerate the transcribe process and avoid [Whisper hallucination ](https://github.com/openai/whisper/discussions/679)
- Supported languages for speech transcribe in video: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py#L113
- Supported languages for translation: https://www.deepl.com/docs-api/translating-text/request/
## Setup
### Local install
```
git clone https://github.com/rufuszhu/WhisperSRT.git
cd WhisperSRT
pip install .
```
### Install [ffmpeg](https://ffmpeg.org/)
```
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```
### If you want to use gpu instead of cpu
```commandline
pip uninstall torch
pip cache purge
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```
### check if cuda is available
```commandline
python -c "import torch; print(torch.cuda.is_available())"
```
### Apply for deepL api key
https://www.deepl.com/pro#developer (It's free)

Save your api key in your environment variable as `DEEPL_API_KEY`

## Command-line usage
The following command will generate chinese subtitles for the video file `video.mp4` containing korean speech, and save the result to `video.srt`:
```commandline
whisperSrt path/to/video.mp4 -t --lang=ko --dest=zh
```
The same command also works for folder, it will generate subtitles for all video files in the folder, including subfolders:
```commandline
whisperSrt path/to/folder -t --lang=ko --dest=zh
```
The following command will translate an existing chinese srt file into an english srt file:
```commandline
whisperSrt path/to/video.srt -tr --lang=zh --dest=en
```
Use `whisperSrt -h` to see all available options.

## TODO
- [ ] Use chatGPT to translate
- [ ] Add UI for MacOS
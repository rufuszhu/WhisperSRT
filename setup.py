from pathlib import Path
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="whisperSrt",
    entry_points={
        "console_scripts": ["whisperSrt=whisperSrt.main:main"],
    },
    description="Generate subtitle for video/audio using whisper and translate it using deepl translate",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/rufuszhu/WhisperSRT",
    version="0.0.1",
    author="Rufus Zhu",
    author_email="rufus.zhu@hotmai.com",
    license="FREE",
    python_requires=">=3.6",
    install_requires=requirements,
    packages=find_packages(),
    keywords=["python", "srt", "languages", "translator", "subtitles", "whisper", "deepl"],
)
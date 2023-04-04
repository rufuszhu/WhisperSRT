import logging
import os
import re

import srt
import opencc

def is_video(filename):
    _, ext = os.path.splitext(filename)
    return ext in [".mp4", ".mov", ".mkv", ".avi", ".flv", ".f4v", ".webm"]

def is_srt(filename):
    _, ext = os.path.splitext(filename)
    return ext == ".srt"

def change_ext(filename, new_ext):
    # Change the extension of filename to new_ext
    base, _ = os.path.splitext(filename)
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    return base + new_ext

def check_exists(output, force):
    if os.path.exists(output):
        if force:
            logging.info(f"{output} exists. Will overwrite it")
        else:
            logging.info(
                f"{output} exists, skipping... Use the --force flag to overwrite"
            )
            return True
    return False


def expand_segments(segments, expand_head, expand_tail, total_length):
    # Pad head and tail for each time segment
    results = []
    for i in range(len(segments)):
        t = segments[i]
        start = max(t["start"] - expand_head, segments[i - 1]["end"] if i > 0 else 0)
        end = min(
            t["end"] + expand_tail,
            segments[i + 1]["start"] if i < len(segments) - 1 else total_length,
        )
        results.append({"start": start, "end": end})
    return results


def remove_short_segments(segments, threshold):
    # Remove segments whose length < threshold
    return [s for s in segments if s["end"] - s["start"] > threshold]


def merge_adjacent_segments(segments, threshold):
    # Merge two adjacent segments if their distance < threshold
    results = []
    i = 0
    while i < len(segments):
        s = segments[i]
        for j in range(i + 1, len(segments)):
            if segments[j]["start"] < s["end"] + threshold:
                s["end"] = segments[j]["end"]
                i = j
            else:
                break
        i += 1
        results.append(s)
    return results
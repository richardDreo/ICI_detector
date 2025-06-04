Audio File Formatting Guide

This document describes the required audio data format and directory structure expected by the ICI Detector application. The tool is designed to work with continuous hydrophone recordings prepared according to the SeisComP Data Structure (SDS) and stored in MiniSEED format.

---

FILE FORMAT REQUIREMENTS

- Format: MiniSEED (.mseed) or FLAC (.flac)
- Sampling rate: 250 Hz (recommanded).
  Recommended: keep the sampling rate below 300 Hz to avoid large files and improve processing speed.
- Channels: Single channel per file (1 component only)
- Duration: 1 full day per file
  It is recommended to include a 3-minute overlap with the previous and next day to avoid the loss of samples.

---

DIRECTORY STRUCTURE (SDS STANDARD)

Files must be stored following the SeisComP Data Structure (SDS):

<SDSROOT>/
└── <YEAR>/
    └── <NET>/<STA>/<CHAN>.D/
        └── <NET>.<STA>.<LOC>.<CHAN>.D.<YEAR>.<DOY>

Where:
- <SDSROOT>: root folder of your audio archive
- <YEAR>: four-digit year (e.g., 2024)
- <NET>: network code (2 characters, e.g., XX)
- <STA>: station identifier (e.g., KERG)
- <LOC>: location code (00 or left empty)
- <CHAN>: channel code (e.g., HHZ, BP1, etc.)
- <DOY>: day-of-year (001 to 366)

Example:
data/2024/XX/KERG/HHZ.D/XX.KERG.00.HHZ.D.2024.073

---

VALIDATION CHECKLIST

Before using the files in the application:

- Files are in .mseed or .flac format
- Sampling rate is exactly 250 Hz
- Each file is 24h long
- File names and paths follow the SDS format
- Files are organized into SDS-compliant folders
- (Recommended) Files include a 3-minute overlap with previous/next day

Incorrectly formatted files will be skipped or cause errors during analysis.

---

TOOLS FOR CONVERSION & VALIDATION

To convert or validate your data:

With ObsPy (Python):

from obspy import read, UTCDateTime
from obspy.core import Stream

st = read("input.wav")
st = st.resample(250)

# Split and export per 24h segment
start_time = UTCDateTime("2024-03-13T00:00:00")
for i in range(1):
    day_stream = st.slice(start_time + i*86400, start_time + (i+1)*86400)
    day_stream.write("XX.KERG.00.HHZ.D.2024.073", format="MSEED")


With FFmpeg (for WAV conversion):

ffmpeg -i input.wav -ac 1 -ar 250 -sample_fmt s16 output.wav

---

NEED HELP?

If you're unsure how to structure your data, feel free to contact the developer (see README).

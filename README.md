# GUI\_ICI\_Detector

A graphical user interface (GUI) for detecting **inter-click intervals (ICI)** in whale acoustic data, specifically for *Balaenoptera physalus* (fin whale) calls.
The tool enables efficient visualization, parameter tuning, and analysis of large-scale underwater acoustic datasets.

---

## 🚀 Features

* 🗺️ **Geographic Visualization** – Network station visualization with Cartopy
* 📂 **Batch Data Processing** – Handle large sets of structured audio data
* 🎧 **Spectrogram Visualization** – Explore acoustic data with spectrograms
* 📈 **ICI Analysis** – Extract ICI using cepstrogram based signal processing
* 🛠️ **Parameter Customization** – Adjust detection parameters via GUI widgets

---

## ⚙️ Requirements

* **Python**: 3.11
* **Core libraries**:

  * `PySide6` – GUI framework
  * `matplotlib`, `numpy`, `scipy` – Signal processing and plotting
  * `obspy` – Seismic/audio file handling (`MiniSEED`, SDS format)
  * `pandas`, `xarray` – Data manipulation
  * `cartopy`, `pyproj`, `shapely`, `geographiclib` – Geographic visualization
  * `mutagen`, `pydub` – Audio file metadata and conversion

👉 Full dependency list: see [`requirements.txt`](requirements.txt)

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/richardDreo/ICI_detector.git
cd ICI_detector
```
### 2. Install python 3.11

### 3. Create and activate a virtual environment

```bash
python3.11 -m venv env_detector
# macOS/Linux
source env_detector/bin/activate
# Windows
.\env_detector\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt --no-deps
```
---

## 📄 Audio File Requirements

This application expects input audio files in **MiniSEED format** and **SDS-compliant directory structure**, with a sampling rate of 250 Hz and 24h duration per file.

📘 See full details here:
**[`docs/audio_format.md`](docs/audio_format.md)**

## Before running the code
-> Set the paths to SDS root folder, and Inventories root Folder in the ./config/config.json


---

## 🧑‍💻 Usage

### Launch the application

```bash
python ici_detector.py
```

### GUI Workflow

1. **Select acoustic data** via the file dialog or directory browser.
2. **Visualize the recording locations** on the map in the **Network** tab.
3. In the **Spectrogram** tab:

   * Configure spectrogram parameters (short term or long term windows).
   * Visualize the spectrogram.
4. In the **Detection** tab:

   * Set ICI detection parameters.
   * Run and visualize the inter-click interval (ICI) extraction.
5. Save results or export figures if needed.

---

## 📁 Project Structure

```
ICI_detector/
├── config/                  
    └── config.json
├── docs/                  
    └── audio_format.md
├── lib/                 
    ├── networkFuntions.py
    ├── signalProcessing.py
    └── whaleIciDetection.py
├── module
    ├── bdd
        └── module.py
    ├── ici_detector
        ├── display.py
        ├── module.py
        ├── plot.py
        ├── widget.py
        └── worker.py
    ├── network
        ├── plot.py
        └── worker.py
    ├── spectrogram
        ├── display.py
        ├── module.py
        ├── plot.py
        ├── widget.py
        └── worker.py
    └── trajectory
├── styles
    └── dark.css
├── utils
    └── report_generator.py  
├── ici_detector.py        # Entry point script to launch the application
├── README.md              # Project documentation
└── requirements.txt       # Dependency list

```

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full terms.

---

## 🙏 Acknowledgments

* [ObsPy](https://docs.obspy.org/) – MiniSEED handling and seismic utilities
* [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) – Geographic plotting
* [PySide6](https://doc.qt.io/qtforpython/) – GUI toolkit
* [Matplotlib](https://matplotlib.org/) – Plotting engine

---

## 📬 Contact

**Richard Dréo**
📧 [richard.dreo@boksound.fr](mailto:richard.dreo@boksound.fr)
🌐 [GitHub – richardDreo](https://github.com/richardDreo)

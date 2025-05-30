# GUI_ICI_Detector

This project is a graphical user interface (GUI) for detecting inter-click intervals (ICI) in whale acoustics data. It provides tools for visualizing spectrograms, analyzing cepstrograms, and managing detection parameters.

---

## Features
- **Spectrogram Visualization**: Display spectrograms for acoustic data analysis.
- **Cepstrogram Analysis**: Analyze inter-click intervals (ICI) using cepstrograms.
- **Parameter Customization**: Configure detection parameters through an intuitive GUI.
- **Geographic Visualization**: Use Cartopy for geographic mapping and feature overlays.
- **Data Management**: Load, process, and analyze acoustic data efficiently.

---

## Requirements
- **Python Version**: Python 3.8 or higher
- **Dependencies**:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `PySide6`
  - `cartopy`
  - `geographiclib`

---

## Installation

### Step 1: Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/GUI_ICI_detector.git
cd GUI_ICI_detector


Step 2: Create a Virtual Environment
It is recommended to use a virtual environment to isolate the project dependencies:

python -m venv env_detector



Activate the virtual environment:

On macOS/Linux: source env_detector/bin/activate
On Windows: .\env_detector\Scripts\activate


Step 3: Install Dependencies
Install the required dependencies using the requirements.txt file:

pip install -r requirements.txt --no-deps


Usage
Running the Application
To launch the GUI, run the main script:

Loading Data
Use the File Dialog in the GUI to load your acoustic data files.
Configure detection parameters using the provided widgets.
Analyzing Data
Visualize spectrograms and cepstrograms.
Customize detection parameters and analyze inter-click intervals (ICI).


GUI_ICI_detector/
├── core/                     # Core logic and algorithms for ICI detection
│   ├── whaleIciDetection.py  # Functions for whale ICI detection
│   └── ...
├── utils/                    # Utility functions (e.g., plotting, data processing)
│   ├── plotting_utils.py     # Helper functions for plotting
│   ├── plotting_cepstrogram.py # Cepstrogram plotting logic
│   └── ...
├── [01_ici_detector.py](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2FUsers%2Fadmin%2FDocuments%2Fscience_workspace%2FSTUDIES_BOKSOUND%2FGUI_ICI_detector%2F01_ici_detector.py%22%2C%22path%22%3A%22%2FUsers%2Fadmin%2FDocuments%2Fscience_workspace%2FSTUDIES_BOKSOUND%2FGUI_ICI_detector%2F01_ici_detector.py%22%2C%22scheme%22%3A%22file%22%7D%7D)        # Main script to launch the GUI
├── [requirements.txt](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2FUsers%2Fadmin%2FDocuments%2Fscience_workspace%2FSTUDIES_BOKSOUND%2FGUI_ICI_detector%2Frequirements.txt%22%2C%22path%22%3A%22%2FUsers%2Fadmin%2FDocuments%2Fscience_workspace%2FSTUDIES_BOKSOUND%2FGUI_ICI_detector%2Frequirements.txt%22%2C%22scheme%22%3A%22file%22%7D%7D)          # List of dependencies
├── README.md                 # Project documentation
└── ...


Dependencies
The project uses the following Python libraries:

numpy: For numerical computations.
pandas: For data manipulation and analysis.
matplotlib: For plotting spectrograms and cepstrograms.
PySide6: For building the graphical user interface (GUI).
cartopy: For geographic visualizations.
geographiclib: For geodesic calculations.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Cartopy for geographic visualizations.
Matplotlib for plotting tools.
PySide6 for the GUI framework.
GeographicLib for geodesic calculations.
Contact
For questions or support, please contact:

Name: Your Name
Email: your.email@example.com
GitHub: your-username


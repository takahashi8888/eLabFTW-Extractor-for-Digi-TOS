# eLabFTW-Extractor-for-Digi-TOS

**A Python-based tool** to extract and convert experiment data from eLabFTW into structured, Excel-compatible formats.

This program connects to an eLabFTW instance via API and:

- Retrieves uploaded JSON files from a specific experiment:
  - `DigiTOS_Info_<ExperimentID>.json`
  - `Reaction_Scheme_<ExperimentID>.json`
- Parses and flattens nested data structures
- Converts them into a tabular format
- Exports them as **CSV / TSV files (Excel-compatible)**

A simple GUI (Tkinter) is provided for ease of use.

---

## Reference

For details on the structure and storage format of the extracted experiment notes, see:

- (Insert URL here)

---

## API Key Generation

1. Log in to your eLabFTW instance  
2. Click the profile icon (initials) in the top-right corner  
3. Navigate to: `Settings` → `API Keys`  
4. Generate a new API key  

---

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the program:

```bash
python elabftw_extract.py
```

---

## 1. Fetch Data

Enter the required information in the GUI:

- **eLabFTW URL**  
  Example: `https://localhost`
- **API Key**
- **Experiment ID**

Then click:

**Fetch Data**

### What happens:

- The program accesses the eLabFTW API
- Retrieves uploaded files linked to the experiment
- Automatically detects:
  - `DigiTOS_Info_<ExperimentID>.json`
  - `Reaction_Scheme_<ExperimentID>.json`

If successful, export options will be displayed.

---

## 2. Select Data to Export

After fetching, choose which data to include:

- **Digi-TOS Info**  
  → Experimental metadata (conditions, parameters, etc.)

- **Reaction Scheme**  
  → Reaction tables and structured chemical data

---

## 3. Choose Output Format

Select one of the following formats:

- **TSV** (Tab-separated)
- **CSV** (Comma-separated)

---

## 4. Export Data

Click:

**Export to File**

Exported files are automatically named using timestamps:

```
elabftw_export_YYYYMMDD_HHMMSS.csv
```

---

## Credits

Developed by **Hayato Takahashi**

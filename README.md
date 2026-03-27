# eLabFTW-Extractor-for-Digi-TOS
This program connects to an eLabFTW instance via API and:

- Retrieves uploaded JSON files from a specific experiment
  - `DigiTOS_Info_<ExperimentID>.json`
  - `Reaction_Scheme_<ExperimentID>.json`
- Parses and flattens nested data structures
- Converts them into a tabular format
- Exports them as **CSV / TSV files (Excel-compatible)**

A simple GUI (Tkinter) is provided for ease of use.

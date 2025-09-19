# ChEMBL Bioactivity Data Extractor

This script retrieves all bioactivity data for a given UniProt ID from the ChEMBL database. It identifies which compounds are commercially available and saves the combined data into a CSV file.

## Installation

### 1. Install Python Libraries
First, install the necessary Python libraries using pip:
```bash
pip install -r requirements.txt
```

### 2. Download ChEMBL Datafiles
This script requires two files from the ChEMBL database FTP site.

*   **ChEMBL SQLite Database:** The complete database in SQLite format.
*   **UniProt to ChEMBL Mapping File:** A tab-separated file mapping UniProt accession numbers to ChEMBL target IDs.

You can download these files with the commands below. Note that the database file is approximately 3GB.

```bash
# Download the UniProt mapping file
wget https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_uniprot_mapping.txt

# Download the latest ChEMBL SQLite database (e.g., version 34)
wget https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_34_sqlite.tar.gz

# Unpack the database file
tar -zxvf chembl_34_sqlite.tar.gz
```
This will create a directory named `chembl_34` containing the database file `chembl_34.db`.

## Usage
Run the script from the command line, providing the UniProt ID you wish to query. The paths to the ChEMBL database and UniProt mapping file can be provided on the command line. Alternatively, the default paths can be modified by editing the `DEFAULT_DB_FILENAME` and `DEFAULT_MAPPING_FILENAME` variables in the `assay_data_from_uniprot.py` script.

```bash
python assay_data_from_uniprot.py <UNIPROT_ID> --db /path/to/chembl_34/chembl_34.db --mapping /path/to/chembl_uniprot_mapping.txt
```

### Example
```bash
python assay_data_from_uniprot.py P08183 --db chembl_34/chembl_34.db --mapping chembl_uniprot_mapping.txt
```
The script will generate a CSV file named after the UniProt ID (e.g., `P08183.csv`).

## Output Fields

The output CSV file contains the following fields:

| Field               | Description                                                               |
| ------------------- | ------------------------------------------------------------------------- |
| `doc_id`            | The ChEMBL document identifier.                                           |
| `doi`               | DOI for the source publication.                                           |
| `title`             | Publication title.                                                        |
| `assay_id`          | The ChEMBL assay identifier.                                              |
| `description`       | Assay description.                                                        |
| `compound_key`      | The compound identifier from the publication.                             |
| `molregno`          | ChEMBL compound identifier.                                               |
| `canonical_smiles`  | SMILES for the compound.                                                  |
| `standard_type`     | Type of activity measured (e.g., IC50, EC50, Ki).                         |
| `standard_value`    | The assay result.                                                         |
| `standard_relation` | Qualifier for the standard_value (e.g., `>`, `<`, `=`).                   |
| `standard_units`    | The units for the standard value (e.g., nM).                              |
| `pchembl_value`     | The negative log of the assay value (only for `standard_relation` of `=`).|
| `purchasable`       | `True` or `False` indicating if the compound is in the ZINC database.     |
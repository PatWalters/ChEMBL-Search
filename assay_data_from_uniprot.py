#!/usr/bin/env python

import sys
import sqlite3
import pandas as pd
from tqdm.auto import tqdm
from molbloom import buy
import os
import argparse
from typing import Optional

# Default location of the ChEMBL database file
DEFAULT_DB_FILENAME = "/Users/pwalters/.data/chembl/35/chembl_35.db"
# Default location of the file mapping UniProt IDs to ChEMBL IDs
DEFAULT_MAPPING_FILENAME = "chembl_uniprot_mapping.txt"

def get_query() -> str:
    """Returns the SQL query to fetch assay data for a given ChEMBL ID."""
    sql = """SELECT
        d.doc_id,
        d.doi,
        d.title,
        a.assay_id,
        a.description,
        cr.compound_key,
        cs.molregno,
        cs.canonical_smiles,
        act.standard_type,
        act.standard_value,
        act.standard_relation,
        act.standard_units,
        act.pchembl_value
    FROM
        target_dictionary td
            JOIN
        assays a ON td.tid = a.tid
            JOIN
        docs d ON a.doc_id = d.doc_id
            JOIN
        activities act ON a.assay_id = act.assay_id AND d.doc_id = act.doc_id
            JOIN
        compound_records cr ON act.record_id = cr.record_id
            JOIN
        compound_structures cs ON cr.molregno = cs.molregno
    WHERE
        td.chembl_id = ?;"""
    return sql

def get_chembl_id(uniprot_id: str, mapping_filename: str) -> Optional[str]:
    """
    Retrieves the ChEMBL ID for a given UniProt ID from the mapping file.
    """
    if not os.path.exists(mapping_filename):
        print(f"Error: Can't find mapping file {mapping_filename}", file=sys.stderr)
        return None

    uniprot_df = pd.read_csv(mapping_filename, sep="	", comment='#',
                             names=['uniprot_id', 'chembl_id', 'target_name', 'target_type'])
    
    uniprot_res = uniprot_df.query("uniprot_id == @uniprot_id and target_type == 'SINGLE PROTEIN'")
    
    if len(uniprot_res) == 0:
        print(f"No ChEMBL ID found for UniProt {uniprot_id}")
        return None
        
    return uniprot_res.chembl_id.values[0]

def process_uniprot_id(uniprot_id: str, db_filename: str, mapping_filename: str):
    """
    Processes a single UniProt ID to fetch and save ChEMBL assay data.
    """
    if not os.path.exists(db_filename):
        print(f"Error: Can't find ChEMBL database file {db_filename}", file=sys.stderr)
        return

    chembl_id = get_chembl_id(uniprot_id, mapping_filename)
    if not chembl_id:
        return

    print(f"Searching for ChEMBL ID {chembl_id} (from UniProt {uniprot_id})")

    try:
        conn = sqlite3.connect(db_filename)
        sql = get_query()
        df = pd.read_sql_query(sql, conn, params=(chembl_id,))
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return

    print(f"Found {len(df)} records")

    if not df.empty:
        # Use MolBloom to label compounds in ZINC as purchasable
        print("Checking for purchasable compounds...")
        df['purchasable'] = [buy(smi, canonicalize=True) for smi in tqdm(df.canonical_smiles)]
        print(f"{df['purchasable'].sum()} of {len(df)} compounds are purchasable")

    # Write the results to a CSV file
    output_filename = f"{uniprot_id}.csv"
    df.to_csv(output_filename, index=False)
    print(f"Results written to {output_filename}")

def main():
    """
    Main function to parse arguments and run the data fetching process.
    """
    parser = argparse.ArgumentParser(description="Fetch ChEMBL assay data for a given UniProt ID.")
    parser.add_argument("uniprot_id", help="The UniProt ID to search for.")
    parser.add_argument("--db", dest="db_filename", default=DEFAULT_DB_FILENAME,
                        help=f"Path to the ChEMBL SQLite database file (default: {DEFAULT_DB_FILENAME})")
    parser.add_argument("--mapping", dest="mapping_filename", default=DEFAULT_MAPPING_FILENAME,
                        help=f"Path to the UniProt to ChEMBL mapping file (default: {DEFAULT_MAPPING_FILENAME})")
    
    args = parser.parse_args()

    process_uniprot_id(args.uniprot_id, args.db_filename, args.mapping_filename)

if __name__ == "__main__":
    main()

        

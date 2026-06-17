#!/usr/bin/env python
import os
import json
import sys
from mp_api.client import MPRester
from pymatgen.io.cif import CifWriter

def download_all(api_key):
    print("Initializing MPRester...")
    rester = MPRester(api_key=api_key)
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Download summary data for MgB2, LiF, Si, Al
    formulas = ["MgB2", "LiF", "Si", "Al"]
    for formula in formulas:
        print(f"Downloading summary data for {formula}...")
        try:
            results = rester.summary_search(formula=formula)
            normalized_results = []
            for r in results:
                sg_symbol = r.get("spacegroup", {}).get("symbol", "")
                sg_number = r.get("spacegroup", {}).get("number", 0)
                
                mid = r.get("material_id")
                try:
                    struct = rester.get_structure_by_material_id(mid)
                    cif_str = str(CifWriter(struct))
                except Exception as e:
                    print(f"  Warning: Could not fetch structure for {mid}: {e}")
                    cif_str = ""

                normalized_results.append({
                    "material_id": mid,
                    "cif": cif_str,
                    "pretty_formula": r.get("formula_pretty") or r.get("pretty_formula") or formula,
                    "e_above_hull": r.get("energy_above_hull") or r.get("e_above_hull") or 0.0,
                    "energy_per_atom": r.get("energy_per_atom") or -5.0,
                    "formation_energy_per_atom": r.get("formation_energy_per_atom") or -0.5,
                    "nsites": r.get("nsites") or (len(struct) if 'struct' in locals() else 3),
                    "volume": r.get("volume") or 28.0,
                    "spacegroup": {"symbol": sg_symbol, "number": sg_number},
                    "band_gap": r.get("band_gap") or 0.0,
                    "total_magnetization": r.get("total_magnetization") or 0.0,
                })
            
            with open(os.path.join(out_dir, f"get_data_{formula}.json"), "w") as f:
                json.dump(normalized_results, f, indent=4)
            print(f"  Saved get_data_{formula}.json")
        except Exception as e:
            print(f"  Error downloading summary for {formula}: {e}")

    # 2. Download structures for mp-149, mp-134, mp-763
    mids = ["mp-149", "mp-134", "mp-763"]
    for mid in mids:
        print(f"Downloading structure for {mid}...")
        try:
            struct = rester.get_structure_by_material_id(mid)
            with open(os.path.join(out_dir, f"structure_{mid}.json"), "w") as f:
                json.dump(struct.as_dict(), f, indent=4)
            print(f"  Saved structure_{mid}.json")
        except Exception as e:
            print(f"  Error downloading structure for {mid}: {e}")

    # 3. Download band structures for mp-565814 and mp-3079
    bs_mids = ["mp-565814", "mp-3079"]
    for mid in bs_mids:
        print(f"Downloading band structure for {mid}...")
        try:
            bs = rester.get_bandstructure_by_material_id(mid)
            with open(os.path.join(out_dir, f"bandstructure_{mid}.json"), "w") as f:
                json.dump(bs.as_dict(), f, indent=4)
            print(f"  Saved bandstructure_{mid}.json")
        except Exception as e:
            print(f"  Error downloading band structure for {mid}: {e}")

    # 4. Download DDBs for mp-149 and mp-1138
    ddb_mids = ["mp-149", "mp-1138"]
    for mid in ddb_mids:
        print(f"Downloading DDB for {mid}...")
        try:
            ddb_str = rester._make_request(f"/materials/{mid}/abinit_ddb")
            with open(os.path.join(out_dir, f"ddb_{mid}.txt"), "w") as f:
                f.write(ddb_str)
            print(f"  Saved ddb_{mid}.txt")
        except Exception as e:
            print(f"  Error downloading DDB for {mid}: {e}")

if __name__ == "__main__":
    api_key = os.environ.get("PMG_MAPI_KEY")
    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]
        
    if not api_key:
        print("Error: PMG_MAPI_KEY environment variable not set and no API key provided as argument.")
        print("Usage: python download_responses.py <your_mp_api_key>")
        sys.exit(1)
        
    download_all(api_key)

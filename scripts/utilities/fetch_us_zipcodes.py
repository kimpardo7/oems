import requests
import sys
from typing import Set, List

API_URL = "https://public.opendatasoft.com/api/records/1.0/search/"
DATASET = "us-zip-code-latitude-and-longitude"
OUTPUT_FILE = "us_zipcodes.txt"


def fetch_all_zip_codes() -> List[str]:
	"""Fetch all ZIP codes from Opendatasoft dataset and return a sorted list of unique 5-digit ZIPs."""
	zip_codes: Set[str] = set()

	start = 0
	rows = 10000  # try to fetch in one go; dataset has ~33k rows

	params = {
		"dataset": DATASET,
		"rows": rows,
		"start": start,
	}

	try:
		resp = requests.get(API_URL, params=params, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		records = data.get("records", [])
		for rec in records:
			fields = rec.get("fields", {})
			zip_val = fields.get("zip") or fields.get("zipcode") or fields.get("zcta5")
			if isinstance(zip_val, int):
				zip_str = f"{zip_val:05d}"
			elif isinstance(zip_val, str):
				zip_str = zip_val.strip()
			else:
				continue
			if zip_str.isdigit() and len(zip_str) == 5:
				zip_codes.add(zip_str)
		# If we didn't get all with one call, try paginating (fallback)
		total = data.get("nhits", len(records))
		if len(records) < total:
			while start + len(records) < total:
				start += rows
				params["start"] = start
				r = requests.get(API_URL, params=params, timeout=30)
				r.raise_for_status()
				d = r.json()
				recs = d.get("records", [])
				if not recs:
					break
				for rec in recs:
					fields = rec.get("fields", {})
					zip_val = fields.get("zip") or fields.get("zipcode") or fields.get("zcta5")
					if isinstance(zip_val, int):
						zip_str = f"{zip_val:05d}"
					elif isinstance(zip_val, str):
						zip_str = zip_val.strip()
					else:
						continue
					if zip_str.isdigit() and len(zip_str) == 5:
						zip_codes.add(zip_str)
	except Exception as e:
		print(f"Error fetching ZIP codes: {e}", file=sys.stderr)
		raise

	return sorted(zip_codes)


def write_zip_codes(zip_list: List[str]) -> None:
	with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
		for z in zip_list:
			f.write(z + "\n")


def main() -> None:
	print("Fetching US 5-digit ZIP codes...")
	zips = fetch_all_zip_codes()
	print(f"Fetched {len(zips)} unique ZIP codes.")
	print(f"Writing to {OUTPUT_FILE}...")
	write_zip_codes(zips)
	print("Done.")


if __name__ == "__main__":
	main()

import pandas as pd
from pathlib import Path
from typing import List, Dict


class JobExporter:
    @staticmethod
    def to_excel(jobs: List[Dict], output_file: str):
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        df = pd.DataFrame(jobs)
        df.to_csv(output_file, index=False)

        print(f"Saved {len(jobs)} jobs to {output_file}")
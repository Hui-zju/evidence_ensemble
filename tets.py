import json
import pandas as pd

# file_path = r"\\bmi-fs\Data.Common\Chenh\data\terminology\cosmic\cmc_export.tsv"
# df = pd.read_csv(file_path, sep="\t", nrows=5, usecols=list(range(21)))  #
# print(len(df))

file_path = r"\\bmi-fs\Data.Common\Chenh\data\terminology\Genecards\EGFR+BRAF.json"
with open(file_path, 'r', encoding='utf-8') as f:
    evidences = json.load(f)
print('ok')




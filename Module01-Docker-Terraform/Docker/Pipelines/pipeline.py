import sys
import pandas as pd

month = sys.argv[1]
df = pd.DataFrame({"Month": [month], "Value": [100]})

df.to_parquet(f"output_{month}.parquet")

print(df.head())
print("Hello from the pipeline where month is", month, "!")
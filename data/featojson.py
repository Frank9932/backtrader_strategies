from pathlib import Path
import pandas as pd
import os
feather_file_path = Path(os.getcwd())/'BTC_USDT-1h.feather'
df = pd.read_feather(feather_file_path)
print(df.head())
json_file_path = 'your_data.json'
df.to_json(json_file_path, orient='records', date_format='iso')
print("Data has been successfully saved to")


# {"date":"2022-01-27T07:00:00.000Z","open":36139.09,"high":36303.8,"low":35915.0,"close":36173.87,"volume":1860.34114},{"date":"2022-01-27T08:00:00.000Z","open":36177.17,"high":36500.0,"low":35815.8,"close":36450.0,"volume":2112.75603},{"date":"2022-01-27T09:00:00.000Z","open":36449.99,"high":36611.21,"low":36333.0,"close":3652
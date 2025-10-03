import pandas as pd

# Read the train.csv file
df = pd.read_csv("data/processed/train.csv", sep=";")

# Extract only the 'uid' and 'question' columns
parsed_df = df[["uid", "question"]]

# Save to new file
parsed_df.to_csv("data/processed/parsed_train_test.csv", sep=";", index=False)

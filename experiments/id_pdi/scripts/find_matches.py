import pandas as pd

DATASET_EMPLOIS = "data/emplois.csv"
DATASET_IF = "data/if.csv"


df_emplois = pd.read_csv(DATASET_EMPLOIS).drop_duplicates(subset=['email'])
df_if = pd.read_csv(DATASET_IF).drop_duplicates(subset=['email'])

df_merged = pd.merge(df_emplois, df_if, on='email', how='inner').drop_duplicates(subset=['email'])

print(len(df_merged) / len(df_emplois) * 100)

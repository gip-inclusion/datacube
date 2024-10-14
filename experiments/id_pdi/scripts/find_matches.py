import pandas as pd

DATASET_EMPLOIS = "data/emplois.csv"
DATASET_IF = "data/if.csv"
DATASET_RDVI = "data/rdvi.csv"


df_emplois = pd.read_csv(DATASET_EMPLOIS).drop_duplicates(subset=['email'])
df_if = pd.read_csv(DATASET_IF).drop_duplicates(subset=['email'])
df_rdvi = pd.read_csv(DATASET_RDVI).drop_duplicates(subset=['email'])

df_merged0 = pd.merge(df_emplois, df_if, on='email', how='inner').drop_duplicates(subset=['email'])
df_merged1 = pd.merge(df_emplois, df_rdvi, on='email', how='inner').drop_duplicates(subset=['email'])

print(df_merged0)
print("Percent IF/Emplois", len(df_merged0) / len(df_emplois) * 100)
print(df_merged1)

print("Percent RDVI/Emplois", len(df_merged1) / len(df_emplois) * 100)

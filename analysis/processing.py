import os


def clean_and_average(df):
    df['Classify_Class'] = df['Classify_Class'].str.strip()
    texture_columns = [col for col in df.columns if 'Texture_SumVariance_GFPInput' in col]
    df['Texture_SumVariance_GFPInput_Average'] = df[texture_columns].mean(axis=1)
    df.dropna(subset=['Texture_SumVariance_GFPInput_Average'], inplace=True)
    return df

def safe_extract(zip_ref, extract_path):
    for member in zip_ref.namelist():
        member_path = os.path.join(extract_path, member)
        if not os.path.abspath(member_path).startswith(os.path.abspath(extract_path)):
            raise Exception("Unsafe ZIP file detected")
    zip_ref.extractall(extract_path)

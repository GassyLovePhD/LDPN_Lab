def clean_and_average(df):
    df['Classify_Class'] = df['Classify_Class'].str.strip()
    texture_columns = [col for col in df.columns if 'Texture_SumVariance_GFPInput' in col]
    df['Texture_SumVariance_GFPInput_Average'] = df[texture_columns].mean(axis=1)
    df.dropna(subset=['Texture_SumVariance_GFPInput_Average'], inplace=True)
    return df
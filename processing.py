import pandas as pd

def remove_duplicates(input_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path)

    # Remove duplicate rows
    df_cleaned = df.drop_duplicates()

    # Save the cleaned DataFrame back to a CSV file
    df_cleaned.to_csv(output_path, index=False)

    return len(df) - len(df_cleaned)  # Return the number of duplicates removed

def remove_empty_rows(input_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path)

    # Remove rows that are completely empty
    df_cleaned = df.dropna(how='all')

    # Save the cleaned DataFrame back to a CSV file
    df_cleaned.to_csv(output_path, index=False)

    return len(df) - len(df_cleaned)  # Return the number of empty rows removed

def normalize_text_case(input_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path)

    # Normalize text case for all string columns
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].str.lower()  # Convert to lowercase

    # Save the cleaned DataFrame back to a CSV file
    df.to_csv(output_path, index=False)

    return len(df)  # Return the number of rows processed
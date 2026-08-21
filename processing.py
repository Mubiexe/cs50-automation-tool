import pandas as pd

def remove_duplicates(input_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path)

    # Remove duplicate rows
    df_cleaned = df.drop_duplicates()

    # Save the cleaned DataFrame back to a CSV file
    df_cleaned.to_csv(output_path, index=False)

    return len(df) - len(df_cleaned)  # Return the number of duplicates removed
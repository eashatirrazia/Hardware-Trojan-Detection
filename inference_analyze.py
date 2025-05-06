import csv
import argparse
import os
import re  # Import the regular expression module

def analyze_csv_files(directory):
    """
    Analyzes CSV files in a given directory to identify folders with consistent 'TJFree' and 'TJIn' classification.

    Args:
        directory (str): The path to the directory containing the CSV files.
    """
    # Store results for each folder
    folder_results = {}

    # Process each CSV file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    folder = row['Folder']
                    prediction = row['Prediction']
                    actual_label = row['Actual Label']
                    correct = row['Correct']

                    # Initialize folder entry if it doesn't exist
                    if folder not in folder_results:
                        folder_results[folder] = {
                            'TJFree': {'correct': 0, 'total': 0, 'consistent': True, 'only_tjfree': True, 'always_misclassified': True},  # Added 'always_misclassified'
                            'TJIn': {'correct': 0, 'total': 0, 'consistent': True, 'only_tjin': True, 'always_misclassified': True},      # Added 'always_misclassified'
                        }

                    # Case-insensitive comparison using regex
                    if re.search(r'TJFree', actual_label, re.IGNORECASE):
                        folder_results[folder]['TJFree']['total'] += 1
                        if correct.lower() == 'yes':
                            folder_results[folder]['TJFree']['correct'] += 1
                            folder_results[folder]['TJFree']['always_misclassified'] = False # set to false if correctly classified even once
                        else:
                            folder_results[folder]['TJFree']['consistent'] = False
                        folder_results[folder]['TJIn']['only_tjin'] = False
                    elif re.search(r'TJIn', actual_label, re.IGNORECASE):
                        folder_results[folder]['TJIn']['total'] += 1
                        if correct.lower() == 'yes':
                            folder_results[folder]['TJIn']['correct'] += 1
                            folder_results[folder]['TJIn']['always_misclassified'] = False  # set to false if correctly classified even once
                        else:
                            folder_results[folder]['TJIn']['consistent'] = False
                        folder_results[folder]['TJFree']['only_tjfree'] = False
                    else:
                        # Handle cases where the actual label is neither TJFree nor TJIn
                        pass

    # Output the results in alphabetical order
    print("Folders with consistent classification for TJFree:")
    consistent_tjfree_folders = [folder for folder, results in folder_results.items() if results['TJFree']['consistent'] and results['TJFree']['only_tjfree']]
    for folder in sorted(consistent_tjfree_folders):
        print(f"- {folder}")

    print("\nFolders with consistent classification for TJIn:")
    consistent_tjin_folders = [folder for folder, results in folder_results.items() if results['TJIn']['consistent'] and results['TJIn']['only_tjin']]
    for folder in sorted(consistent_tjin_folders):
        print(f"- {folder}")

    print("\nFolders with consistent misclassification for TJFree:")
    misclassified_tjfree_folders = [folder for folder, results in folder_results.items() if results['TJFree']['always_misclassified'] and results['TJFree']['only_tjfree']]
    for folder in sorted(misclassified_tjfree_folders):
        print(f"- {folder}")

    print("\nFolders with consistent misclassification for TJIn:")
    misclassified_tjin_folders = [folder for folder, results in folder_results.items() if results['TJIn']['always_misclassified'] and results['TJIn']['only_tjin']]
    for folder in sorted(misclassified_tjin_folders):
        print(f"- {folder}")

    print("\nDetailed breakdown:")
    for folder, results in folder_results.items():
        print(f"\nFolder: {folder}")
        print(f"  TJFree: {results['TJFree']['correct']} correct out of {results['TJFree']['total']}")
        print(f"  TJIn: {results['TJIn']['correct']} correct out of {results['TJIn']['total']}")
        if results['TJFree']['consistent']:
            print("  Consistently classified TJFree entries.")
        else:
            print("  Inconsistently classified TJFree entries.")
        if results['TJIn']['consistent']:
            print("  Consistently classified TJIn entries.")
        else:
            print("  Inconsistently classified TJIn entries.")
        if results['TJFree']['only_tjfree']:
            print("  Only contains TJFree entries.")
        else:
            print("  Contains mixed labels (not only TJFree).")
        if results['TJIn']['only_tjin']:
            print("  Only contains TJIn entries.")
        else:
            print("  Contains mixed labels (not only TJIn).")
        if results['TJFree']['always_misclassified']:
            print("  Always misclassified TJFree entries.")
        else:
            print("  Not always misclassified TJFree entries.")
        if results['TJIn']['always_misclassified']:
            print("  Always misclassified TJIn entries.")
        else:
            print("  Not always misclassified TJIn entries.")

def main():
    """
    Main function to parse command line arguments and run the analysis.
    """
    parser = argparse.ArgumentParser(description="Analyze CSV files in a directory.")
    parser.add_argument("directory", help="Path to the directory containing the CSV files.")
    args = parser.parse_args()

    # Check if the directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' not found.")
        return

    analyze_csv_files(args.directory)

if __name__ == "__main__":
    main()

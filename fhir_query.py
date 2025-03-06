import requests
import pandas as pd
import json
from datetime import datetime
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from imblearn.over_sampling import SMOTE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FHIR Server Configuration
fhir_url = 'http://hapi.fhir.org/baseR4/Patient'  # Replace with actual FHIR server URL
headers = {'Accept': 'application/fhir+json'}

def get_patients():
    """Retrieves patients from the FHIR server, processing raw JSON with pagination."""
    patients = []
    next_url = fhir_url  # Start with the initial URL
    while next_url:
        try:
            response = requests.get(next_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                for entry in data['entry']:
                    resource = entry.get('resource', {})
                    patients.append(resource)

            # Check for the 'next' link in the bundle
            next_url = None
            if 'link' in data:
                for link in data['link']:
                    if link['relation'] == 'next':
                        next_url = link['url']
                        break  # Found the 'next' link, exit loop

        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving patients: {e}")
            break  # Exit the loop on error
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            break

    return patients

def validate_birth_date(birth_date):
    """Validates and formats the birthDate to YYYY-MM-DD."""
    try:
        if not birth_date:
            return None
        # Parse the date to ensure it's in the correct format
        formatted_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        return formatted_date.isoformat()
    except (ValueError, TypeError):
        return None

def patients_to_dataframe(patients):
    """Converts a list of raw Patient resources to a Pandas DataFrame."""
    data = []
    for p in patients:
        try:
            birth_date_str = p.get('birthDate', None)
            birth_date = validate_birth_date(birth_date_str)
            age = None  # Calculate age

            if birth_date:
                birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

            gender = p.get('gender', 'Unknown')
            name_list = p.get('name', [])
            given_names = name_list[0].get('given', []) if name_list else []
            family_name = name_list[0].get('family', 'Unknown') if name_list else 'Unknown'
            given_name = ' '.join(given_names) if given_names else 'Unknown'  # Join given names

            patient_data = {
                'id': p.get('id', 'Unknown'),
                'gender': gender,
                'birthDate': birth_date,
                'age': age,
                'given_name': given_name,
                'family_name': family_name
            }
            data.append(patient_data)
        except Exception as e:
            logging.error(f"Error processing patient data: {e}")
            raise
    return pd.DataFrame(data)

def add_sepsis_label(df):
    """Add a sepsis label for demonstration purposes."""
    # For demonstration, randomly assign sepsis labels
    df['sepsis'] = (df.index % 2 == 0).astype(int)
    return df

def train_model(df):
    """Train a machine learning model to predict sepsis."""
    df['gender'] = df['gender'].astype('category').cat.codes

    # Define features and target
    X = df[['gender', 'age']]
    y = df['sepsis']

    # Handle missing values
    imputer = SimpleImputer(strategy='mean')
    X = imputer.fit_transform(X)

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Apply SMOTE to oversample the minority class
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train_resampled, y_train_resampled)

    y_pred = model.predict(X_test)
    logging.info("\n" + classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()

    return model

def main():
    try:
        patients = get_patients()
        if patients:
            df_patients = patients_to_dataframe(patients)
            df_patients = add_sepsis_label(df_patients)
            logging.info(df_patients.head())  # Display first few rows
            model = train_model(df_patients)
        else:
            logging.info("No patient data to display.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
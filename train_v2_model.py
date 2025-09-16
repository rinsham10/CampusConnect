# train_v2_model.py

import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import pickle

# --- 1. Load the new dataset ---
try:
    df = pd.read_csv('college_student_placement_dataset.csv')
except FileNotFoundError:
    print("FATAL ERROR: 'college_student_placement_dataset.csv' not found. Please place it in the same folder.")
    exit()

# --- 2. Select the 5 features + 1 target column ---
features_to_use = [
    'CGPA',
    'Academic_Performance',
    'Internship_Experience',
    'Communication_Skills',
    'Projects_Completed',
    'Placement'  # The 'answer' column is required for training
]
df_model = df[features_to_use].copy()

# --- 3. Preprocess the Data ---
le = LabelEncoder()
df_model['Internship_Experience'] = le.fit_transform(df_model['Internship_Experience'])
df_model['Placement'] = le.fit_transform(df_model['Placement'])

# --- 4. Define Features (X) and Target (y) ---
X = df_model.drop('Placement', axis=1)
y = df_model['Placement']

# --- 5. Train the SVM Model with Probability Enabled ---
# Using probability=True is the key to getting percentage chances
model_v2 = SVC(kernel='linear', probability=True, random_state=42)
model_v2.fit(X, y)

# --- 6. Save the new model with a new name ---
with open('placement_model_v2.pkl', 'wb') as file:
    pickle.dump(model_v2, file)

print("✅ Success! New model trained and saved as 'placement_model_v2.pkl'")
print("Features used:", list(X.columns))
# compare_models.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Import the algorithms we want to compare
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

print("--- Starting Model Comparison ---")

# --- 1. Load and Prepare the Dataset (same as before) ---
try:
    df = pd.read_csv('college_student_placement_dataset.csv')
except FileNotFoundError:
    print("FATAL ERROR: 'college_student_placement_dataset.csv' not found.")
    exit()

features_to_use = [
    'CGPA', 'Academic_Performance', 'Internship_Experience',
    'Communication_Skills', 'Projects_Completed', 'Placement'
]
df_model = df[features_to_use].copy()

# Preprocess the data
le = LabelEncoder()
df_model['Internship_Experience'] = le.fit_transform(df_model['Internship_Experience'])
df_model['Placement'] = le.fit_transform(df_model['Placement'])

X = df_model.drop('Placement', axis=1)
y = df_model['Placement']

# --- 2. Create a Consistent Training and Testing Split ---
# Using the same `random_state` ensures all models are tested on the exact same data, which is crucial for a fair comparison.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training data has {len(X_train)} samples. Testing data has {len(X_test)} samples.")
print("-" * 30)

# --- 3. Define the Models to Compare ---
models = {
    "Random Forest": SVC(kernel='linear', probability=True, random_state=42),
    "Logistic Regression": LogisticRegression(random_state=42),
    "Support Vector Classifier (SVC)": RandomForestClassifier(random_state=42)
}

# --- 4. Train and Evaluate Each Model ---
results = {}

for name, model in models.items():
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions on the test data
    predictions = model.predict(X_test)
    
    # Calculate the accuracy score
    accuracy = accuracy_score(y_test, predictions)
    
    # Store the result
    results[name] = accuracy
    print(f"{name} -> Success Percentage: {accuracy:.2%}")

print("-" * 30)

# --- 5. Announce the Winner ---
best_model_name = max(results, key=results.get)
best_accuracy = results[best_model_name]

print(f"🏆 The best performing algorithm is: {best_model_name} with an accuracy of {best_accuracy:.2%}")
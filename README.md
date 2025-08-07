# 🎓 CampusConnect – Student Portal & Campus Placement Predictor

**CampusConnect** is a Django web application that predicts whether a student is likely to be **placed** or **not placed** based on academic and profile features using a machine learning model trained on the [Campus Placement Dataset](https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement).

---

## 🚀 Features

- Clean and simple UI to input student details.
- Predicts placement status using a trained ML model.
- Uses `joblib` to load the model and make predictions.
- Built using Django, HTML/CSS, and scikit-learn.

---

## 📊 Model Inputs (Total = 6 features)

These are the **processed inputs** used by the ML model after one-hot encoding:
 
1. `ssc_p` – Secondary Education Percentage (10th)
2. `hsc_p` – Higher Secondary Percentage (12th)
3. `degree_p` – Degree Percentage
4. `workex` – Work Experience (Yes = 1, No = 0)
5. `etest_p` – E-test (Aptitude Test) Percentage
6. `mba_p` – MCA Percentage

> Note: One-hot encoded fields are expanded into multiple binary inputs.

---

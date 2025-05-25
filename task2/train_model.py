# importing pandas library
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib

# importing the data from the dataset
df = pd.read_csv('dataset/sample_task_dataset.csv', parse_dates=["Deadline", "Date Created"])

# adding a label
# this is mapping of priority to number
label_map = {"Low": 0, "Medium": 1, "High": 2}
df["Label"] = df["Importance"].map(label_map)

# Extracting the numerical values from the datasets (deadline, and estimated time)
df["DaysUntilDeadline"] = (df["Deadline"] - df["Date Created"]).dt.days
df["EstimatedMinutes"] = df["Estimation Time"].str.extract(r'(\d+)').astype(int)

# now preparing the data for model 
# selecting features and label 
# features are the things model uses to predict label 
X = df[["DaysUntilDeadline", "EstimatedMinutes"]]
y = df["Label"]

# splitting the data into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# training the data using the decisionTreeClassifier
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

# saving this model that can be used later
joblib.dump(clf, "model.pkl")

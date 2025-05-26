import joblib
import pandas as pd 

# getting the model 
model = joblib.load("models/model.pkl")

def convert_prediction_number(prediction):
    if prediction == 2:
        return "High"
    elif prediction == 1:
        return "Medium"
    else:
        return "Low"

# writing the predict function that predicts the priority of the task based on the users input
def predict_priority(deadline, date_created, estimation):
    daysLeft = (deadline - date_created).days
    minutes = int(estimation)
    X = pd.DataFrame([[daysLeft, minutes]], columns=["DaysUntilDeadline", "EstimatedMinutes"]) # type ignore 
    prediction_number = model.predict(X)[0]
    return convert_prediction_number(prediction_number)

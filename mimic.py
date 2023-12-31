# -*- coding: utf-8 -*-
"""MIMIC.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hn6x6JrAU-EBJMtwIyzqJns3pzMluJtR

# Case strudy: Cancer Classification in Clinical data from the MIMIC-II database for a case study on indwelling arterial catheters

## Problem definition

- Predicting if patients have a malignant tumor base on demographic data (e.g. age, weight), clinical observations collected during the first day of ICU stay (e.g. white blood cell count, heart rate), and outcomes (e.g. 28 day mortality and length of stay).

- 46 features are used, examples:
      - aline_flg: Indwelling arterial catheters (IACs) used (binary, 1 = year, 0 = no)
      - icu_los_day: length of stay in ICU (days, numeric)
      - hospital_los_day: length of stay in hospital (days, numeric)
      - age: age at baseline (years, numeric)
      - gender_num: patient gender (1 = male; 0=female)
      - weight_first: first weight, (kg, numeric)
      - bmi: patient BMI, (numeric)
      - sapsi_first: first SAPS I score (numeric)
      - sofa_first: first SOFA score (numeric)


- Datasets are linearly separable using all 46 input features
- Number of Instances: 1776
- Class Distribution: 256 Malignant, 1520 Normal
- Target class (mal_flag):
         - Normal = 0
         - Malignant = 1

### Bibliogrphy
- Raffa, J. (2016). Clinical data from the MIMIC-II database for a case study on indwelling arterial catheters (version 1.0). PhysioNet. https://doi.org/10.13026/C2NC7F.

- Data, M. C. (2016). Secondary analysis of electronic health records. En Springer eBooks. https://doi.org/10.1007/978-3-319-43742-2

- Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., ... & Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation [Online]. 101 (23), pp. e215–e220.

- Kulin-Patel. (s. f.). Breast-cancer-classification/breast _cancer_classification.ipynb at main · kulin-patel/breast-cancer-classification. GitHub. https://github.com/kulin-patel/breast-cancer-classification/blob/main/breast%20_cancer_classification.ipynb

## Importing Data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report,confusion_matrix

import joblib
from joblib import dump, load

!pip install -U imbalanced-learn
from imblearn.over_sampling import SMOTE

from random import randint



!wget -r -N -c -np https://physionet.org/files/mimic2-iaccd/1.0/
table = pd.read_csv('/content/physionet.org/files/mimic2-iaccd/1.0/full_cohort_data.csv')

table

table.keys()

table.shape

table['mal_flg']

"""### Drop mal_flg variable"""

data=table.drop(['mal_flg'],axis=1)
label=table['mal_flg']

data.keys()

data

"""### Create a Dataframe"""

df=pd.DataFrame(np.c_[data,label],columns=np.append(data.keys(),'cancer'))
df

"""# Preprocessing Data

## Checking of empty variables
"""

df.any()

"""## Correct Data"""

class CustomTransform(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Copies the DataFrame to avoid modifying the original one
        X_transformado = X.copy()

        # Map service_unit categories to numbers
        X_transformado['service_unit'].replace({'MICU': 0, 'SICU': 1, 'FICU': 2}, inplace=True)

        # Remove columns 'day_icu_intime' and 'sepsis_flg'.
        X_transformado = X_transformado.drop(['day_icu_intime', 'sepsis_flg'], axis=1)

        try:
            #Create DataFrame as in the previous steps
            X_transformado = pd.DataFrame(np.c_[X_transformado, X_transformado['mal_flg']], columns=np.append(X_transformado.keys(),'cancer'))
            X_transformado = X_transformado.drop(['mal_flg'],axis=1)

        except:
            print('Ther is no mal_flg')

        return X_transformado



# Create an instance of the custom transformation
MyTransformation = CustomTransform()

# Apply the transformation to the DataFrame
df_transf = MyTransformation.transform(df)
df_transf

"""## Check correction"""

df_transf.any()

df_transf.shape

"""## Imputation of NaN values and data normalisation"""

imputer = KNNImputer(n_neighbors=7, weights="uniform")
DATA=imputer.fit_transform(df_transf)


DATA=pd.DataFrame(DATA)
DATA.columns=df_transf.keys()

min_max_scaler = MinMaxScaler()
NormDATA = min_max_scaler.fit_transform(DATA)
NormDATA=pd.DataFrame(NormDATA)
NormDATA.columns=df_transf.keys()
NormDATA

"""## DataFrame transform"""

class DF_Transform(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, Y=None):
        Data_transf = X.copy()

        Data_transf = pd.DataFrame(Data_transf)
        Data_transf.columns=Y


        return Data_transf

DF = DF_Transform()

"""## Saving Transformations"""

joblib.dump({'cleaner': MyTransformation, 'imputer': imputer, 'scaler': min_max_scaler, 'dataframe': DF}, 'MIMIC_Cancer_Classifier_Preprocessing.joblib')

"""# Data Visualization"""

sns.countplot(x=NormDATA['cancer'], label = "Count")

"""### Correlation Matrix"""

plt.figure(figsize=(35,20))
sns.heatmap(NormDATA.corr(numeric_only=True),annot=True)

"""### Mapping of the variables most correlated with cancer"""

sns.pairplot(NormDATA,hue='cancer',vars=['age','sofa_first','sapsi_first','hospital_los_day','hour_icu_intime'])

"""# Model Training"""

x=NormDATA.drop(['cancer'],axis=1)
y=NormDATA['cancer']


# Split data 70%-30% into training set and test set
x_train, x_test, y_train, y_test = train_test_split(x,y.values,test_size=0.30,random_state=5)

print ('Training Set: %d, Test Set: %d \n' % (len(x_train), len(x_test)))

x_train.shape

x_test.shape

y_train.shape

y_test.shape

svc_model=SVC(class_weight={0: 1, 1: 4})
svc_model.fit(x_train,y_train)

"""## Model Evaluation"""

y_predict = svc_model.predict(x_test)
cm=confusion_matrix(y_test,y_predict)
sns.heatmap(cm,annot=True)

print(classification_report(y_test,y_predict))

"""## Improve Accuracy

### Searching for C and Gamma parameters, with class weights
"""

param_grid = {'C': np.linspace(-10,10,30), 'gamma': np.linspace(-10,10,30), 'kernel': ['rbf']}

grid = GridSearchCV(SVC(class_weight={0: 1, 1: 5}),param_grid,refit=True,verbose=4)

grid.fit(x_train,y_train)

grid.best_params_

grid.best_estimator_

grid_predictions= grid.predict(x_test)

"""## Model Evaluation"""

cm=confusion_matrix(y_test,grid_predictions)
sns.heatmap(cm,annot=True)

print(classification_report(y_test,grid_predictions))

"""# Ups! We will follow another path

## Adding synthetic data for training to balance the classes
"""

X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.2, random_state=10)

# Aplicar SMOTE solo en el conjunto de entrenamiento
smote = SMOTE(random_state=10)
X_resampled, Y_resampled = smote.fit_resample(X_train, Y_train)

# Imprimir las formas de los conjuntos antes y después de SMOTE
print("\n")
print("Forma antes de SMOTE:", X_train.shape, Y_train.shape)
print("Forma después de SMOTE:", X_resampled.shape, Y_resampled.shape)

"""### Visualization new training data


"""

sns.countplot(x=Y_resampled, label = "Count")

PLOT=pd.DataFrame(np.c_[X_resampled,Y_resampled],columns=np.append(X_resampled.keys(),'cancer'))

plt.figure(figsize=(35,20))
sns.heatmap(PLOT.corr(numeric_only=True),annot=True)

sns.pairplot(PLOT ,hue='cancer' ,vars=['age','sofa_first','sapsi_first','hospital_los_day','hour_icu_intime'])

"""### Evaluation Model"""

y_predict = svc_model.predict(x_test)
cm=confusion_matrix(y_test,y_predict)

sns.heatmap(cm,annot=True)

"""# Improving Model

### Searching for C and Gamma parameters, with class weights
"""

param_grid = {'C': np.linspace(0.01,10,5), 'gamma': np.linspace(0.01,10,5), 'kernel': ['rbf']}
MODEL = GridSearchCV(SVC(class_weight={0: 1, 1: 2}),param_grid,refit=True,verbose=4)

MODEL.fit(X_resampled,Y_resampled)

MODEL.best_params_

MODEL.best_estimator_

"""### Evaluation Model"""

grid_predictions= MODEL.predict(x_test)
cm=confusion_matrix(y_test,grid_predictions)
sns.heatmap(cm,annot=True)

print(classification_report(y_test,grid_predictions))

"""## Save the model"""

dump(MODEL, 'MIMIC_Cancer_Classifier_Model.joblib')

"""## Delete the model"""

del(MODEL)

"""## Reload the model"""

Reload_Model = load('MIMIC_Cancer_Classificator.joblib')

"""# Small Test

## Reload Preprocess
"""

reload_trnsf=joblib.load("MIMIC_Cancer_Classifier_Preprocessing.joblib")
reload_trnsf

"""## Preprocessing raw data"""

# Preprocess Step 1
preproc_1 = reload_trnsf['cleaner'].transform(table)
keys=preproc_1.keys()

#Preproces Step 2
preproc_2 = reload_trnsf['imputer'].transform(preproc_1)
preproc_2 = reload_trnsf['dataframe'].transform(preproc_2, keys)

#Preproces Step 3
preproc_3 = reload_trnsf['scaler'].transform(preproc_2)
preproc_3 = reload_trnsf['dataframe'].transform(preproc_3, keys)
display(preproc_3)

"""## Generate a random trial"""

x_trial=preproc_3.drop(['cancer'],axis=1)
y_trial=preproc_3['cancer']


random_num=randint(0,len(x_trial)-1)

data_trial=x_trial.loc[random_num:random_num+1]
label_trial=y_trial.loc[random_num:random_num+1]

print ("Predicted label:", Reload_Model.predict(data_trial))
print ("Groundtruth label:",label_trial.to_numpy())
# -*- coding: utf-8 -*-
"""DRW Data Science.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/118Xx_U6_Pk7cfL2IX20vy8TVjj7c3Odt

# Traders@MIT Data Science Case 2024

You are a member of the fictional trading arm of Traders@MIT, and you are asked to present evidence that some hand-crafted signals can be used to create a profitable trading strategy. To do this, you will construct a trading strategy in the form of a `python` function. You will be given a small amount of data to train your models, and you will be evaluated on a large hidden dataset. Your objective is to maximize the t-statistic of your trading strategy.

More technical details are provided below:

You are given a training dataset (`"train.csv"`) which is a DataFrame with `200` rows, each representing a different moment in time. Each row has some number of columns labeled "regressor{i}" or "target{i}". For each row, "regressor{i}" represents the value of the $i$'th signal for the given tick. "target{i}" represents the return of the $i$'th stock, meaning if your position in stock $i$ is $\$X$ for the given tick, your PNL for that tick is $\$X \cdot \text{target\{i\}}$. You can use this dataset to learn how to predict the stock movements given your feature set.

You will write a `python` function called `strategy` which takes as input *only* the regressors in a row in a DataFrame, and returns as output a list-like object with the same length as the number of stocks. The output represents the dollar positions you wish to acquire in each stock, and they can be any real number. You may assume that you have no market impact, no trading costs, etc. Your submitted function will run on every row of the hidden DataFrame, and your score will be t-statistic of your PNL over all the ticks. A copy of the code that computes this score for the training set and an example trading strategy are provided below.

It is guaranteed that each tick is an independent generation of the same statistical process.

Please do not try to abuse floating point calculations (any `inf` scores will be turned into `0`). On that note, also make sure your code won't crash and will run under `10` seconds on `200,000` DataFrame rows and under `1` second on `200` DataFrame rows. Your function should also not remember things between calls. You are free to explore the dataset however you like, but your submission must only import from `numpy` and `pandas`. Feel free to omit `numpy` and `pandas` imports in your submission as they are imported as `np` and `pd` respectively automatically.
"""

import numpy as np
import sklearn
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

def tstat(returns):
    returns = np.array(returns)
    return np.mean(returns)/np.std(returns,ddof=1)*np.sqrt(len(returns))

def score_trading_strategy(test_df, strategy_fn, score_fn=tstat):
    """
    test_df: pd.Dataframe where columns are named "regressor{i}" or "target{i}"
    strategy_fn: (row of test_df) -> [positions in each stock]
    score_fn: (list of returns) -> (scalar)
    """
    targets = [col for col in test_df if col.startswith("target")]
    X_df = test_df.drop(columns=targets)
    y_df = test_df[targets]

    positions = X_df.apply(strategy_fn, axis=1)
    returns = [np.dot(y_df.iloc[idx],pos) for idx,pos in enumerate(positions)]

    return score_fn(returns)

"""## Your Code Here:"""

df = pd.read_csv("http://54.89.159.39:8080/data")
df = df.drop(columns=['Unnamed: 0'])
data = df.iloc[:140].copy()
display(data)

df.head()

missing_values = data.isnull().sum()
print("Missing Values in Each Column:\n", missing_values)

# No missing values

def cap_outliers(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    # Cap the outliers
    series_capped = series.clip(lower=lower_bound, upper=upper_bound)
    return series_capped

# Apply the function to each numerical column
for column in ['regressor1', 'regressor2', 'target1', 'target2']:
    data[column] = cap_outliers(data[column])
# No values removed due to outliers

# Standardize regressors
for column in ['regressor1', 'regressor2']:
    mean = data[column].mean()
    std = data[column].std()
    data[column] = (data[column] - mean) / std
    print(f"\nStandardized {column}: Mean = {data[column].mean()}, Std = {data[column].std()}")
display(data.head())

summary_stats = data.describe()
print("Summary Statistics:\n", summary_stats)

corr_matrix = data[['regressor1', 'regressor2', 'target1', 'target2']].corr()
print("\nCorrelation Matrix:\n", corr_matrix)

import seaborn as sns
import matplotlib.pyplot as plt

# Heatmap of Correlations
plt.figure(figsize=(8,6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap')
plt.show()

# Scatter Plots between Regressors and Targets
import seaborn as sns
import matplotlib.pyplot as plt

# Scatter plot for regressor1 vs target1
plt.figure(figsize=(6,4))
sns.scatterplot(x='regressor1', y='target1', data=data)
plt.title('Regressor1 vs Target1')
plt.show()

# Scatter plot for regressor2 vs target1
plt.figure(figsize=(6,4))
sns.scatterplot(x='regressor2', y='target1', data=data)
plt.title('Regressor2 vs Target1')
plt.show()

# Scatter plot for regressor1 vs target2
plt.figure(figsize=(6,4))
sns.scatterplot(x='regressor1', y='target2', data=data)
plt.title('Regressor1 vs Target2')
plt.show()

# Scatter plot for regressor2 vs target2
plt.figure(figsize=(6,4))
sns.scatterplot(x='regressor2', y='target2', data=data)
plt.title('Regressor2 vs Target2')
plt.show()

# Distribution Plots
import seaborn as sns
import matplotlib.pyplot as plt

# Histograms with Kernel Density Estimate (KDE) for each column
for column in ['regressor1', 'regressor2', 'target1', 'target2']:
    plt.figure(figsize=(6,4))
    sns.histplot(data[column], kde=True, bins=30)
    plt.title(f'Distribution of {column}')
    plt.show()

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score


train_df = data.copy()
test_df = df.iloc[140:].copy()


# 3.1. Create Interaction Term
train_df['regressor1_regressor2'] = train_df['regressor1'] * train_df['regressor2']
test_df['regressor1_regressor2'] = test_df['regressor1'] * test_df['regressor2']

# 3.2. Create Polynomial Features (Squared Terms)
train_df['regressor1_squared'] = train_df['regressor1'] ** 2
train_df['regressor2_squared'] = train_df['regressor2'] ** 2

test_df['regressor1_squared'] = test_df['regressor1'] ** 2
test_df['regressor2_squared'] = test_df['regressor2'] ** 2


# Define the feature columns including engineered features
feature_cols = ['regressor1', 'regressor2', 'regressor1_regressor2', 'regressor1_squared', 'regressor2_squared']

# ================================
# Step 5: Model Training and Validation
# ================================

# 5.1. Split Features and Targets for Training
X_train = train_df[feature_cols]
y_train_target1 = train_df['target1']
y_train_target2 = train_df['target2']

# Split Features and Targets for Testing
X_test = test_df[feature_cols]
y_test_target1 = test_df['target1']
y_test_target2 = test_df['target2']

# 5.2. Initialize Ridge Regression Models
ridge_target1 = Ridge(alpha=0.0001)
ridge_target2 = Ridge(alpha=0.0001)

# 5.3. Train the Models on Training Data
ridge_target1.fit(X_train, y_train_target1)
ridge_target2.fit(X_train, y_train_target2)

# 5.4. Cross-Validation to Evaluate Models

# Function to compute RMSE from cross_val_score
def compute_cv_rmse(model, X, y, cv=5):
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='neg_mean_squared_error')
    rmse = np.sqrt(-cv_scores.mean())
    return rmse

# Compute Cross-Validated RMSE for Target1
cv_rmse_target1 = compute_cv_rmse(ridge_target1, X_train, y_train_target1, cv=5)
print(f"Cross-Validated RMSE for Target 1: {cv_rmse_target1:.5f}")

# Compute Cross-Validated RMSE for Target2
cv_rmse_target2 = compute_cv_rmse(ridge_target2, X_train, y_train_target2, cv=5)
print(f"Cross-Validated RMSE for Target 2: {cv_rmse_target2:.5f}")

# 5.5. Predict on Test Set
y_pred_target1 = ridge_target1.predict(X_test)
y_pred_target2 = ridge_target2.predict(X_test)

# 5.6. Calculate Test RMSE
test_rmse_target1 = mean_squared_error(y_test_target1, y_pred_target1, squared=False)
test_rmse_target2 = mean_squared_error(y_test_target2, y_pred_target2, squared=False)
print(f"Test RMSE for Target 1: {test_rmse_target1:.5f}")
print(f"Test RMSE for Target 2: {test_rmse_target2:.5f}")


# Extract coefficients and intercepts for Target 1
intercept_t1 = ridge_target1.intercept_
coef_t1 = ridge_target1.coef_

# Map coefficients to feature names for Target 1
coef_t1_dict = dict(zip(feature_cols, coef_t1))

# Extract coefficients and intercepts for Target 2
intercept_t2 = ridge_target2.intercept_
coef_t2 = ridge_target2.coef_

# Map coefficients to feature names for Target 2
coef_t2_dict = dict(zip(feature_cols, coef_t2))

"""### Example Linear Regression"""

from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(df[["regressor1"]], df["target1"])

print(model.coef_, model.intercept_)

for reg in ['regressor1', 'regressor2']:
    mean = train_df[reg].mean()
    std = train_df[reg].std()
    print(f"{reg} - Mean: {mean:.5f}, Std Dev: {std:.5f}")

from sklearn.linear_model import ElasticNet

train_df = data.copy()
test_df = df.iloc[140:].copy()


# 3.1. Create Interaction Term
train_df['regressor1_regressor2'] = train_df['regressor1'] * train_df['regressor2']

# 3.2. Create Polynomial Features (Squared Terms)
train_df['regressor1_squared'] = train_df['regressor1'] ** 2
train_df['regressor2_squared'] = train_df['regressor2'] ** 2


# Define the feature columns including engineered features
feature_cols = ['regressor1', 'regressor2', 'regressor1_regressor2', 'regressor1_squared', 'regressor2_squared']

# ================================
# Ridge Regression
# ================================

# 5.1. Split Features and Targets for Training
X_train = train_df[feature_cols]
y_train_target1 = train_df['target1']
y_train_target2 = train_df['target2']


# 5.2. Initialize Ridge Regression Models
ridge_target1 = Ridge(alpha= 120)
ridge_target2 = Ridge(alpha=120)

# 5.3. Train the Models on Training Data
ridge_target1.fit(X_train, y_train_target1)
ridge_target2.fit(X_train, y_train_target2)


# Feature columns used in the models
feature_cols = ['regressor1', 'regressor2', 'regressor1_regressor2', 'regressor1_squared', 'regressor2_squared']

# Extract coefficients and intercepts for Target 1
intercept_t1 = ridge_target1.intercept_
coef_t1 = ridge_target1.coef_

# Map coefficients to feature names for Target 1
coef_t1_dict = dict(zip(feature_cols, coef_t1))

# Extract coefficients and intercepts for Target 2
intercept_t2 = ridge_target2.intercept_
coef_t2 = ridge_target2.coef_

# Map coefficients to feature names for Target 2
coef_t2_dict = dict(zip(feature_cols, coef_t2))

# Print coefficients and intercepts for Target 1
print("Coefficients for Target 1:")
print(f"t1_intercept = {intercept_t1}")
for feature, coef in coef_t1_dict.items():
    print(f"t1_{feature} = {coef}")

# Print coefficients and intercepts for Target 2
print("\nCoefficients for Target 2:")
print(f"t2_intercept = {intercept_t2}")
for feature, coef in coef_t2_dict.items():
    print(f"t2_{feature} = {coef}")


# Lasso Model
from sklearn.linear_model import Lasso

# Define a range of alpha values for Lasso
alpha_values_lasso = np.logspace(-3, 1, 50)  # Alphas from 0.001 to 10

# Define the parameter grid for Lasso
param_grid_lasso = {'alpha': alpha_values_lasso}

# Grid Search for Target 1 (Lasso)
lasso = Lasso(max_iter=10000)
grid_search_lasso_t1 = GridSearchCV(estimator=lasso, param_grid=param_grid_lasso,
                                    scoring='neg_mean_squared_error', cv=5)

grid_search_lasso_t1.fit(X_train, y_train_target1)
best_alpha_lasso_t1 = grid_search_lasso_t1.best_params_['alpha']
print(f"\nBest alpha for Lasso Target 1: {best_alpha_lasso_t1}")

# Retrain the Lasso model with the best alpha
lasso_target1 = Lasso(alpha=best_alpha_lasso_t1, max_iter=10000)
lasso_target1.fit(X_train, y_train_target1)

# Extract coefficients and intercepts for Lasso Target 1
intercept_lasso_t1 = lasso_target1.intercept_
coef_lasso_t1 = lasso_target1.coef_
coef_lasso_t1_dict = dict(zip(feature_cols, coef_lasso_t1))

# Print coefficients and intercepts for Lasso Target 1
print("\nLasso Coefficients for Target 1:")
print(f"t1_intercept = {intercept_lasso_t1}")
for feature, coef in coef_lasso_t1_dict.items():
    print(f"t1_{feature} = {coef}")

# Grid Search for Target 2 (Lasso)
lasso = Lasso(max_iter=10000)
grid_search_lasso_t2 = GridSearchCV(
    estimator=lasso,
    param_grid=param_grid_lasso,
    scoring='neg_mean_squared_error',
    cv=5
)
grid_search_lasso_t2.fit(X_train, y_train_target2)
best_alpha_lasso_t2 = grid_search_lasso_t2.best_params_['alpha']
print(f"\nBest alpha for Lasso Target 2: {best_alpha_lasso_t2}")

# Retrain the Lasso model with the best alpha for Target 2
lasso_target2 = Lasso(alpha=best_alpha_lasso_t2, max_iter=10000)
lasso_target2.fit(X_train, y_train_target2)

# Extract coefficients and intercepts for Lasso Target 2
intercept_lasso_t2 = lasso_target2.intercept_
coef_lasso_t2 = lasso_target2.coef_
coef_lasso_t2_dict = dict(zip(feature_cols, coef_lasso_t2))

# Print coefficients and intercepts for Lasso Target 2
print("\nLasso Coefficients for Target 2:")
print(f"t2_intercept = {intercept_lasso_t2}")
for feature, coef in coef_lasso_t2_dict.items():
    print(f"t2_{feature} = {coef}")

# Elastic net regressoion

# Define a range of alpha values and l1_ratio values for Elastic Net
alpha_values_enet = np.logspace(-3, 1, 50)  # Alphas from 0.001 to 10
l1_ratio_values = np.linspace(0, 1, 10)     # l1_ratio from 0 (Ridge) to 1 (Lasso)

# Define the parameter grid for Elastic Net
param_grid_enet = {'alpha': alpha_values_enet, 'l1_ratio': l1_ratio_values}


# Grid Search for Target 1 (Elastic Net)
enet = ElasticNet(max_iter=10000)
grid_search_enet_t1 = GridSearchCV(
    estimator=enet,
    param_grid=param_grid_enet,
    scoring='neg_mean_squared_error',
    cv=5
)
grid_search_enet_t1.fit(X_train, y_train_target1)

# Get the best parameters for Elastic Net Target 1
best_params_enet_t1 = grid_search_enet_t1.best_params_
best_alpha_enet_t1 = best_params_enet_t1['alpha']
best_l1_ratio_t1 = best_params_enet_t1['l1_ratio']

# Retrain the Elastic Net model with the best parameters
enet_target1 = ElasticNet(alpha=100, l1_ratio=best_l1_ratio_t1, max_iter=10000)
enet_target1.fit(X_train, y_train_target1)

# Extract coefficients and intercepts for Elastic Net Target 1
intercept_enet_t1 = enet_target1.intercept_
coef_enet_t1 = enet_target1.coef_
coef_enet_t1_dict = dict(zip(feature_cols, coef_enet_t1))

# Print coefficients and intercepts for Elastic Net Target 1
print("\nElastic Net Coefficients for Target 1:")
print(f"t1_intercept = {intercept_enet_t1}")
for feature, coef in coef_enet_t1_dict.items():
    print(f"t1_{feature} = {coef}")

# Grid Search for Target 2 (Elastic Net)
enet = ElasticNet(max_iter=10000)
grid_search_enet_t2 = GridSearchCV(
    estimator=enet,
    param_grid=param_grid_enet,
    scoring='neg_mean_squared_error',
    cv=5
)
grid_search_enet_t2.fit(X_train, y_train_target2)

# Get the best parameters for Elastic Net Target 2
best_params_enet_t2 = grid_search_enet_t2.best_params_
best_alpha_enet_t2 = best_params_enet_t2['alpha']
best_l1_ratio_t2 = best_params_enet_t2['l1_ratio']

# Retrain the Elastic Net model with the best parameters
enet_target2 = ElasticNet(alpha=100, l1_ratio=best_l1_ratio_t2, max_iter=10000)
enet_target2.fit(X_train, y_train_target2)

# Extract coefficients and intercepts for Elastic Net Target 2
intercept_enet_t2 = enet_target2.intercept_
coef_enet_t2 = enet_target2.coef_
coef_enet_t2_dict = dict(zip(feature_cols, coef_enet_t2))

# Print coefficients and intercepts for Elastic Net Target 2
print("\nElastic Net Coefficients for Target 2:")
print(f"t2_intercept = {intercept_enet_t2}")
for feature, coef in coef_enet_t2_dict.items():
    print(f"t2_{feature} = {coef}")

def strategy(row):
    import numpy as np
    import pandas as pd


    # Hard-coded coefficients for Target 1
    t1_intercept = 0.005447410225656136
    t1_regressor1 = -0.0
    t1_regressor2 = 0.0
    t1_regressor1_regressor2 = 0.0
    t1_regressor1_squared = 0.0
    t1_regressor2_squared = -0.0


    # Hard-coded coefficients for Target 2
    t2_intercept = -0.006483134152720453
    t2_regressor1 = 0.0
    t2_regressor2 = -0.0
    t2_regressor1_regressor2 = -0.0
    t2_regressor1_squared = -0.0
    t2_regressor2_squared = -0.0

    # Extract regressor values
    reg1 = row["regressor1"]
    reg2 = row["regressor2"]

    # Feature engineering
    reg1_reg2 = reg1 * reg2
    reg1_squared = reg1 ** 2
    reg2_squared = reg2 ** 2

    # Predict target returns for Target 1
    predicted_target1 = (
        t1_intercept +
        t1_regressor1 * reg1 +
        t1_regressor2 * reg2 +
        t1_regressor1_regressor2 * reg1_reg2 +
        t1_regressor1_squared * reg1_squared +
        t1_regressor2_squared * reg2_squared
    )

    # Predict target returns for Target 2
    predicted_target2 = (
        t2_intercept +
        t2_regressor1 * reg1 +
        t2_regressor2 * reg2 +
        t2_regressor1_regressor2 * reg1_reg2 +
        t2_regressor1_squared * reg1_squared +
        t2_regressor2_squared * reg2_squared
    )

    # Decide on positions based on predicted returns
    position_t1 = np.sign(predicted_target1)
    position_t2 = np.sign(predicted_target2)

    return [position_t1, position_t2]

t_stat = score_trading_strategy(test_df, strategy)
print(f"T-Statistic of PNL: {t_stat:.5f}")

# Import necessary modules
from sklearn.model_selection import GridSearchCV
import numpy as np

# Define a range of alpha values to test
alpha_values = np.logspace(-3, 3, 50)  # Alphas from 0.001 to 1000

# Define the parameter grid
param_grid = {'alpha': alpha_values}

# ================================
# Grid Search for Target 1
# ================================

# Initialize Ridge Regression model
ridge = Ridge()

# Perform grid search with cross-validation for Target 1
grid_search_t1 = GridSearchCV(estimator=ridge, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5)
grid_search_t1.fit(X_train, y_train_target1)

# Get the best alpha value for Target 1
best_alpha_t1 = grid_search_t1.best_params_['alpha']
print(f"Best alpha for Target 1: {best_alpha_t1}")

# Retrain the model with the best alpha
ridge_target1 = Ridge(alpha=best_alpha_t1)
ridge_target1.fit(X_train, y_train_target1)

# Extract coefficients and intercepts for Target 1
intercept_t1 = ridge_target1.intercept_
coef_t1 = ridge_target1.coef_
coef_t1_dict = dict(zip(feature_cols, coef_t1))

# Print updated coefficients and intercepts for Target 1
print("\nUpdated Coefficients for Target 1:")
print(f"t1_intercept = {intercept_t1}")
for feature, coef in coef_t1_dict.items():
    print(f"t1_{feature} = {coef}")

# ================================
# Grid Search for Target 2
# ================================

# Perform grid search with cross-validation for Target 2
grid_search_t2 = GridSearchCV(estimator=ridge, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5)
grid_search_t2.fit(X_train, y_train_target2)

# Get the best alpha value for Target 2
best_alpha_t2 = grid_search_t2.best_params_['alpha']
print(f"\nBest alpha for Target 2: {best_alpha_t2}")

# Retrain the model with the best alpha
ridge_target2 = Ridge(alpha=best_alpha_t2)
ridge_target2.fit(X_train, y_train_target2)

# Extract coefficients and intercepts for Target 2
intercept_t2 = ridge_target2.intercept_
coef_t2 = ridge_target2.coef_
coef_t2_dict = dict(zip(feature_cols, coef_t2))

# Print updated coefficients and intercepts for Target 2
print("\nUpdated Coefficients for Target 2:")
print(f"t2_intercept = {intercept_t2}")
for feature, coef in coef_t2_dict.items():
    print(f"t2_{feature} = {coef}")

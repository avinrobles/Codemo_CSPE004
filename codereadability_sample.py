# -*- coding: utf-8 -*-
"""codereadability_sample.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Py16UUgJe-CmTVkOGuVLgsqyXkGBEvf0

INSTALL & IMPORT NECESSARY LIBRARIES
"""

!pip install streamlit
!pip install tensorflow
!pip install --upgrade pyngrok

import numpy as np
import pandas as pd
import re
import ast
import streamlit as st
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,r2_score, explained_variance_score, accuracy_score, precision_score, recall_score, f1_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping

"""PREPROCESSING USING THE DATASET - PYTHON"""

# Code based from Maheshwari (2023)
df = pd.read_csv('data_python.csv')

# Remove the "class Solution:/n"
df['python_solutions'] = df['python_solutions'].str.replace(r'^class Solution:\n', '', regex=True)

# Save the updated dataset (optional)
df.to_csv('updated_dataset.csv', index=False)

df.head()

def count_comments(code):
 # Count the number of comments using a regular expression
    comments = re.findall(r'#.*|(\'\'\'[\s\S]*?\'\'\'|\"\"\"[\s\S]*?\"\"\`)|```[\s\S]*?```', code)
    return len(comments)

df['comments'] = df['python_solutions'].apply(count_comments)

def cyclomatic_complexity(code):
    decision_points = len(re.findall(r"(if|elif|while|for)\s+.*:", code, re.IGNORECASE))
    exits = len(re.findall(r"(return|break|continue)\b", code, re.IGNORECASE))
    complexity = decision_points + 1 - exits
    return complexity

df['cyclomatic_complexity'] = df['python_solutions'].apply(lambda x: cyclomatic_complexity(x))

def count_indents(code):
    lines = code.split('\n')
    num_indents = 0
    for line in lines:
        num_indents += line.count('    ')  # Assuming each indent is represented by four spaces
    return num_indents

def calculate_rounded_ratio(row):
    return math.ceil(row['num_of_indents'] / row['num_of_lines'])

def count_loops(code):
    loop_keywords = ['for', 'while', 'if']
    count = sum(code.lower().count(keyword) for keyword in loop_keywords)
    return count

def count_identifiers(code):
    identifiers = [':', '=', '==', '<', '>', ',']
    count = sum(code.lower().count(keyword) for keyword in identifiers)
    return count

"""CNN TRAINING & TESTING"""

# Assuming df is already defined and contains the necessary columns
X = df[['num_of_lines', 'code_length', 'comments', 'cyclomatic_complexity', 'indents', 'loop_count', 'identifiers']]
y = df['readability']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X.values, y, test_size=0.2, random_state=42)

# Reshape the data for CNN (add a sequence dimension)
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)  # Shape: (batch_size, 7, 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)      # Shape: (batch_size, 7, 1)

# Define the enhanced CNN model
model = Sequential()

# Input layer
model.add(Conv1D(filters=128, kernel_size=1, activation='relu', padding='same', input_shape=(X_train.shape[1], 1)))  # kernel_size=1, padding='same'
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=1))  # No pooling to avoid shrinking sequence length
model.add(Dropout(0.3))

# Hidden layers
model.add(Conv1D(filters=256, kernel_size=1, activation='relu', padding='same'))  # kernel_size=1, padding='same'
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=1))  # No pooling to avoid shrinking sequence length
model.add(Dropout(0.4))

model.add(Conv1D(filters=512, kernel_size=1, activation='relu', padding='same'))  # kernel_size=1, padding='same'
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=1))  # No pooling to avoid shrinking sequence length
model.add(Dropout(0.5))

# Flatten and fully connected layers
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.5))

model.add(Dense(128, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.4))

model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.3))

# Output layer for regression
model.add(Dense(1))

# Compile the model
optimizer = Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='mean_absolute_error', metrics=['mae'])

# Callbacks for better training
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.0001)
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Train the model
history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[reduce_lr, early_stopping]
)

# Evaluate the model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: {mae}')

# Predict readability for user input
user_input = """class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if (i != j and nums[i] + nums[j] == target):
                    return [i, j]
        return []"""

user_features = np.array([[len(user_input.split('\n')), len(user_input),
                           count_comments(user_input), cyclomatic_complexity(user_input),
                           count_indents(user_input), count_loops(user_input),
                           count_identifiers(user_input)]])

user_features = user_features.reshape(1, user_features.shape[1], 1)  # Reshape to (1, 7, 1)
user_score = model.predict(user_features)
print(f'Predicted Readability Score for User Input: {user_score[0][0]:.2f}')

# Predict on the test set
y_pred = model.predict(X_test)

# Calculate regression metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
explained_variance = explained_variance_score(y_test, y_pred)

print(f'Mean Squared Error (MSE): {mse:.4f}')
print(f'R-squared (R²): {r2:.4f}')
print(f'Explained Variance Score: {explained_variance:.4f}')

# Bin the readability scores into categories (e.g., low, medium, high)
bins = np.linspace(min(y), max(y), 4)  # Create 3 bins
y_binned = np.digitize(y, bins)
y_test_binned = np.digitize(y_test, bins)
y_pred_binned = np.digitize(y_pred, bins)

# Calculate classification metrics
accuracy = accuracy_score(y_test_binned, y_pred_binned)
precision = precision_score(y_test_binned, y_pred_binned, average='weighted')
recall = recall_score(y_test_binned, y_pred_binned, average='weighted')
f1 = f1_score(y_test_binned, y_pred_binned, average='weighted')

print(f'Accuracy: {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1-score: {f1:.4f}')
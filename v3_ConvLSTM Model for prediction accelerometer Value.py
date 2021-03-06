# -*- coding: utf-8 -*-
"""V3_Model for Accelerometer classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17oavHnzv3gUzOVIu3kE75X4q5MEovbTG

#Using CNN_LSTM for Time Series Classification also Prediction 
References: 
https://arxiv.org/abs/1411.4389
https://www.mdpi.com/1424-8220/16/1/115/html

Combine Deel CNN and LSTM
![alt_text](https://3qeqpr26caki16dnhd19sv6by6v-wpengine.netdna-ssl.com/wp-content/uploads/2018/07/Depiection-of-CNN-LSTM-Model-for-Activity-Recognition.png)

LSTM network models are a type of recurrent neural network that are able to learn and remember over long sequences of input data. They are intended for use with data that is comprised of long sequences of data, up to 200 to 400 time steps.

The CNN model learns to map a given window of signal data from each axis Accelerometer where the model reads across each window of data and prepares an internal representation of the window.

The CNN LSTM model will read subsequences of the main sequence in as blocks, extract features from each block, then allow the LSTM to interpret the features extracted from each block.

### IMPORT LIBRARY
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf  
from sklearn import metrics
from numpy import mean
from numpy import std #(standard deviation)
from tensorflow import keras
import os
from __future__ import print_function

#also Using KERAS FOR RNN (LSTM Cell)
from keras.models import Sequential 
from keras.layers import Dense
import seaborn as sns
from scipy import stats
from pylab import rcParams
from sklearn import metrics
from sklearn.model_selection import train_test_split

#import for CNN_LSTM

from numpy import dstack
from keras.layers import Dropout,Flatten, Reshape,Dense, TimeDistributed
from keras.layers import LSTM
from keras.layers.convolutional import Conv2D,Conv1D
from keras.layers.convolutional import MaxPooling1D, MaxPooling2D
from keras.utils import to_categorical
from keras.utils import np_utils
from __future__ import absolute_import, division, print_function, unicode_literals
from sklearn.metrics import classification_report
#import for filter
from scipy import signal

!pip install h5py pyyaml
!pip install tf_nightly

"""### IMPORT DATASET"""

from google.colab import files 
upload = files.upload()

"""### DATA PREPROCESSING

**Low Pass Filter**
"""

dataset= pd.read_csv('VeryHIGH_movement.csv')
dataset

#@author: Yi Yu

D = 'processingdataset_Disaster_prevention.csv'   

def butter_lowpass(cutoff, nyq_freq, order=4):
    normal_cutoff = float(cutoff) / nyq_freq
    b, a = signal.butter(order, normal_cutoff, btype='lowpass')
    return b, a

def butter_lowpass_filter(data, cutoff_freq, nyq_freq, order=4):
    b, a = butter_lowpass(cutoff_freq, nyq_freq, order=order)
    y = signal.filtfilt(b, a, data)
    return y
    
acceler = ['x1','y1','z1','x2','y2','z2']
    

data = pd.read_csv('VeryHIGH_movement.csv')
sample_rate = 50                                                                                     

for i in acceler :

  x = data[i]
  signal_length = len(x)

  # Filter signal x, result stored to y: 
  cutoff_frequency = 0.5                                                                           ######### CAN be CHANGED
  y = butter_lowpass_filter(x, cutoff_frequency, sample_rate/2)

  # Difference acts as a special high-pass from a reversed butterworth filter. 
  diff = np.array(x)-np.array(y)

  plt.figure(figsize = (6,3))  
  plt.plot(x, color='red', label="Original signal, {} samples".format(signal_length))

  plt.figure(figsize = (6,3))
  plt.plot(y, color='blue', label="Filtered low-pass with cutoff frequency of {} Hz".format(cutoff_frequency))

  plt.figure(figsize = (6,3))
  plt.plot(diff, color='gray', label="What has been removed")

  plt.legend()
  plt.show()

df= pd.DataFrame(data=y)
df.to_csv('low_pass_filter.csv')
     
  # Visualize

"""**Moving Avrage**"""

#@author: Yi-Yu

import warnings
from scipy import signal
import math

data = pd.read_csv('low_pass_filter.csv')

X = data['0']
     
window=[7]                                                 ######### CAN BE CHANGED

for i in window:
    rolling = X.rolling(window=i)                                   
    rolling_mean = rolling.mean()
    True_rolling_mean1 = rolling_mean
    
    for j in range(0,i):
        
        True_rolling_mean1.iloc[j] = X[j]
        
plt.figure(figsize=(6,3))  
plt.plot(True_rolling_mean1[:])
plt.show()

df= pd.DataFrame(data=True_rolling_mean1)
df.to_csv('after_moving_average.csv')

"""### LABEL DATA"""

dataset= pd.read_csv('processingdatafilter1.csv')
dataset = dataset.iloc[:, 1:3]
dataset.size

dataset.head()

#Look Backstep to create the dataset (Decreasing or increasing number of step depend of the raw dataset)
look_back_step = 10
total_size_of_dataset = dataset.size-look_back_step
threshold = 0.005
threshold1=0.04
threshold2=0.1

memory_of_label= list()
# we should adding more threshold to our model

for i in range(total_size_of_dataset):
  
  if(abs(dataset[look_back_step+i])-abs(dataset[i])>=threshold):
    memory_of_label.append('slow_movement')
  elif((abs(dataset[look_back_step+i])-abs(dataset[i])>=threshold1):
    memory_of_label.append('high')
  elif((abs(dataset[look_back_step+i])-abs(dataset[i])>=threshold2):      
    memory_of_label.append('very_high')
  else: 
    memory_of_label.append('stable')

#Reviewing data and saving the file 
print(memory_of_label)
df= pd.DataFrame(data=memory_of_label)
df.to_csv('label.csv')
!ls

"""### IMPORT DATA"""

# load a single file as a numpy array

df = pd.read_csv('processingdatafilter1.csv')
df.head(10)

"""### PREPARING & PROCESSING INPUT TO MODEL

**Transfer All data to Numeric Before Feeding to model**
"""

from sklearn import preprocessing
# Define column name of the label vector

LABEL = 'LableEncoder'
# Transform the labels from String to Integer via LabelEncoder
le = preprocessing.LabelEncoder()
# Add a new column to the existing DataFrame with the encoded values
df[LABEL] = le.fit_transform(df['Lable'].values.ravel())
df[LABEL]


'''
#The Simple way label by ourself

# Classify How many special object
df["Lable"].unique()
# Taking all the unique data to abitrary number 
df["Lable"].astype("category").cat.codes
#Map the dataste into dictionary
Lable_class_dict={"stable":1, "movement":2, "highly movement ": 3, "SLOWMOVEMNT":4}
# ENCODE THEM INTO THE NUMBER
df['Lable'] = df['Lable'].map(Lable_class_dict)
Label= 'Lable'
df['Lable']
df.head()
'''

"""## ** Look at my data**
**[1]Cleaning Data**
**[2] Inspect Data to See Corelation of Each Column & Statistic The data 
**[3]Split Data {Testing, Training}**
**[4] Normaliz The Data to 0---->1**

- How many rows are in the dataset?
- How many columns are in this dataset?
- What data types are the columns?
- Is the data complete? Are there nulls? Do we have to infer values?
- What is the definition of these columns?
- What are some other caveats to the data?
"""

# CLEAN DATA
  #The Dataset contains a few Unkowns values 
df = df.dropna()
df.isna().sum()

from sklearn.utils import shuffle
df = shuffle(df)
df.head()

#SPLITING DATASET TESTING & TRAINING
train_dataset = df.sample(frac=0.8,random_state=0)
test_dataset = df.drop(train_dataset.index)

#INSPECT THE DATA
sns.pairplot(train_dataset[["LableEncoder","AcX", "AcY", "AcZ", ]], diag_kind="kde")
#kde smooth histogram

df.head()

#STATIC DATASET 
train_stats = train_dataset.describe()
train_stats.pop("LableEncoder")
train_stats = train_stats.transpose()
train_stats

#NORMALIZE THE DATASET
'''
def norm(x):
  return (x - train_stats['mean']) / train_stats['std']
normed_train_data = norm(train_dataset)
normed_test_data = norm(test_dataset)

'''

# Surpress warning for next 3 operation
pd.options.mode.chained_assignment = None  # default='warn'
train_dataset['AcX'] = train_dataset['AcX'] /train_dataset['AcX'].max()
train_dataset['AcY'] =train_dataset['AcY'] /train_dataset['AcY'].max()
train_dataset['AcZ'] =train_dataset['AcZ'] / train_dataset['AcZ'].max()
# Round numbers
train_dataset = train_dataset.round({'AcX': 5, 'AcY': 5, 'AcZ': 5})

df['AcZ'] = df['AcZ'].astype('float32')
df['AcX'] = df['AcX'].astype('float32')
df['AcY'] = df['AcY'].astype('float32')
df['LableEncoder'] = df['LableEncoder'].astype('float32')
train_dataset.head()

"""### RESHAPE DATA INTO SEGMENT AND 3DIMENSION
with 80 steps (see constant defined earlier). Taking into consideration the 20 Hz sampling rate, this equals to 4 second time intervals (calculation: 0.05 * 80 = 4). Besides reshaping the data, the function will also separate the features (x-acceleration, y-acceleration, z-acceleration) and the labels.
"""

# The number of steps within one time segment
TIME_PERIODS = 2
# The steps to take from one segment to the next; if this value is equal to
# TIME_PERIODS, then there is no overlap between the segments
STEP_DISTANCE = 2


def create_segments_and_labels(df, time_steps, step, label_name):

    # x, y, z acceleration as features
    N_FEATURES = 3
    # Number of steps to advance in each iteration (for me, it should always
    # be equal to the time_steps in order to have no overlap between segments)
    # step = time_steps
    segments = []
    labels = []
    for i in range(0, len(df) - time_steps, step):
        xs = df['AcX'].values[i: i + time_steps]
        ys = df['AcY'].values[i: i + time_steps]
        zs = df['AcZ'].values[i: i + time_steps]
        
        # Retrieve the most often used label in this segment
        
  # What is exactly the lable here findout to make sure Y lable = X train 
        label = stats.mode(df['LableEncoder'][i: i + time_steps])[0][0]
        segments.append([xs, ys, zs])
        labels.append(label)

  # Bring the segments into a better shape
    reshaped_segments = np.asarray(segments, dtype= np.float32).reshape(-1, time_steps, N_FEATURES)
    labels = np.asarray(labels)

    return reshaped_segments, labels

x_train, y_train = create_segments_and_labels(train_dataset,
                                              TIME_PERIODS,
                                              STEP_DISTANCE,
                                           train_dataset)

# Here The Shape of X training and Y lable has to the same length if not something wrong 
print('x_train shape: ', x_train.shape)
print(x_train.shape[0], 'training samples')
print('y_train shape: ', y_train.shape)

num_time_periods, num_axis = x_train.shape[1], x_train.shape[2]

num_classes = le.classes_.size
print(list(le.classes_))

# Set input & output dimensions
input_shape = (num_time_periods*3)
x_train = x_train.reshape(x_train.shape[0], input_shape)
print('x_train shape:', x_train.shape)
print('input_shape:', input_shape)

y_train_hot = np_utils.to_categorical(y_train)
print('New y_train shape: ', y_train_hot.shape)

x_train = x_train.astype('float32')
y_train = y_train.astype('float32')

"""The new method feeding the data to model

### DEFINE CNN_LSTM MODEL

![alt](https://www.researchgate.net/profile/Tao_Jiang10/publication/320441691/figure/download/fig2/AS:631629156454418@1527603534354/A-fully-connected-feedforward-NN-architecture-where-all-neurons-between-adjacent-layers.png)
"""

model = Sequential()
# Remark: since coreml cannot accept vector shapes of complex shape like
# prior feeding it into the network
model.add(Reshape((TIME_PERIODS, 3), input_shape=(input_shape,)))
model.add(Dense(100, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Flatten())
model.add(Dense(num_classes, activation='softmax'))
print(model.summary())

"""### TRAINING MODEL"""

from keras.callbacks import History 
history = History()
callbacks_list = [
    keras.callbacks.ModelCheckpoint(
        filepath='best_model.{epoch:02d}-{val_loss:.2f}.h5',
        monitor='val_loss', save_best_only=True),
    keras.callbacks.EarlyStopping(monitor='acc', patience=100), history]


model.compile(loss='categorical_crossentropy',
                optimizer='adam', metrics=['accuracy'])

# Hyper-parameters
BATCH_SIZE =30
EPOCHS = 100

# Enable validation to use ModelCheckpoint and EarlyStopping callbacks.
history = model.fit(x_train,
                      y_train_hot,
                      batch_size=BATCH_SIZE,
                      epochs=EPOCHS,
                      callbacks=callbacks_list,
                      validation_split=0.2,
                      verbose=1)

"""**SECOND WAY VISUALIZE ALL TRAINING TESTING MODEL BETTER**
Visualize the model's training progress using the stats stored in the `history` object.

**CHECKING GENERALIZATION**
"""

hist = pd.DataFrame(history.history)
hist['epochs'] = history.epoch
hist.tail()

plt.figure(figsize=(10, 8))
plt.plot(history.history['acc'], 'r', label='Accuracy of training data')
plt.plot(history.history['val_acc'], 'b', label='Accuracy of validation data')
plt.plot(history.history['loss'], 'r--', label='Loss of training data')
plt.plot(history.history['val_loss'], 'b--', label='Loss of validation data')
plt.title('Model Accuracy and Loss')
plt.ylabel('Accuracy and Loss')
plt.xlabel('Training Epoch')
plt.ylim(0)
plt.legend()
plt.show()

LABELS = ['Stable', 'Slow', 'High_move', 'Very_High']
from sklearn.metrics import confusion_matrix
def show_confusion_matrix(validations, predictions):
  
    matrix = metrics.confusion_matrix(validations, predictions)
    plt.figure(figsize=(6, 4))
    sns.heatmap(matrix,
                cmap='coolwarm',
                linecolor='white',
                linewidths=1,
                xticklabels=LABELS,
                yticklabels=LABELS,
                annot=True,
                fmt='d')
    plt.title ('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()

# Print confusion matrix for training data
y_pred_train = model.predict(x_train)
# Take the class with the highest probability from the train predictions
max_y_pred_train = np.argmax(y_pred_train, axis=1)
max_y_train = np.argmax(y_train_hot, axis=1)
show_confusion_matrix(max_y_train,max_y_pred_train)
#print(classification_report(y_train, max_y_pred_train))


print(y_pred_train)
print(max_y_pred_train)
plt.plot(max_y_pred_train)
plt.plot(y_pred_train)
plt.show()

# The number of steps within one time segment
TIME_PERIODS = 2
# The steps to take from one segment to the next; if this value is equal to
# TIME_PERIODS, then there is no overlap between the segments
STEP_DISTANCE = 3


def create_segments_and_labels(df, time_steps, step, label_name):

    # x, y, z acceleration as features
    N_FEATURES = 3
    # Number of steps to advance in each iteration (for me, it should always
    # be equal to the time_steps in order to have no overlap between segments)
    # step = time_steps
    segments = []
    labels = []
    for i in range(0, len(df) - time_steps, step):
        xs = df['AcX'].values[i: i + time_steps]
        ys = df['AcY'].values[i: i + time_steps]
        zs = df['AcZ'].values[i: i + time_steps]
        
        # Retrieve the most often used label in this segment
        
  # What is exactly the lable here findout to make sure Y lable = X train 
        label = stats.mode(df['LableEncoder'][i: i + time_steps])[0][0]
        segments.append([xs, ys, zs])
        labels.append(label)

  # Bring the segments into a better shape
    reshaped_segments = np.asarray(segments, dtype= np.float32).reshape(-1, time_steps, N_FEATURES)
    labels = np.asarray(labels)

    return reshaped_segments, labels

x_test, y_test= create_segments_and_labels(test_dataset,
                                              TIME_PERIODS,
                                              STEP_DISTANCE,
                                           test_dataset)

print(x_test.shape)
print(y_test.shape)

num_time_periods, num_axis = x_test.shape[1], x_test.shape[2]
num_classes = le.classes_.size
print(list(le.classes_))

num_time_periods, num_sensor = x_test.shape[1], x_test.shape[2]

input_shape1 = num_time_periods*3
x_test = x_test.reshape(x_test.shape[0], input_shape1)
print('x_test shape:', x_test.shape)
print('input_shape1:', input_shape1)

y_test_hot = np_utils.to_categorical(y_test, num_classes)
print('New y_test shape: ', y_test_hot.shape)

y_test = y_test.astype('float32')
x_test= x_test.astype('float32')

"""### CLASSIFICATION MODEL"""

from sklearn.metrics import confusion_matrix
LABELS = ['Stable', 'Slow', 'High_move', 'Very_High']
def show_confusion_matrix(validations, predictions):

    matrix = metrics.confusion_matrix(validations, predictions)
    plt.figure(figsize=(6, 4))
    sns.heatmap(matrix,
                cmap='coolwarm',
                linecolor='white',
                linewidths=1,
                xticklabels=LABELS,
                yticklabels=LABELS,
                annot=True,
                fmt='d')
    plt.title ('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()
    
y_pred_test = model.predict(x_test)
# Take the class with the highest probability from the test predictions
max_y_pred_test = np.argmax(y_pred_test, axis=1)

max_y_test = np.argmax(y_test_hot, axis=1)
show_confusion_matrix(max_y_test, max_y_pred_test)
print(classification_report(max_y_test, max_y_pred_test))

"""# PREDICTION MODEL

### Prediction With LSTM-- CNN Model
"""

from google.colab import files 
upload = files.upload()

df=pd.read_csv('AcZ.csv')
df.head()

df.values.shape

train_dataset = df.sample(frac=0.8,random_state=0)
test_dataset = df.drop(train_dataset.index)
train_dataset.shape

x_train = train_dataset
y_train= test_dataset

# Here The Shape of X training and Y lable has to the same length if not something wrong 
print('x_train shape: ', x_train.shape)
print(x_train.shape[0], 'training samples')
print('y_train shape: ', y_train.shape)

x_train= x_train.values.ravel()
x_train.shape

def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the sequence
		if end_ix > len(sequence)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

from numpy import array
# choose a number of time steps
n_steps = 4
# split into samples
X, y = split_sequence(x_train, n_steps)

X.shape

# Creating the input Shape with 4 Dimension 
n_features = 1
n_seq = 2
n_steps = 2
X = X.reshape((X.shape[0], n_seq, n_steps, n_features))
X.shape

"""**DEFINE CNN_LSTM Model**"""



"""![alt](https://ai2-s2-public.s3.amazonaws.com/figures/2017-08-08/dd026816de81029934bd4481f209eed4ff439fbe/2-Figure1-1.png)"""

#Define the Model 
model = Sequential()
model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1, activation='relu'), input_shape=(None, n_steps, n_features)))
model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
model.add(TimeDistributed(Flatten()))
model.add(LSTM(100, activation='relu'))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')



#adding Check point and history to review the model accuracy 
# include the epoch in the file name. (uses `str.format`)
from keras.callbacks import History 
history = History()
checkpoint_path = "training_1.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

cp_callback = [tf.keras.callbacks.ModelCheckpoint(
    checkpoint_path, verbose=1, save_weights_only=True,period=10, ),
               keras.callbacks.EarlyStopping(monitor='loss', patience=20), history]


history = model.fit(X, y, callbacks = cp_callback, epochs=50, verbose=0)

hist = pd.DataFrame(history.history)
hist['epochs'] = history.epoch
hist.tail()

plt.figure(figsize=(10, 8))

plt.plot(history.history['loss'], 'r--', label='Loss of training data')


plt.ylabel(' Loss Value')
plt.xlabel('Training Epoch')
plt.ylim(0)
plt.legend()
plt.show()

x_test= test_dataset
x_test.shape

x_test= x_test.values.ravel()
x_test.shape

# choose a number of time steps
n_steps = 4
# split into samples
x_test, y = split_sequence(x_test, n_steps)
x_test.shape

# Creating the input Shape with 4 Dimension 
n_features = 1
n_seq = 2
n_steps = 2
x_input = x_test.reshape((x_test.shape[0], n_seq, n_steps, n_features))
predict_result=  model.predict(x_input, verbose=0)
predict_result.shape

x_input

predict_result

plt.figure(figsize = (10,8))
plt.plot(predict_result, 'r', label='Loss of training data')

plt.figure(figsize = (10,8))
plt.plot(x_test)
plt.show()

hist = pd.DataFrame(history.history)
hist['epochs'] = history.epoch
hist.tail()
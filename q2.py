# -*- coding: utf-8 -*-
"""q2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1a_sLEVtKeLcVu9k45bXJ93sxRNSed2co
"""

from tensorflow.keras.datasets import cifar10
import numpy as np
from tensorflow.keras.utils import to_categorical

(X_train, y_train), (_,_) = cifar10.load_data()

X_train = (X_train.astype('float32') - 127.5) / 127.5
y_train = y_train.flatten()
y_train = to_categorical(y_train, 10)

from tensorflow.keras import models, layers

def build_generator() :
  model = models.Sequential([
      layers.Dense(8*8*128, activation = 'relu', input_dim = 100 + 10),
      layers.Reshape((8,8,128)),
      layers.Conv2DTranspose(128, kernel_size = 4, strides = 2, padding = 'same', activation = 'relu'),
      layers.BatchNormalization(),
      layers.Conv2DTranspose(32, kernel_size = 4, strides = 2, padding = 'same', activation = 'relu'),
      layers.BatchNormalization(),
      layers.Conv2D(3, kernel_size = 3, padding = 'same', activation = 'tanh')

  ])

  return model

def build_discriminator() :
  model = models.Sequential([
      layers.Conv2D(64, kernel_size = 4, strides = 2, padding = 'same', activation = 'relu'),
      layers.Conv2D(128, kernel_size = 4, strides = 2, padding = 'same', activation = 'relu'),
      layers.Flatten(),
      layers.Dense(128, activation = 'relu'),
      layers.Dense(1, activation = 'sigmoid')
  ])

  return model

generator = build_generator()
discriminator = build_discriminator()

discriminator.compile(optimizer = 'adam', loss ='binary_crossentropy', metrics = ['accuracy'])


noise_input = layers.Input(shape = (100,))
label_input = layers.Input(shape = (10,))
combined_input = layers.Concatenate()([noise_input, label_input])
generated_image = generator(combined_input)
gan_output = discriminator(generated_image)
gan = models.Model([noise_input,label_input], gan_output)

gan.compile(optimizer = 'adam', loss ='binary_crossentropy')

epochs = 10
batch_size = 64

for epoch in range(epochs) :
  idx = np.random.randint(0, X_train.shape[0], batch_size)
  real_image = X_train[idx]
  real_labels = y_train[idx]

  noise = np.random.normal(0, 1, (batch_size, 100))
  fake_images = generator.predict(np.concatenate([noise, real_labels], axis = 1))

  real_y = np.ones((batch_size, 1))
  fake_y = np.zeros((batch_size, 1))

  d_lossr = discriminator.train_on_batch(real_image, real_y)
  d_lossf = discriminator.train_on_batch(fake_images, fake_y)

  noise = np.random.normal(0, 1, (batch_size, 100))
  gan_loss = gan.train_on_batch([noise, real_labels], np.ones((batch_size,1)))

class_label = 3
noise = np.random.normal(0,1,(1,100))
y = [class_label]
y = to_categorical(y, num_classes = 10)
combined_input = np.concatenate([noise, y], axis = 1)
image = generator.predict(combined_input)

import matplotlib.pyplot as plt
plt.imshow((image[0] * 127.5 + 127.5).astype(np.uint8))
plt.show()
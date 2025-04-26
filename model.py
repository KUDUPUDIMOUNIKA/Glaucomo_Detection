import os
import numpy as np
import cv2
import io
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils import class_weight


tf.config.run_functions_eagerly(True)

class GlaucomaModel:
    def __init__(self, model_path=None):
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)
            print("[INFO] Loaded trained model from disk.")
        else:
            self.model = self._build_model()
            print("[INFO] Initialized new model.")

    def _build_model(self, input_shape=(256, 256, 3)):
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(256, activation='relu'),
            Dropout(0.5),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer=Adam(learning_rate=0.0001),
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model

    def train(self, train_dir, val_dir, epochs=10, batch_size=32):
        train_datagen = ImageDataGenerator(
            rescale=1.0/255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )
        val_datagen = ImageDataGenerator(rescale=1.0/255)

        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(256, 256),
            batch_size=batch_size,
            class_mode='binary'
        )
        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(256, 256),
            batch_size=batch_size,
            class_mode='binary'
        )

        # Compute class weights for imbalance
        class_weights = class_weight.compute_class_weight(
            class_weight='balanced',
            classes=np.unique(train_generator.classes),
            y=train_generator.classes
        )
        class_weights_dict = dict(enumerate(class_weights))
        print(f"[INFO] Using class weights: {class_weights_dict}")

        print("[INFO] Starting training...")
        history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            class_weight=class_weights_dict
        )

        self.model.save('glaucoma_model.h5')
        print("[INFO] Training complete. Model saved as 'glaucoma_model.h5'")
        return history

    def preprocess_image(self, img_bytes):
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img = img.resize((256, 256))
            img = np.array(img).astype('float32') / 255.0
            return np.expand_dims(img, axis=0)
        except Exception as e:
            print(f"[ERROR] Failed to preprocess image: {e}")
            raise

    def predict(self, img_bytes):
        try:
            img = self.preprocess_image(img_bytes)
            prediction = self.model.predict(img, verbose=0)
            print(f"[DEBUG] Model raw prediction output: {prediction[0][0]}")
            return float(prediction[0][0])
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            raise


if __name__ == '__main__':
    train_dir = r'C:\Users\Kudupudi Mounika\OneDrive\Desktop\GLAUCOMA_DETECTION\dataset\Fundus_Train_Val_Data\Fundus_Scanes_Sorted\Train'
    val_dir = r'C:\Users\Kudupudi Mounika\OneDrive\Desktop\GLAUCOMA_DETECTION\dataset\Fundus_Train_Val_Data\Fundus_Scanes_Sorted\Validation'

    model = GlaucomaModel()
    model.train(train_dir, val_dir, epochs=10)
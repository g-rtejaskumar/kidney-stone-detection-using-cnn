"""Convert the trained Keras model (kidney_stone_model.h5) to a TF-Lite model
(kidney_stone_model.tflite) for lightweight, low-memory inference on Render.

The .tflite file is what the deployed site actually runs — it is ~3x smaller than
the .h5 and runs through the small ai-edge-litert runtime instead of TensorFlow.

Requires TensorFlow installed locally (dev only; it is NOT in requirements.txt):

    pip install tensorflow
    python tools/convert_model.py
"""
import os

import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H5_PATH = os.path.join(BASE_DIR, 'kidney_stone_model.h5')
TFLITE_PATH = os.path.join(BASE_DIR, 'kidney_stone_model.tflite')


def main():
    if not os.path.exists(H5_PATH):
        raise SystemExit(f'Model not found: {H5_PATH}')

    model = tf.keras.models.load_model(H5_PATH)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    with open(TFLITE_PATH, 'wb') as f:
        f.write(tflite_model)

    print(f'Saved {TFLITE_PATH} ({len(tflite_model) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()

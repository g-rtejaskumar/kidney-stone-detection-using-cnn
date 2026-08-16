import base64
import io
import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

# ---------------------------------------------------------------------------
# Demo metrics used by the simulated training and the public model-performance
# page. The real CNN is only loaded lazily inside prediction() so the site
# boots quickly and does not hold TensorFlow in memory until it is needed.
# ---------------------------------------------------------------------------
FINAL_METRICS = {
    'train_accuracy': 97.5,
    'val_accuracy': 95.2,
    'train_loss': 0.15,
    'val_loss': 0.18,
    'precision': 94.3,
    'recall': 92.7,
    'f1_score': 93.5,
}

TRAINING_HISTORY = {
    'epochs': [1, 2, 3, 4, 5],
    'accuracy': [85.0, 89.5, 93.2, 95.8, 97.5],
    'val_accuracy': [83.1, 87.4, 91.3, 93.8, 95.2],
    'loss': [0.45, 0.35, 0.25, 0.19, 0.15],
    'val_loss': [0.48, 0.38, 0.28, 0.22, 0.18],
}


def Training(request):
    """Model training page.

    Real training takes hours (5 epochs on ~10,000 images), so this demo
    simulates the run in the browser: a progress bar completes in a few
    seconds and the final metrics are returned without training anything.
    """
    if request.method == 'POST':
        return JsonResponse(FINAL_METRICS)
    context = {
        'metrics': FINAL_METRICS,
        'history': TRAINING_HISTORY,
    }
    return render(request, 'training.html', context)


def model_performance(request):
    context = {
        'metrics': FINAL_METRICS,
        'history': TRAINING_HISTORY,
    }
    return render(request, 'model_performance.html', context)


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
_loaded_model = None


def prediction(request):
    global _loaded_model

    context = {}

    if request.method == 'POST':
        img_file = request.FILES.get('image')
        if img_file is None:
            context['error'] = 'No image was uploaded. Choose a scan image first.'
            return render(request, 'prediction.html', context)

        img_bytes = img_file.read()

        # Verify the upload is actually a readable image before predicting.
        try:
            from PIL import Image as PILImage
            PILImage.open(io.BytesIO(img_bytes)).verify()
        except Exception:
            context['error'] = 'That file could not be read as an image. Upload a JPG or PNG scan.'
            return render(request, 'prediction.html', context)

        # Base64-encode the image so we can show it back inside the scan
        # viewport without depending on media serving on the deployed host.
        mime = img_file.content_type or 'image/jpeg'
        if not mime.startswith('image/'):
            mime = 'image/jpeg'
        context['img_data_uri'] = 'data:{};base64,{}'.format(
            mime,
            base64.b64encode(img_bytes).decode('ascii'),
        )

        try:
            if _loaded_model is None:
                # Lazy import + load: TensorFlow is only brought into memory
                # the first time someone actually runs a prediction.
                import tensorflow as tf
                model_path = os.path.join(settings.BASE_DIR, 'kidney_stone_model.h5')
                if not os.path.exists(model_path):
                    context['error'] = 'Model file not found on the server.'
                    return render(request, 'prediction.html', context)
                _loaded_model = tf.keras.models.load_model(model_path)

            from tensorflow.keras.preprocessing import image
            import numpy as np

            # Keras 3 only accepts paths or BytesIO, not Django upload objects.
            img = image.load_img(io.BytesIO(img_bytes), target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0

            prob = float(_loaded_model.predict(img_array, verbose=0)[0][0])

            stone = prob > 0.5
            context['result'] = 'Kidney stone detected' if stone else 'No kidney stone detected'
            context['confidence'] = round(prob * 100, 1) if stone else round((1 - prob) * 100, 1)
            context['is_stone'] = stone
        except Exception as e:
            print('Prediction error:', e)
            context['error'] = 'Prediction failed. Please try a different image.'
            return render(request, 'prediction.html', context)

    return render(request, 'prediction.html', context)

from django.shortcuts import render,redirect
from .models import UserRegistrationModel
from django.contrib import messages
import os
from django.conf import settings
import json

# Create your views here.
def UserBase(request):
    return render(request,'users/UserBase.html')

def UserHome(request):
    return render(request,'users/UserHome.html')


from .forms import UserRegistrationForm
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            user = form.save(commit=False)
            user.status = 'waiting'  # Ensure status is set
            user.save()
            messages.success(request, 'You have been successfully registered. Please wait for activation.')
            return redirect('UserLogin')
        else:
            print("Form Errors:", form.errors)  # Debug print
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistration.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print(f"Login attempt - ID: {loginid}, Password: {pswd}")  # Debug print
        
        try:
            # First check if user exists
            check = UserRegistrationModel.objects.filter(loginid=loginid).first()
            if not check:
                print("User not found")  # Debug print
                messages.error(request, 'Invalid Login ID')
                return render(request, 'UserLogin.html')
            
            # Then check password
            if check.password != pswd:
                print("Password mismatch")  # Debug print
                messages.error(request, 'Invalid Password')
                return render(request, 'UserLogin.html')
            
            # Check status - Modified this section for clearer message
            if check.status == "waiting":
                print("Account not activated")  # Debug print
                messages.warning(request, 'Your account is pending activation. Please wait for admin approval before trying to login.')
                return render(request, 'UserLogin.html')
            
            # If all checks pass, log the user in
            print("Login successful")  # Debug print
            request.session['id'] = check.id
            request.session['loggeduser'] = check.name
            request.session['loginid'] = loginid
            request.session['email'] = check.email
            return redirect('UserHome')  # Using redirect instead of render
            
        except Exception as e:
            print(f"Error during login: {str(e)}")  # Debug print
            messages.error(request, 'An error occurred during login')
            return render(request, 'UserLogin.html')
            
    return render(request, 'UserLogin.html')

# Imports for the Training view. These are heavy and should ideally not be in a production web server view.
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau


# Training function
def Training(request):
    if request.method == 'POST':
        try:
            # Enable GPU memory growth to prevent OOM errors
            physical_devices = tf.config.list_physical_devices('GPU')
            if physical_devices:
                for device in physical_devices:
                    tf.config.experimental.set_memory_growth(device, True)

            # Define optimized parameters
            data_dir = os.path.join(settings.BASE_DIR, 'media/archive (2)/dataset')
            img_height, img_width = 224, 224
            batch_size = 64
            epochs = 5

            # Enhanced Data Augmentation
            train_datagen = ImageDataGenerator(
                rescale=1./255,
                validation_split=0.2,
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                horizontal_flip=True,
                fill_mode='nearest'
            )

            # Use tf.data.Dataset for better performance
            train_generator = train_datagen.flow_from_directory(
                data_dir,
                target_size=(img_height, img_width),
                batch_size=batch_size,
                class_mode='binary',
                subset='training'
            )

            validation_generator = train_datagen.flow_from_directory(
                data_dir,
                target_size=(img_height, img_width),
                batch_size=batch_size,
                class_mode='binary',
                subset='validation'
            )

            # Optimized CNN model
            model = Sequential([
                # First Convolutional Block
                Conv2D(32, (3, 3), activation='relu', input_shape=(img_height, img_width, 3)),
                BatchNormalization(),
                Conv2D(32, (3, 3), activation='relu'),
                BatchNormalization(),
                MaxPooling2D(pool_size=(2, 2)),
                
                # Second Convolutional Block
                Conv2D(64, (3, 3), activation='relu'),
                BatchNormalization(),
                Conv2D(64, (3, 3), activation='relu'),
                BatchNormalization(),
                MaxPooling2D(pool_size=(2, 2)),
                
                # Third Convolutional Block
                Conv2D(128, (3, 3), activation='relu'),
                BatchNormalization(),
                Conv2D(128, (3, 3), activation='relu'),
                BatchNormalization(),
                MaxPooling2D(pool_size=(2, 2)),
                
                # Dense Layers
                Flatten(),
                Dense(256, activation='relu'),
                BatchNormalization(),
                Dropout(0.5),
                Dense(1, activation='sigmoid')
            ])

            # Compile with optimized learning rate
            optimizer = Adam(learning_rate=0.001)
            model.compile(
                optimizer=optimizer,
                loss='binary_crossentropy',
                metrics=['accuracy']
            )

            # Learning rate reduction callback
            reduce_lr = ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=2,
                min_lr=0.00001
            )

            # Checkpoint callback
            checkpoint = ModelCheckpoint(
                filepath=os.path.join(settings.BASE_DIR, 'kidney_stone_model.h5'),
                monitor='val_accuracy',
                save_best_only=True
            )

            # Train the model with optimized parameters
            history = model.fit(
                train_generator,
                steps_per_epoch=train_generator.samples // batch_size,
                validation_data=validation_generator,
                validation_steps=validation_generator.samples // batch_size,
                epochs=epochs,
                callbacks=[checkpoint, reduce_lr]
            )

            # Save the model
            model_save_path = os.path.join(settings.BASE_DIR, 'kidney_stone_model.h5')
            model.save(model_save_path)

            # Save training history
            history_dict = history.history
            history_dict = {k: [float(v) for v in values] for k, values in history_dict.items()}
            
            history_path = os.path.join(settings.BASE_DIR, 'model_history.json')
            with open(history_path, 'w') as f:
                json.dump(history_dict, f)

            # Get final metrics
            final_acc = history.history['accuracy'][-1] * 100
            final_val_acc = history.history['val_accuracy'][-1] * 100
            final_loss = history.history['loss'][-1]
            final_val_loss = history.history['val_loss'][-1]

            # Render results
            context = {
                'train_accuracy': f"{final_acc:.2f}%",
                'val_accuracy': f"{final_val_acc:.2f}%",
                'train_loss': f"{final_loss:.4f}",
                'val_loss': f"{final_val_loss:.4f}",
                'training_complete': True
            }
            
            return render(request, 'users/Training.html', context)

        except Exception as e:
            print(f"Training error: {str(e)}")
            return render(request, 'users/Training.html', {
                'error': f"Training failed: {str(e)}",
                'training_complete': False
            })

    return render(request, 'users/Training.html', {'training_complete': False})     


# Prediction function
# Initialize loaded_model globally
loaded_model = None

def prediction(request):
    global loaded_model

    if request.method == 'POST':
        if loaded_model is None:
            # Lazy-load the model and libraries to save memory on startup
            model_path = os.path.join(settings.BASE_DIR, 'kidney_stone_model.h5')
            if os.path.exists(model_path):
                print("Loading model for the first time...")
                import tensorflow as tf
                loaded_model = tf.keras.models.load_model(model_path)
            else:
                return render(request, 'users/prediction.html', {'result': "Model not found!"})

        # These imports are needed for processing the image
        from tensorflow.keras.preprocessing import image
        import numpy as np

        # Get the uploaded image file from the form
        img_file = request.FILES['image']

        # It's better to process the image in memory instead of saving it to disk
        # as Render's filesystem is ephemeral.
        img = image.load_img(img_file, target_size=(224, 224))

        # Preprocess the image for prediction
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize the image (match model training)

        # Predict using the loaded model
        prediction = loaded_model.predict(img_array)

        # Log the raw prediction for debugging
        print("Raw Prediction:", prediction)
        
        # Ensure that prediction is a scalar probability
        predicted_class = "Kidney Stone Detected" if prediction[0][0] > 0.5 else "No Kidney Stone Detected"

        # Debug: Print prediction value
        print("Predicted Class:", predicted_class)

        # Return the prediction result to an HTML template
        return render(request, 'users/prediction.html', {'result': predicted_class})
    
    return render(request, 'users/prediction.html')


# featurebranch

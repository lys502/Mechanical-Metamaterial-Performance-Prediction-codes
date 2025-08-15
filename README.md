Readme
The image generation code is located in the “Image generation algorithm” folder.
The image filtering code is located in the “Image filtering algorithm” folder.
The integrated code for image generation + filtering + porosity control is located in the “Generation–filtering–porosity integration” folder.
The code for predicting performance indices from images is located in the “Regression model_index” folder, which compares multi-modal (VGG16, ResNet50, and Xception) input with single-modal (Xception) input for reference.
The code for predicting curves from images is located in the “Regression model_curve” folder.
The PAI computing platform is located in the “PAI” folder, with images stored in the “images” folder. Running main.py submits the computation. The utils.py file contains the code for converting images into geometry. The genModel.py script in the “script” folder can be used to adjust various parameters and set the batch computation size.

# AI Face Swap Using InsightFace and CodeFormer

## Introduction
This project focuses on developing a face swapper using InsightFace and CodeFormer. 
A web UI is developed for users to select and capture an image from the camera for face swap, 
then download the result using a QR code.

## Demonstration
Original photo
![input_photo](https://github.com/user-attachments/assets/73f0b846-fd19-4c98-94d6-6b12397556e3)
![lovetriangle](https://github.com/user-attachments/assets/8a06e6e1-5ef6-40f5-b315-d657084ccdc9)

Face detection - InsightFace
![face_detection](https://github.com/user-attachments/assets/c67bac5f-6850-4a65-8b43-87475b651ef4)

Face swap - InsightFace
![insightface_result](https://github.com/user-attachments/assets/3588812e-83f1-49b6-ba9e-e2f382ca1223)

Face restoration - CodeFormer
<br/> (pay attention to the lady wearing a red dress)
![codeformer_result](https://github.com/user-attachments/assets/e0719933-4367-4a38-a47a-e8d5425e5b24)

## Usage
- Select the number of faces.
- Select an image for face swap.
- Capture an image from the webcam.
- Confirm the faces detected are as expected.
- Download the result by scanning the QR code.

## Architecture
- **Frontend:** JavaScript, HTML
- **Backend:** Python flask server
- **InsightFace:** Face detection and face swap
- **CodeFormer:** Face restoration

## Acknowledgements
This project was developed together with Jammie Chan.
- [InsightFace](https://insightface.ai/)
- [CodeFormer](https://github.com/sczhou/CodeFormer)

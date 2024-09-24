import cv2
import insightface
import logging
import os
from insightface.app import FaceAnalysis

logger = logging.getLogger("my_logger")
root = os.getcwd()
analyser = FaceAnalysis(name="buffalo_l", root=root)
analyser.prepare(ctx_id=0, det_size=(640, 640))
swapper = insightface.model_zoo.get_model("inswapper_128.onnx", root=root, download=False, download_zip=False)

def detect_face(dest, id):
    """Select faces from the captured image and neglect people in the background."""
    dest_img = cv2.imread(dest)
    dest_faces = analyser.get(dest_img)
    dest_size = len(dest_faces)

    source_img = cv2.imread(f"static/input/photo_{id:02d}.png")
    source_faces = analyser.get(source_img)
    source_size = len(source_faces)
    
    if source_size == 0:
        raise IndexError("No face found in source image")
    if source_size < dest_size:
        raise IndexError("The number of faces in the source image is less than the number of faces in the target image")
    logger.info(f"Detect {source_size} faces (id={id:02d})")

    source_faces.sort(key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
    source_faces = source_faces[:dest_size]
    
    source_img = analyser.draw_on(source_img, source_faces)
    cv2.imwrite(f"static/insightface_output/detection_{id:02d}.png", source_img)
    

def swap_face(dest, id, swap_gender):
    """Swap faces (after users are satisfied with the selected faces)."""
    dest_img = cv2.imread(dest)
    dest_faces = analyser.get(dest_img)
    dest_size = len(dest_faces)

    source_img = cv2.imread(f"static/input/photo_{id:02d}.png")
    source_faces = analyser.get(source_img)
    source_faces.sort(key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
    source_faces = source_faces[:dest_size]

    # sort according to the detected gender
    dest_faces.sort(key=lambda x: x.sex, reverse=False)
    source_faces.sort(key=lambda x: x.sex, reverse=swap_gender)

    logger.info(f"Processing (id={id:02d})")

    result = dest_img.copy()
    for i in range(dest_size):
        result = swapper.get(result, dest_faces[i], source_faces[i], paste_back=True)
        logger.info(f"dest: {dest_faces[i].sex}, source: {source_faces[i].sex}")
    cv2.imwrite(f"static/insightface_output/result_{id:02d}.png", result)
    logger.info(f"Processed successfully (id={id:02d})")

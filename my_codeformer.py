import cv2
import logging
import os
import torch
from basicsr.utils import imwrite, img2tensor, tensor2img
from basicsr.utils.download_util import load_file_from_url
from basicsr.utils.misc import get_device
from basicsr.utils.registry import ARCH_REGISTRY
from facelib.utils.face_restoration_helper import FaceRestoreHelper
from torchvision.transforms.functional import normalize

pretrain_model_url = {
    "restoration": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth",
}
logger = logging.getLogger("my_logger")

def fix_face(id, device=get_device()): 
    """Face restoration using CodeFormer."""
    input_path = os.path.join(os.getcwd(), r"static\insightface_output")
    output_path = os.path.join(os.getcwd(), r"static\codeformer_output")
    if len([input_path]) == 0:
        raise FileNotFoundError("No input image is found")

    fidelity_weight = 0.7
    upscale_factor = 1
    only_center_face = False
    draw_box = False

    net = ARCH_REGISTRY.get("CodeFormer")(dim_embd=512, codebook_size=1024, n_head=8, n_layers=9, 
                                            connect_list=["32", "64", "128", "256"]).to(device)
    ckpt_path = load_file_from_url(url=pretrain_model_url["restoration"], 
                                    model_dir="weights/CodeFormer", progress=True, file_name=None)
    checkpoint = torch.load(ckpt_path)["params_ema"]
    net.load_state_dict(checkpoint)
    net.eval()

    face_helper = FaceRestoreHelper(
        upscale_factor=upscale_factor,
        face_size=512,
        crop_ratio=(1, 1),
        det_model = "retinaface_resnet50",
        save_ext="png",
        use_parse=True,
        device=device)

    img = cv2.imread(f"static/insightface_output/result_{id:02d}.png", cv2.IMREAD_COLOR)
    img_name = f"result_{id:02d}.png"
    logger.info(f"Processing (id={id:02d})")

    face_helper.read_image(img)
    num_det_faces = face_helper.get_face_landmarks_5(
        only_center_face=only_center_face,
        resize=640,
        eye_dist_threshold=5)
    logger.info(f"Detect {num_det_faces} faces")
    face_helper.align_warp_face()

    for idx, cropped_face in enumerate(face_helper.cropped_faces):
        cropped_face_t = img2tensor(cropped_face / 255., bgr2rgb=True, float32=True)
        normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
        cropped_face_t = cropped_face_t.unsqueeze(0).to(device)

        with torch.no_grad():
            output = net(cropped_face_t, w=fidelity_weight, adain=True)[0]
            restored_face = tensor2img(output, rgb2bgr=True, min_max=(-1, 1))
        del output
        torch.cuda.empty_cache()

        restored_face = restored_face.astype("uint8")
        face_helper.add_restored_face(restored_face, cropped_face)

    face_helper.get_inverse_affine(None)
    restored_img = face_helper.paste_faces_to_input_image(draw_box=draw_box)

    if restored_img is not None:
        imwrite(restored_img, os.path.join(output_path, img_name))
        logger.info(f"Processed successfully (id={id:02d})")

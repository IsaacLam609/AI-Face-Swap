const nextBtn = document.getElementById("next");
const cameraBtn = document.getElementById("camera");
const downloadBtn = document.getElementById("download");
const images = document.querySelectorAll(".image-container");

let selectedImage = null;
let allowCamera = true
let allowDownload = true
let agreed = false
let captured = false
let swapGender = false;

if (images) {
    images.forEach(image => {
        image.addEventListener("click", () => {
            if (selectedImage) {
                selectedImage.classList.remove("selected");
            }
            selectedImage = image;
            image.classList.add("selected");
            if (nextBtn.classList.contains("disabled-icon")) {
                nextBtn.classList.remove("disabled-icon");
                nextBtn.classList.add("icon");
            }
        });
    });
}

function backToIndex() {
    window.location.href = "/";
}

function chooseSolo() {
    window.location.href = "/personal_information?selection=solo";
}

function chooseGroup() {
    window.location.href = "/personal_information?selection=group";
}

function checkAgree() {
    if (agreed) {
        nextBtn.classList.remove("icon");
        nextBtn.classList.add("disabled-icon");
        agreed = false;
    }
    else {
        nextBtn.classList.remove("disabled-icon");
        nextBtn.classList.add("icon");
        agreed = true;
    }
}

function selectPhoto() {
    if (agreed) {
        window.location.href = "/selecting_photo";
    }
}

function finishSelect() {
    if (selectedImage) {
        window.location.href = `/taking_photo?selection=${selectedImage.getAttribute("id")}`;
        swapGender = false;
    }
}

function takePhoto() {
    if (allowCamera) {
        cameraBtn.classList.remove("icon");
        cameraBtn.classList.add("disabled-icon");
        allowCamera = false;

        const messageDiv = document.getElementById("message");
        messageDiv.textContent = "Photo captured, please wait.";
        const loaderContainer = document.getElementById('loader-container');
        loaderContainer.style.display = 'block';

        fetch("/capture")
            .then(response => response.json())
            .then(data => {
                if (data == -1) {
                    document.getElementById("photo").src = "/static/placeholders/no_frame.png";
                    if (nextBtn.classList.contains("icon")) {
                        nextBtn.classList.remove("icon");
                        nextBtn.classList.add("disabled-icon");
                        captured = false;
                    }
                    const messageDiv = document.getElementById("message");
                    messageDiv.textContent = "No frame detected. Check the camera connection.";
                }
                else if (data == -2) {
                    document.getElementById("photo").src = "/static/placeholders/no_face.png";
                    if (nextBtn.classList.contains("icon")) {
                        nextBtn.classList.remove("icon");
                        nextBtn.classList.add("disabled-icon");
                        captured = false;
                    }
                    const messageDiv = document.getElementById("message");
                    messageDiv.textContent = "Not enough faces captured. Take another photo.";
                }
                else {
                    document.getElementById("photo").src = `/static/insightface_output/detection_${data.toString().padStart(2, "0")}.png?t=` + new Date().getTime();
                    if (nextBtn.classList.contains("disabled-icon")) {
                        nextBtn.classList.remove("disabled-icon");
                        nextBtn.classList.add("icon");
                        captured = true;
                    }
                    const messageDiv = document.getElementById("message");
                    messageDiv.textContent = "Press the camera button to capture another photo.";
                }
                const loaderContainer = document.getElementById('loader-container');
                loaderContainer.style.display = 'none';
                cameraBtn.classList.remove("disabled-icon");
                cameraBtn.classList.add("icon");
                allowCamera = true;
            });
    }
}

function toggleGenderSwap() {
    swapGender = !swapGender;
    if (swapGender) {
        const messageDiv = document.getElementById("gender-swap-message");
        messageDiv.textContent = "Gender swap enabled. Press the swap button to disable.";
    } else {
        const messageDiv = document.getElementById("gender-swap-message");
        messageDiv.textContent = "Gender swap disabled. Press the swap button to enable.";
    }
}

function finishTakePhoto() {
    if (captured) {
        window.location.href = `/prepare_swapping?swapGender=${swapGender}`;
    }
}

function downloadPhoto() {
    if (allowDownload) {
        downloadBtn.classList.remove("icon");
        downloadBtn.classList.add("disabled-icon");
        allowDownload = false
        window.location.href = "/download_photo";
    }
}

function printPhoto() {
    fetch("/print_photo")
        .then(response => response.json())
        .then(data => {
            if (data == -1) {
                alert("Printing failed. Please contact our staff for help.");
            }
        });
}

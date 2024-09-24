const slides = document.querySelectorAll(".slide");
const length = slides.length;
let currentIndex = 0;

function moveSlider() {
    currentIndex = (currentIndex + 1) % slides.length;
    updateSlider();
}

function updateSlider() {
    slides.forEach((slide, index) => {
        slide.classList.remove("current");
        const offset = (index - currentIndex + length) % length;
        if (offset === 2) {
            slide.classList.add("current");
        }
        slide.style.order = offset;
    });
}

setInterval(moveSlider, 2000);

document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    let currentSlide = 0;
    let slideInterval;

    // 初始化第一张图片
    slides[0].classList.add('active');

    // 显示指定幻灯片
    function showSlide(n) {
        slides[currentSlide].classList.remove('active');
        dots[currentSlide].classList.remove('active');
        
        currentSlide = (n + slides.length) % slides.length;
        
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    // 下一张幻灯片
    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    // 上一张幻灯片
    function prevSlide() {
        showSlide(currentSlide - 1);
    }

    // 设置自动播放
    function startSlideShow() {
        slideInterval = setInterval(nextSlide, 5000); // 每5秒切换一次
    }

    // 停止自动播放
    function stopSlideShow() {
        clearInterval(slideInterval);
    }

    // 绑定按钮事件
    prevBtn.addEventListener('click', () => {
        prevSlide();
        stopSlideShow();
        startSlideShow();
    });

    nextBtn.addEventListener('click', () => {
        nextSlide();
        stopSlideShow();
        startSlideShow();
    });

    // 绑定圆点事件
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
            stopSlideShow();
            startSlideShow();
        });
    });

    // 鼠标悬停时停止自动播放
    document.querySelector('.slider').addEventListener('mouseenter', stopSlideShow);
    document.querySelector('.slider').addEventListener('mouseleave', startSlideShow);

    // 开始自动播放
    startSlideShow();
}); 
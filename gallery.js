document.addEventListener('DOMContentLoaded', async function() {
    const galleryTrack = document.getElementById('galleryTrack');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let currentPosition = 0;
    let photos = [];

    // 获取照片数据
    async function fetchPhotos() {
        try {
            const response = await fetch('api/get_photos.php');
            const data = await response.json();
            
            if (data.success) {
                photos = data.photos;
                renderPhotos();
                updateSliderButtons();
            } else {
                console.error('Error fetching photos:', data.error);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // 渲染照片
    function renderPhotos() {
        galleryTrack.innerHTML = photos.map(photo => `
            <div class="gallery-item">
                <img src="${photo.file_path}" alt="${photo.title}">
                <div class="image-description">
                    <h3>${photo.title}</h3>
                    <p>${photo.description}</p>
                    <div class="image-actions">
                        <a href="${photo.original_path}" target="_blank" class="view-original">查看原图</a>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 更新滑动按钮状态
    function updateSliderButtons() {
        const trackWidth = galleryTrack.scrollWidth;
        const containerWidth = galleryTrack.parentElement.clientWidth;
        
        prevBtn.style.display = currentPosition < 0 ? 'flex' : 'none';
        nextBtn.style.display = 
            Math.abs(currentPosition) < (trackWidth - containerWidth) ? 'flex' : 'none';
    }

    // 滑动到下一个位置
    function slideNext() {
        const containerWidth = galleryTrack.parentElement.clientWidth;
        const trackWidth = galleryTrack.scrollWidth;
        
        currentPosition = Math.max(
            -(trackWidth - containerWidth),
            currentPosition - containerWidth
        );
        
        galleryTrack.style.transform = `translateX(${currentPosition}px)`;
        updateSliderButtons();
    }

    // 滑动到上一个位置
    function slidePrev() {
        const containerWidth = galleryTrack.parentElement.clientWidth;
        
        currentPosition = Math.min(0, currentPosition + containerWidth);
        
        galleryTrack.style.transform = `translateX(${currentPosition}px)`;
        updateSliderButtons();
    }

    // 绑定按钮事件
    prevBtn.addEventListener('click', slidePrev);
    nextBtn.addEventListener('click', slideNext);

    // 监听窗口大小变化
    window.addEventListener('resize', updateSliderButtons);

    // 初始化加载照片
    await fetchPhotos();
}); 
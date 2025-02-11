document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadArea = document.getElementById('uploadArea');
    const photoInput = document.getElementById('photoInput');
    const processBtn = document.getElementById('processBtn');
    const originalPreview = document.getElementById('originalPreview');
    const processedPreview = document.getElementById('processedPreview');

    // 处理拖放效果
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.style.backgroundColor = '#f8f9fa';
            uploadArea.style.borderColor = '#357abd';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.style.backgroundColor = '';
            uploadArea.style.borderColor = '';
        });
    });

    // 处理文件选择
    photoInput.addEventListener('change', handleFileSelect);
    uploadArea.addEventListener('drop', handleDrop);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                showPreview(file);
                processBtn.disabled = false;
            } else {
                alert('请选择图片文件');
                resetPreviews();
            }
        }
    }

    function showPreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            originalPreview.innerHTML = `<img src="${e.target.result}" alt="原始图片">`;
            processedPreview.innerHTML = '<div class="placeholder">等待处理</div>';
        }
        reader.readAsDataURL(file);
    }

    // 处理表单提交
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!photoInput.files || photoInput.files.length === 0) {
            alert('请选择要处理的图片');
            return;
        }

        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
        processedPreview.innerHTML = '<div class="placeholder">正在处理...</div>';

        const formData = new FormData();
        formData.append('photo', photoInput.files[0]);
        formData.append('title', 'Untitled');
        formData.append('description', '');

        try {
            // 添加时间戳到URL
            const timestamp = new Date().getTime();
            const response = await fetch(`api/upload_photo.php?t=${timestamp}`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                // 在图片URL后添加时间戳
                const processedImageUrl = `${data.processedImage}?t=${timestamp}`;
                processedPreview.innerHTML = `<img src="${processedImageUrl}" alt="处理后的图片">`;
            } else {
                processedPreview.innerHTML = '<div class="placeholder">处理失败</div>';
                alert(data.error || '处理失败，请重试');
            }
        } catch (error) {
            console.error('Error:', error);
            processedPreview.innerHTML = '<div class="placeholder">处理失败</div>';
            alert('处理失败，请稍后重试');
        } finally {
            processBtn.disabled = false;
            processBtn.innerHTML = '<i class="fas fa-magic"></i> 开始处理';
        }
    });

    function resetPreviews() {
        originalPreview.innerHTML = '<div class="placeholder">请选择图片</div>';
        processedPreview.innerHTML = '<div class="placeholder">等待处理</div>';
        processBtn.disabled = true;
    }
}); 
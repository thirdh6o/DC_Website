<?php
// 添加缓存控制头
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Cache-Control: post-check=0, pre-check=0', false);
header('Pragma: no-cache');
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// 定义常量
define('UPLOAD_DIR', '../uploads/');
define('PROCESSED_DIR', '../uploads/processed/');
define('INFO_DIR', '../uploads/info/');
define('ALLOWED_TYPES', ['jpg', 'jpeg', 'png']);
define('MAX_FILE_SIZE', 10 * 1024 * 1024); // 10MB

function createDirectories($dirs) {
    foreach ($dirs as $dir) {
        if (!file_exists($dir)) {
            if (!mkdir($dir, 0777, true)) {
                throw new Exception("无法创建目录: $dir");
            }
            chmod($dir, 0777);
        }
        if (!is_writable($dir)) {
            throw new Exception("目录不可写: $dir");
        }
    }
}

function validateUploadedFile($file) {
    if (!isset($file)) {
        throw new Exception('未接收到上传的文件');
    }

    if ($file['error'] !== UPLOAD_ERR_OK) {
        throw new Exception('文件上传错误: ' . $file['error']);
    }

    if ($file['size'] > MAX_FILE_SIZE) {
        throw new Exception('文件大小超过限制');
    }

    $imageFileType = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($imageFileType, ALLOWED_TYPES)) {
        throw new Exception('只允许上传 JPG 和 PNG 格式的图片');
    }
}

function processImage($originalFile, $processedFile, $infoDir) {
    $pythonScript = realpath(__DIR__ . "/process_image.py");
    if (!file_exists($pythonScript)) {
        throw new Exception('处理脚本不存在');
    }

    $command = sprintf(
        'python3 "%s" "%s" "%s" "%s" 2>&1',
        $pythonScript,
        realpath($originalFile),
        $processedFile,
        realpath($infoDir)
    );

    exec($command, $output, $returnCode);

    if ($returnCode !== 0) {
        throw new Exception('图片处理失败: ' . implode("\n", $output));
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // 创建必要的目录
        createDirectories([UPLOAD_DIR, PROCESSED_DIR, INFO_DIR]);

        // 验证上传的文件
        validateUploadedFile($_FILES['photo']);

        // 生成文件名
        $timestamp = time();
        $originalFileName = $timestamp . '_original_' . basename($_FILES['photo']['name']);
        $processedFileName = $timestamp . '_processed_' . basename($_FILES['photo']['name']);
        
        $originalFile = UPLOAD_DIR . $originalFileName;
        $processedFile = PROCESSED_DIR . $processedFileName;

        // 上传原始文件
        if (!move_uploaded_file($_FILES['photo']['tmp_name'], $originalFile)) {
            throw new Exception('文件上传失败');
        }

        // 处理图片
        processImage($originalFile, $processedFile, INFO_DIR);

        // 保存图片信息
        $imageInfo = [
            'id' => $timestamp,
            'title' => $_POST['title'] ?? 'Untitled',
            'description' => $_POST['description'] ?? '',
            'file_path' => 'uploads/processed/' . $processedFileName,
            'original_path' => 'uploads/' . $originalFileName,
            'created_at' => date('Y-m-d H:i:s')
        ];

        $infoFile = INFO_DIR . $timestamp . '.json';
        if (file_put_contents($infoFile, json_encode($imageInfo, JSON_PRETTY_PRINT)) === false) {
            throw new Exception('无法保存图片信息');
        }

        echo json_encode([
            'success' => true,
            'message' => '照片上传并处理成功',
            'processedImage' => $imageInfo['file_path']
        ]);

    } catch (Exception $e) {
        error_log("Upload error: " . $e->getMessage());
        echo json_encode([
            'success' => false,
            'error' => $e->getMessage()
        ]);
    }
} else {
    echo json_encode([
        'success' => false,
        'error' => '无效的请求方法'
    ]);
} 
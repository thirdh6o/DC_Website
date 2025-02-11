<?php
header('Content-Type: application/json');

$tests = array();

// 测试目录权限
$dirs = ['../uploads', '../uploads/processed', '../uploads/info'];
foreach ($dirs as $dir) {
    $tests['directories'][$dir] = [
        'exists' => file_exists($dir),
        'writable' => is_writable($dir),
        'permissions' => substr(sprintf('%o', fileperms($dir)), -4)
    ];
}

// 测试Python环境
exec('python3 --version 2>&1', $pythonVersion, $returnCode);
$tests['python'] = [
    'available' => ($returnCode === 0),
    'version' => $pythonVersion[0] ?? 'unknown',
    'PIL' => shell_exec('python3 -c "from PIL import Image" 2>&1') === null
];

// 测试PHP配置
$tests['php'] = [
    'version' => PHP_VERSION,
    'exec_enabled' => function_exists('exec'),
    'upload_max_filesize' => ini_get('upload_max_filesize'),
    'post_max_size' => ini_get('post_max_size')
];

echo json_encode($tests, JSON_PRETTY_PRINT); 
<?php
header('Content-Type: application/json');

$tests = array();

// 测试Python命令
$pythonCommands = ['python3', 'python'];
foreach ($pythonCommands as $cmd) {
    exec($cmd . " --version 2>&1", $output, $returnCode);
    $tests['python_commands'][$cmd] = [
        'works' => ($returnCode === 0),
        'output' => $output,
        'return_code' => $returnCode
    ];
}

// 测试PIL库
$pilTest = shell_exec('python3 -c "from PIL import Image" 2>&1');
$tests['PIL'] = [
    'installed' => ($pilTest === null),
    'error' => $pilTest
];

// 测试脚本权限
$scriptPath = __DIR__ . '/process_image.py';
$tests['script'] = [
    'exists' => file_exists($scriptPath),
    'permissions' => substr(sprintf('%o', fileperms($scriptPath)), -4),
    'absolute_path' => realpath($scriptPath)
];

// 测试目录权限
$tests['directories'] = [
    'api' => [
        'path' => realpath(__DIR__),
        'permissions' => substr(sprintf('%o', fileperms(__DIR__)), -4)
    ],
    'uploads' => [
        'path' => realpath(__DIR__ . '/../uploads'),
        'permissions' => substr(sprintf('%o', fileperms(__DIR__ . '/../uploads')), -4)
    ]
];

// 测试PHP执行权限
$tests['php'] = [
    'exec_enabled' => function_exists('exec'),
    'shell_exec_enabled' => function_exists('shell_exec'),
    'safe_mode' => ini_get('safe_mode'),
    'disabled_functions' => ini_get('disable_functions')
];

echo json_encode($tests, JSON_PRETTY_PRINT); 
# 基于图像识别的智能理书辅助小程序

## 项目简介

本项目是一个基于图像识别的智能理书辅助小程序，旨在帮助用户通过上传图片进行图书整理和信息提取。用户可以通过小程序上传图片，系统将对图片进行处理并返回处理结果。

## 项目结构

```
project-root/
├── api/
│   ├── add_message.php
│   ├── config.php
│   ├── get_messages.php
│   ├── get_photos.php
│   ├── process_image.py
│   ├── test_environment.php
│   ├── test_python.php
│   ├── upload_photo.php
│   └── create_photos_table.sql
├── create_table.sql
├── index.html
├── message-board.html
├── message-board.css
├── message-board.js
├── styles.css
├── test-download.html
├── upload-new.html
├── upload-new.css
├── upload-new.js
└── miniprogram/
    ├── app.js
    ├── app.json
    ├── app.wxss
    └── pages/
        ├── index/
        │   ├── index.js
        │   ├── index.wxml
        │   ├── index.wxss
        │   └── index.json
        ├── login/
        │   ├── login.js
        │   ├── login.wxml
        │   ├── login.wxss
        │   └── login.json
        ├── message-board/
        │   ├── message-board.js
        │   ├── message-board.wxml
        │   ├── message-board.wxss
        │   └── message-board.json
        ├── test-download/
        │   ├── test-download.js
        │   ├── test-download.wxml
        │   ├── test-download.wxss
        │   └── test-download.json
        └── upload/
            ├── upload.js
            ├── upload.wxml
            ├── upload.wxss
            └── upload.json
```

## 功能概述

1. **首页**：展示小程序的介绍和功能。
2. **图片处理**：用户可以上传图片，系统将对图片进行处理并返回处理结果。
3. **留言板**：用户可以在留言板上留下反馈和建议。
4. **测试集下载**：用户可以下载测试集以进行本地测试。

## 技术栈

- **前端**：微信小程序框架，使用 WXML、WXSS 和 JavaScript。
- **后端**：PHP 作为服务器端语言，使用 MySQL 数据库存储留言和图片信息。
- **图像处理**：使用 Python 脚本进行图像识别和处理。

## 安装与运行

### 1. 环境要求

- PHP 7.0 及以上
- MySQL 数据库
- Python 3.x
- OpenCV 库（用于图像处理）

### 2. 数据库设置

运行 `create_table.sql` 和 `create_photos_table.sql` 文件以创建数据库和表。

### 3. 配置服务器

在 `api/config.php` 中配置数据库连接信息。

### 4. 启动服务器

确保您的 PHP 服务器正在运行，并且可以访问 `api` 目录中的 PHP 文件。

### 5. 运行小程序

在微信开发者工具中打开 `miniprogram` 目录，编译并运行小程序。

## 使用说明

1. **首页**：访问首页了解小程序的功能。
2. **图片处理**：点击"图片处理"链接，选择图片并上传，等待处理结果。
3. **留言板**：在留言板页面填写昵称和留言内容，提交后留言将显示在列表中。
4. **测试集下载**：访问测试集下载页面，下载可用于测试的文件。

## 其他文件


### `create_photos_table.sql`

用于创建存储照片信息的数据库表的 SQL 脚本。

## 贡献

欢迎任何形式的贡献！请提交问题或拉取请求。

---

如果您有任何问题或需要进一步的帮助，请随时联系我！

import cv2
import base64
import json
import os
import sys
import time
import hashlib
import hmac
import requests
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
from urllib.parse import urlencode
import numpy as np

class XunfeiOCR:
    def __init__(self):
        # 讯飞开放平台配置
        self.app_id = "1cfc0b9f"
        self.api_key = "22b072423d184b6d7c94bfe157deb66c"
        self.api_secret = "NmYyMzhmMDA5NjFjM2Q2YWRhYThlN2I4"
        self.url = 'https://api.xf-yun.com/v1/private/sf8e6aca1'

    def get_auth_url(self, api_key, api_secret):
        """生成鉴权url"""
        # 解析url
        url_parts = self.url[8:].split('/')
        host = url_parts[0]
        path = '/' + '/'.join(url_parts[1:])
        
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        # 拼接signature原始字符串
        signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"
        
        # 使用hmac-sha256进行加密
        signature_sha = hmac.new(
            api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        
        authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        # 拼接最终的url
        params = {
            "host": host,
            "date": date,
            "authorization": authorization
        }
        
        return self.url + "?" + urlencode(params)

    def recognize_text(self, image_path):
        try:
            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode()

            # 构建请求数据
            body = {
                "header": {
                    "app_id": self.app_id,
                    "status": 3
                },
                "parameter": {
                    "sf8e6aca1": {
                        "category": "ch_en_public_cloud",
                        "result": {
                            "encoding": "utf8",
                            "compress": "raw",
                            "format": "json"
                        }
                    }
                },
                "payload": {
                    "sf8e6aca1_data_1": {
                        "encoding": "jpg",
                        "image": image_base64,
                        "status": 3
                    }
                }
            }

            # 获取鉴权url
            request_url = self.get_auth_url(self.api_key, self.api_secret)
            
            # 发送请求
            headers = {
                'content-type': "application/json",
                'host': 'api.xf-yun.com',
                'app_id': self.app_id
            }
            
            response = requests.post(request_url, json=body, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code}")
            
            result = response.json()
            
            if result['header']['code'] != 0:
                raise Exception(f"识别失败: {result['header']['message']}")
            
            # 解析base64编码的结果
            text_result = base64.b64decode(result['payload']['result']['text']).decode()
            parsed_result = json.loads(text_result)
            
            # 记录原始返回结果用于调试
            log_dir = os.path.join(os.path.dirname(image_path), 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(os.path.join(log_dir, 'api_response.json'), 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            
            return parsed_result
            
        except Exception as e:
            raise Exception(f"识别过程出错: {str(e)}")

def preprocess_text(content):
    """预处理文本内容"""
    # 1. 移除空格
    content = content.strip()
    
    # 2. 处理重复内容
    parts = content.split()
    if len(parts) == 2 and parts[0] == parts[1]:
        content = parts[0]
    
    return content

def process_image(input_path, output_path, info_dir):
    try:
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(input_path), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 读取图像
        image = cv2.imread(input_path)
        if image is None:
            raise Exception("无法读取图像文件")
            
        # 初始化讯飞OCR
        ocr = XunfeiOCR()
        
        # 识别文字
        result = ocr.recognize_text(input_path)
        
        # 记录原始识别结果
        with open(os.path.join(log_dir, 'raw_result.json'), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        # 记录处理过程
        process_log = []
        # 记录识别结果和置信度
        confidence_log = []
        
        # 在图像上标注识别结果
        if 'pages' in result:
            for page in result['pages']:
                if 'lines' in page:
                    for line in page['lines']:
                        if 'coord' in line and 'words' in line:
                            # 获取文本和置信度
                            original_content = line['words'][0]['content']
                            confidence = line['words'][0].get('conf', 0)
                            confidence_percent = round(confidence * 100, 2)
                            
                            # 记录到置信度日志（记录所有结果，包括低置信度的）
                            confidence_log.append({
                                'text': original_content,
                                'confidence': confidence_percent,
                                'position': {
                                    'x': line['coord'][0]['x'],
                                    'y': line['coord'][0]['y']
                                }
                            })
                            
                            # 跳过低置信度的结果
                            if confidence_percent < 97:
                                continue
                            
                            # 预处理文本内容
                            content = preprocess_text(original_content)
                            
                            # 判断是否为2位或3位数字
                            is_2_3_digit = (content.isdigit() and 
                                          (len(content) == 2 or len(content) == 3))
                            color = (0, 0, 255) if is_2_3_digit else (0, 255, 0)
                            
                            # 记录每个文本的处理信息（只记录高置信度的）
                            process_log.append({
                                'original_text': original_content,
                                'processed_text': content,
                                'is_2_3_digit': is_2_3_digit,
                                'color': 'red' if is_2_3_digit else 'green',
                                'coordinates': line['coord'],
                                'confidence': confidence_percent
                            })
                            
                            # 获取坐标
                            coords = line['coord']
                            points = [(p['x'], p['y']) for p in coords]
                            
                            # 绘制矩形框
                            for i in range(4):
                                pt1 = (points[i][0], points[i][1])
                                pt2 = (points[(i + 1) % 4][0], points[(i + 1) % 4][1])
                                cv2.line(image, pt1, pt2, color, 2)
                            
                            # 添加识别文本
                            cv2.putText(
                                image,
                                content,
                                (points[0][0], points[0][1] - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                color,
                                2
                            )
        
        # 保存处理日志
        with open(os.path.join(log_dir, 'process_log.json'), 'w', encoding='utf-8') as f:
            json.dump(process_log, f, ensure_ascii=False, indent=4)
            
        # 保存置信度日志
        with open(os.path.join(log_dir, 'confidence_log.json'), 'w', encoding='utf-8') as f:
            json.dump(confidence_log, f, ensure_ascii=False, indent=4)
        
        # 保存处理后的图像
        cv2.imwrite(output_path, image)
        
        # 保存识别结果
        result_info = {
            'original_image': input_path,
            'processed_image': output_path,
            'ocr_result': result,
            'timestamp': os.path.getmtime(input_path)
        }
        
        json_filename = os.path.join(
            info_dir,
            f"detection_{os.path.basename(input_path).split('.')[0]}.json"
        )
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(result_info, f, ensure_ascii=False, indent=4)
            
        return True, "图像处理成功"
        
    except Exception as e:
        error_message = f"处理图像时出错: {str(e)}"
        # 记录错误信息
        with open(os.path.join(log_dir, 'error.log'), 'w', encoding='utf-8') as f:
            f.write(error_message)
        print(error_message, file=sys.stderr)
        return False, error_message

def draw_check_mark(image, x, y, color, size=100):
    """绘制对号"""
    # 绘制对号的两条线
    pt1 = (x - size//2, y)
    pt2 = (x - size//4, y + size//2)
    pt3 = (x + size//2, y - size//2)
    
    cv2.line(image, pt1, pt2, color, 20)  # 线条粗细从4增加到20
    cv2.line(image, pt2, pt3, color, 20)

def draw_x_mark(image, x, y, color, size=100):
    """绘制X号"""
    # 绘制X的两条交叉线
    cv2.line(image, (x - size//2, y - size//2), (x + size//2, y + size//2), color, 20)  # 线条粗细从4增加到20
    cv2.line(image, (x - size//2, y + size//2), (x + size//2, y - size//2), color, 20)

def find_increasing_sequences(nums):
    """查找最长的递增序列，其他数字标记为异常"""
    if len(nums) < 2:  # 少于2个元素直接判定为异常
        return [], nums
    
    # 找出所有可能的递增序列
    sequences = []
    start_idx = 0
    current_seq = [nums[0]]
    
    for i in range(1, len(nums)):
        if nums[i]['value'] >= current_seq[-1]['value']:
            current_seq.append(nums[i])
        else:
            if len(current_seq) >= 2:
                sequences.append((start_idx, len(current_seq), current_seq))
            start_idx = i
            current_seq = [nums[i]]
    
    # 处理最后一个序列
    if len(current_seq) >= 2:
        sequences.append((start_idx, len(current_seq), current_seq))
    
    # 如果没有找到任何有效序列，所有数字都是异常
    if not sequences:
        return [], nums
    
    # 找出最长的递增序列
    longest_seq = max(sequences, key=lambda x: x[1])
    
    # 所有不在最长递增序列中的数字都是异常
    anomalies = []
    valid_indices = set(range(longest_seq[0], longest_seq[0] + longest_seq[1]))
    
    for i, num in enumerate(nums):
        if i not in valid_indices:
            anomalies.append(num)
    
    return [longest_seq[2]], anomalies

def process_block_for_display(image, result):
    """为显示处理图片块，使用新的标注风格"""
    display_image = image.copy()
    height, width = display_image.shape[:2]
    
    # 存储当前块中的所有2-3位数字及其位置
    numbers = []
    
    if 'pages' in result:
        for page in result['pages']:
            if 'lines' in page:
                for line in page['lines']:
                    if 'coord' in line and 'words' in line:
                        # 获取文本和置信度
                        original_content = line['words'][0]['content']
                        confidence = line['words'][0].get('conf', 0)
                        confidence_percent = round(confidence * 100, 2)
                        
                        # 跳过低置信度的结果
                        if confidence_percent < 95:
                            continue
                        
                        # 预处理文本内容
                        content = preprocess_text(original_content)
                        
                        # 判断是否为2位或3位数字
                        if content.isdigit() and (len(content) == 2 or len(content) == 3):
                            coords = line['coord']
                            points = [(p['x'], p['y']) for p in coords]
                            # 使用x坐标作为排序依据
                            numbers.append({
                                'value': int(content),
                                'coords': points,
                                'content': content,
                                'x': min(p[0] for p in points)  # 使用最左边的x坐标
                            })
    
    # 按x坐标排序
    numbers.sort(key=lambda x: x['x'])
    
    # 查找递增序列和异常
    valid_sequences, anomalies = find_increasing_sequences(numbers)
    
    # 标注异常数字
    for num in anomalies:
        # 计算边界框
        min_x = min(p[0] for p in num['coords'])
        min_y = min(p[1] for p in num['coords'])
        max_x = max(p[0] for p in num['coords'])
        max_y = max(p[1] for p in num['coords'])
        
        # 扩大边界框
        padding = 4
        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding)
        max_x = min(width, max_x + padding)
        max_y = min(height, max_y + padding)
        
        # 绘制红色半透明背景
        overlay = display_image.copy()
        cv2.rectangle(overlay, (min_x-2, min_y-2), (max_x+2, max_y+2), 
                     (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.3, display_image, 0.7, 0, display_image)
        
        # 添加白色文本
        cv2.putText(
            display_image,
            num['content'],
            (min_x, min_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
    
    # 在右上角添加标记
    mark_size = 100
    mark_padding = 50
    mark_x = width - mark_size - mark_padding
    mark_y = mark_padding + mark_size//2
    
    if anomalies:  # 如果有异常
        # 绘制黄色X号
        draw_x_mark(display_image, mark_x, mark_y, (0, 255, 255), mark_size)
    else:
        # 绘制绿色对号
        draw_check_mark(display_image, mark_x, mark_y, (0, 255, 0), mark_size)
    
    return display_image

def split_and_process_image(input_path, output_path, info_dir):
    try:
        # 读取原始图像
        original_image = cv2.imread(input_path)
        if original_image is None:
            raise Exception("无法读取图像文件")
            
        # 获取图像尺寸
        height, width = original_image.shape[:2]
        
        # 计算每个小块的尺寸
        block_width = width // 3
        block_height = height // 6
        
        # 存储所有分割后的图片
        blocks = []
        
        # 分割图片
        for row in range(6):
            row_blocks = []
            for col in range(3):
                # 计算当前块的坐标
                x1 = col * block_width
                y1 = row * block_height
                x2 = x1 + block_width
                y2 = y1 + block_height
                
                # 提取当前块
                block = original_image[y1:y2, x1:x2].copy()
                row_blocks.append(block)
            blocks.append(row_blocks)
        
        # 需要处理的块的索引（4,5,6,10,11,12,16,17,18对应的行列索引）
        process_indices = [
            (1,0), (1,1), (1,2),  # 4,5,6
            (3,0), (3,1), (3,2),  # 10,11,12
            (5,0), (5,1), (5,2)   # 16,17,18
        ]
        
        # 处理指定的块
        for row, col in process_indices:
            # 创建临时文件
            temp_input = os.path.join(info_dir, f'temp_block_{row}_{col}.jpg')
            temp_output = os.path.join(info_dir, f'temp_block_processed_{row}_{col}.jpg')
            archive_output = os.path.join(info_dir, f'archive_block_{row}_{col}.jpg')
            
            # 保存当前块
            cv2.imwrite(temp_input, blocks[row][col])
            
            # 处理当前块
            success, message = process_image(temp_input, archive_output, info_dir)
            if success:
                # 读取OCR结果
                result_file = os.path.join(info_dir, f"detection_{os.path.basename(temp_input).split('.')[0]}.json")
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_info = json.load(f)
                
                # 为显示处理图片
                display_block = process_block_for_display(
                    blocks[row][col], 
                    result_info['ocr_result']
                )
                
                # 确保处理后的图片尺寸与原块相同
                display_block = cv2.resize(display_block, (block_width, block_height))
                blocks[row][col] = display_block
            
            # 删除临时文件
            if os.path.exists(temp_input):
                os.remove(temp_input)
            if os.path.exists(temp_output):
                os.remove(temp_output)
        
        # 重新组合图片
        result_image = np.zeros_like(original_image)
        for row in range(6):
            for col in range(3):
                x1 = col * block_width
                y1 = row * block_height
                x2 = x1 + block_width
                y2 = y1 + block_height
                
                result_image[y1:y2, x1:x2] = blocks[row][col]
        
        # 保存最终结果
        cv2.imwrite(output_path, result_image)
        
        return True, "图像处理成功"
        
    except Exception as e:
        error_message = f"处理图像时出错: {str(e)}"
        print(error_message, file=sys.stderr)
        return False, error_message

# 修改主函数
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python process_image.py <input_path> <output_path> <info_dir>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    info_dir = sys.argv[3]
    
    success, message = split_and_process_image(input_path, output_path, info_dir)
    if not success:
        sys.exit(1) 
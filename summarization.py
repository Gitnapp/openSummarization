import requests
import dotenv
import os
import json
dotenv.load_dotenv()

def main(transcript):
    url = os.getenv('SILICONFLOW_BASE_URL') + "/chat/completions"

    payload = {
        "model": "tencent/Hunyuan-MT-7B",
        "stream": False,
        "max_tokens": 32000,
        "temperature": 0.6,
        "top_p": 0.6,
        "top_k": 1,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": [
            {
                "role": "user",
                "content": f"用中文输出。概括文本中的细节，同时不要遗漏事实：{transcript}"
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('SILICONFLOW_API_KEY')}",
        "Content-Type": "application/json"
    }

    print("开始生成总结")

    try:
        response = requests.request("POST", url, json=payload, headers=headers, timeout=120)
    except Exception as e:
        print(f"请求API时发生网络错误: {e}")
        return f"请求API超时或失败: {e}"

    print("成功获取API响应")
    
    # 检查响应状态码
    if response.status_code != 200:
        print(f"API 请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return f"API 请求失败，状态码: {response.status_code}"
    
    try:
        # 尝试解析JSON响应
        response_data = response.json()
        
        # 检查响应数据是否为字典类型
        if not isinstance(response_data, dict):
            print(f"响应数据不是字典格式: {type(response_data)}")
            return f"响应格式错误: {response.text}"
        
        # 检查是否包含choices字段
        if 'choices' not in response_data:
            print(f"响应中没有choices字段: {response_data}")
            return f"响应格式错误: 缺少choices字段"
        
        # 检查choices是否为空
        if not response_data['choices']:
            print("choices字段为空")
            return "响应格式错误: choices为空"
        
        # 提取内容
        message = response_data['choices'][0]['message']
        content = message.get('content', '')
        reasoning = message.get('reasoning_content', '')
        
        final_output = ""
        if reasoning:
            final_output += f"【思考过程】\n{reasoning}\n\n"
        if content:
            final_output += f"【总结】\n{content}"
            
        if not final_output.strip():
            print("警告：API返回了空内容")
            return "API返回了空内容"
            
        return final_output.strip()
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return f"JSON解析失败: {response.text}"
    except Exception as e:
        print(f"解析响应时出错: {e}")
        return f"解析响应失败: {str(e)}"
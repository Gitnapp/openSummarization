import requests
import dotenv
import os
import json
dotenv.load_dotenv()

def main(transcript):
    url = os.getenv('SILICONFLOW_BASE_URL') + "/v1/chat/completions"

    payload = {
        "model": "Qwen/Qwen2.5-VL-72B-Instruct",
        "stream": False,
        "max_tokens": 4096,
        "enable_thinking": True,
        "thinking_budget": 32768,
        "min_p": 0.05,
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

    response = requests.request("POST", url, json=payload, headers=headers)

    print("成功生成总结")
    
    # 检查响应状态码
    if response.status_code != 200:
        print(f"API 请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return "API 请求失败"
    
    try:
        # 尝试解析JSON响应
        response_data = response.json()
        
        # 检查响应数据是否为字典类型
        if not isinstance(response_data, dict):
            print(f"响应数据不是字典格式: {type(response_data)}")
            print(f"响应内容: {response.text}")
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
        content = response_data['choices'][0]['message']['content']
        return content
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {response.text}")
        return f"JSON解析失败: {response.text}"
    except KeyError as e:
        print(f"响应格式错误，缺少字段: {e}")
        print(f"响应数据: {response_data}")
        return f"响应格式错误: 缺少字段 {e}"
    except Exception as e:
        print(f"解析响应时出错: {e}")
        print(f"响应内容: {response.text}")
        return f"解析响应失败: {str(e)}"
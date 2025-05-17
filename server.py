from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64
import urllib.request
import urllib.error

class CORSRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def generate_mock_brewing_plan(self, coffee_data):
        """生成模拟的冲煮方案，用于测试"""
        return {
            "brewingGoal": f"针对这款来自{coffee_data['origin']}的{coffee_data['variety']}，我们的目标是突出其独特风味。{coffee_data['process']}处理法和{coffee_data['roastLevel']}的特点要求我们特别注意温度和时间的控制。",
            "parameters": {
                "研磨度": "中细偏细（类似红糖颗粒大小）",
                "粉水比": "1:15",
                "水温": "92℃",
                "总时间": "2分30秒",
                "TDS目标": "1.3-1.4%",
                "萃取率目标": "19-20%"
            },
            "equipment": [
                "V60滤杯",
                "专业咖啡磨豆机",
                "电子秤",
                "温控壶",
                "滤纸"
            ],
            "brewingSteps": [
                {
                    "title": "准备阶段",
                    "content": "将水加热至92℃，冲洗滤纸并预热滤杯，磨好15g咖啡粉"
                },
                {
                    "title": "注水预湿",
                    "content": "倒入30g水润湿咖啡粉，等待30秒让咖啡充分膨胀"
                },
                {
                    "title": "第一次注水",
                    "content": "以螺旋形方式缓慢注入到90g水，保持水位稳定"
                },
                {
                    "title": "第二次注水",
                    "content": "等待15秒后，继续注入至150g水"
                },
                {
                    "title": "第三次注水",
                    "content": "再次等待15秒，最后注入至225g水"
                },
                {
                    "title": "收尾阶段",
                    "content": "轻轻搅拌咖啡床，等待滤完，总时间控制在2分30秒左右"
                }
            ],
            "adjustmentTips": [
                {
                    "aspect": "口感过淡",
                    "tip": "可以适当调细研磨度，或延长总萃取时间"
                },
                {
                    "aspect": "口感过浓",
                    "tip": "可以调粗研磨度，或加快注水速度"
                },
                {
                    "aspect": "酸味过重",
                    "tip": "可以提高水温至94℃，或调细研磨度"
                },
                {
                    "aspect": "苦味明显",
                    "tip": "可以降低水温至90℃，或调粗研磨度"
                }
            ]
        }

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            print("收到的请求数据:", data)
            
            if self.path == '/api/brewing':
                # 使用模拟数据进行测试
                coffee_data = {
                    "origin": data["messages"][0]["content"].split("产地：")[1].split("\n")[0].strip(),
                    "variety": data["messages"][0]["content"].split("品种：")[1].split("\n")[0].strip(),
                    "process": data["messages"][0]["content"].split("处理法：")[1].split("\n")[0].strip(),
                    "roastLevel": data["messages"][0]["content"].split("烘焙度：")[1].split("\n")[0].strip()
                }
                
                result = self.generate_mock_brewing_plan(coffee_data)
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response_data = {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(result)
                            }
                        }
                    ]
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                print("发送的响应数据:", response_data)
                
            else:
                # 处理图片识别请求
                if 'image' not in data:
                    raise Exception("缺少图片数据")
                    
                result = {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps({
                                    "variety": "阿拉比卡",
                                    "origin": "埃塞俄比亚",
                                    "process": "水洗",
                                    "roastLevel": "中度烘焙"
                                })
                            }
                        }
                    ]
                }
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
        except Exception as e:
            print("处理请求时出错:", str(e))
            self.send_response(400)
            self._send_cors_headers()
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run() 
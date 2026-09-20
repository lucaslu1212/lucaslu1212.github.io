import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import threading
import time

class HTTPRequestTool:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP 请求工具")
        self.root.geometry("800x700")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧 - 请求设置
        left_frame = ttk.LabelFrame(main_frame, text="请求设置", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 请求网址
        ttk.Label(left_frame, text="请求网址:").pack(anchor=tk.W)
        self.url_var = tk.StringVar(value="http://10.136.120.100:3000/api/students/f5fd4e9a-2b03-433d-8c49-0732270562aa/points")
        ttk.Entry(left_frame, textvariable=self.url_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # 请求方法
        ttk.Label(left_frame, text="请求方法:").pack(anchor=tk.W)
        self.method_var = tk.StringVar(value="POST")
        method_combo = ttk.Combobox(left_frame, textvariable=self.method_var, 
                                     values=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"], state="readonly")
        method_combo.pack(fill=tk.X, pady=(0, 10))
        
        # 请求体 (Payload)
        ttk.Label(left_frame, text="请求体 (Payload):").pack(anchor=tk.W)
        self.payload_text = scrolledtext.ScrolledText(left_frame, height=8, width=50)
        self.payload_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.payload_text.insert(tk.END, '{"delta":99,"reason":"课堂点名奖励"}')
        
        # 请求标头
        ttk.Label(left_frame, text="请求标头 (每行一个 Header: Name: Value):").pack(anchor=tk.W)
        self.headers_text = scrolledtext.ScrolledText(left_frame, height=8, width=50)
        self.headers_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.headers_text.insert(tk.END, "Accept: */*\nAccept-Encoding: gzip, deflate\nAccept-Language: zh-CN,zh;q=0.9\nConnection: keep-alive\nContent-Type: application/json\nHost: 10.136.120.100:3000\nOrigin: http://10.136.120.100:3000\nReferer: http://10.136.120.100:3000/roll-call.html\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")
        
        # 右侧 - 循环设置和响应
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 循环设置
        loop_frame = ttk.LabelFrame(right_frame, text="循环设置", padding="10")
        loop_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(loop_frame, text="循环次数:").pack(anchor=tk.W)
        self.loop_count_var = tk.StringVar(value="100")
        ttk.Entry(loop_frame, textvariable=self.loop_count_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(loop_frame, text="间隔时间 (秒):").pack(anchor=tk.W)
        self.interval_var = tk.StringVar(value="0.1")
        ttk.Entry(loop_frame, textvariable=self.interval_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        # 按钮
        btn_frame = ttk.Frame(loop_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.send_btn = ttk.Button(btn_frame, text="发送请求", command=self.send_request)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_sending, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        self.clear_btn = ttk.Button(btn_frame, text="清空响应", command=self.clear_response)
        self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 响应区域
        response_frame = ttk.LabelFrame(right_frame, text="响应内容", padding="10")
        response_frame.pack(fill=tk.BOTH, expand=True)
        
        # 响应信息
        self.response_info_var = tk.StringVar(value="状态代码: -\n远程地址: -")
        ttk.Label(response_frame, textvariable=self.response_info_var, justify=tk.LEFT).pack(anchor=tk.W)
        
        # 响应标头
        ttk.Label(response_frame, text="响应标头:").pack(anchor=tk.W, pady=(5, 0))
        self.response_headers_text = scrolledtext.ScrolledText(response_frame, height=5, width=40, state=tk.DISABLED)
        self.response_headers_text.pack(fill=tk.X, pady=(0, 5))
        
        # 响应内容
        ttk.Label(response_frame, text="响应体:").pack(anchor=tk.W)
        self.response_text = scrolledtext.ScrolledText(response_frame, height=8, width=40, state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # 停止标志
        self.stop_flag = False
    
    def parse_headers(self):
        """解析请求标头"""
        headers = {}
        for line in self.headers_text.get("1.0", tk.END).split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        return headers
    
    def send_request(self):
        """发送请求"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入请求网址")
            return
        
        try:
            loop_count = int(self.loop_count_var.get())
            interval = float(self.interval_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的循环次数和间隔时间")
            return
        
        self.stop_flag = False
        self.send_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 在新线程中执行请求
        thread = threading.Thread(target=self._send_requests, args=(url, loop_count, interval))
        thread.daemon = True
        thread.start()
    
    def _send_requests(self, url, loop_count, interval):
        """在后台发送请求"""
        method = self.method_var.get()
        headers = self.parse_headers()
        payload = self.payload_text.get("1.0", tk.END).strip()
        
        # 将payload编码为UTF-8字节
        if payload:
            payload = payload.encode('utf-8')
        
        for i in range(loop_count):
            if self.stop_flag:
                break
            
            try:
                # 根据方法发送请求
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                elif method == "POST":
                    response = requests.post(url, headers=headers, data=payload, timeout=10)
                elif method == "PUT":
                    response = requests.put(url, headers=headers, data=payload, timeout=10)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=10)
                elif method == "PATCH":
                    response = requests.patch(url, headers=headers, data=payload, timeout=10)
                elif method == "HEAD":
                    response = requests.head(url, headers=headers, timeout=10)
                elif method == "OPTIONS":
                    response = requests.options(url, headers=headers, timeout=10)
                
                # 更新UI
                self.root.after(0, self._update_response, response, i + 1, loop_count)
                
            except Exception as e:
                self.root.after(0, self._show_error, str(e), i + 1, loop_count)
            
            # 间隔等待
            if i < loop_count - 1 and not self.stop_flag:
                time.sleep(interval)
        
        # 恢复按钮状态
        self.root.after(0, self._reset_buttons)
    
    def _update_response(self, response, current, total):
        """更新响应内容"""
        # 更新状态信息
        info = f"状态代码: {response.status_code}\n远程地址: {response.url}\n完成: {current}/{total}"
        self.response_info_var.set(info)
        
        # 更新响应标头
        self.response_headers_text.config(state=tk.NORMAL)
        self.response_headers_text.delete("1.0", tk.END)
        for key, value in response.headers.items():
            self.response_headers_text.insert(tk.END, f"{key}: {value}\n")
        self.response_headers_text.config(state=tk.DISABLED)
        
        # 更新响应体
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, response.text)
        self.response_text.config(state=tk.DISABLED)
    
    def _show_error(self, error, current, total):
        """显示错误信息"""
        self.response_info_var.set(f"错误: {error}\n完成: {current}/{total}")
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, f"请求出错:\n{error}")
        self.response_text.config(state=tk.DISABLED)
    
    def _reset_buttons(self):
        """重置按钮状态"""
        self.send_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def stop_sending(self):
        """停止发送"""
        self.stop_flag = True
    
    def clear_response(self):
        """清空响应内容"""
        self.response_info_var.set("状态代码: -\n远程地址: -")
        self.response_headers_text.config(state=tk.NORMAL)
        self.response_headers_text.delete("1.0", tk.END)
        self.response_headers_text.config(state=tk.DISABLED)
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = HTTPRequestTool(root)
    root.mainloop()

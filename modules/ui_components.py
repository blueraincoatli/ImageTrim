import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb

class RoundedButton(tk.Canvas):
    """自定义圆角按钮"""
    
    def __init__(self, parent, width, height, text="", radius=25, color="#4285F4", text_color="white", command=None, **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.radius = radius
        self.color = color
        self.text_color = text_color
        self.command = command
        self.text = text
        
        # 绘制圆角矩形
        self.draw_rounded_rect()
        
        # 添加文本
        if text:
            self.create_text(width/2, height/2, text=text, fill=text_color, font=("Arial", 10))
        
        # 绑定事件
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def draw_rounded_rect(self):
        """绘制圆角矩形"""
        self.delete("all")
        
        # 创建圆角矩形
        self.rounded_rect = self.create_rounded_rectangle(
            2, 2, self.width-2, self.height-2, 
            radius=self.radius, fill=self.color, outline=""
        )
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def _on_click(self, event=None):
        """点击事件"""
        if self.command:
            self.command()
            
    def _on_enter(self, event=None):
        """鼠标进入事件"""
        # 可以在这里添加悬停效果
        pass
        
    def _on_leave(self, event=None):
        """鼠标离开事件"""
        # 可以在这里恢复原始状态
        pass

class RoundedFrame(tk.Canvas):
    """自定义圆角框架"""
    
    def __init__(self, parent, width, height, radius=20, color="#f0f0f0", **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.radius = radius
        self.color = color
        
        # 绘制圆角框架
        self.draw_rounded_frame()
        
    def draw_rounded_frame(self):
        """绘制圆角框架"""
        self.delete("all")
        
        # 创建圆角矩形框架
        self.create_rounded_rectangle(
            1, 1, self.width-1, self.height-1, 
            radius=self.radius, fill=self.color, outline="#d0d0d0", width=1
        )
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        
        return self.create_polygon(points, smooth=True, **kwargs)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path

class ImageToIconConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("图片转图标工具")
        self.root.geometry("900x800")
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口图标和样式
        self.setup_styles()
        
        # 存储选择的文件和预览图片
        self.selected_file = None
        self.preview_image = None
        self.size_previews = {}  # 存储不同尺寸的预览图片
        self.size_frames = {}    # 存储尺寸框架
        
        # 创建界面
        self.create_widgets()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置按钮样式
        style.configure('Custom.TButton', 
                       padding=(10, 5),
                       font=('Arial', 10, 'bold'))
        
        style.configure('Small.TButton', 
                       padding=(5, 2),
                       font=('Arial', 8))
        
        # 配置标签样式
        style.configure('Title.TLabel',
                       font=('Arial', 16, 'bold'),
                       foreground='#2c3e50',
                       background='#f0f0f0')
        
        style.configure('Info.TLabel',
                       font=('Arial', 10),
                       foreground='#34495e',
                       background='#f0f0f0')
    
    def create_widgets(self):
        """创建所有界面组件"""
        # 创建滚动框架
        self.create_scrollable_frame()
        
        # 主标题
        self.create_title_section()
        
        # 文件选择区域
        self.create_file_selection_area()
        
        # 原图预览区域
        self.create_original_preview_area()
        
        # 尺寸选择和预览区域
        self.create_size_preview_area()
        
        # 批量转换按钮区域
        self.create_batch_conversion_area()
        
        # 状态栏
        self.create_status_bar()
    
    def create_scrollable_frame(self):
        """创建可滚动的主框架"""
        # 创建画布和滚动条
        self.canvas = tk.Canvas(self.root, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_title_section(self):
        """创建标题区域"""
        title_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0', pady=20)
        title_frame.pack(fill='x')
        
        title_label = ttk.Label(title_frame, text="🖼️ 图片转图标工具", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="支持PNG、JPG、JPEG、BMP等格式转换为ICO图标", style='Info.TLabel')
        subtitle_label.pack(pady=(5, 0))
    
    def create_file_selection_area(self):
        """创建文件选择区域"""
        file_frame = tk.LabelFrame(self.scrollable_frame, text="📁 选择图片文件", 
                                  font=('Arial', 12, 'bold'), 
                                  bg='#f0f0f0', fg='#2c3e50', 
                                  padx=20, pady=15)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        # 文件路径显示
        self.file_path_var = tk.StringVar()
        self.file_path_var.set("未选择文件")
        
        path_frame = tk.Frame(file_frame, bg='#f0f0f0')
        path_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(path_frame, text="文件路径：", font=('Arial', 10), 
                bg='#f0f0f0', fg='#2c3e50').pack(side='left')
        
        self.path_label = tk.Label(path_frame, textvariable=self.file_path_var,
                                  font=('Arial', 10), bg='#f0f0f0', 
                                  fg='#7f8c8d', wraplength=500, justify='left')
        self.path_label.pack(side='left', padx=(10, 0))
        
        # 选择文件按钮
        select_btn = ttk.Button(file_frame, text="🔍 选择图片文件", 
                               command=self.select_file, style='Custom.TButton')
        select_btn.pack(pady=5)
    
    def create_original_preview_area(self):
        """创建原图预览区域"""
        preview_frame = tk.LabelFrame(self.scrollable_frame, text="👁️ 原图预览", 
                                     font=('Arial', 12, 'bold'), 
                                     bg='#f0f0f0', fg='#2c3e50',
                                     padx=20, pady=15)
        preview_frame.pack(fill='x', padx=20, pady=10)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(preview_frame, width=200, height=200, 
                                       bg='white', relief='sunken', bd=2)
        self.preview_canvas.pack(pady=10)
        
        # 图片信息标签
        self.info_label = tk.Label(preview_frame, text="请选择一张图片进行预览", 
                                  font=('Arial', 10), bg='#f0f0f0', fg='#7f8c8d')
        self.info_label.pack()
    
    def create_size_preview_area(self):
        """创建尺寸选择和预览区域"""
        size_frame = tk.LabelFrame(self.scrollable_frame, text="📏 图标尺寸预览与下载", 
                                  font=('Arial', 12, 'bold'), 
                                  bg='#f0f0f0', fg='#2c3e50',
                                  padx=20, pady=15)
        size_frame.pack(fill='x', padx=20, pady=10)
        
        # 说明文字
        tk.Label(size_frame, text="选择图片后，各种尺寸的图标预览将显示在下方，点击对应的下载按钮可单独保存", 
                font=('Arial', 10), bg='#f0f0f0', fg='#2c3e50').pack(anchor='w', pady=(0, 15))
        
        # 创建网格容器
        self.sizes_container = tk.Frame(size_frame, bg='#f0f0f0')
        self.sizes_container.pack(fill='x')
        
        # 预设尺寸
        sizes = [16, 24, 32, 48, 64, 96, 128, 256]
        
        # 创建每个尺寸的预览框
        for i, size in enumerate(sizes):
            self.create_size_preview_item(self.sizes_container, size, i)
    
    def create_size_preview_item(self, parent, size, index):
        """创建单个尺寸的预览项"""
        # 计算网格位置（每行4个）
        row = index // 4
        col = index % 4
        
        # 创建单个尺寸的框架
        item_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1, padx=10, pady=10)
        item_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # 配置网格权重
        parent.grid_columnconfigure(col, weight=1)
        
        # 尺寸标题
        title_label = tk.Label(item_frame, text=f"{size}×{size}", 
                              font=('Arial', 10, 'bold'), 
                              bg='#ffffff', fg='#2c3e50')
        title_label.pack(pady=(0, 5))
        
        # 预览画布
        canvas_size = min(size + 20, 80)  # 限制画布最大尺寸
        preview_canvas = tk.Canvas(item_frame, width=canvas_size, height=canvas_size,
                                  bg='white', relief='solid', bd=1)
        preview_canvas.pack(pady=(0, 5))
        
        # 下载按钮
        download_btn = ttk.Button(item_frame, text="下载", style='Small.TButton',
                                 command=lambda s=size: self.save_single_size(s))
        download_btn.pack()
        
        # 存储预览画布和框架的引用
        self.size_previews[size] = preview_canvas
        self.size_frames[size] = item_frame
    
    def create_batch_conversion_area(self):
        """创建批量转换按钮区域"""
        batch_frame = tk.LabelFrame(self.scrollable_frame, text="🔄 批量转换", 
                                   font=('Arial', 12, 'bold'), 
                                   bg='#f0f0f0', fg='#2c3e50',
                                   padx=20, pady=15)
        batch_frame.pack(fill='x', padx=20, pady=10)
        
        # 说明文字
        tk.Label(batch_frame, text="点击下方按钮可一次性生成所有尺寸的图标文件", 
                font=('Arial', 10), bg='#f0f0f0', fg='#2c3e50').pack(pady=(0, 10))
        
        # 批量转换按钮
        convert_btn = ttk.Button(batch_frame, text="🎯 生成所有尺寸图标", 
                                command=self.batch_convert, style='Custom.TButton')
        convert_btn.pack()
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        
        status_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        status_frame.pack(fill='x', padx=20, pady=10)
        
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               font=('Arial', 10), bg='#f0f0f0', fg='#7f8c8d')
        status_label.pack(side='left')
    
    def select_file(self):
        """选择图片文件"""
        filetypes = [
            ("图片文件", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                self.selected_file = filename
                self.file_path_var.set(filename)
                self.load_preview()
                self.status_var.set("图片加载成功")
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片：{str(e)}")
                self.status_var.set("图片加载失败")
    
    def load_preview(self):
        """加载预览图片"""
        if not self.selected_file:
            return
        
        try:
            # 加载原图预览
            image = Image.open(self.selected_file)
            
            # 显示图片信息
            self.info_label.config(text=f"原始尺寸：{image.size[0]}×{image.size[1]} 像素")
            
            # 调整原图预览大小
            preview_size = (200, 200)
            preview = image.copy()
            preview.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # 在画布中居中显示
            x = (preview_size[0] - preview.size[0]) // 2
            y = (preview_size[1] - preview.size[1]) // 2
            
            # 更新预览
            self.preview_image = ImageTk.PhotoImage(preview)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_image)
            
            # 更新所有尺寸的预览
            self.update_size_previews(image)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览图片时出错：{str(e)}")
    
    def update_size_previews(self, image):
        """更新所有尺寸的预览图片"""
        for size, canvas in self.size_previews.items():
            # 创建指定尺寸的预览
            preview = image.copy()
            preview.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # 创建白色背景
            bg = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            
            # 计算居中位置
            x = (size - preview.size[0]) // 2
            y = (size - preview.size[1]) // 2
            bg.paste(preview, (x, y))
            
            # 缩放到画布大小
            canvas_size = min(size + 20, 80)
            display_size = (canvas_size, canvas_size)
            bg_resized = bg.resize(display_size, Image.Resampling.LANCZOS)
            
            # 更新预览
            photo = ImageTk.PhotoImage(bg_resized)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=photo)
            canvas.image = photo  # 保持引用
    
    def save_single_size(self, size):
        """保存单个尺寸的图标"""
        if not self.selected_file:
            messagebox.showwarning("警告", "请先选择一张图片")
            return
        
        try:
            # 获取保存路径
            initial_file = f"icon_{size}x{size}.ico"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".ico",
                filetypes=[("ICO 文件", "*.ico")],
                initialfile=initial_file
            )
            
            if save_path:
                # 在新线程中执行转换
                thread = threading.Thread(
                    target=self._convert_single_size,
                    args=(size, save_path)
                )
                thread.start()
                
        except Exception as e:
            messagebox.showerror("错误", f"保存图标时出错：{str(e)}")
    
    def _convert_single_size(self, size, save_path):
        """在新线程中执行单个尺寸的转换"""
        try:
            self.status_var.set(f"正在生成 {size}×{size} 图标...")
            
            # 加载原图
            image = Image.open(self.selected_file)
            
            # 创建指定尺寸的图标
            icon = image.copy()
            icon.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # 创建白色背景
            bg = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            
            # 计算居中位置
            x = (size - icon.size[0]) // 2
            y = (size - icon.size[1]) // 2
            bg.paste(icon, (x, y))
            
            # 保存为ICO文件
            bg.save(save_path, format='ICO')
            
            self.status_var.set(f"{size}×{size} 图标已保存")
            
        except Exception as e:
            self.status_var.set(f"生成 {size}×{size} 图标时出错")
            messagebox.showerror("错误", f"生成图标时出错：{str(e)}")
    
    def batch_convert(self):
        """批量转换所有尺寸的图标"""
        if not self.selected_file:
            messagebox.showwarning("警告", "请先选择一张图片")
            return
        
        try:
            # 获取保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            
            if save_dir:
                # 在新线程中执行转换
                thread = threading.Thread(
                    target=self._batch_convert,
                    args=(save_dir,)
                )
                thread.start()
                
        except Exception as e:
            messagebox.showerror("错误", f"批量转换时出错：{str(e)}")
    
    def _batch_convert(self, save_dir):
        """在新线程中执行批量转换"""
        try:
            self.status_var.set("正在批量生成图标...")
            
            # 加载原图
            image = Image.open(self.selected_file)
            
            # 获取所有尺寸
            sizes = list(self.size_previews.keys())
            
            # 转换每个尺寸
            for size in sizes:
                try:
                    # 更新状态
                    self.status_var.set(f"正在生成 {size}×{size} 图标...")
                    
                    # 创建指定尺寸的图标
                    icon = image.copy()
                    icon.thumbnail((size, size), Image.Resampling.LANCZOS)
                    
                    # 创建白色背景
                    bg = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                    
                    # 计算居中位置
                    x = (size - icon.size[0]) // 2
                    y = (size - icon.size[1]) // 2
                    bg.paste(icon, (x, y))
                    
                    # 保存为ICO文件
                    save_path = os.path.join(save_dir, f"icon_{size}x{size}.ico")
                    bg.save(save_path, format='ICO')
                    
                except Exception as e:
                    messagebox.showerror("错误", f"生成 {size}×{size} 图标时出错：{str(e)}")
            
            self.status_var.set("批量转换完成")
            messagebox.showinfo("完成", "所有图标已生成完成！")
            
        except Exception as e:
            self.status_var.set("批量转换失败")
            messagebox.showerror("错误", f"批量转换时出错：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToIconConverter(root)
    root.mainloop()
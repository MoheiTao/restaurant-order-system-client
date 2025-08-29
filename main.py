import tkinter as tk
from tkinter import ttk, messagebox
import requests

class RestaurantOrderSystem:
    def __init__(self, root):
        self.root = root
        self.root.title('餐厅点菜系统')
        self.root.geometry('800x600')
        
        self.server_url = 'http://localhost:5000'
        
        self.setup_ui()
        self.load_dishes()
        
    def setup_ui(self):
        # 左侧菜品列表
        self.dish_frame = ttk.LabelFrame(self.root, text='菜品列表')
        self.dish_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.dish_tree = ttk.Treeview(self.dish_frame, columns=('name', 'price', 'category'), show='headings')
        self.dish_tree.heading('name', text='名称')
        self.dish_tree.heading('price', text='价格')
        self.dish_tree.heading('category', text='类别')
        self.dish_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右侧订单区
        self.order_frame = ttk.LabelFrame(self.root, text='当前订单')
        self.order_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 桌号输入
        ttk.Label(self.order_frame, text='桌号：').pack()
        self.table_number = ttk.Entry(self.order_frame)
        self.table_number.pack()
        
        # 订单项列表
        self.order_tree = ttk.Treeview(self.order_frame, columns=('name', 'price', 'quantity', 'subtotal'), show='headings')
        self.order_tree.heading('name', text='菜品')
        self.order_tree.heading('price', text='单价')
        self.order_tree.heading('quantity', text='数量')
        self.order_tree.heading('subtotal', text='小计')
        self.order_tree.pack(fill=tk.BOTH, expand=True)
        
        # 总计
        self.total_label = ttk.Label(self.order_frame, text='总计：￥0.00')
        self.total_label.pack()
        
        # 按钮区
        button_frame = ttk.Frame(self.order_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text='添加到订单', command=self.add_to_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='删除选中项', command=self.remove_from_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='提交订单', command=self.submit_order).pack(side=tk.LEFT, padx=5)
        
    def load_dishes(self):
        try:
            response = requests.get(f'{self.server_url}/dishes')
            dishes = response.json()
            
            for dish in dishes:
                self.dish_tree.insert('', 'end', values=(dish['name'], f'￥{dish["price"]:.2f}', dish['category']))
        except Exception as e:
            messagebox.showerror('错误', f'加载菜品失败：{str(e)}')
    
    def add_to_order(self):
        selection = self.dish_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请选择要添加的菜品')
            return
            
        item = self.dish_tree.item(selection[0])
        name = item['values'][0]
        price = float(item['values'][1].replace('￥', ''))
        
        # 弹出数量输入窗口
        quantity_window = tk.Toplevel(self.root)
        quantity_window.title('输入数量')
        quantity_window.geometry('200x100')
        
        ttk.Label(quantity_window, text='数量：').pack()
        quantity_var = tk.StringVar(value='1')
        quantity_entry = ttk.Entry(quantity_window, textvariable=quantity_var)
        quantity_entry.pack()
        
        def confirm():
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    raise ValueError('数量必须大于0')
                    
                subtotal = price * quantity
                self.order_tree.insert('', 'end', values=(name, f'￥{price:.2f}', quantity, f'￥{subtotal:.2f}'))
                self.update_total()
                quantity_window.destroy()
            except ValueError as e:
                messagebox.showerror('错误', str(e))
        
        ttk.Button(quantity_window, text='确定', command=confirm).pack(pady=5)
    
    def remove_from_order(self):
        selection = self.order_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请选择要删除的项目')
            return
            
        self.order_tree.delete(selection[0])
        self.update_total()
    
    def update_total(self):
        total = 0
        for item in self.order_tree.get_children():
            subtotal = float(self.order_tree.item(item)['values'][3].replace('￥', ''))
            total += subtotal
        self.total_label.config(text=f'总计：￥{total:.2f}')
    
    def submit_order(self):
        if not self.table_number.get():
            messagebox.showwarning('提示', '请输入桌号')
            return
            
        if not self.order_tree.get_children():
            messagebox.showwarning('提示', '订单为空')
            return
            
        try:
            table_number = int(self.table_number.get())
            order_items = []
            
            for item in self.order_tree.get_children():
                values = self.order_tree.item(item)['values']
                order_items.append({
                    'name': values[0],
                    'price': float(values[1].replace('￥', '')),
                    'quantity': int(values[2])
                })
            
            response = requests.post(f'{self.server_url}/orders', json={
                'table_number': table_number,
                'items': order_items
            })
            
            if response.status_code == 200:
                messagebox.showinfo('成功', '订单提交成功')
                # 清空订单
                self.order_tree.delete(*self.order_tree.get_children())
                self.table_number.delete(0, tk.END)
                self.update_total()
            else:
                messagebox.showerror('错误', response.json().get('error', '提交订单失败'))
                
        except ValueError:
            messagebox.showerror('错误', '桌号必须为数字')
        except Exception as e:
            messagebox.showerror('错误', f'提交订单失败：{str(e)}')

if __name__ == '__main__':
    root = tk.Tk()
    app = RestaurantOrderSystem(root)
    root.mainloop()

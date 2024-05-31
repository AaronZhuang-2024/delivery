from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import time

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def button_1_click(self, **event_args):
        """This method is called when the user clicks the button"""
        case_number = self.text_box_1.text
        start_page = self.text_box_2.text
        end_page = self.text_box_3.text
        
        if not case_number:
            alert("请输入有效的案号")
            return
        
        try:
            start_page = int(start_page)
            end_page = int(end_page)
        except ValueError:
            alert("请输入有效的页码范围")
            return
        
        Notification("该案号已提交!").show()
        
        # 调用后端函数
        try:
            print(f"Calling server with case_number: {case_number}, start_page: {start_page}, end_page: {end_page}")  # Debug info
            results = anvil.server.call('search_and_store_delivery_notices', case_number, start_page, end_page)
            self.clear_inputs()
        
            if results:
                self.result_text.text = '\n'.join(results)
            else:
                self.result_text.text = "没有找到与任何案号相关的送达公告。"
        except anvil.server.InternalError as e:
            alert(f"服务器内部错误: {e}")
        except anvil.server.RuntimeUnavailableError as e:
            alert(f"服务器运行不可用: {e}")
        except Exception as e:
            alert(f"发生错误: {e}")
  
    def clear_inputs(self):
        # Clear our three text boxes
        self.text_box_1.text = ""
        self.text_box_2.text = ""
        self.text_box_3.text = ""

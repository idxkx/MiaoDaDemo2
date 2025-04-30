import time
import random # 用于模拟不同的结果
import os

# --- 新增导入 --- 
from PyQt6.QtCore import QObject, pyqtSignal
import torch
import torchvision.transforms as transforms
from PIL import Image
# ---

# --- 新增导入 torchvision.models --- 
# import torchvision.models as models
import torch.nn as nn # 需要导入 nn 来修改全连接层
# ---

# --- 新增：导入我们自定义的模型 --- 
from model import ClothesModel
# ---

# --- 定义模型路径和类别映射 --- 
DEFAULT_MODEL_PATH = "models/MD_resnet50_40_32_10e4_clothes_model/best_model_MD_resnet50_40_32_10e4_clothes_model_epoch4.pth"

NUM_CLASSES = 50

# --- 修改：使用建议的中文类别名称列表 --- 
CLASS_NAMES = [
    # 类型 1 (上装类) - 20个
    "冲锋衣", "西装外套", "女式衬衫", "飞行员夹克", "纽扣衬衫", "开襟衫", "法兰绒衬衫", 
    "挂脖上衣", "亨利衫", "连帽衫", "夹克", "运动上衣", "派克大衣", "海军呢大衣", "斗篷(上装)", 
    "毛衣", "背心", "T恤", "上衣", "高领衫", 
    # 类型 2 (下装类) - 16个
    "中裤", "卡其裤", "阔腿裤", 
    "剪短裤", "高乔裤", "牛仔裤", "紧身牛仔裤", "马裤", "慢跑裤", "打底裤", 
    "纱笼", "短裤", "半身裙", "运动裤", "运动短裤", "泳裤", 
    # 类型 3 (全身/外套类) - 14个
    "长衫", 
    "披肩", "大衣", "罩衫", "连衣裙", "连体裤", "卡夫坦长袍", "和服", "睡裙", 
    "连身衣", "浴袍", "连身短裤", "衬衫裙", "太阳裙"
]
# 确保正好是 50 个类别
assert len(CLASS_NAMES) == NUM_CLASSES, f"类别名称列表长度 ({len(CLASS_NAMES)}) 与 NUM_CLASSES ({NUM_CLASSES}) 不匹配！"
# ---

# 属性数量保持不变
NUM_ATTRIBUTES = 26
# ---

# --- 新增：后台识别 Worker ---
class RecognitionWorker(QObject):
    """在后台线程执行识别任务的 Worker"""
    finished = pyqtSignal(dict)  # 任务完成信号，发送识别结果字典
    error = pyqtSignal(str)      # 任务出错信号，发送错误信息字符串

    def __init__(self, service, image_path):
        super().__init__()
        self.service = service
        self.image_path = image_path

    def run(self):
        """执行识别任务"""
        try:
            # 调用实际的识别逻辑
            result = self.service.recognize_real(self.image_path)
            self.finished.emit(result)
        except Exception as e:
            # 发送错误信号
            self.error.emit(f"识别过程中出错: {e}")
# --- Worker 结束 ---


class ClothingRecognitionService:
    """
    负责加载服装识别模型并执行推理。
    """
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Initializing ClothingRecognitionService. Using device: {self.device}")
        self.model = self._load_model()
        self.transform = self._get_transformations()

    def _load_model(self):
        """加载自定义的 ClothesModel 并应用 state_dict 权重"""
        if not self.model_path or not os.path.exists(self.model_path):
            print(f"错误: 模型文件路径无效或文件不存在: {self.model_path}")
            return None
        try:
            print(f"Loading model weights from: {self.model_path}")

            # 1. 实例化我们自己的 ClothesModel 结构
            #    重要：使用训练时的骨干网络名称和类别/属性数量
            print(f"Instantiating ClothesModel with backbone='efficientnet_b4', num_categories={NUM_CLASSES}, num_attributes={NUM_ATTRIBUTES}")
            model = ClothesModel(
                num_categories=NUM_CLASSES,
                num_attributes=NUM_ATTRIBUTES,
                backbone='efficientnet_b4' # <--- 从 'resnet50' 改为 'efficientnet_b4'
            )

            # 2. 加载状态字典 (权重)
            state_dict = torch.load(self.model_path, map_location=self.device)

            # 3. 将权重加载到模型实例中
            #    如果 state_dict 键名与模型层名完全匹配，可以直接加载
            #    如果遇到键名不匹配（例如多了'module.'前缀），可能需要处理 state_dict
            model.load_state_dict(state_dict)
            print("Weights loaded into ClothesModel structure.")

            # 4. 将模型移至设备并设置为评估模式
            model = model.to(self.device)
            model.eval()
            print("ClothesModel loaded and set to eval mode successfully.")
            return model

        except FileNotFoundError:
            print(f"错误: 模型文件未找到: {self.model_path}")
            return None
        except RuntimeError as e:
            print(f"错误: 加载模型权重失败，请检查:")
            print(f"  - 骨干网络名称 ('efficientnet_b4') 是否正确？")
            print(f"  - 类别数量 ({NUM_CLASSES}) 和属性数量 ({NUM_ATTRIBUTES}) 是否与训练时一致？")
            print(f"  - 模型文件是否损坏？")
            print(f"  - 原始错误: {e}")
            return None
        except ImportError as e:
             print(f"错误：无法导入模型定义或其依赖。确保 ClothesModel 类及其依赖（如 timm）可用。错误：{e}")
             return None
        except Exception as e:
            print(f"错误: 加载模型时发生意外错误: {e}")
            import traceback
            traceback.print_exc() # 打印详细堆栈
            return None

    def _get_transformations(self):
        """获取图像预处理转换"""
        # TODO: 这些参数需要根据模型的训练配置来确定
        return transforms.Compose([
            transforms.Resize((224, 224)), # 调整大小
            transforms.ToTensor(),         # 转换为 Tensor
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) # 标准化
        ])

    def _preprocess_image(self, image_path: str) -> torch.Tensor | None:
        """加载、预处理图像并返回 Tensor"""
        try:
            image = Image.open(image_path).convert('RGB') # 确保是 RGB
            image_tensor = self.transform(image)
            # 添加 batch 维度 (模型通常需要 BxCxHxW)
            return image_tensor.unsqueeze(0).to(self.device)
        except FileNotFoundError:
            print(f"错误: 图片文件未找到: {image_path}")
            return None
        except Exception as e:
            print(f"错误: 预处理图片失败: {e}")
            return None

    def _postprocess_results(self, model_outputs) -> dict:
        """处理 ClothesModel 的输出元组，提取类别信息，并在置信度高时标记用于标签"""
        if not isinstance(model_outputs, tuple) or len(model_outputs) < 1:
            print("错误: 模型输出格式不符合预期 (应为元组)")
            return {}

        # 解包输出元组，我们目前只用第一个 (category_logits)
        category_logits = model_outputs[0]
        # attribute_logits = model_outputs[1] # 备用

        if category_logits is None:
            print("错误: 模型输出中 category_logits 为 None")
            return {}
        try:
            # 处理类别 Logits (与之前类似)
            probabilities = torch.softmax(category_logits, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            category_idx = predicted_idx.item()
            category_name = CLASS_NAMES[category_idx] if 0 <= category_idx < len(CLASS_NAMES) else "未知类别"
            confidence_score = confidence.item()
            print(f"Predicted category: {category_name} (Confidence: {confidence_score:.4f})")

            result = {
                "category": category_name,
                "confidence": confidence_score
            }

            # --- 新增：如果置信度 >= 0.85，添加用于标签的信息 --- 
            if confidence_score >= 0.85:
                 result['tag_category'] = category_name # 将识别出的类别作为标签内容
                 # result['tag_color'] = ... # 未来可以添加颜色标签
                 # result['tag_material'] = ... # 未来可以添加材质标签
                 print(f"Confidence >= 0.85, marking '{category_name}' for tagging.")
            # ---

            return result
        except IndexError:
             print(f"错误: 预测的类别索引 {category_idx} 超出 CLASS_NAMES 列表范围 (长度 {len(CLASS_NAMES)})。请确认 CLASS_NAMES 是否正确且完整。")
             return {}
        except Exception as e:
            print(f"错误: 后处理模型结果失败: {e}")
            return {}

    def recognize_real(self, image_path: str) -> dict:
        """对给定图片执行真正的 AI 识别"""
        if not self.model:
            print("错误: 模型未加载，无法执行识别。")
            # return {} # 或者抛出异常
            raise RuntimeError("模型未成功加载")

        print(f"Starting real recognition for: {image_path}")
        image_tensor = self._preprocess_image(image_path)
        if image_tensor is None:
            raise ValueError("图片预处理失败")

        with torch.no_grad(): # 关闭梯度计算，节省内存并加速
            model_outputs = self.model(image_tensor)

        results = self._postprocess_results(model_outputs)
        print(f"Real recognition finished. Results: {results}")
        return results

    # 保留旧的模拟方法，以备不时之需或对比
    def recognize_dummy(self, image_path: str) -> dict:
        """(保留的模拟方法)"""
        print(f"Recognizing image: {image_path} (Placeholder)")
        time.sleep(1.5) # 模拟耗时操作
        possible_results = [
            {"category": "上装", "color": "蓝色", "material": "棉", "brand": "优衣库"},
            {"category": "下装", "color": "黑色", "material": "涤纶"},
            {"category": "连衣裙", "color": "红色", "material": "丝"},
            {"category": "外套", "color": "灰色", "brand": "ZARA"},
            {"category": "鞋子", "color": "白色", "brand": "耐克"},
        ]
        results = random.choice(possible_results)
        print(f"Recognition result (Placeholder): {results}")
        return results 
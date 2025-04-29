import torch
import time

def print_gpu_info():
    """打印GPU基本信息"""
    print("\n=== GPU基本信息 ===")
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA是否可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU设备数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"\nGPU {i} 信息:")
            print(f"设备名称: {torch.cuda.get_device_name(i)}")
            print(f"当前显存使用: {torch.cuda.memory_allocated(i) / 1024**2:.2f} MB")
            print(f"显存总量: {torch.cuda.get_device_properties(i).total_memory / 1024**2:.2f} MB")

def test_matrix_operations(size=10000):
    """测试矩阵运算性能"""
    print("\n=== 矩阵运算性能测试 ===")
    
    # 创建大矩阵
    print(f"\n创建 {size}x{size} 的矩阵...")
    
    # CPU测试
    start_time = time.time()
    a_cpu = torch.randn(size, size)
    b_cpu = torch.randn(size, size)
    c_cpu = torch.matmul(a_cpu, b_cpu)
    cpu_time = time.time() - start_time
    print(f"CPU矩阵乘法耗时: {cpu_time:.2f} 秒")
    
    # GPU测试
    if torch.cuda.is_available():
        start_time = time.time()
        a_gpu = torch.randn(size, size, device='cuda')
        b_gpu = torch.randn(size, size, device='cuda')
        torch.cuda.synchronize()  # 确保GPU操作完成
        start_compute = time.time()
        c_gpu = torch.matmul(a_gpu, b_gpu)
        torch.cuda.synchronize()  # 确保GPU操作完成
        gpu_time = time.time() - start_compute
        total_time = time.time() - start_time
        print(f"GPU矩阵乘法耗时: {gpu_time:.2f} 秒")
        print(f"GPU总耗时(包含数据传输): {total_time:.2f} 秒")
        print(f"GPU加速比: {cpu_time/gpu_time:.2f}x")

def test_neural_network():
    """测试神经网络基础运算性能"""
    print("\n=== 神经网络基础运算测试 ===")
    
    # 创建一个简单的神经网络
    class SimpleNet(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = torch.nn.Linear(1000, 2000)
            self.fc2 = torch.nn.Linear(2000, 1000)
            self.relu = torch.nn.ReLU()
        
        def forward(self, x):
            x = self.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    # 测试数据
    batch_size = 1000
    input_size = 1000
    
    # CPU测试
    model_cpu = SimpleNet()
    input_cpu = torch.randn(batch_size, input_size)
    start_time = time.time()
    output_cpu = model_cpu(input_cpu)
    cpu_time = time.time() - start_time
    print(f"CPU前向传播耗时: {cpu_time:.2f} 秒")
    
    # GPU测试
    if torch.cuda.is_available():
        model_gpu = SimpleNet().cuda()
        input_gpu = torch.randn(batch_size, input_size, device='cuda')
        torch.cuda.synchronize()
        start_time = time.time()
        output_gpu = model_gpu(input_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time
        print(f"GPU前向传播耗时: {gpu_time:.2f} 秒")
        print(f"GPU加速比: {cpu_time/gpu_time:.2f}x")

if __name__ == "__main__":
    print("开始GPU性能测试...")
    print_gpu_info()
    test_matrix_operations()
    test_neural_network()
    print("\n性能测试完成！") 
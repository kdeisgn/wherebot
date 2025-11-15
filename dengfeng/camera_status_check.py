#!/usr/bin/env python3
import pyrealsense2 as rs

def check_realsense_status():
    """检查RealSense摄像头状态"""
    print("🔍 检查RealSense摄像头状态...")
    
    try:
        # 创建上下文
        ctx = rs.context()
        devices = ctx.query_devices()
        
        print(f"找到 {len(devices)} 个RealSense设备")
        
        for i, device in enumerate(devices):
            print(f"\n📷 设备 {i}:")
            print(f"  名称: {device.get_info(rs.camera_info.name)}")
            print(f"  序列号: {device.get_info(rs.camera_info.serial_number)}")
            print(f"  固件版本: {device.get_info(rs.camera_info.firmware_version)}")
            
            # 检查传感器
            sensors = device.query_sensors()
            print(f"  传感器数量: {len(sensors)}")
            
            for j, sensor in enumerate(sensors):
                print(f"    传感器 {j}: {sensor.get_info(rs.camera_info.name)}")
    
    except Exception as e:
        print(f"❌ 检查摄像头状态时出错: {e}")

def test_camera_stream():
    """测试摄像头数据流"""
    print("\n🎥 测试摄像头数据流...")
    
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        
        # 尝试不同的配置
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        print("启动管道...")
        pipeline.start(config)
        print("✅ 管道启动成功")
        
        # 尝试获取几帧
        for i in range(10):
            frames = pipeline.wait_for_frames(5000)  # 5秒超时
            color_frame = frames.get_color_frame()
            
            if color_frame:
                print(f"✅ 第{i+1}帧: 获取成功 - 宽度: {color_frame.get_width()}, 高度: {color_frame.get_height()}")
                
                # 检查帧数据
                frame_data = color_frame.get_data()
                print(f"   数据大小: {len(frame_data)} 字节")
                print(f"   数据类型: {type(frame_data)}")
                
            else:
                print(f"❌ 第{i+1}帧: 获取失败")
        
        pipeline.stop()
        print("✅ 摄像头数据流测试完成")
        
    except Exception as e:
        print(f"❌ 摄像头数据流测试失败: {e}")

if __name__ == "__main__":
    check_realsense_status()
    test_camera_stream()
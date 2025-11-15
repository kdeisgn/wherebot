#!/usr/bin/env python3
import cv2
import numpy as np
from ultralytics import YOLO

def test_yolo():
    """测试YOLOv8是否工作"""
    print("测试YOLOv8...")
    model = YOLO('yolov8n.pt')
    results = model('https://ultralytics.com/images/bus.jpg')
    print("✅ YOLOv8测试成功!")
    for r in results:
        for box in r.boxes:
            class_name = model.names[int(box.cls)]
            print(f"检测到: {class_name}, 置信度: {float(box.conf):.2f}")

def test_camera():
    """测试RealSense摄像头"""
    print("测试RealSense摄像头...")
    try:
        import pyrealsense2 as rs
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
        print("✅ RealSense摄像头连接成功!")
        
        # 获取一帧图像
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if color_frame:
            image = np.asanyarray(color_frame.get_data())
            print(f"✅ 图像尺寸: {image.shape}")
        
        pipeline.stop()
        return True
    except Exception as e:
        print(f"❌ 摄像头错误: {e}")
        return False

if __name__ == "__main__":
    test_yolo()
    test_camera()
#!/usr/bin/env python3
import cv2
import numpy as np
from ultralytics import YOLO

class DesktopObjectDetector:
    def __init__(self):
        print("加载YOLOv8模型...")
        self.model = YOLO('yolov8n.pt')
        # YOLO预训练模型中可能与盒子相关的类别
        self.box_related_classes = ['box', 'package', 'cardboard', 'paper', 'tissue']
        
    def detect_objects(self):
        """检测桌面物体"""
        try:
            import pyrealsense2 as rs
            
            # 初始化摄像头
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            pipeline.start(config)
            print("🎥 摄像头启动成功! 将纸巾盒和纸箱放在摄像头前")
            print("📦 按 'q' 退出, 按 's' 保存当前图像")
            
            while True:
                # 获取帧
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue
                
                # 转换为numpy数组
                image = np.asanyarray(color_frame.get_data())
                
                # YOLO检测
                results = self.model(image)
                
                # 显示结果
                annotated_frame = results[0].plot()
                cv2.imshow('桌面物体检测 - Stretch', annotated_frame)
                
                # 专门检测盒子类物体
                self._detect_box_objects(results, image)
                
                # 键盘控制
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # 保存当前图像用于后续训练
                    cv2.imwrite('desktop_objects.jpg', image)
                    print("💾 图像已保存为 'desktop_objects.jpg'")
                    
            pipeline.stop()
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"摄像头错误: {e}")
    
    def _detect_box_objects(self, results, image):
        """专门检测盒子类物体"""
        box_detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                # 检查是否是盒子类物体
                if any(box_word in class_name.lower() for box_word in self.box_related_classes):
                    box_detections.append((class_name, confidence))
                    
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    print(f"📦 检测到盒子类物体: {class_name} ({confidence:.2f})")
                    print(f"   位置: [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")
        
        # 如果没有检测到盒子类物体，给出提示
        if not box_detections and len(results[0].boxes) > 0:
            print("👀 检测到物体，但没有识别为盒子类。尝试调整物体位置或光线。")

if __name__ == "__main__":
    detector = DesktopObjectDetector()
    detector.detect_objects()
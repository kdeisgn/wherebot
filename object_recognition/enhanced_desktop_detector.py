#!/usr/bin/env python3
import cv2
import numpy as np
from ultralytics import YOLO

class EnhancedDesktopDetector:
    def __init__(self):
        print("🚀 初始化增强版物体检测器...")
        self.model = YOLO('yolov8n.pt')
        self.box_related_classes = ['box', 'package', 'cardboard', 'paper', 'tissue']
        
        # 检测统计
        self.detection_count = 0
        self.box_detections = []
        
    def detect_objects(self):
        """增强版物体检测"""
        try:
            import pyrealsense2 as rs
            
            # 初始化RealSense摄像头
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)  # 更高分辨率
            pipeline.start(config)
            
            print("🎥 Stretch RealSense摄像头启动成功!")
            print("📋 控制说明:")
            print("   q - 退出程序")
            print("   s - 保存当前图像")
            print("   c - 清除检测历史")
            print("   d - 显示/隐藏详细信息")
            print("\n📦 将纸巾盒和纸箱放在摄像头前...")
            
            show_details = True
            
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
                self.detection_count += 1
                
                # 创建增强的可视化界面
                display_image = self._create_enhanced_display(image, results, show_details)
                
                # 显示结果
                cv2.imshow('Stretch 桌面物体检测 - RealSense D405摄像头', display_image)
                
                # 专门检测盒子类物体
                current_boxes = self._detect_box_objects(results)
                
                # 键盘控制
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_image(image)
                elif key == ord('c'):
                    self.box_detections = []
                    print("🗑️ 检测历史已清除")
                elif key == ord('d'):
                    show_details = not show_details
                    print(f"🔍 详细信息: {'开启' if show_details else '关闭'}")
                    
            pipeline.stop()
            cv2.destroyAllWindows()
            print(f"\n📊 检测会话总结: 总共处理了 {self.detection_count} 帧")
            
        except Exception as e:
            print(f"❌ 摄像头错误: {e}")
    
    def _create_enhanced_display(self, image, results, show_details=True):
        """创建增强的可视化界面"""
        # 使用YOLO的默认标注
        display_image = results[0].plot()
        
        # 添加自定义信息层
        h, w = display_image.shape[:2]
        
        # 创建信息面板
        info_panel = np.zeros((100, w, 3), dtype=np.uint8)
        
        # 添加标题和状态信息
        cv2.putText(info_panel, "Stretch RealSense D405 - 物体检测", 
                   (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(info_panel, f"检测帧数: {self.detection_count}", 
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(info_panel, f"历史检测数: {len(self.box_detections)}", 
                   (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 垂直拼接图像和信息面板
        final_image = np.vstack([display_image, info_panel])
        
        # 如果显示详细信息，添加检测结果
        if show_details:
            detail_text = self._get_detection_details(results)
            y_offset = h + 100
            for i, line in enumerate(detail_text):
                cv2.putText(final_image, line, (10, y_offset + i*20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        return final_image
    
    def _get_detection_details(self, results):
        """获取检测详细信息"""
        details = []
        details.append("实时检测结果:")
        
        for r in results:
            boxes = r.boxes
            if len(boxes) == 0:
                details.append("  未检测到物体")
            else:
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    if confidence > 0.5:  # 只显示高置信度检测
                        status = "📦" if any(box_word in class_name.lower() for box_word in self.box_related_classes) else "📄"
                        details.append(f"  {status} {class_name}: {confidence:.2f}")
        
        return details
    
    def _detect_box_objects(self, results):
        """检测盒子类物体并记录"""
        current_boxes = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                # 检查是否是盒子类物体
                if any(box_word in class_name.lower() for box_word in self.box_related_classes) and confidence > 0.5:
                    current_boxes.append((class_name, confidence))
                    
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # 只在第一次检测到时打印详细信息
                    if (class_name, confidence) not in self.box_detections:
                        print(f"🎯 新检测: {class_name} (置信度: {confidence:.2f})")
                        print(f"   位置: X[{x1:.0f}-{x2:.0f}] Y[{y1:.0f}-{y2:.0f}]")
                        self.box_detections.append((class_name, confidence))
        
        return current_boxes
    
    def _save_image(self, image):
        """保存当前图像"""
        timestamp = cv2.getTickCount()
        filename = f"detection_{timestamp}.jpg"
        cv2.imwrite(filename, image)
        print(f"💾 图像已保存: {filename}")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Stretch 物体检测系统")
    print("📷 使用: RealSense D405 夹爪摄像头")
    print("🎯 目标: 识别纸巾盒和纸箱")
    print("=" * 50)
    
    detector = EnhancedDesktopDetector()
    detector.detect_objects()
#!/usr/bin/env python3
import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO

class FixedDetector:
    def __init__(self):
        print("🚀 初始化修复版检测器...")
        self.model = YOLO('yolov8n.pt')
        print("✅ YOLOv8加载成功")
        
    def frame_to_numpy(self, frame):
        """安全地将帧转换为numpy数组"""
        try:
            # 方法1: 直接使用asanyarray (推荐)
            image = np.asanyarray(frame.get_data())
            return image
        except Exception as e:
            print(f"方法1失败: {e}")
            try:
                # 方法2: 使用frame数据
                image = np.array(frame.get_data())
                return image
            except Exception as e:
                print(f"方法2失败: {e}")
                return None
    
    def run_detection(self):
        """修复版检测主循环"""
        try:
            # 配置管道
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            
            print("🎥 启动摄像头管道...")
            pipeline.start(config)
            print("✅ 摄像头启动成功!")
            print("📦 将纸巾盒/纸箱放在摄像头前")
            print("⏹️ 按 'q' 退出程序")
            
            frame_count = 0
            
            while True:
                # 等待帧
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                
                if not color_frame:
                    print("❌ 未获取到颜色帧")
                    continue
                
                # 安全转换帧数据
                image = self.frame_to_numpy(color_frame)
                
                if image is None:
                    print("❌ 帧数据转换失败")
                    continue
                
                frame_count += 1
                
                # 显示原始图像
                display_image = image.copy()
                cv2.putText(display_image, f"Frame: {frame_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(display_image, "Press 'q' to quit", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # 每5帧进行一次检测（提高性能）
                if frame_count % 5 == 0:
                    try:
                        results = self.model(image)
                        
                        # 处理检测结果
                        if len(results) > 0 and len(results[0].boxes) > 0:
                            print(f"\n🎯 第{frame_count}帧检测结果:")
                            for r in results:
                                for box in r.boxes:
                                    class_id = int(box.cls[0])
                                    class_name = self.model.names[class_id]
                                    confidence = float(box.conf[0])
                                    print(f"   📍 {class_name}: {confidence:.2f}")
                            
                            # 在图像上绘制检测结果
                            display_image = results[0].plot()
                        else:
                            print(f"第{frame_count}帧: 未检测到物体")
                            cv2.putText(display_image, "No objects detected", (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    except Exception as e:
                        print(f"❌ 检测失败: {e}")
                        cv2.putText(display_image, "Detection Error", (10, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # 显示图像
                cv2.imshow('Stretch Object Detection - FIXED', display_image)
                
                # 检查退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            print(f"❌ 主循环错误: {e}")
        finally:
            try:
                pipeline.stop()
                print("✅ 摄像头管道已停止")
            except:
                pass
            cv2.destroyAllWindows()
            print("🎯 程序结束")

if __name__ == "__main__":
    detector = FixedDetector()
    detector.run_detection()
#!/usr/bin/env python3
import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO

def main():
    print("🚀 启动可靠物体检测器...")
    
    # 初始化YOLO
    model = YOLO('yolov8n.pt')
    print("✅ YOLOv8加载成功")
    
    try:
        # 初始化摄像头
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        print("🎥 启动摄像头...")
        pipeline.start(config)
        print("✅ 摄像头启动成功!")
        print("📦 请将纸巾盒、纸箱等物体放在摄像头前")
        print("⏹️ 按 'q' 退出程序")
        print("-" * 50)
        
        frame_count = 0
        
        while True:
            # 获取帧
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            
            if not color_frame:
                continue
            
            # 转换为numpy数组
            image = np.asanyarray(color_frame.get_data())
            frame_count += 1
            
            # 进行检测
            results = model(image)
            
            # 使用YOLO自带的绘图功能 - 这会自动绘制边界框和标签
            display_frame = results[0].plot()
            
            # 在图像上直接添加状态信息（不改变图像尺寸）
            cv2.putText(display_frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 显示检测到的物体数量
            num_detections = len(results[0].boxes)
            cv2.putText(display_frame, f"Detections: {num_detections}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 添加退出提示
            cv2.putText(display_frame, "Press 'q' to quit", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 在终端打印检测结果
            if num_detections > 0:
                print(f"\n🎯 第{frame_count}帧检测结果:")
                for box in results[0].boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    print(f"   📍 {class_name}: {confidence:.2f}")
            
            # 显示图像
            cv2.imshow('Object Detection - Stretch', display_frame)
            
            # 检查退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        try:
            pipeline.stop()
            print("✅ 摄像头已关闭")
        except:
            pass
        cv2.destroyAllWindows()
        print("🎯 程序结束")

if __name__ == "__main__":
    main()
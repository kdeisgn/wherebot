#!/usr/bin/env python3
import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO

def main():
    print("🚀 启动简单物体检测器...")
    
    # 初始化YOLO
    model = YOLO('yolov8n.pt')
    print("✅ YOLOv8加载成功")
    
    try:
        # 初始化摄像头 - 最简单的配置
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        print("🎥 启动摄像头...")
        pipeline.start(config)
        print("✅ 摄像头启动成功!")
        print("📦 请将物体放在摄像头前")
        print("⏹️ 按 'q' 退出")
        
        frame_count = 0
        
        while True:
            # 获取帧
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            
            if not color_frame:
                print("❌ 没有获取到帧")
                continue
            
            # 转换为numpy数组
            image = np.asanyarray(color_frame.get_data())
            frame_count += 1
            
            # 每帧都进行检测（确保实时性）
            results = model(image)
            
            # 使用YOLO自带的绘图功能
            annotated_frame = results[0].plot()  # 这会自动绘制边界框和标签
            
            # 添加简单的状态信息
            cv2.putText(annotated_frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(annotated_frame, "Press 'q' to quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 在终端打印检测结果
            if len(results[0].boxes) > 0:
                print(f"\n🎯 第{frame_count}帧检测到物体:")
                for box in results[0].boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    print(f"   {class_name}: {confidence:.2f}")
            else:
                if frame_count % 30 == 0:  # 每30帧打印一次"未检测到"
                    print(f"第{frame_count}帧: 等待检测物体...")
            
            # 显示图像
            cv2.imshow('Simple Object Detection', annotated_frame)
            
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
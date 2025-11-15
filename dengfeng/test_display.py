#!/usr/bin/env python3
import cv2
import numpy as np

def test_display():
    """测试OpenCV显示是否正常工作"""
    print("🖥️ 测试显示窗口...")
    
    # 创建一个测试图像
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cv2.putText(test_image, "OpenCV Display Test", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(test_image, "If you see this, display works!", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    cv2.imshow('Display Test Window', test_image)
    print("👀 请查看是否显示测试窗口...")
    print("按任意键关闭窗口")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("✅ 显示测试完成")

if __name__ == "__main__":
    test_display()
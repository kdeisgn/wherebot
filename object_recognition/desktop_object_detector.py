#!/usr/bin/env python3
import cv2
import numpy as np
from ultralytics import YOLO

class DesktopObjectDetector:
    def __init__(self):
        print("Loading YOLOv8 model...")
        self.model = YOLO('yolov8n.pt')
        # YOLO pre-trained model classes that might be related to boxes
        self.box_related_classes = ['box', 'package', 'cardboard', 'paper', 'tissue']
        
    def detect_objects(self):
        """Detect desktop objects"""
        try:
            import pyrealsense2 as rs
            
            # Initialize camera
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            pipeline.start(config)
            print("🎥 Camera started successfully! Place tissue boxes and cardboard boxes in front of the camera")
            print("📦 Press 'q' to quit, press 's' to save current image")
            
            while True:
                # Get frame
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue
                
                # Convert to numpy array
                image = np.asanyarray(color_frame.get_data())
                
                # YOLO detection
                results = self.model(image)
                
                # Display results
                annotated_frame = results[0].plot()
                cv2.imshow('Desktop Object Detection - Stretch', annotated_frame)
                
                # Specifically detect box-like objects
                self._detect_box_objects(results, image)
                
                # Keyboard controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current image for later training
                    cv2.imwrite('desktop_objects.jpg', image)
                    print("💾 Image saved as 'desktop_objects.jpg'")
                    
            pipeline.stop()
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"Camera error: {e}")
    
    def _detect_box_objects(self, results, image):
        """Specifically detect box-like objects"""
        box_detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                # Check if it's a box-like object
                if any(box_word in class_name.lower() for box_word in self.box_related_classes):
                    box_detections.append((class_name, confidence))
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    print(f"📦 Detected box-like object: {class_name} ({confidence:.2f})")
                    print(f"   Position: [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")
        
        # If no box-like objects detected, provide hint
        if not box_detections and len(results[0].boxes) > 0:
            print("👀 Objects detected, but none recognized as box-like. Try adjusting object position or lighting.")

if __name__ == "__main__":
    detector = DesktopObjectDetector()
    detector.detect_objects()
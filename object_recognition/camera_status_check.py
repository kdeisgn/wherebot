#!/usr/bin/env python3
import pyrealsense2 as rs

def check_realsense_status():
    """Check Camera Status"""
    print("Checking Camera Status...")
    
    try:
        ctx = rs.context()
        devices = ctx.query_devices()
        
        print(f"Found {len(devices)} RealSense Devices")
        
        for i, device in enumerate(devices):
            print(f"\n📷 Device {i}:")
            print(f"  Name: {device.get_info(rs.camera_info.name)}")
            print(f"  Serial Number: {device.get_info(rs.camera_info.serial_number)}")
            print(f"  Version: {device.get_info(rs.camera_info.firmware_version)}")
            
            sensors = device.query_sensors()
            print(f"  Sensors: {len(sensors)}")
            
            for j, sensor in enumerate(sensors):
                print(f"    Sensor {j}: {sensor.get_info(rs.camera_info.name)}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_camera_stream():
    """Testing Camera Stream"""
    print("\n🎥 Testing Camera Stream...")
    
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        print("Creating pipeline...")
        pipeline.start(config)
        print("✅ Pipeline started successfully")
        

        for i in range(10):
            frames = pipeline.wait_for_frames(5000)  
            color_frame = frames.get_color_frame()
            
            if color_frame:
                print(f"✅ Frame {i+1}: Success - Width: {color_frame.get_width()}, Height: {color_frame.get_height()}")
                
                # Check frame data
                frame_data = color_frame.get_data()
                print(f"   Data size: {len(frame_data)} bytes")
                print(f"   Data type: {type(frame_data)}")
                
            else:
                print(f"❌ Frame {i+1}: Failed to capture")
        
        pipeline.stop()
        print("✅ Camera stream test completed")
        
    except Exception as e:
        print(f"❌ Camera Streaming Failed: {e}")

if __name__ == "__main__":
    check_realsense_status()
    test_camera_stream()
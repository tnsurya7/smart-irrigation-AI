#!/usr/bin/env python3
"""
Startup Script for USB Bridge System
Manages WebSocket server and USB bridge processes
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import signal
import threading

class USBBridgeManager:
    def __init__(self):
        self.processes = []
        self.running = False
        
    def start_websocket_server(self):
        """Start WebSocket server"""
        print("🚀 Starting WebSocket Server...")
        try:
            process = subprocess.Popen([
                sys.executable, "websocket_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("WebSocket Server", process))
            print("✅ WebSocket Server started (PID: {})".format(process.pid))
            return True
        except Exception as e:
            print(f"❌ Failed to start WebSocket Server: {e}")
            return False
    
    def start_usb_bridge(self):
        """Start USB to WebSocket bridge"""
        print("🔗 Starting USB Bridge...")
        try:
            process = subprocess.Popen([
                sys.executable, "usb_to_ws.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("USB Bridge", process))
            print("✅ USB Bridge started (PID: {})".format(process.pid))
            return True
        except Exception as e:
            print(f"❌ Failed to start USB Bridge: {e}")
            return False
    
    def start_simulator(self):
        """Start data simulator (for testing without hardware)"""
        print("🎮 Starting Data Simulator...")
        try:
            process = subprocess.Popen([
                sys.executable, "simulate_usb_data.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("Data Simulator", process))
            print("✅ Data Simulator started (PID: {})".format(process.pid))
            return True
        except Exception as e:
            print(f"❌ Failed to start Data Simulator: {e}")
            return False
    
    def check_processes(self):
        """Check if processes are still running"""
        for name, process in self.processes:
            if process.poll() is not None:
                print(f"⚠️ {name} stopped unexpectedly (exit code: {process.returncode})")
                return False
        return True
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all processes...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 {name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        self.processes.clear()
        self.running = False
    
    def run(self, use_simulator=False):
        """Run the USB bridge system"""
        print("🌱 Smart Agriculture USB Bridge System")
        print("=" * 50)
        
        # Check if files exist
        required_files = ["websocket_server.py"]
        if use_simulator:
            required_files.append("simulate_usb_data.py")
        else:
            required_files.append("usb_to_ws.py")
        
        for file in required_files:
            if not Path(file).exists():
                print(f"❌ Required file not found: {file}")
                return False
        
        self.running = True
        
        try:
            # Start WebSocket server
            if not self.start_websocket_server():
                return False
            
            # Wait for server to start
            time.sleep(3)
            
            # Start USB bridge or simulator
            if use_simulator:
                if not self.start_simulator():
                    return False
            else:
                if not self.start_usb_bridge():
                    return False
            
            print("\n✅ All services started successfully!")
            print("🔗 WebSocket Server: ws://localhost:8080/ws")
            print("📊 Status: http://localhost:8080/status")
            print("🧪 Test Data: http://localhost:8080/simulate-data")
            print("\nPress Ctrl+C to stop all services")
            
            # Monitor processes
            while self.running:
                if not self.check_processes():
                    print("❌ Some processes stopped. Shutting down...")
                    break
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        except Exception as e:
            print(f"❌ System error: {e}")
        finally:
            self.stop_all()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Agriculture USB Bridge System")
    parser.add_argument("--simulate", action="store_true", 
                       help="Use data simulator instead of real USB device")
    parser.add_argument("--detect-ports", action="store_true",
                       help="Detect available USB ports")
    
    args = parser.parse_args()
    
    if args.detect_ports:
        print("🔍 Running USB port detection...")
        subprocess.run([sys.executable, "detect_usb_ports.py"])
        return
    
    manager = USBBridgeManager()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the system
    success = manager.run(use_simulator=args.simulate)
    
    if not success:
        print("❌ Failed to start USB bridge system")
        sys.exit(1)

if __name__ == "__main__":
    main()
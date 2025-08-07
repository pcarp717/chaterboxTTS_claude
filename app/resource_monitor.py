"""
Resource monitoring for ChatterboxTTS Desktop
Monitors GPU, VRAM, and system resources
"""

import psutil
import torch
from typing import Dict, Optional

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


class ResourceMonitor:
    """Monitors system and GPU resources."""
    
    def __init__(self):
        self.nvml_enabled = False
        
        if NVML_AVAILABLE and torch.cuda.is_available():
            try:
                nvml.nvmlInit()
                self.nvml_enabled = True
            except Exception:
                self.nvml_enabled = False
    
    def get_gpu_status(self) -> Dict:
        """Get current GPU status and VRAM usage."""
        status = {
            "gpu_available": torch.cuda.is_available(),
            "vram_used_mb": 0,
            "vram_total_mb": 0,
            "vram_usage_percent": 0.0,
            "gpu_name": None,
            "cuda_version": None
        }
        
        if not torch.cuda.is_available():
            return status
        
        # Get GPU info
        status["gpu_name"] = torch.cuda.get_device_name(0)
        status["cuda_version"] = torch.version.cuda
        
        # Get VRAM info using NVML if available
        if self.nvml_enabled:
            try:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                info = nvml.nvmlDeviceGetMemoryInfo(handle)
                
                status["vram_used_mb"] = info.used // (1024 ** 2)
                status["vram_total_mb"] = info.total // (1024 ** 2)
                status["vram_usage_percent"] = (info.used / info.total) * 100
                
            except Exception as e:
                print(f"Warning: Could not get NVML info: {e}")
        
        # Fallback to PyTorch memory info
        if status["vram_used_mb"] == 0:
            try:
                status["vram_used_mb"] = torch.cuda.memory_allocated(0) // (1024 ** 2)
                status["vram_total_mb"] = torch.cuda.get_device_properties(0).total_memory // (1024 ** 2)
                if status["vram_total_mb"] > 0:
                    status["vram_usage_percent"] = (status["vram_used_mb"] / status["vram_total_mb"]) * 100
            except Exception:
                pass
        
        return status
    
    def get_system_status(self) -> Dict:
        """Get current system resource usage."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "cpu_usage_percent": cpu_percent,
            "cpu_cores": psutil.cpu_count(),
            "ram_used_gb": (memory.total - memory.available) / (1024 ** 3),
            "ram_total_gb": memory.total / (1024 ** 3),
            "ram_usage_percent": memory.percent
        }
    
    def get_full_status(self) -> Dict:
        """Get comprehensive system status."""
        gpu_status = self.get_gpu_status()
        system_status = self.get_system_status()
        
        return {
            "gpu": gpu_status,
            "system": system_status,
            "timestamp": psutil.time.time()
        }
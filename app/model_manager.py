import torch
import time
import threading
from typing import Optional
from chatterbox.tts import ChatterboxTTS
import psutil
try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


class ModelManager:
    """Manages ChatterboxTTS model loading, caching, and memory management."""
    
    def __init__(self, cache_duration_minutes: int = 5, vram_threshold: float = 0.85):
        self.model: Optional[ChatterboxTTS] = None
        self.last_used: Optional[float] = None
        self.cache_duration = cache_duration_minutes * 60  # Convert to seconds
        self.vram_threshold = vram_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._should_stop = False
        
        if NVML_AVAILABLE and self.device == "cuda":
            try:
                nvml.nvmlInit()
                self.nvml_enabled = True
            except:
                self.nvml_enabled = False
        else:
            self.nvml_enabled = False
            
    def get_model(self) -> ChatterboxTTS:
        """Get the model, loading if necessary."""
        with self._lock:
            current_time = time.time()
            
            # Check VRAM usage before loading
            if self._should_unload_for_memory():
                self._unload_model()
            
            # Load model if not cached or expired
            if self.model is None:
                print("Loading ChatterboxTTS model...")
                start_time = time.time()
                
                self.model = ChatterboxTTS.from_pretrained(device=self.device)
                
                # Optimize with torch.compile if on CUDA
                if self.device == "cuda":
                    print("Optimizing model with torch.compile...")
                    try:
                        self.model = torch.compile(self.model)
                    except Exception as e:
                        print(f"Warning: torch.compile failed: {e}")
                
                load_time = time.time() - start_time
                print(f"Model loaded in {load_time:.2f} seconds")
            
            self.last_used = current_time
            self._start_cleanup_thread()
            return self.model
    
    def _should_unload_for_memory(self) -> bool:
        """Check if model should be unloaded due to high VRAM usage."""
        if not self.nvml_enabled or self.model is None:
            return False
            
        try:
            handle = nvml.nvmlDeviceGetHandleByIndex(0)  # Assuming first GPU
            info = nvml.nvmlDeviceGetMemoryInfo(handle)
            usage_ratio = info.used / info.total
            return usage_ratio > self.vram_threshold
        except:
            return False
    
    def _unload_model(self):
        """Unload model and free VRAM."""
        if self.model is not None:
            print("Unloading model to free VRAM...")
            del self.model
            self.model = None
            self.last_used = None
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
    
    def _start_cleanup_thread(self):
        """Start background thread to monitor cache expiry."""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._should_stop = False
            self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self._cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Background worker to unload expired models."""
        while not self._should_stop:
            time.sleep(30)  # Check every 30 seconds
            
            with self._lock:
                if (self.model is not None and 
                    self.last_used is not None and 
                    time.time() - self.last_used > self.cache_duration):
                    self._unload_model()
                    break  # Exit thread after cleanup
    
    def get_memory_stats(self) -> dict:
        """Get current memory usage statistics."""
        stats = {
            "model_loaded": self.model is not None,
            "device": self.device,
            "last_used": self.last_used,
            "cache_duration": self.cache_duration,
        }
        
        if self.device == "cuda" and torch.cuda.is_available():
            stats["cuda_memory_allocated"] = torch.cuda.memory_allocated() / 1024**3  # GB
            stats["cuda_memory_reserved"] = torch.cuda.memory_reserved() / 1024**3   # GB
            
        if self.nvml_enabled:
            try:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                info = nvml.nvmlDeviceGetMemoryInfo(handle)
                stats["vram_used"] = info.used / 1024**3      # GB
                stats["vram_total"] = info.total / 1024**3    # GB
                stats["vram_usage_percent"] = (info.used / info.total) * 100
            except:
                pass
                
        stats["ram_usage_percent"] = psutil.virtual_memory().percent
        return stats
    
    def is_model_loaded(self) -> bool:
        """Check if model is currently loaded."""
        return self.model is not None
    
    def shutdown(self):
        """Clean shutdown of model manager."""
        self._should_stop = True
        with self._lock:
            self._unload_model()
"""
MapBench.Live - Caching System
Intelligent caching for benchmark results to avoid redundant API calls
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import asdict

from .runner import EvaluationResult, Task, ModelConfig


class BenchmarkCache:
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Version identifier for cache invalidation
        self.cache_version = "v2.0"  # Update when changing evaluation logic
        
        # Cache metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "version": self.cache_version,
            "created": datetime.utcnow().isoformat(),
            "entries": {}
        }
    
    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _compute_task_hash(self, task: Task) -> str:
        """Compute hash for task content"""
        # Include all task properties that affect evaluation
        task_content = {
            "id": task.id,
            "context": task.context,
            "questions": task.questions,
            "type": task.type
        }
        
        # Add image file hash if it exists
        image_path = Path("data/tasks") / task.map_image
        if image_path.exists():
            with open(image_path, 'rb') as f:
                image_hash = hashlib.md5(f.read()).hexdigest()[:8]
            task_content["image_hash"] = image_hash
        
        content_str = json.dumps(task_content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    def _compute_model_hash(self, model_config: ModelConfig) -> str:
        """Compute hash for model configuration"""
        model_content = {
            "id": model_config.id,
            "provider": model_config.provider,
            "endpoint": model_config.endpoint,
            "model": model_config.model,
            "region": model_config.region
        }
        content_str = json.dumps(model_content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    def _generate_cache_key(self, model_config: ModelConfig, task: Task) -> str:
        """Generate unique cache key for model-task combination"""
        model_hash = self._compute_model_hash(model_config)
        task_hash = self._compute_task_hash(task)
        
        return f"{self.cache_version}_{model_config.id}_{model_hash}_{task.id}_{task_hash}"
    
    def get_cached_result(self, model_config: ModelConfig, task: Task) -> Optional[EvaluationResult]:
        """Retrieve cached result if available and valid"""
        cache_key = self._generate_cache_key(model_config, task)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check if cache entry is in metadata and not expired
        if cache_key in self.metadata.get("entries", {}):
            entry_info = self.metadata["entries"][cache_key]
            
            # Check expiration (default: 30 days)
            created_time = datetime.fromisoformat(entry_info.get("created", "1970-01-01"))
            if datetime.utcnow() - created_time > timedelta(days=30):
                # Cache expired, remove it
                cache_file.unlink(missing_ok=True)
                del self.metadata["entries"][cache_key]
                self._save_metadata()
                return None
        
        # Load and return cached result
        try:
            with open(cache_file, 'r') as f:
                result_data = json.load(f)
            
            # Reconstruct EvaluationResult object
            return EvaluationResult(**result_data)
        
        except Exception as e:
            # Cache file corrupted, remove it
            cache_file.unlink(missing_ok=True)
            if cache_key in self.metadata.get("entries", {}):
                del self.metadata["entries"][cache_key]
                self._save_metadata()
            return None
    
    def cache_result(self, model_config: ModelConfig, task: Task, result: EvaluationResult):
        """Cache an evaluation result"""
        cache_key = self._generate_cache_key(model_config, task)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Save result to cache file
        try:
            with open(cache_file, 'w') as f:
                json.dump(asdict(result), f, indent=2, default=str)
            
            # Update metadata
            self.metadata["entries"][cache_key] = {
                "created": datetime.utcnow().isoformat(),
                "model_id": model_config.id,
                "task_id": task.id,
                "file_size": cache_file.stat().st_size
            }
            self._save_metadata()
            
        except Exception as e:
            # If caching fails, remove partial files
            cache_file.unlink(missing_ok=True)
    
    def invalidate_model_cache(self, model_id: str):
        """Invalidate all cached results for a specific model"""
        removed_keys = []
        
        for cache_key, entry_info in self.metadata.get("entries", {}).items():
            if entry_info.get("model_id") == model_id:
                cache_file = self.cache_dir / f"{cache_key}.json"
                cache_file.unlink(missing_ok=True)
                removed_keys.append(cache_key)
        
        # Update metadata
        for key in removed_keys:
            del self.metadata["entries"][key]
        
        if removed_keys:
            self._save_metadata()
        
        return len(removed_keys)
    
    def invalidate_task_cache(self, task_id: str):
        """Invalidate all cached results for a specific task"""
        removed_keys = []
        
        for cache_key, entry_info in self.metadata.get("entries", {}).items():
            if entry_info.get("task_id") == task_id:
                cache_file = self.cache_dir / f"{cache_key}.json"
                cache_file.unlink(missing_ok=True)
                removed_keys.append(cache_key)
        
        # Update metadata
        for key in removed_keys:
            del self.metadata["entries"][key]
        
        if removed_keys:
            self._save_metadata()
        
        return len(removed_keys)
    
    def clear_cache(self):
        """Clear all cached results"""
        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != "cache_metadata.json":
                cache_file.unlink(missing_ok=True)
        
        # Reset metadata
        self.metadata = {
            "version": self.cache_version,
            "created": datetime.utcnow().isoformat(),
            "entries": {}
        }
        self._save_metadata()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        entries = self.metadata.get("entries", {})
        
        # Calculate total size
        total_size = 0
        for cache_key in entries.keys():
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                total_size += cache_file.stat().st_size
        
        # Group by model
        model_stats = {}
        for entry_info in entries.values():
            model_id = entry_info.get("model_id", "unknown")
            if model_id not in model_stats:
                model_stats[model_id] = 0
            model_stats[model_id] += 1
        
        return {
            "version": self.cache_version,
            "total_entries": len(entries),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_model": model_stats,
            "cache_dir": str(self.cache_dir)
        }
    
    def print_cache_stats(self):
        """Print human-readable cache statistics"""
        stats = self.get_cache_stats()
        
        print("\n=== CACHE STATISTICS ===")
        print(f"Cache Version: {stats['version']}")
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Total Size: {stats['total_size_mb']} MB")
        print(f"Cache Directory: {stats['cache_dir']}")
        
        if stats['by_model']:
            print("\nCached Results by Model:")
            for model_id, count in sorted(stats['by_model'].items()):
                print(f"  {model_id}: {count} tasks")
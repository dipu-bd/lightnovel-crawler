import logging
import os
import shutil
from typing import Dict, List, Any, Optional
import traceback
import threading
from lncrawl.models.formats import OutputFormat

from lncrawl.core.app import App
from lncrawl.core.sources import prepare_crawler
from lncrawl.utils.uploader import upload

logger = logging.getLogger(__name__)


class PythonApiBot:
    """Bot that allows another python app to use the crawler functionality via method calls"""
    
    def __init__(self):
        self.app = None
        self.initialized = False
        self.search_completed = False
        self.download_completed = False
        self.search_thread = None
        self.download_thread = None
        self.search_in_progress = False
        self.download_in_progress = False
    
    def start(self):
        """Initialize the bot - required method for all bots"""
        # Set necessary environment variables
        os.environ["debug_mode"] = "yes"
        
        # Ensure sources are loaded
        from lncrawl.core.sources import load_sources
        load_sources()
        
        logger.info("Python API bot initialized and ready for requests")
        self.initialized = True
        return {"status": "ready"}
    
    def init_app(self) -> Dict[str, Any]:
        """Initialize a new app session"""
        if self.app:
            self.destroy_app()
        
        # Ensure the application is properly set up
        from lncrawl.core import init
        try:
            init()
        except Exception:
            # Ignore if already initialized
            pass
        
        self.app = App()
        self.app.initialize()
        self.search_completed = False
        self.download_completed = False
        
        return {"status": "success", "message": "New session created"}
    
    def set_logger(self, custom_logger):
        """Set a custom logger for the bot"""
        global logger
        logger = custom_logger

    def destroy_app(self) -> Dict[str, Any]:
        """Destroy the current app session"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        self.app.destroy()
        
        self.app = None
        self.search_completed = False
        self.download_completed = False
        
        return {"status": "success", "message": "Session closed"}
    
    def start_search(self, query: str) -> Dict[str, Any]:
        """Start a search for novels"""
        if not self.app:
            return {"status": "error", "message": "No active session. Call init_app first."}
        
        try:
            self.app.user_input = query.strip()
            self.search_completed = False
            self.search_in_progress = True
            
            # Try to prepare search
            try:
                self.app.prepare_search()
            except Exception as e:
                self.search_in_progress = False
                return {
                    "status": "error",
                    "message": f"Failed to prepare search: {str(e)}",
                    "error": traceback.format_exc()
                }
            
            # If crawler is ready, we have a direct URL
            if self.app.crawler:
                self.search_completed = True
                self.search_in_progress = False
                return {"status": "success", "message": "Direct novel URL found, no search needed"}
            
            # Start search in background thread to avoid blocking
            def search_worker():
                try:
                    self.app.search_novel()
                    self.search_completed = True
                except Exception as e:
                    logger.error(f"Search thread error: {e}")
                finally:
                    self.search_in_progress = False
            
            self.search_thread = threading.Thread(target=search_worker)
            self.search_thread.daemon = True
            self.search_thread.start()
            
            return {"status": "success", "message": f"Search started for '{query}'"}
        except Exception as e:
            self.search_in_progress = False
            logger.error(f"Search error: {e}")
            return {"status": "error", "message": str(e), "error": traceback.format_exc()}
    
    def get_search_status(self) -> Dict[str, Any]:
        """Get the current status of the search process"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        return {
            "status": "success", 
            "search_completed": self.search_completed,
            "search_in_progress": self.search_in_progress,
            "progress": getattr(self.app, "progress", 0),
            "total_items": len(getattr(self.app, "crawler_links", [])),
            "has_results": len(getattr(self.app, "search_results", [])) > 0 or self.app.crawler is not None
        }
    
    def get_search_results(self) -> Dict[str, Any]:
        """Get the results of the search"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        if not self.search_completed and not self.app.crawler:
            return {"status": "error", "message": "Search not completed"}
        
        if self.app.crawler:
            # Direct URL was provided
            return {
                "status": "success",
                "direct_novel": True,
                "novel_url": self.app.crawler.novel_url
            }
        
        if not hasattr(self.app, "search_results") or not self.app.search_results:
            return {"status": "error", "message": "No results found"}
            
        # Format the search results
        results = []
        for i, res in enumerate(self.app.search_results):
            sources = []
            for j, novel in enumerate(res["novels"]):
                source = {
                    "index": j,
                    "url": novel["url"],
                }
                if "info" in novel:
                    source["info"] = novel["info"]
                sources.append(source)
                
            results.append({
                "index": i,
                "title": res["title"],
                "sources": sources
            })
            
        return {
            "status": "success",
            "results": results
        }
    
    def select_novel(self, novel_index: int, source_index: int = 0) -> Dict[str, Any]:
        """Select a novel from search results to download"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        if not self.search_completed:
            return {"status": "error", "message": "Search not completed"}
        
        if not hasattr(self.app, "search_results") or novel_index >= len(self.app.search_results):
            return {"status": "error", "message": "Invalid novel index"}
        
        selected = self.app.search_results[novel_index]
        if source_index >= len(selected["novels"]):
            return {"status": "error", "message": "Invalid source index"}
        
        source = selected["novels"][source_index]
        self.app.crawler = prepare_crawler(source.get("url"))
        
        try:
            self.app.get_novel_info()
            return {
                "status": "success",
                "novel_title": self.app.crawler.novel_title,
                "volumes": len(self.app.crawler.volumes),
                "chapters": len(self.app.crawler.chapters),
                "novel_url": self.app.crawler.novel_url
            }
        except Exception as e:
            logger.error(f"Error getting novel info: {e}")
            return {"status": "error", "message": str(e), "error": traceback.format_exc()}
    
    def set_novel_url(self, url: str) -> Dict[str, Any]:
        """Set novel directly by URL"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        try:
            self.app.crawler = prepare_crawler(url)
            self.app.get_novel_info()
            return {
                "status": "success",
                "novel_title": self.app.crawler.novel_title,
                "volumes": len(self.app.crawler.volumes),
                "chapters": len(self.app.crawler.chapters),
                "novel_url": self.app.crawler.novel_url
            }
        except Exception as e:
            logger.error(f"Error setting novel URL: {e}")
            return {"status": "error", "message": str(e), "error": traceback.format_exc()}
    
    def get_novel_info(self) -> Dict[str, Any]:
        """Get information about the selected novel"""
        if not self.app or not self.app.crawler:
            return {"status": "error", "message": "No novel selected"}
        
        return {
            "status": "success",
            "title": self.app.crawler.novel_title,
            "author": getattr(self.app.crawler, "novel_author", "Unknown"),
            "volumes": len(self.app.crawler.volumes),
            "chapters": len(self.app.crawler.chapters),
            "url": self.app.crawler.novel_url
        }
    
    def select_chapters(self, selection_type: str, 
                       start: Optional[int] = None, 
                       end: Optional[int] = None,
                       volumes: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Select chapters to download
        
        selection_type: "all", "first", "last", "range", "volumes"
        start, end: Used for range selection
        volumes: List of volume numbers for volume selection
        """
        if not self.app or not self.app.crawler:
            return {"status": "error", "message": "No novel selected"}
        
        try:
            if selection_type == "all":
                self.app.chapters = self.app.crawler.chapters[:]
            elif selection_type == "first":
                limit = start or 50
                self.app.chapters = self.app.crawler.chapters[:limit]
            elif selection_type == "last":
                limit = start or 50
                self.app.chapters = self.app.crawler.chapters[-limit:]
            elif selection_type == "range":
                if start is None or end is None:
                    return {"status": "error", "message": "Start and end required for range selection"}
                self.app.chapters = self.app.crawler.chapters[start-1:end]
            elif selection_type == "volumes":
                if not volumes:
                    return {"status": "error", "message": "Volume list required for volume selection"}
                self.app.chapters = [
                    chap for chap in self.app.crawler.chapters if volumes.count(chap["volume"]) > 0
                ]
            else:
                return {"status": "error", "message": f"Unknown selection type: {selection_type}"}
            
            return {
                "status": "success",
                "chapters_selected": len(self.app.chapters)
            }
        except Exception as e:
            logger.error(f"Error selecting chapters: {e}")
            return {"status": "error", "message": str(e), "error": traceback.format_exc()}
    
    def set_output_path(self, output_path: str) -> Dict[str, Any]:
        """Set custom output path for downloads"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        try:
            # Make sure the directory exists
            os.makedirs(output_path, exist_ok=True)
            # Set output path
            self.app.output_path = output_path
            return {
                "status": "success",
                "message": f"Output path set to: {output_path}"
            }
        except Exception as e:
            logger.error(f"Error setting output path: {e}")
            return {"status": "error", "message": str(e), "error": traceback.format_exc()}
    
    def start_download(self, output_formats: List[str] = None, pack_by_volume: bool = False, output_path: str = None) -> Dict[str, Any]:
        """
        Start downloading the selected novel
        
        output_formats: List of formats to generate. Defaults to ["epub"]
        pack_by_volume: Whether to split output by volumes
        output_path: Custom output directory path (optional)
        """
        if not self.app or not self.app.crawler:
            return {"status": "error", "message": "No novel selected"}
        
        if not hasattr(self.app, "chapters") or not self.app.chapters:
            return {"status": "error", "message": "No chapters selected"}
        
        try:
            # Set custom output path if provided
            if output_path:
                result = self.set_output_path(output_path)
                if result["status"] != "success":
                    return result
            
            # Set output formats
            available_formats =  OutputFormat.__members__.values()
            self.app.output_formats = {}
            
            if not output_formats:
                output_formats = ["json"]
                
            for fmt in available_formats:
                self.app.output_formats[fmt] = fmt in output_formats
            
            # Set packing preference
            self.app.pack_by_volume = pack_by_volume
            
            # Start download in background thread
            self.download_completed = False
            self.download_in_progress = True
            
            def download_worker():
                try:
                    self.app.start_download()
                    # Generate output files
                    self.app.bind_books()
                    self.download_completed = True
                except Exception as e:
                    logger.error(f"Download thread error: {e}")
                finally:
                    self.download_in_progress = False
            
            self.download_thread = threading.Thread(target=download_worker)
            self.download_thread.daemon = True
            self.download_thread.start()
            
            return {
                "status": "success",
                "download_started": True,
                "message": "Download started in background"
            }
        except Exception as e:
            self.download_in_progress = False
            logger.error(f"Error starting download: {e}")
            return {"status": "error", "message": str(e), "error": traceback.format_exc()}
    
    def get_download_status(self) -> Dict[str, Any]:
        """Get the current download status"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        if not hasattr(self.app, "chapters"):
            return {"status": "error", "message": "No chapters selected"}
        
        return {
            "status": "success",
            "download_completed": self.download_completed,
            "download_in_progress": self.download_in_progress,
            "progress": getattr(self.app, "progress", 0),
            "total_chapters": len(self.app.chapters)
        }
    
    def get_download_results(self) -> Dict[str, Any]:
        """Get the results of the download"""
        if not self.app:
            return {"status": "error", "message": "No active session"}
        
        if not self.download_completed:
            return {"status": "error", "message": "Download not completed"}
        
        return {
            "status": "success",
            "output_path": self.app.output_path,
            "archived_outputs": getattr(self.app, "archived_outputs", []),
            "output_files": getattr(self.app, "output_files", [])
        }
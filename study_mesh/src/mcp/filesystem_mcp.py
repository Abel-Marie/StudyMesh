import os
import json
from pathlib import Path

class FilesystemMCP:
    """MCP server for filesystem operations (document management)."""
    
    def __init__(self, base_dir="documents"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def save_document(self, filename, content, category="general"):
        """Save a document to the filesystem."""
        category_dir = self.base_dir / category
        category_dir.mkdir(exist_ok=True)
        
        file_path = category_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def read_document(self, filename, category="general"):
        """Read a document from the filesystem."""
        file_path = self.base_dir / category / filename
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_documents(self, category=None):
        """List all documents, optionally filtered by category."""
        if category:
            search_dir = self.base_dir / category
            if not search_dir.exists():
                return []
            return [f.name for f in search_dir.iterdir() if f.is_file()]
        
        # List all documents across all categories
        documents = []
        for category_dir in self.base_dir.iterdir():
            if category_dir.is_dir():
                for file in category_dir.iterdir():
                    if file.is_file():
                        documents.append({
                            "category": category_dir.name,
                            "filename": file.name,
                            "path": str(file)
                        })
        return documents
    
    def delete_document(self, filename, category="general"):
        """Delete a document."""
        file_path = self.base_dir / category / filename
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_document_info(self, filename, category="general"):
        """Get information about a document."""
        file_path = self.base_dir / category / filename
        
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        return {
            "filename": filename,
            "category": category,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "path": str(file_path)
        }

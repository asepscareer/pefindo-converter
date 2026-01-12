from typing import Optional, Any, Dict

class XMLTransformer:
    """Base class untuk transformasi XML yang lebih optimal"""
    
    @staticmethod
    def safe_find(element: Any, xpath: str, namespaces: Optional[Dict[str, str]] = None, default: Any = None) -> Any:
        """Safe XPath dengan default value dan type hinting"""
        if element is None:
            return default
        found = element.find(xpath, namespaces=namespaces)
        return found if found is not None else default
    
    @staticmethod
    def safe_text(element: Any, xpath: str, namespaces: Optional[Dict[str, str]] = None, default: str = "", strip: bool = True) -> str:
        """Safe text extraction dengan opsi pembersihan whitespace"""
        if element is None:
            return default
            
        found = element.find(xpath, namespaces=namespaces)
        if found is not None and found.text is not None:
            return found.text.strip() if strip else found.text
        return default
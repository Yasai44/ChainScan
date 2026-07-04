import re
from pathlib import Path

# Suspicious functions and modules commonly abused in malicious packages
SUSPICIOUS_FUNCS = ["exec", "eval", "compile"]
SUSPICIOUS_MODULES = ["subprocess", "os.system", "pickle"]

class CodeIndicators:
    """Scan local Python files for suspicious patterns."""
    
    def scan_file(self, path: Path) -> list[dict]:
        findings = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return findings
        
        # Look for suspicious functions
        for func in SUSPICIOUS_FUNCS:
            if func in content:
                findings.append({
                    "type": "code",
                    "indicator": f"use_of_{func}",
                    "score": 3,
                    "details": f"{func} found in {path}"
                })
                
        # Look for suspicious modules
        for mod in SUSPICIOUS_MODULES:
            if mod in content:
                findings.append({
                    "type": "code",
                    "indicator": f"use_of_{mod}",
                    "score": 2,
                    "details": f"{mod} found in {path}"
                })
                    
        return findings

"""
Advanced Writer - Orchestrates specialized writers with multi-source support
"""
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from writers.tech_writer import TechWriter
from writers.journalism_writer import JournalismWriter
from writers.educational_writer import EducationalWriter
from publisher import Publisher

class AdvancedWriter:
    def __init__(self):
        self.writers = {
            'tech': TechWriter(),
            'journalism': JournalismWriter(),
            'educational': EducationalWriter()
        }
        self.publisher = Publisher()
    
    def generate(self, config):
        """Generate article using specified writer"""
        writer_type = config.get('writer', 'tech')
        writer = self.writers.get(writer_type)
        
        if not writer:
            raise ValueError(f"Unknown writer type: {writer_type}")
        
        print(f"Starting {writer_type} writer for: {config['topic']}")
        
        # Generate article
        result = writer.write(config)
        
        print(f"Generated article: {result['title']}")
        print(f"Word count: {result['metadata']['word_count']}")
        
        # Publish
        self.publisher.publish(result)
        
        print(f"Published: {result['title']}")
        
        return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python advanced_writer.py <config_file>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        writer_system = AdvancedWriter()
        result = writer_system.generate(config)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

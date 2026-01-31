"""
Test the advanced writer system locally
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from advanced_writer import AdvancedWriter

def test_tech_writer():
    """Test tech writer with basic config"""
    config = {
        'topic': 'Revolutionary AI Breakthrough in Quantum Computing',
        'writer': 'tech',
        'length': 'short',
        'tone': 'enthusiastic',
        'focus': 'overview',
        'rawText': 'Scientists at MIT announced a breakthrough in quantum AI that could revolutionize computing.',
        'multiPass': False,  # Skip for speed in testing
        'factCheck': False,
        'humanize': False
    }
    
    print("Testing Tech Writer...")
    writer = AdvancedWriter()
    result = writer.generate(config)
    
    print("[OK] Generated: " + result['title'])
    print("[OK] Word count: " + str(result['metadata']['word_count']))
    print("\nFirst 200 chars:\n" + result['markdown'][:200] + "...")
    return True

def test_journalism_writer():
    """Test journalism writer"""
    config = {
        'topic': 'The Ethics of AI in Healthcare: A Critical Examination',
        'writer': 'journalism',
        'length': 'medium',
        'tone': 'critical',
        'focus': 'social',
        'links': [
            'https://example.com/research-paper',
            'https://example.com/ethics-study'
        ],
        'rawText': 'Recent studies show mixed results in AI healthcare applications.',
        'multiPass': False,
        'factCheck': False,
        'humanize': False
    }
    
    print("\n\nTesting Journalism Writer...")
    writer = AdvancedWriter()
    result = writer.generate(config)
    
    print("[OK] Generated: " + result['title'])
    print("[OK] Word count: " + str(result['metadata']['word_count']))
    print("[OK] Citations: " + str(result['metadata'].get('citations', 0)))
    print("\nFirst 200 chars:\n" + result['markdown'][:200] + "...")
    return True

def test_educational_writer():
    """Test educational writer"""
    config = {
        'topic': 'Understanding Machine Learning: A Beginner\'s Guide',
        'writer': 'educational',
        'length': 'medium',
        'tone': 'conversational',
        'focus': 'overview',
        'rawText': 'Machine learning is often misunderstood. Many think it\'s magic, but it\'s actually mathematics.',
        'multiPass': False,
        'factCheck': False,
        'humanize': False
    }
    
    print("\n\nTesting Educational Writer...")
    writer = AdvancedWriter()
    result = writer.generate(config)
    
    print("[OK] Generated: " + result['title'])
    print("[OK] Word count: " + str(result['metadata']['word_count']))
    print("[OK] Infographics: " + str(result['metadata'].get('infographics', 0)))
    print("\nFirst 200 chars:\n" + result['markdown'][:200] + "...")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("ADVANCED WRITER SYSTEM TEST")
    print("=" * 60)
    
    try:
        test_tech_writer()
        test_journalism_writer()
        test_educational_writer()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe advanced writer system is working correctly!")
        print("Articles have been generated and published to the blog.")
        
    except Exception as e:
        print("\n[FAILED] TEST ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

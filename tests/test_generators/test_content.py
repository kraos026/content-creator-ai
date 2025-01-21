import pytest
from backend.app.generators.content import ContentGenerator

@pytest.fixture
def content_generator():
    return ContentGenerator()

def test_generate_content_brief(content_generator):
    brief = content_generator.generate_content_brief(
        topic="Python Programming",
        platform="youtube",
        content_type="tutorial"
    )
    
    assert isinstance(brief, dict)
    assert all(key in brief for key in [
        'hook',
        'structure',
        'cta',
        'optimal_length',
        'key_elements',
        'content_tips'
    ])
    
    # Test hook
    assert isinstance(brief['hook'], str)
    assert len(brief['hook']) > 0
    assert "python programming" in brief['hook'].lower()
    
    # Test structure
    assert isinstance(brief['structure'], list)
    assert len(brief['structure']) > 0
    for section in brief['structure']:
        assert isinstance(section, dict)
        assert all(key in section for key in ['section', 'duration', 'key_points'])
    
    # Test CTA
    assert isinstance(brief['cta'], str)
    assert len(brief['cta']) > 0
    
    # Test optimal length
    assert isinstance(brief['optimal_length'], dict)
    assert all(key in brief['optimal_length'] for key in ['min', 'max', 'optimal'])
    assert brief['optimal_length']['min'] <= brief['optimal_length']['optimal'] <= brief['optimal_length']['max']
    
    # Test key elements
    assert isinstance(brief['key_elements'], list)
    assert len(brief['key_elements']) > 0
    assert all(isinstance(element, str) for element in brief['key_elements'])
    
    # Test content tips
    assert isinstance(brief['content_tips'], list)
    assert len(brief['content_tips']) > 0
    assert all(isinstance(tip, str) for tip in brief['content_tips'])

def test_generate_hook(content_generator):
    topic = "Python Programming"
    content_type = "tutorial"
    
    hook = content_generator._generate_hook(topic, content_type)
    
    assert isinstance(hook, str)
    assert len(hook) > 0
    assert "python programming" in hook.lower()

def test_generate_structure(content_generator):
    content_types = ["tutorial", "review", "story"]
    
    for content_type in content_types:
        structure = content_generator._generate_structure(content_type)
        
        assert isinstance(structure, list)
        assert len(structure) > 0
        for section in structure:
            assert isinstance(section, dict)
            assert all(key in section for key in ['section', 'duration', 'key_points'])
            assert isinstance(section['key_points'], list)

def test_generate_cta(content_generator):
    topic = "Python Programming"
    
    cta = content_generator._generate_cta(topic)
    
    assert isinstance(cta, str)
    assert len(cta) > 0
    assert any(char in cta for char in ['👉', '❤️', '💬', '🔔', '⬇️'])

def test_get_optimal_length(content_generator):
    platforms = ["youtube", "tiktok", "instagram"]
    content_types = ["tutorial", "review", "story"]
    
    for platform in platforms:
        for content_type in content_types:
            length = content_generator._get_optimal_length(platform, content_type)
            
            assert isinstance(length, dict)
            assert all(key in length for key in ['min', 'max', 'optimal'])
            assert length['min'] <= length['optimal'] <= length['max']

def test_get_key_elements(content_generator):
    platforms = ["youtube", "tiktok", "instagram"]
    content_types = ["tutorial", "review", "story"]
    
    for platform in platforms:
        for content_type in content_types:
            elements = content_generator._get_key_elements(platform, content_type)
            
            assert isinstance(elements, list)
            assert len(elements) > 0
            assert all(isinstance(element, str) for element in elements)

def test_generate_content_tips(content_generator):
    platforms = ["youtube", "tiktok"]
    content_types = ["tutorial", "review"]
    
    for platform in platforms:
        for content_type in content_types:
            tips = content_generator._generate_content_tips(platform, content_type)
            
            assert isinstance(tips, list)
            assert len(tips) > 0
            assert all(isinstance(tip, str) for tip in tips)

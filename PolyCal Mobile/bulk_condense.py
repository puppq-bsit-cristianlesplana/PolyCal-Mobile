#!/usr/bin/env python3
"""
Bulk code condensation script to convert all multi-line widget definitions to single lines.
This will significantly reduce the file size from 8000+ lines.
"""

import re

def condense_multiline_widgets(file_path):
    """Convert all multi-line widget definitions to single lines"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match multi-line widget definitions
    patterns = [
        # Button definitions
        (r'(\s+)(\w+)\s*=\s*Button\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = Button(\3)'),
        # Label definitions  
        (r'(\s+)(\w+)\s*=\s*Label\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = Label(\3)'),
        # TextInput definitions
        (r'(\s+)(\w+)\s*=\s*TextInput\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = TextInput(\3)'),
        # BoxLayout definitions
        (r'(\s+)(\w+)\s*=\s*BoxLayout\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = BoxLayout(\3)'),
        # Popup definitions
        (r'(\s+)(\w+)\s*=\s*Popup\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = Popup(\3)'),
        # Image definitions
        (r'(\s+)(\w+)\s*=\s*Image\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = Image(\3)'),
        # GridLayout definitions
        (r'(\s+)(\w+)\s*=\s*GridLayout\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = GridLayout(\3)'),
        # ScrollView definitions
        (r'(\s+)(\w+)\s*=\s*ScrollView\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = ScrollView(\3)'),
        # FileChooserListView definitions
        (r'(\s+)(\w+)\s*=\s*FileChooserListView\(\s*\n(\s+[^)]+\n)+\s*\)', r'\1\2 = FileChooserListView(\3)'),
    ]
    
    # Apply each pattern
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Manual cleanup for specific multi-line patterns
    content = manual_cleanup(content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Condensed multi-line widgets in {file_path}")

def manual_cleanup(content):
    """Manual cleanup for specific patterns that regex might miss"""
    
    # Split into lines for processing
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a multi-line widget definition
        if ('= Button(' in line or '= Label(' in line or '= TextInput(' in line or 
            '= BoxLayout(' in line or '= Popup(' in line or '= Image(' in line or
            '= GridLayout(' in line or '= ScrollView(' in line) and line.strip().endswith('('):
            
            # Collect all lines until closing parenthesis
            widget_lines = [line]
            i += 1
            paren_count = 1
            
            while i < len(lines) and paren_count > 0:
                current_line = lines[i]
                widget_lines.append(current_line)
                paren_count += current_line.count('(') - current_line.count(')')
                i += 1
            
            # Condense to single line
            condensed = condense_widget_definition(widget_lines)
            result_lines.append(condensed)
        else:
            result_lines.append(line)
            i += 1
    
    return '\n'.join(result_lines)

def condense_widget_definition(widget_lines):
    """Condense a multi-line widget definition to a single line"""
    
    if not widget_lines:
        return ""
    
    # Extract the widget name and type from first line
    first_line = widget_lines[0].strip()
    indent = len(widget_lines[0]) - len(widget_lines[0].lstrip())
    
    # Collect all parameters
    params = []
    for line in widget_lines[1:-1]:  # Skip first and last lines
        param_line = line.strip()
        if param_line and not param_line.startswith('#'):
            # Remove trailing comma if present
            if param_line.endswith(','):
                param_line = param_line[:-1]
            params.append(param_line)
    
    # Combine into single line
    if params:
        params_str = ', '.join(params)
        condensed = f"{' ' * indent}{first_line[:-1]}{params_str})"
    else:
        condensed = widget_lines[0]
    
    return condensed

if __name__ == "__main__":
    condense_multiline_widgets("polycal_app.py")
    print("Bulk condensation complete!")

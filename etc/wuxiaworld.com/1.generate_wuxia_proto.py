#!/usr/bin/env python3
"""
Generate wuxia.proto that imports all protobuf files from wuxiaworld_typescript.
Reads .ts files, converts to .proto, and creates a main wuxia.proto with all imports.
"""
import os
import re
import sys

# Add ts_to_proto to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from ts_to_proto import parse_typescript, generate_proto

def get_imports_from_proto(proto_content):
    """Extract all import statements from proto content"""
    imports = re.findall(r'^import "([^"]+)";', proto_content, re.MULTILINE)
    return imports

def get_service_names(ts_content):
    """Extract service names from TypeScript"""
    services = re.findall(r'export class (\w+)(?:Service|\$)', ts_content)
    return services

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_dir = os.path.join(script_dir, "wuxiaworld_typescript")  # sibling folder
    output_dir = os.path.join(script_dir, "proto_temp")  # sibling folder
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .ts files (excluding .ignor_client)
    ts_files = []
    for root, dirs, files in os.walk(input_dir):
        # Skip .ignor_client directories
        dirs[:] = [d for d in dirs if not d.startswith('.ignor')]
        for f in files:
            if f.endswith('.ts'):
                ts_files.append(os.path.join(root, f))
    
    # Sort for consistent ordering
    ts_files = sorted(ts_files)
    
    print(f"Found {len(ts_files)} TypeScript files")
    
    # Generate proto files
    proto_files = {}
    for ts_file in ts_files:
        # Parse and generate
        data = parse_typescript(ts_file)
        proto_content = generate_proto(data)
        
        # Create output filename
        base_name = os.path.splitext(os.path.basename(ts_file))[0]
        proto_file = os.path.join(output_dir, f"{base_name}.proto")
        
        with open(proto_file, 'w', encoding='utf-8') as f:
            f.write(proto_content)
        
        proto_files[base_name] = {
            'content': proto_content,
            'file': proto_file,
            'imports': get_imports_from_proto(proto_content),
            'local_imports': [imp.replace('.proto', '') for imp in get_imports_from_proto(proto_content) 
                             if not imp.startswith('google/') and not imp.startswith('extra_')]
        }
        
        print(f"Generated: {proto_file}")
    
    # Create extra_fieldoption_wuxiaworld.proto in output directory
    from ts_to_proto import ensure_extra_fieldoption
    ensure_extra_fieldoption(output_dir)
    
    # Build dependency graph and topological sort
    # Map proto names to their local imports
    deps = {name: data['local_imports'] for name, data in proto_files.items()}
    
    # Find all proto files that are imported
    all_protos = set(proto_files.keys())
    
    # Topological sort
    sorted_protos = []
    visited = set()
    
    def visit(name):
        if name in visited:
            return
        visited.add(name)
        # Visit dependencies first
        for dep in deps.get(name, []):
            if dep in all_protos:
                visit(dep)
        sorted_protos.append(name)
    
    # Start with files that have no dependencies or only external deps
    for name in sorted(proto_files.keys()):
        visit(name)
    
    print(f"\nOrdered {len(sorted_protos)} proto files")
    
    # Generate wuxia.proto with all imports (sorted alphabetically for consistency)
    lines = ['syntax = "proto3";', '']
    
    # Add extra_fieldoption import first (before other imports)
    lines.append('import "extra_fieldoption_wuxiaworld.proto";')
    
    # Add imports in topological order
    for proto_name in sorted_protos:
        if proto_name not in ['options']:  # options is imported by extra_fieldoption
            lines.append(f'import "{proto_name}.proto";')
    
    lines.append('')
    lines.append('package wuxiaworld.api.v2;')
    lines.append('')
    lines.append('// WUXIA API - Import all proto files above')
    
    wuxia_file = os.path.join(output_dir, 'wuxia.proto')
    with open(wuxia_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\nGenerated: {wuxia_file}")
    print(f"Total: {len(proto_files)} proto files + wuxia.proto")
    
    print(f"\nGenerated: {wuxia_file}")
    print("\nDone!")

if __name__ == "__main__":
    main()
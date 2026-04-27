
#!/usr/bin/env python3
import re
import sys
import os
import argparse

EXTRA_FIELDOPTION_CONTENT = '''syntax = "proto3";
package wuxiaworld.api.v2;

import "google/protobuf/descriptor.proto";
import "options.proto";

extend google.protobuf.FieldOptions {
    FieldStringLengthOptions stringLength = 50001;
    FieldWordLengthOptions wordLength = 50002;
    FieldRequiredOption required = 50003;
    FieldDisplayOption display = 50004;
    FieldRangeOption range = 50005;
}
'''

def ensure_extra_fieldoption(output_dir):
    """Create extra_fieldoption_wuxiaworld.proto in output directory if needed"""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extra_fieldoption_wuxiaworld.proto')
    options_file = os.path.join(output_dir, 'options.proto')
    
    # Copy options.proto from ts_to_proto if it doesn't exist
    source_options = os.path.join(os.path.dirname(__file__), 'options.proto')
    if not os.path.exists(options_file) and os.path.exists(source_options):
        import shutil
        shutil.copy(source_options, options_file)
        print(f'Generated: {options_file}')
    
    # Create extra_fieldoption_wuxiaworld.proto
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(EXTRA_FIELDOPTION_CONTENT)
        print(f'Generated: {output_file}')

def main():
    parser = argparse.ArgumentParser(description='Convert TypeScript to proto file')
    parser.add_argument('input', help='Input TypeScript file or folder')
    parser.add_argument('output', nargs='?', help='Output proto file or folder (default: same name with .proto extension)')
    args = parser.parse_args()
    
    input_path = args.input
    output_path = args.output
    
    if os.path.isdir(input_path):
        ts_files = [f for f in os.listdir(input_path) if f.endswith('.ts')]
        output_dir = output_path if output_path else input_path
        ensure_extra_fieldoption(output_dir)
        for ts_file in sorted(ts_files):
            full_input = os.path.join(input_path, ts_file)
            if output_path:
                full_output = os.path.join(output_path, os.path.splitext(ts_file)[0] + '.proto')
            else:
                full_output = os.path.splitext(full_input)[0] + '.proto'
            data = parse_typescript(full_input)
            proto_content = generate_proto(data)
            with open(full_output, 'w', encoding='utf-8') as f:
                f.write(proto_content)
            print(f'Generated: {full_output}')
    else:
        if not output_path:
            output_path = os.path.splitext(input_path)[0] + '.proto'
        
        output_dir = os.path.dirname(output_path)
        if output_dir:
            ensure_extra_fieldoption(output_dir)
        else:
            ensure_extra_fieldoption('.')
        
        data = parse_typescript(input_path)
        proto_content = generate_proto(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(proto_content)
        
        print(f'Generated: {output_path}')

def parse_typescript(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    package_match = re.search(r'@generated from protobuf file "[^"]+" \(package "([^"]+)"', content)
    package = package_match.group(1) if package_match else "package"

    # Parse enums
    enums = {}
    for em in re.finditer(r'export\s+enum\s+(\w+)\s*\{(.*?)\}', content, re.DOTALL):
        values = {vm.group(1): int(vm.group(2)) for vm in re.finditer(r'(\w+)\s*=\s*(-?\d+)', em.group(2))}
        enums[em.group(1)] = {'name': em.group(1), 'values': values}

    # Find all message class definitions
    messages = {}
    nested = {}
    
    msg_class_pattern = r'class\s+(\w+)\$Type\s+extends\s+MessageType'
    
    for m in re.finditer(msg_class_pattern, content):
        class_name = m.group(1)
        region = content[m.end():m.end()+4000]
        # Try multiple patterns for compatibility
        super_match = re.search(r'super\s*\(\s*"([^"]+)",\s*\[(.*?)\]\)', region, re.DOTALL)
        if not super_match:
            super_match = re.search(r'super\("([^"]+)",\s*\[(.*?)\]\)', region, re.DOTALL)
        
        if not super_match:
            continue
            
        full_name = super_match.group(1)
        fields_str = super_match.group(2)
        fields = []
        
        # Find all fields in the message
        field_pattern = r'\{ no:\s*(\d+),\s*name:\s*"([^"]+)",\s*kind:\s*"([^"]+)"'
        
        for f in re.finditer(field_pattern, fields_str):
            field_no = int(f.group(1))
            field_name = f.group(2)
            kind = f.group(3)
            
            is_map = (kind == "map")
            
            # Get region for type info
            field_end_match = re.search(r'\}(?:,|\s*\])', fields_str[f.end():])
            next_field_match = re.search(r',\s*no:', fields_str[f.end():])
            
            # Find the matching closing brace by counting
            brace_count = 1
            end_pos = f.end()
            while end_pos < len(fields_str) and brace_count > 0:
                c = fields_str[end_pos]
                if c == '{':
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1
                end_pos += 1
            
            # Just extend region far enough to include options but NOT into next field
            # Find next field start first
            next_field_match = re.search(r',\s*\{ no:\s*\d+', fields_str[f.end():])
            if next_field_match:
                # Cut region at next field
                region = fields_str[f.end():f.end() + next_field_match.start()]
            else:
                region = fields_str[f.end():f.end() + 800]
            
            # Check for oneof
            oneof_match = re.search(r'oneof:\s*"([^"]+)"', region)
            oneof_name = oneof_match.group(1) if oneof_match else None
            
            # Check for types
            scalar_match = re.search(r'T:\s*(\d+)', region)
            enum_match = re.search(r'T:\s*\(\)\s*=>\s*\["[^"]+",\s*(\w+)\]', region)
            msg_match = re.search(r'T:\s*\(\)\s*=>\s*(\w+)', region)
            
# Check for field options (e.g., "wuxiaworld.api.v2.range": { max: { value: 100 } })
            field_options = []
            # Find options block - need to match balanced braces
            region_search = region
            options_start = region_search.find('options:')
            if options_start >= 0:
                options_region = region_search[options_start:]
                # Count braces to find matching closing brace
                brace_count = 0
                opts_end = 0
                for i, c in enumerate(options_region):
                    if c == '{':
                        brace_count += 1
                    elif c == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            opts_end = i + 1
                            break
                
                if opts_end > 0:
                    opts_str = options_region[options_region.find('{')+1:opts_end-1]
                else:
                    opts_str = None
                
                # Find all individual options
                if opts_str:
                    for opt_match in re.finditer(r'"([^"]+)":\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}', opts_str):
                        opt_name = opt_match.group(1)
                        opt_value_str = opt_match.group(2)
                    
                        # Parse value: true/false for required option
                        value_match = re.search(r'value:\s*(true|false)', opt_value_str)
                        if value_match:
                            value = value_match.group(1)
                            field_options.append({'name': opt_name, 'value': value})
                        # Parse minLength/maxLength for stringLength option
                        elif 'minLength:' in opt_value_str or 'maxLength:' in opt_value_str:
                            min_match = re.search(r'minLength:\s*\{\s*value:\s*(\d+)\s*\}', opt_value_str)
                            max_match = re.search(r'maxLength:\s*\{\s*value:\s*(\d+)\s*\}', opt_value_str)
                            error_match = re.search(r'errorMessage:\s*\{\s*value:\s*"([^"]+)"\s*\}', opt_value_str)
                            min_val = min_match.group(1) if min_match else None
                            max_val = max_match.group(1) if max_match else None
                            error_val = error_match.group(1) if error_match else None
                            if min_val or max_val or error_val:
                                field_options.append({'name': opt_name, 'min': min_val, 'max': max_val, 'error': error_val, 'key': 'stringLength'})
                        # Parse minWords/maxWords for wordLength option
                        elif 'minWords:' in opt_value_str or 'maxWords:' in opt_value_str:
                            min_match = re.search(r'minWords:\s*\{\s*value:\s*(\d+)\s*\}', opt_value_str)
                            max_match = re.search(r'maxWords:\s*\{\s*value:\s*(\d+)\s*\}', opt_value_str)
                            min_val = min_match.group(1) if min_match else None
                            max_val = max_match.group(1) if max_match else None
                            if min_val or max_val:
                                field_options.append({'name': opt_name, 'min': min_val, 'max': max_val, 'key': 'wordLength'})
                        # Parse name for display option
                        elif 'name:' in opt_value_str:
                            name_match = re.search(r'name:\s*"([^"]+)"', opt_value_str)
                            if name_match:
                                field_options.append({'name': opt_name, 'value': name_match.group(1), 'key': 'display'})
            if scalar_match:
                type_code = int(scalar_match.group(1))
                type_map = {1: 'double', 2: 'float', 3: 'int64', 4: 'uint64', 5: 'int32', 6: 'fixed64', 7: 'fixed32', 8: 'bool', 9: 'string', 12: 'bytes', 13: 'uint32', 15: 'sfixed32', 16: 'sfixed64'}
                ftype = type_map.get(type_code, f'int{type_code}')
            elif enum_match:
                ftype = enum_match.group(1)
            elif msg_match:
                ftype = msg_match.group(1)
            else:
                ftype = 'unknown'
            
            repeated_match = re.search(r'repeat:\s*[12]', region)
            is_repeated = repeated_match is not None
            
            # Parse map key/value types
            map_key_type = None
            map_value_type = None
            if is_map:
                k_match = re.search(r'K:\s*(\d+)', region)
                if k_match:
                    key_code = int(k_match.group(1))
                    type_map = {1: 'double', 2: 'float', 3: 'int64', 4: 'uint64', 5: 'int32', 6: 'fixed64', 7: 'fixed32', 8: 'bool', 9: 'string', 12: 'bytes', 13: 'uint32', 15: 'sfixed32', 16: 'sfixed64'}
                    map_key_type = type_map.get(key_code, f'int{key_code}')
                # Try message type first (V: { kind: "message", T: () => TypeName })
                v_match = re.search(r'V:\s*\{[^}]*T:\s*\(\)\s*=>\s*(\w+)', region)
                if v_match:
                    map_value_type = v_match.group(1)
                else:
                    # Try scalar type (V: { kind: "scalar", T: code })
                    v_scalar_match = re.search(r'V:\s*\{[^}]*kind:\s*"scalar"[^}]*T:\s*(\d+)', region)
                    if v_scalar_match:
                        val_code = int(v_scalar_match.group(1))
                        map_value_type = type_map.get(val_code, f'int{val_code}')
            
            fields.append({
                'name': field_name,
                'type': ftype,
                'number': field_no,
                'repeated': is_repeated or is_map,
                'oneof': oneof_name,
                'is_map': is_map,
                'map_key_type': map_key_type,
                'map_value_type': map_value_type,
                'field_options': field_options
            })
        
        fields.sort(key=lambda x: x['number'])
        
        # Determine if this is a nested message
        if '_' in class_name:
            parts = class_name.split('_', 1)
            parent = parts[0]
            child = parts[1]
            full_nested_name = f"{parent}.{child}"
            nested[full_nested_name] = {'name': child, 'fields': fields}
        else:
            messages[class_name] = {'name': full_name, 'fields': fields}

    # Detect nested enums (enums with underscore that belong to a message)
    nested_enums = {}
    for enum_name, enum_data in list(enums.items()):
        if '_' in enum_name:
            parts = enum_name.split('_')
            if len(parts) >= 2:
                potential_parent = parts[0]
                # Check if this parent exists in messages
                if potential_parent in messages:
                    parent = parts[0]
                    child = '_'.join(parts[1:])
                    nested_enums[enum_name] = {
                        'parent': parent,
                        'name': child,
                        'values': enum_data['values']
                    }
                    del enums[enum_name]

    # Services
    services = {}
    for sm in re.finditer(r'export\s+const\s+(\w+)\s*=\s*new\s+ServiceType\("([^"]+)",\s*\[(.*?)\]\)', content, re.DOTALL):
        rpcs = []
        for rm in re.finditer(r'\{ name: "(\w+)",\s*options: \{\},\s*I: (\w+),\s*O: (\w+) \}', sm.group(3)):
            rpcs.append({
                'name': rm.group(1),
                'request': rm.group(2),
                'response': rm.group(3)
            })
        services[sm.group(1)] = {'name': sm.group(2), 'rpcs': rpcs}

    return {'package': package, 'enums': enums, 'messages': messages, 'nested_messages': nested, 'nested_enums': nested_enums, 'services': services}

def get_proto_type(t):
    # Map google protobuf types
    google_map = {
        'Empty': 'google.protobuf.Empty',
        'StringValue': 'google.protobuf.StringValue',
        'Int32Value': 'google.protobuf.Int32Value',
        'Int64Value': 'google.protobuf.Int64Value',
        'UInt32Value': 'google.protobuf.UInt32Value',
        'UInt64Value': 'google.protobuf.UInt64Value',
        'DoubleValue': 'google.protobuf.DoubleValue',
        'FloatValue': 'google.protobuf.FloatValue',
        'BoolValue': 'google.protobuf.BoolValue',
        'BytesValue': 'google.protobuf.BytesValue',
        'Timestamp': 'google.protobuf.Timestamp',
        'Duration': 'google.protobuf.Duration',
        'Timestamp_': 'google.protobuf.Timestamp',
        'Any': 'google.protobuf.Any',
    }
    if t in google_map:
        return google_map[t]
    
    # Map scalar types
    scalar_map = {'int32': 'int32', 'int64': 'int64', 'bool': 'bool', 'string': 'string'}
    if t in scalar_map:
        return scalar_map[t]
    
    # Convert nested message type from underscore to dot notation
    # e.g., GetChapterListRequest_BaseChapterInfo -> GetChapterListRequest.BaseChapterInfo
    # But skip MapEntry types: MapEntry_0 should stay as MapEntry_0, not MapEntry.0
    # Also skip types that contain _MapEntry_ (nested map entries like SubscriptionLineItem_MapEntry_0)
    if '_' in t and 'MapEntry' not in t:
        # Check if this looks like a nested type (ParentName_NestedName)
        parts = t.split('_')
        # Only convert if there are at least 2 parts and first part starts with uppercase
        if len(parts) >= 2 and parts[0][0].isupper():
            # Reconstruct with dot: ParentName.NestedName
            return t.replace('_', '.')
    
    return t

def get_import_for_type(t, local_types):
    """Map type names to proto files - returns None if local/builtin"""
    external_map = {
        'PaymentMethodItem': 'payments.proto',
        'PaymentMethodGateway': 'payments.proto',
        'DecimalValue': 'types.proto',
        'PageInfoRequest': 'pagination.proto',
        'PageInfoResponse': 'pagination.proto',
        'GenreItem': 'genres.proto',
        'PricingModel': 'pricing.proto',
        'OrderItem': 'orders.proto',
        'ProductItem': 'products.proto',
        'ProductType': 'products.proto',
        'ProductSurveyItem': 'product_surveys.proto',
        'BillingPeriod': 'billing.proto',
        'KarmaTransactionItem': 'karma.proto',
        'ChapterItem': 'chapters.proto',
        'NovelItem': 'novels.proto',
        'Discount': 'discounts.proto',
        'VipItem': 'vips.proto',
        'UnlockedVipNovelInfo': 'vips.proto',
        'ObjectItem': 'objects.proto',
        'Role': 'roles.proto',
        'ChapterAudioInfo': 'audio.proto',
        'ChapterParagraph': 'chapter_paragraphs.proto',
        'UnlockItemMethod': 'unlocks.proto',
        'SeriesItem': 'series.proto',
        'SeriesTypeItem': 'series_types.proto',
        'Entity': 'entity.proto',
        'UserItem': 'users.proto',
        'SponsorPlanItem': 'sponsors.proto',
        'ChapterGroupItem': 'chapters.proto',
        'ChapterItem': 'chapters.proto',
        'MissionItem': 'missions.proto',
        'UnlockedItem': 'unlocks.proto',
        'NovelInfo': 'novels.proto',
    }
    if t in external_map and t not in local_types:
        result = external_map[t]
        return result
    return None

def generate_proto(data):
    lines = ['syntax = "proto3";']
    
    # Collect all local types
    local_types = set(data['messages'].keys())
    local_types.update(data['enums'].keys())
    for nested in data['nested_messages'].keys():
        parts = nested.split('.')
        local_types.add(parts[0])
    
    # Check what imports we need
    needs_empty = False
    needs_timestamp = False
    needs_descriptor = False
    needs_duration = False
    needs_stringvalue = False
    needs_wrappers = False
    needs_any = False
    needs_payments = False
    needs_types = False
    needs_pagination = False
    needs_genres = False
    needs_pricing = False
    needs_orders = False
    needs_products = False
    needs_discounts = False
    needs_vips = False
    needs_objects = False
    needs_roles = False
    needs_audio = False
    needs_chapter_paragraphs = False
    needs_unlocks = False
    needs_series = False
    needs_series_types = False
    needs_entity = False
    needs_users = False
    needs_sponsors = False
    needs_chapters = False
    needs_novels = False
    needs_missions = False
    needs_product_surveys = False
    needs_billing = False
    needs_karma = False
    
# Check main messages
    all_wrappers = ['google.protobuf.Int32Value', 'google.protobuf.Int64Value', 'google.protobuf.UInt32Value', 'google.protobuf.UInt64Value', 'google.protobuf.DoubleValue', 'google.protobuf.FloatValue', 'google.protobuf.BoolValue', 'google.protobuf.StringValue', 'google.protobuf.BytesValue']
    for msg_name, msg in data['messages'].items():
        for f in msg['fields']:
            ftype = get_proto_type(f['type'])
            if 'google.protobuf.Empty' in ftype:
                needs_empty = True
            elif 'google.protobuf.Timestamp' in ftype:
                needs_timestamp = True
            elif 'google.protobuf.Duration' in ftype:
                needs_duration = True
            elif any(w in ftype for w in all_wrappers):
                needs_wrappers = True
            elif 'google.protobuf.Any' in ftype:
                needs_any = True
            # Check for field options (like range)
            if f.get('field_options'):
                needs_descriptor = True
            # Always check for external imports
            ext_import = get_import_for_type(ftype, local_types)
            if ext_import:
                if ext_import == 'payments.proto':
                    needs_payments = True
                elif ext_import == 'types.proto':
                    needs_types = True
                elif ext_import == 'pagination.proto':
                    needs_pagination = True
                elif ext_import == 'genres.proto':
                    needs_genres = True
                elif ext_import == 'pricing.proto':
                    needs_pricing = True
                elif ext_import == 'orders.proto':
                    needs_orders = True
                elif ext_import == 'products.proto':
                    needs_products = True
                elif ext_import == 'discounts.proto':
                    needs_discounts = True
                elif ext_import == 'vips.proto':
                    needs_vips = True
                elif ext_import == 'objects.proto':
                    needs_objects = True
                elif ext_import == 'roles.proto':
                    needs_roles = True
                elif ext_import == 'audio.proto':
                    needs_audio = True
                elif ext_import == 'chapter_paragraphs.proto':
                    needs_chapter_paragraphs = True
                elif ext_import == 'unlocks.proto':
                    needs_unlocks = True
                elif ext_import == 'series.proto':
                    needs_series = True
                elif ext_import == 'series_types.proto':
                    needs_series_types = True
                elif ext_import == 'entity.proto':
                    needs_entity = True
                elif ext_import == 'product_surveys.proto':
                    needs_product_surveys = True
                elif ext_import == 'billing.proto':
                    needs_billing = True
                elif ext_import == 'karma.proto':
                    needs_karma = True
                elif ext_import == 'chapters.proto':
                    needs_chapters = True
                elif ext_import == 'novels.proto':
                    needs_novels = True
                elif ext_import == 'missions.proto':
                    needs_missions = True
                elif ext_import == 'users.proto':
                    needs_users = True
                elif ext_import == 'sponsors.proto':
                    needs_sponsors = True
    
    # Check nested messages
    for nested_name, nested_data in data['nested_messages'].items():
        for f in nested_data['fields']:
            ftype = get_proto_type(f['type'])
            if 'google.protobuf.Timestamp' in ftype:
                needs_timestamp = True
            elif 'google.protobuf.Duration' in ftype:
                needs_duration = True
            elif any(w in ftype for w in all_wrappers):
                needs_wrappers = True
            elif 'google.protobuf.Any' in ftype:
                needs_any = True
            # Check for field options (like range)
            if f.get('field_options'):
                needs_descriptor = True
# Always check for external imports
            ext_import = get_import_for_type(ftype, local_types)
            if ext_import:
                if ext_import == 'payments.proto':
                    needs_payments = True
                elif ext_import == 'types.proto':
                    needs_types = True
                elif ext_import == 'pagination.proto':
                    needs_pagination = True
                elif ext_import == 'genres.proto':
                    needs_genres = True
                elif ext_import == 'pricing.proto':
                    needs_pricing = True
                elif ext_import == 'orders.proto':
                    needs_orders = True
                elif ext_import == 'products.proto':
                    needs_products = True
                elif ext_import == 'discounts.proto':
                    needs_discounts = True
                elif ext_import == 'vips.proto':
                    needs_vips = True
                elif ext_import == 'objects.proto':
                    needs_objects = True
                elif ext_import == 'roles.proto':
                    needs_roles = True
                elif ext_import == 'audio.proto':
                    needs_audio = True
                elif ext_import == 'chapter_paragraphs.proto':
                    needs_chapter_paragraphs = True
                elif ext_import == 'unlocks.proto':
                    needs_unlocks = True
                elif ext_import == 'series.proto':
                    needs_series = True
                elif ext_import == 'series_types.proto':
                    needs_series_types = True
                elif ext_import == 'entity.proto':
                    needs_entity = True
                elif ext_import == 'product_surveys.proto':
                    needs_product_surveys = True
                elif ext_import == 'billing.proto':
                    needs_billing = True
                elif ext_import == 'karma.proto':
                    needs_karma = True
                elif ext_import == 'chapters.proto':
                    needs_chapters = True
                elif ext_import == 'novels.proto':
                    needs_novels = True
                elif ext_import == 'missions.proto':
                    needs_missions = True
                elif ext_import == 'users.proto':
                    needs_users = True
                elif ext_import == 'sponsors.proto':
                    needs_sponsors = True
    
    # Check service RPCs for Empty type (both request and response)
    for sn, svc in data['services'].items():
        for r in svc['rpcs']:
            if r['request'] == 'Empty' or r['response'] == 'Empty':
                needs_empty = True
    
    # Package goes before imports (per expected format)
    if data['package']:
        lines.append(f"package {data['package']};")
    
    if needs_empty or needs_timestamp or needs_duration or needs_wrappers or needs_any or needs_payments or needs_types or needs_pagination or needs_genres or needs_pricing or needs_orders or needs_products or needs_discounts or needs_vips or needs_objects or needs_roles or needs_audio or needs_chapter_paragraphs or needs_unlocks or needs_series or needs_users or needs_sponsors or needs_chapters or needs_product_surveys or needs_billing or needs_karma or needs_novels or needs_missions or needs_series_types or needs_entity or needs_descriptor:
        lines.append('')
        if needs_empty:
            lines.append('import "google/protobuf/empty.proto";')
        if needs_timestamp:
            lines.append('import "google/protobuf/timestamp.proto";')
        if needs_duration:
            lines.append('import "google/protobuf/duration.proto";')
        if needs_stringvalue or needs_wrappers:
            lines.append('import "google/protobuf/wrappers.proto";')
        if needs_any:
            lines.append('import "google/protobuf/any.proto";')
        if needs_descriptor:
            lines.append('import "google/protobuf/descriptor.proto";')
            lines.append('import "extra_fieldoption_wuxiaworld.proto";')
        
        # Collect local imports and sort alphabetically
        local_imports = []
        if needs_payments:
            local_imports.append('payments.proto')
        if needs_types:
            local_imports.append('types.proto')
        if needs_pagination:
            local_imports.append('pagination.proto')
        if needs_genres:
            local_imports.append('genres.proto')
        if needs_pricing:
            local_imports.append('pricing.proto')
        if needs_orders:
            local_imports.append('orders.proto')
        if needs_products:
            local_imports.append('products.proto')
        if needs_discounts:
            local_imports.append('discounts.proto')
        if needs_vips:
            local_imports.append('vips.proto')
        if needs_objects:
            local_imports.append('objects.proto')
        if needs_roles:
            local_imports.append('roles.proto')
        if needs_audio:
            local_imports.append('audio.proto')
        if needs_chapter_paragraphs:
            local_imports.append('chapter_paragraphs.proto')
        if needs_unlocks:
            local_imports.append('unlocks.proto')
        if needs_series:
            local_imports.append('series.proto')
        if needs_series_types:
            local_imports.append('series_types.proto')
        if needs_entity:
            local_imports.append('entity.proto')
        if needs_users:
            local_imports.append('users.proto')
        if needs_sponsors:
            local_imports.append('sponsors.proto')
        if needs_chapters:
            local_imports.append('chapters.proto')
        if needs_product_surveys:
            local_imports.append('product_surveys.proto')
        if needs_billing:
            local_imports.append('billing.proto')
        if needs_karma:
            local_imports.append('karma.proto')
        if needs_novels:
            local_imports.append('novels.proto')
        if needs_missions:
            local_imports.append('missions.proto')
        
        for imp in sorted(local_imports):
            lines.append(f'import "{imp}";')
        
        lines.append('')
    
    # Top-level enums (preserve order from TypeScript)
    for en in sorted(data['enums'].keys()):
        lines.append(f"enum {en} {{")
        for vn in data['enums'][en]['values'].keys():
            lines.append(f"    {vn} = {data['enums'][en]['values'][vn]};")
        lines.append('}')
        lines.append('')

    # Messages in order (preserve original order from TypeScript)
    order = list(data['messages'].keys())
    
    for mn in order:
        if mn not in data['messages']:
            continue
        msg = data['messages'][mn]
        lines.append(f"message {mn} {{")
        
        # Check for nested messages in this message
        nested_enums_data = data.get('nested_enums', {})
        for nested_name, nested_data in data['nested_messages'].items():
            if nested_name.startswith(mn + '.'):
                lines.append(f"    message {nested_data['name']} {{")
                
                # Group nested fields by oneof
                nested_oneof_groups = {}
                nested_regular_fields = []
                for f in nested_data['fields']:
                    if f.get('oneof'):
                        oneof_name = f['oneof']
                        if oneof_name not in nested_oneof_groups:
                            nested_oneof_groups[oneof_name] = []
                        nested_oneof_groups[oneof_name].append(f)
                    else:
                        nested_regular_fields.append(f)
                
                # Output oneofs in nested message
                for oneof_name, oneof_fields in nested_oneof_groups.items():
                    lines.append(f"        oneof {oneof_name} {{")
                    for f in oneof_fields:
                        lines.append(f"            {get_proto_type(f['type'])} {f['name']} = {f['number']};")
                    lines.append("        }")
                
                # Output regular fields in nested message
                for f in nested_regular_fields:
                    prefix = 'repeated ' if f.get('repeated') else 'optional '
                    field_opts = f.get('field_options', [])
                    opt_parts = []
                    for opt in field_opts:
                        if opt.get('key') == 'stringLength':
                            min_part = f"minLength: {{value: {opt['min']}}}" if opt.get('min') else ""
                            max_part = f"maxLength: {{value: {opt['max']}}}" if opt.get('max') else ""
                            error_part = f"errorMessage: {{value: \"{opt['error']}\"}}" if opt.get('error') else ""
                            parts = [p for p in [min_part, max_part, error_part] if p]
                            inner = ', '.join(parts)
                            opt_parts.append(f"({opt['name']}) = {{ {inner} }}")
                        elif opt.get('key') == 'wordLength':
                            min_part = f"minWords: {{value: {opt['min']}}}" if opt.get('min') else ""
                            max_part = f"maxWords: {{value: {opt['max']}}}" if opt.get('max') else ""
                            inner = ', '.join(filter(None, [min_part, max_part]))
                            opt_parts.append(f"({opt['name']}) = {{ {inner} }}")
                        elif 'min' in opt or 'max' in opt:
                            min_part = f"min: {{value: {opt['min']}}}" if opt.get('min') else ""
                            max_part = f"max: {{value: {opt['max']}}}" if opt.get('max') else ""
                            inner = ', '.join(filter(None, [min_part, max_part]))
                            opt_parts.append(f"({opt['name']}) = {{ {inner} }}")
                        elif opt.get('value') == 'true':
                            opt_parts.append(f"({opt['name']}) = {{value: true}}")
                        elif opt.get('value') == 'false':
                            opt_parts.append(f"({opt['name']}) = {{value: false}}")
                        elif opt.get('key') == 'display':
                            opt_parts.append(f"({opt['name']}) = {{name: \"{opt['value']}\"}}")
                        else:
                            opt_parts.append(f"({opt['name']}) = {{value: {opt['value']} }}")
                    field_opt = f" [{', '.join(opt_parts)}]" if field_opts else ''
                    lines.append(f"        {prefix}{get_proto_type(f['type'])} {f['name']} = {f['number']}{field_opt};")
                
                # Check for nested enums in this nested message (output BEFORE closing brace)
                for enum_name, enum_data in nested_enums_data.items():
                    if enum_data.get('parent') == mn:
                        enum_full = enum_data['name']
                        simple_name = enum_full.split('_')[-1]
                        # Check if this enum belongs to current nested message
                        if nested_data['name'] in enum_full or enum_full.endswith(f"_{nested_data['name']}_{simple_name}"):
                            lines.append(f"        enum {simple_name} {{")
                            for vn in enum_data['values'].keys():
                                lines.append(f"            {vn} = {enum_data['values'][vn]};")
                            lines.append("        }")
                            lines.append('')
                
                lines.append("    }")
                lines.append('')
        
        # Check for nested enums in this message (that are NOT inside nested messages - those are handled above)
        nested_messages_names = {name for name in data.get('nested_messages', {}).keys() if name.startswith(mn + '.')}
        nested_enums_data = data.get('nested_enums', {})
        for enum_name, enum_data in nested_enums_data.items():
            if enum_data.get('parent') == mn:
                # Check if enum belongs to a nested message (e.g., RejectionInfo_State for ReviewItem.RejectionInfo)
                enum_full = enum_data['name']
                # Extract simple name (e.g., "State" from "ReviewItem_RejectionInfo_State")
                simple_name = enum_full.split('_')[-1]
                
                # Check if this enum should go inside a nested message
                is_in_nested = False
                for nest_name in nested_messages_names:
                    # e.g., "ReviewItem.RejectionInfo" - extract "RejectionInfo"
                    nest_simple = nest_name.split('.')[-1]
                    if enum_full.startswith(mn + '_' + nest_simple + '_'):
                        # This enum belongs to a nested message, will be output there
                        is_in_nested = True
                        break
                
                if is_in_nested:
                    continue  # Skip - will be handled when outputting nested message
                
                lines.append(f"    enum {simple_name} {{")
                for vn in enum_data['values'].keys():
                    lines.append(f"        {vn} = {enum_data['values'][vn]};")
                lines.append("    }")
                lines.append('')
        
        # Generate nested MapEntry messages for map fields
        map_counter = 0
        for f in msg['fields']:
            if f.get('is_map'):
                map_counter += 1
                map_entry_name = f"MapEntry_{map_counter - 1}"
                key_type = f.get('map_key_type', 'int32')
                val_type = f.get('map_value_type', f['type'])
                lines.append(f"    message {map_entry_name} {{")
                lines.append(f"        optional {key_type} key = 1;")
                lines.append(f"        optional {val_type} value = 2;")
                lines.append("    }")
                lines.append('')
                f['map_entry_name'] = map_entry_name
        
        # Group fields by oneof
        oneof_groups = {}
        regular_fields = []
        
        for f in msg['fields']:
            if f.get('oneof'):
                oneof_name = f['oneof']
                if oneof_name not in oneof_groups:
                    oneof_groups[oneof_name] = []
                oneof_groups[oneof_name].append(f)
            else:
                regular_fields.append(f)
        
        # Output oneofs
        for oneof_name, oneof_fields in oneof_groups.items():
            lines.append(f"    oneof {oneof_name} {{")
            for f in oneof_fields:
                # Convert underscore to dot for oneof field types
                ftype = f['type']
                if '_' in ftype and ftype not in ['ChapterAudioPart']:
                    parts = ftype.split('_', 1)
                    ftype = parts[0] + '.' + parts[1]
                lines.append(f"        {get_proto_type(ftype)} {f['name']} = {f['number']};")
            lines.append("    }")
            lines.append('')
        
        # Output regular fields
        for f in regular_fields:
            prefix = 'repeated ' if f.get('repeated') else 'optional '
            ftype = f['type']
            # Handle map fields - use MapEntry nested message
            if f.get('is_map') and f.get('map_entry_name'):
                ftype = f"{mn}.{f['map_entry_name']}"
            elif '_' in ftype:
                parts = ftype.split('_', 1)
                ftype = parts[0] + '.' + parts[1]
            field_opts = f.get('field_options', [])
            opt_parts = []
            for opt in field_opts:
                if opt.get('key') == 'stringLength':
                    min_part = f"minLength: {{value: {opt['min']}}}" if opt.get('min') else ""
                    max_part = f"maxLength: {{value: {opt['max']}}}" if opt.get('max') else ""
                    error_part = f"errorMessage: {{value: \"{opt['error']}\"}}" if opt.get('error') else ""
                    parts = [p for p in [min_part, max_part, error_part] if p]
                    inner = ', '.join(parts)
                    opt_parts.append(f"({opt['name']}) = {{ {inner} }}")
                elif opt.get('key') == 'wordLength':
                    min_part = f"minWords: {{value: {opt['min']}}}" if opt.get('min') else ""
                    max_part = f"maxWords: {{value: {opt['max']}}}" if opt.get('max') else ""
                    inner = ', '.join(filter(None, [min_part, max_part]))
                    opt_parts.append(f"({opt['name']}) = {{ {inner} }}")
                elif 'min' in opt or 'max' in opt:
                    min_part = f"min: {{value: {opt['min']}}}" if opt.get('min') else ""
                    max_part = f"max: {{value: {opt['max']}}}" if opt.get('max') else ""
                    inner = ', '.join(filter(None, [min_part, max_part]))
                    opt_parts.append(f"({opt['name']}) = {{ {inner} }}")
                elif opt.get('value') == 'true':
                    opt_parts.append(f"({opt['name']}) = {{value: true}}")
                elif opt.get('value') == 'false':
                    opt_parts.append(f"({opt['name']}) = {{value: false}}")
                elif opt.get('key') == 'display':
                    opt_parts.append(f"({opt['name']}) = {{name: \"{opt['value']}\"}}")
                else:
                    opt_parts.append(f"({opt['name']}) = {{value: {opt['value']} }}")
            field_opt = f" [{', '.join(opt_parts)}]" if field_opts else ''
            lines.append(f"    {prefix}{get_proto_type(ftype)} {f['name']} = {f['number']}{field_opt};")
        
        lines.append('}')
        lines.append('')

    # Services
    for sn in sorted(data['services'].keys()):
        svc = data['services'][sn]
        name = svc['name'].split('.')[-1]
        lines.append(f"service {name} {{")
        for r in svc['rpcs']:
            req = get_proto_type(r['request'])
            resp = get_proto_type(r['response'])
            lines.append(f"    rpc {r['name']}({req}) returns ({resp});")
        lines.append('}')

    return '\n'.join(lines)

if __name__ == '__main__':
    main()
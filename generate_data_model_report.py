"""
Generate comprehensive data model report
Analyzes entities, fields, field groups, requirements, and relationships
"""

import json
import os
from datetime import datetime
from collections import defaultdict


def load_data_model(json_file="generated_data_model.json"):
    """Load data model from JSON file"""
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Data model file not found: {json_file}")
    
    with open(json_file, 'r') as f:
        return json.load(f)


def analyze_entity(entity):
    """Analyze a single entity and extract key information"""
    entity_name = entity.get('name', 'Unknown')
    entity_type = entity.get('type', 'Unknown')
    description = entity.get('description', 'No description')
    fields = entity.get('fields', [])
    
    # Categorize fields
    identifiers = []
    general_attributes = []
    field_groups = defaultdict(list)
    meta_fields = []
    lookup_fields = []
    custom_fields = []
    required_fields = []
    
    for field in fields:
        field_name = field.get('name', '')
        field_group = field.get('fieldGroup')
        data_type = field.get('dataType', '')
        is_custom = field.get('isCustom', False)
        is_required = field.get('isRequired', False)
        is_lookup = field.get('isLookup', False)
        
        # Categorize
        if field_group == '_meta':
            meta_fields.append(field)
        elif field_group and field_group != '_meta':
            field_groups[field_group].append(field)
        elif 'id' in field_name.lower() or 'identifier' in field_name.lower():
            identifiers.append(field)
        else:
            general_attributes.append(field)
        
        # Track special properties
        if is_lookup or 'lookup' in data_type.lower():
            lookup_fields.append(field)
        if is_custom:
            custom_fields.append(field)
        if is_required:
            required_fields.append(field)
    
    # Analyze requirements
    all_requirement_ids = set()
    requirement_to_fields = defaultdict(list)
    requirement_to_text = {}  # Map requirement ID to full text
    
    for field in fields:
        req_ids = field.get('requirementIds', [])
        source_reqs = field.get('sourceRequirements', [])
        
        for req_id in req_ids:
            all_requirement_ids.add(req_id)
            requirement_to_fields[req_id].append(field)
            
            # Extract full requirement text
            # If we haven't found text for this requirement ID yet, try to find it
            if req_id not in requirement_to_text:
                for source_req in source_reqs:
                    # Check if source requirement matches this requirement ID
                    if source_req.startswith(req_id + ':'):
                        requirement_to_text[req_id] = source_req
                        break
                    elif req_id in source_req:
                        requirement_to_text[req_id] = source_req
                        break
                    # For STANDARD requirements, look for "Standard" in the text
                    elif req_id == 'STANDARD' and 'standard' in source_req.lower():
                        requirement_to_text[req_id] = source_req
                        break
    
    return {
        'name': entity_name,
        'type': entity_type,
        'description': description,
        'total_fields': len(fields),
        'identifiers': identifiers,
        'general_attributes': general_attributes,
        'field_groups': dict(field_groups),
        'meta_fields': meta_fields,
        'lookup_fields': lookup_fields,
        'custom_fields': custom_fields,
        'required_fields': required_fields,
        'requirement_ids': sorted(all_requirement_ids),
        'requirement_to_fields': dict(requirement_to_fields),
        'requirement_to_text': requirement_to_text
    }


def generate_html_report(data_model, output_file="data_model_report.html"):
    """Generate comprehensive HTML report"""
    
    entities = data_model.get('entities', [])
    relationships = data_model.get('relationships', [])
    
    # Analyze all entities
    entity_analyses = [analyze_entity(entity) for entity in entities]
    
    # Overall statistics - Only count BusinessEntity
    business_entities_list = [e for e in entities if e.get('type') == 'BusinessEntity']
    total_entities = len(business_entities_list)
    total_fields = sum(len(e.get('fields', [])) for e in business_entities_list)
    total_relationships = len(relationships)
    all_field_groups = set()
    all_requirements = set()
    
    business_analyses = [a for a in entity_analyses if a['type'] == 'BusinessEntity']
    for analysis in business_analyses:
        all_field_groups.update(analysis['field_groups'].keys())
        all_requirements.update(analysis['requirement_ids'])
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Model Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .header .timestamp {{
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #34495e;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #34495e;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .entity-card {{
            background: #f8f9fa;
            border-left: 5px solid #34495e;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        
        .entity-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .entity-name {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        
        .entity-type {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-left: 15px;
        }}
        
        .entity-type.business {{
            background: #34495e;
            color: white;
        }}
        
        .entity-type.reference {{
            background: #48bb78;
            color: white;
        }}
        
        .entity-description {{
            color: #666;
            font-style: italic;
            margin-bottom: 25px;
        }}
        
        .field-category {{
            margin-bottom: 25px;
        }}
        
        .category-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #34495e;
            margin-bottom: 15px;
            padding: 10px;
            background: #ecf0f1;
            border-radius: 5px;
        }}
        
        .field-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
        }}
        
        .field-item {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 12px;
            font-size: 0.9em;
        }}
        
        .field-item.lookup-field {{
            background: #E3F2FD;
            border: 1px solid #2196F3;
        }}
        
        .field-item .field-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .field-item.lookup-field .field-name {{
            color: #1976D2;
        }}
        
        .field-item .field-details {{
            color: #666;
            font-size: 0.85em;
        }}
        
        .field-group-section {{
            margin-bottom: 20px;
        }}
        
        .field-group-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: #FFC107;
            margin-bottom: 10px;
            padding: 8px;
            background: #FFF9C4;
            border-radius: 5px;
        }}
        
        .requirement-section {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .requirement-item {{
            margin-bottom: 15px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #2196F3;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .requirement-id {{
            font-weight: 600;
            color: #1976D2;
            margin-bottom: 5px;
        }}
        
        .requirement-fields {{
            font-size: 1em;
            color: #333;
            margin-top: 10px;
            line-height: 1.6;
        }}
        
        .requirement-fields ul {{
            margin-top: 10px;
            padding-left: 20px;
        }}
        
        .requirement-fields li {{
            margin-bottom: 12px;
            line-height: 1.6;
        }}
        
        .requirement-fields li strong {{
            color: #1976D2;
            display: block;
            margin-bottom: 4px;
        }}
        
        .requirement-fields li span {{
            color: #444 !important;
            font-size: 0.95em !important;
            display: block;
            padding: 8px;
            background: #f8f9fa;
            border-left: 3px solid #2196F3;
            margin-top: 4px;
            border-radius: 3px;
        }}
        
        .relationship-card {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        
        .relationship-entities {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .relationship-arrow {{
            font-size: 1.5em;
            color: white;
        }}
        
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .summary-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        
        .summary-table td {{
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .summary-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            margin-right: 5px;
        }}
        
        .badge.fr {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge.dqr {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge.standard {{
            background: #ecf0f1;
            color: #34495e;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Model Analysis Report</h1>
            <div class="subtitle">Comprehensive Analysis of Informatica MDM Data Model</div>
            <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <h2 class="section-title">Executive Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="number">{total_entities}</div>
                        <div class="label">Entities</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{total_fields}</div>
                        <div class="label">Total Fields</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{len(all_field_groups)}</div>
                        <div class="label">Field Groups</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{len(all_requirements)}</div>
                        <div class="label">Requirements</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{total_relationships}</div>
                        <div class="label">Relationships</div>
                    </div>
                </div>
            </div>
'''
    
    # Entity Details - Only show BusinessEntity, filter out ReferenceEntity
    html += '''
            <div class="section">
                <h2 class="section-title">Entity Analysis</h2>
    '''
    
    # Filter to only show BusinessEntity types
    business_entities = [a for a in entity_analyses if a['type'] == 'BusinessEntity']
    
    for analysis in business_entities:
        entity_type_class = 'business' if analysis['type'] == 'BusinessEntity' else 'reference'
        
        html += f'''
                <div class="entity-card">
                    <div class="entity-header">
                        <div>
                            <span class="entity-name">{analysis['name']}</span>
                            <span class="entity-type {entity_type_class}">{analysis['type']}</span>
                        </div>
                        <div style="font-size: 1.1em; color: #666;">
                            {analysis['total_fields']} fields
                        </div>
                    </div>
                    <div class="entity-description">{analysis['description']}</div>
        '''
        
        # Field Categories
        if analysis['identifiers']:
            html += f'''
                    <div class="field-category">
                        <div class="category-title">🔑 Identifiers ({len(analysis['identifiers'])})</div>
                        <div class="field-list">
            '''
            for field in analysis['identifiers']:
                html += f'''
                            <div class="field-item">
                                <div class="field-name">{field.get('name', 'Unknown')}</div>
                                <div class="field-details">
                                    Type: {field.get('dataType', 'N/A')} | 
                                    Required: {'Yes' if field.get('isRequired') else 'No'}
                                </div>
                            </div>
                '''
            html += '</div></div>'
        
        if analysis['general_attributes']:
            html += f'''
                    <div class="field-category">
                        <div class="category-title">📋 General Attributes ({len(analysis['general_attributes'])})</div>
                        <div class="field-list">
            '''
            for field in analysis['general_attributes']:
                is_lookup = field.get('isLookup', False) or 'lookup' in field.get('dataType', '').lower()
                lookup_class = 'lookup-field' if is_lookup else ''
                lookup_info = f' | Lookup: {field.get("lookupEntity", "N/A")}' if is_lookup else ''
                html += f'''
                            <div class="field-item {lookup_class}">
                                <div class="field-name">{field.get('name', 'Unknown')}</div>
                                <div class="field-details">
                                    Type: {field.get('dataType', 'N/A')} | 
                                    Required: {'Yes' if field.get('isRequired') else 'No'}
                                    {lookup_info}
                                </div>
                            </div>
                '''
            html += '</div></div>'
        
        # Field Groups
        if analysis['field_groups']:
            html += f'''
                    <div class="field-category">
                        <div class="category-title">📦 Field Groups ({len(analysis['field_groups'])})</div>
            '''
            for group_name, group_fields in sorted(analysis['field_groups'].items()):
                html += f'''
                        <div class="field-group-section">
                            <div class="field-group-title">{group_name} ({len(group_fields)} fields)</div>
                            <div class="field-list">
                '''
                for field in group_fields:
                    is_lookup = field.get('isLookup', False) or 'lookup' in field.get('dataType', '').lower()
                    lookup_class = 'lookup-field' if is_lookup else ''
                    lookup_info = f' | Lookup: {field.get("lookupEntity", "N/A")}' if is_lookup else ''
                    html += f'''
                                <div class="field-item {lookup_class}">
                                    <div class="field-name">{field.get('name', 'Unknown')}</div>
                                    <div class="field-details">
                                        Type: {field.get('dataType', 'N/A')} | 
                                        Required: {'Yes' if field.get('isRequired') else 'No'}
                                        {lookup_info}
                                    </div>
                                </div>
                    '''
                html += '</div></div>'
            html += '</div>'
        
        # Meta Fields
        if analysis['meta_fields']:
            html += f'''
                    <div class="field-category">
                        <div class="category-title">⚙️ Meta Fields ({len(analysis['meta_fields'])})</div>
                        <div class="field-list">
            '''
            for field in analysis['meta_fields']:
                html += f'''
                            <div class="field-item">
                                <div class="field-name">{field.get('name', 'Unknown')}</div>
                                <div class="field-details">
                                    Type: {field.get('dataType', 'N/A')} | 
                                    Required: {'Yes' if field.get('isRequired') else 'No'}
                                </div>
                            </div>
                '''
            html += '</div></div>'
        
        # Requirements Traceability
        if analysis['requirement_ids']:
            html += '''
                    <div class="requirement-section">
                        <div class="category-title">📝 Requirement Traceability</div>
            '''
            for req_id in sorted(analysis['requirement_ids']):
                fields_for_req = analysis['requirement_to_fields'].get(req_id, [])
                requirement_text = analysis['requirement_to_text'].get(req_id, 'No description available')
                badge_class = 'fr' if req_id.startswith('FR-') else 'dqr' if req_id.startswith('DQR-') else 'standard'
                
                # Build field list with reasoning
                field_list_html = '<ul>'
                for field in fields_for_req:
                    field_name = field.get('name', 'Unknown')
                    field_reasoning = field.get('fieldReasoning', {}).get(req_id, '')
                    if field_reasoning:
                        field_list_html += f'<li><strong>{field_name}:</strong><span>{field_reasoning}</span></li>'
                    else:
                        field_list_html += f'<li><strong>{field_name}</strong></li>'
                field_list_html += '</ul>'
                
                html += f'''
                        <div class="requirement-item">
                            <div class="requirement-id">
                                <span class="badge {badge_class}">{req_id}</span>
                                ({len(fields_for_req)} field(s))
                            </div>
                            <div style="margin: 8px 0; padding: 8px; background: white; border-radius: 4px; font-style: italic; color: #555;">
                                <strong>Requirement Text:</strong> {requirement_text}
                            </div>
                            <div class="requirement-fields">
                                <strong>Mapped Fields & Reasoning:</strong>
                                {field_list_html}
                            </div>
                        </div>
                '''
            html += '</div>'
        
        # Statistics
        html += f'''
                    <div style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
                        <strong>Field Statistics:</strong><br>
                        • Custom Fields: {len(analysis['custom_fields'])}<br>
                        • Lookup Fields: {len(analysis['lookup_fields'])}<br>
                        • Required Fields: {len(analysis['required_fields'])}<br>
                        • Optional Fields: {analysis['total_fields'] - len(analysis['required_fields'])}
                    </div>
                </div>
        '''
    
    html += '</div>'
    
    # Relationships
    if relationships:
        html += '''
            <div class="section">
                <h2 class="section-title">Entity Relationships</h2>
        '''
        for rel in relationships:
            html += f'''
                <div class="relationship-card">
                    <div class="relationship-entities">
                        <span>{rel.get('fromEntity', 'Unknown')}</span>
                        <span class="relationship-arrow">→</span>
                        <span>{rel.get('toEntity', 'Unknown')}</span>
                    </div>
                    <div style="color: white; margin-top: 10px; opacity: 0.95;">
                        <strong>Type:</strong> {rel.get('relationshipType', 'Unknown')}<br>
                        <strong>Description:</strong> {rel.get('description', 'No description')}
                    </div>
                </div>
            '''
        html += '</div>'
    
    # Field Groups Summary - Only for BusinessEntity
    html += '''
            <div class="section">
                <h2 class="section-title">Field Groups Summary</h2>
                <table class="summary-table">
                    <thead>
                        <tr>
                            <th>Field Group</th>
                            <th>Entity</th>
                            <th>Field Count</th>
                            <th>Fields</th>
                        </tr>
                    </thead>
                    <tbody>
    '''
    
    for analysis in business_entities:
        for group_name, group_fields in sorted(analysis['field_groups'].items()):
            field_names = ', '.join([f.get('name', 'Unknown') for f in group_fields])
            html += f'''
                        <tr>
                            <td><strong>{group_name}</strong></td>
                            <td>{analysis['name']}</td>
                            <td>{len(group_fields)}</td>
                            <td style="font-size: 0.9em;">{field_names}</td>
                        </tr>
            '''
    
    html += '''
                    </tbody>
                </table>
            </div>
    '''
    
    # Close HTML
    html += '''
        </div>
    </div>
</body>
</html>
'''
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Report generated: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "generated_data_model.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data_model_report.html"
    
    try:
        data_model = load_data_model(json_file)
        generate_html_report(data_model, output_file)
        print(f"\n✅ Successfully generated comprehensive data model report!")
        print(f"   Open {output_file} in your browser to view the report.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


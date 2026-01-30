"""
Output Generators
Convert JSON data model to Draw.io format and HTML report
"""

import json
from typing import Dict, List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def generate_drawio(data_model: Dict) -> str:
    """
    Generate Draw.io XML from data model matching architect template format exactly
    
    Template Reference: Aswin_shared.drawio
    - Entity header: x=-101, y=127, w=90, h=20
    - Fields: x=-27 (entity_x + 74), spacing=28px
    - Field groups: x=-29 (entity_x + 72), w=158
    - Expanded fields: x=175, w=146
    
    Args:
        data_model: Parsed data model dictionary with metadata, reasoning, and dataModel
    
    Returns:
        Draw.io XML string
    """
    
    # Extract entities from dataModel section
    entities = data_model.get('dataModel', {}).get('entities', [])
    
    # Filter to only show Business Entities
    business_entities = [e for e in entities if e.get('type') == 'BusinessEntity']
    
    # ============================================
    # LAYOUT CONSTANTS - Matching Aswin_shared.drawio
    # ============================================
    
    # Entity header positioning
    ENTITY_X = -101
    ENTITY_Y_START = 127
    ENTITY_WIDTH = 90
    ENTITY_HEIGHT = 20
    
    # Field positioning (standalone fields)
    FIELD_X = -27
    FIELD_WIDTH = 166
    FIELD_HEIGHT = 20
    FIELD_Y_START = 165
    FIELD_SPACING = 28
    
    # Field group positioning (yellow boxes)
    FIELD_GROUP_X = -29
    FIELD_GROUP_WIDTH = 158
    
    # Expanded fields (children of field groups)
    EXPANDED_X = 175
    EXPANDED_WIDTH = 146
    
    # Lookup icon
    LOOKUP_ICON_SIZE = 17
    LOOKUP_ICON_OFFSET = 5
    
    # Container box
    CONTAINER_X = -121
    CONTAINER_Y = 80
    
    # ============================================
    # COLOR SCHEME - Matching template exactly
    # ============================================
    COLORS = {
        'business_entity': {'fill': '#1ba1e2', 'stroke': '#006EAF', 'font': '#ffffff'},
        'general_attribute': {'fill': '#d5e8d4', 'stroke': '#82b366'},
        'identifier': {'fill': '#f8cecc', 'stroke': '#b85450'},
        'field_group': {'fill': '#e3c800', 'stroke': '#B09500', 'font': '#000000'}
    }
    
    # ============================================
    # HELPER FUNCTIONS
    # ============================================
    
    id_counter = [2]  # Start from 2 to match template
    
    def get_next_id():
        current_id = id_counter[0]
        id_counter[0] += 1
        return str(current_id)
    
    def get_field_style(field):
        """Determine field color based on type. Custom fields (including lookup) always red."""
        # Custom fields (including custom lookup fields like classification) → red
        if field.get('isCustom', False):
            return COLORS['identifier']
        
        field_group = field.get('fieldGroup')
        field_name = field.get('name', '').lower()
        
        # Identifiers (pink/red) - meta fields or fields with 'id' in name
        if field_group == '_meta' or 'id' in field_name or 'pidm' in field_name or 'cwid' in field_name:
            return COLORS['identifier']
        
        # General attributes (green)
        return COLORS['general_attribute']
    
    def create_mxcell(parent, cell_id, value, style, x, y, width, height, is_vertex=True):
        """Create an mxCell element with geometry"""
        cell = SubElement(parent, 'mxCell', {
            'id': cell_id,
            'parent': '1',
            'style': style,
            'value': value,
            'vertex': '1' if is_vertex else '0'
        })
        SubElement(cell, 'mxGeometry', {
            'x': str(x),
            'y': str(y),
            'width': str(width),
            'height': str(height),
            'as': 'geometry'
        })
        return cell
    
    def create_edge(parent, edge_id, source_id, target_id, style):
        """Create an edge connection"""
        edge = SubElement(parent, 'mxCell', {
            'id': edge_id,
            'edge': '1',
            'parent': '1',
            'source': source_id,
            'target': target_id,
            'style': style
        })
        SubElement(edge, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        return edge
    
    def create_lookup_icon(parent, icon_id, x, y):
        """Create lookup dropdown icon"""
        icon = SubElement(parent, 'mxCell', {
            'id': icon_id,
            'parent': '1',
            'style': 'shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=https://cdn1.iconfinder.com/data/icons/material-core/10/arrow-drop-down-128.png;fillColor=#008A8A;',
            'value': '',
            'vertex': '1'
        })
        SubElement(icon, 'mxGeometry', {
            'x': str(x),
            'y': str(y),
            'width': str(LOOKUP_ICON_SIZE),
            'height': str(LOOKUP_ICON_SIZE),
            'as': 'geometry'
        })
        return icon
    
    # ============================================
    # CALCULATE TOTAL CONTENT SIZE
    # ============================================
    
    total_standalone_fields = 0
    total_field_groups = 0
    max_expanded_per_group = 0
    
    for entity in business_entities:
        fields = entity.get('fields', [])
        field_groups_in_entity = {}
        
        for field in fields:
            fg = field.get('fieldGroup')
            if fg and fg != '_meta':
                if fg not in field_groups_in_entity:
                    field_groups_in_entity[fg] = 0
                field_groups_in_entity[fg] += 1
            else:
                total_standalone_fields += 1
        
        total_field_groups += len(field_groups_in_entity)
        
        # For each field group, we need vertical space for all its expanded fields
        for fg_name, fg_count in field_groups_in_entity.items():
            max_expanded_per_group = max(max_expanded_per_group, fg_count)
    
    # Calculate total vertical space needed
    # Each field group takes up space = max(1, number of expanded fields) * FIELD_SPACING
    total_rows = total_standalone_fields
    for entity in business_entities:
        fields = entity.get('fields', [])
        field_groups_in_entity = {}
        for field in fields:
            fg = field.get('fieldGroup')
            if fg and fg != '_meta':
                if fg not in field_groups_in_entity:
                    field_groups_in_entity[fg] = 0
                field_groups_in_entity[fg] += 1
        for fg_name, fg_count in field_groups_in_entity.items():
            total_rows += max(1, fg_count)
    
    # Calculate container height with generous padding
    # Content starts at FIELD_Y_START and each row takes FIELD_SPACING
    content_bottom_y = FIELD_Y_START + (total_rows + 2) * FIELD_SPACING
    container_height = content_bottom_y - CONTAINER_Y + 50  # +50 for padding at bottom
    container_height = max(806, container_height)  # Minimum 806
    
    # Calculate container width
    container_width = max(729, EXPANDED_X + EXPANDED_WIDTH + 50 - CONTAINER_X)
    
    # ============================================
    # BUILD XML STRUCTURE
    # ============================================
    
    # Create root mxfile element
    mxfile = Element('mxfile', {
        'host': 'app.diagrams.net',
        'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'version': '29.3.0'
    })
    
    diagram = SubElement(mxfile, 'diagram', {
        'name': 'Data Model',
        'id': 'data-model-diagram'
    })
    
    mxGraphModel = SubElement(diagram, 'mxGraphModel', {
        'dx': '1826',
        'dy': '824',
        'grid': '0',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '0',
        'pageScale': '1',
        'pageWidth': '850',
        'pageHeight': str(max(1100, int(container_height) + 200)),
        'math': '0',
        'shadow': '0'
    })
    
    root = SubElement(mxGraphModel, 'root')
    SubElement(root, 'mxCell', {'id': '0'})
    SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
    
    # ============================================
    # CREATE CONTAINER BOX
    # ============================================
    
    container_id = get_next_id()
    create_mxcell(
        root, container_id, 'Data Model',
        'rounded=0;whiteSpace=wrap;html=1;horizontal=1;verticalAlign=top;align=left;fontStyle=5',
        CONTAINER_X, CONTAINER_Y, container_width, container_height
    )
    
    # ============================================
    # CREATE COLOR-CODED LABELS (LEGEND) - top right of diagram
    # ============================================
    
    LABEL_PADDING = 15
    LABEL_GAP = 12
    LABEL_HEIGHT = 20
    LABEL_Y = CONTAINER_Y + LABEL_PADDING
    
    # Place legend labels from right edge inward to cover top right
    label_specs = [
        ('Business Entity', 97, 'business_entity'),
        ('General Attributes', 109, 'general_attribute'),
        ('Identifiers / Custom', 140, 'identifier'),
        ('Field Groups', 112, 'field_group'),
    ]
    # Right edge of container
    legend_right = CONTAINER_X + container_width - LABEL_PADDING
    # Place labels right-to-left so they cover top right
    label_x = legend_right
    for text, w, key in reversed(label_specs):
        label_x -= (w + LABEL_GAP)
        if key == 'business_entity':
            style = f'rounded=0;whiteSpace=wrap;html=1;align=left;fillColor={COLORS["business_entity"]["fill"]};fontColor={COLORS["business_entity"]["font"]};strokeColor={COLORS["business_entity"]["stroke"]};'
            value = f'<font color="{COLORS["business_entity"]["font"]}">{text}</font>'
        elif key == 'general_attribute':
            style = f'rounded=0;whiteSpace=wrap;html=1;align=left;fillColor={COLORS["general_attribute"]["fill"]};strokeColor={COLORS["general_attribute"]["stroke"]};'
            value = text
        elif key == 'identifier':
            style = f'rounded=0;whiteSpace=wrap;html=1;align=left;fillColor={COLORS["identifier"]["fill"]};strokeColor={COLORS["identifier"]["stroke"]};'
            value = text
        else:
            style = f'rounded=0;whiteSpace=wrap;html=1;fillColor={COLORS["field_group"]["fill"]};fontColor={COLORS["field_group"]["font"]};strokeColor={COLORS["field_group"]["stroke"]};'
            value = text
        create_mxcell(root, get_next_id(), value, style, label_x, LABEL_Y, w, LABEL_HEIGHT)
    
    # ============================================
    # DRAW ENTITIES AND FIELDS
    # ============================================
    
    current_field_y = FIELD_Y_START
    
    for entity_idx, entity in enumerate(business_entities):
        entity_name = entity.get('name', 'Entity')
        fields = entity.get('fields', [])
        
        # Create entity header (blue box)
        entity_id = get_next_id()
        create_mxcell(
            root, entity_id, f'<font color="{COLORS["business_entity"]["font"]}">{entity_name}</font>',
            f'rounded=0;whiteSpace=wrap;html=1;align=left;fillColor={COLORS["business_entity"]["fill"]};fontColor={COLORS["business_entity"]["font"]};strokeColor={COLORS["business_entity"]["stroke"]};',
            ENTITY_X, ENTITY_Y_START, ENTITY_WIDTH, ENTITY_HEIGHT
        )
        
        # Separate standalone fields from field groups
        standalone_fields = []
        field_groups_dict = {}
        
        for field in fields:
            fg = field.get('fieldGroup')
            if fg and fg != '_meta':
                if fg not in field_groups_dict:
                    field_groups_dict[fg] = []
                field_groups_dict[fg].append(field)
            else:
                standalone_fields.append(field)
        
        # ============================================
        # DRAW STANDALONE FIELDS
        # ============================================
        
        for field in standalone_fields:
            field_name = field.get('name', 'field')
            field_style = get_field_style(field)
            is_lookup = field.get('isLookup', False)
            
            # Create field box (add spacingRight for lookup fields to make room for icon)
            field_id = get_next_id()
            field_style_str = f'rounded=0;whiteSpace=wrap;html=1;align=left;fillColor={field_style["fill"]};strokeColor={field_style["stroke"]};'
            if is_lookup:
                field_style_str += 'spacingRight=20;'
            create_mxcell(
                root, field_id, field_name,
                field_style_str,
                FIELD_X, current_field_y, FIELD_WIDTH, FIELD_HEIGHT
            )
            
            # Connect to entity (exit from bottom center, enter from left middle)
            edge_id = get_next_id()
            create_edge(
                root, edge_id, entity_id, field_id,
                'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;startArrow=none;startFill=0;endArrow=none;endFill=0;'
            )
            
            # Add lookup icon inside the box (right side)
            if is_lookup:
                icon_id = get_next_id()
                icon_x = FIELD_X + FIELD_WIDTH - LOOKUP_ICON_SIZE - 3
                icon_y = current_field_y + (FIELD_HEIGHT - LOOKUP_ICON_SIZE) // 2
                create_lookup_icon(root, icon_id, icon_x, icon_y)
            
            current_field_y += FIELD_SPACING
        
        # ============================================
        # DRAW FIELD GROUPS AND THEIR CHILDREN
        # Each field group's expanded fields start at the SAME Y as the field group
        # ============================================
        
        for group_name, group_fields in field_groups_dict.items():
            # Calculate how many expanded fields this group has
            num_expanded = len(group_fields)
            
            # Position the field group box
            group_y = current_field_y
            
            # Create field group box (yellow)
            group_id = get_next_id()
            create_mxcell(
                root, group_id, group_name,
                f'rounded=0;whiteSpace=wrap;html=1;fillColor={COLORS["field_group"]["fill"]};fontColor={COLORS["field_group"]["font"]};strokeColor={COLORS["field_group"]["stroke"]};',
                FIELD_GROUP_X, group_y, FIELD_GROUP_WIDTH, FIELD_HEIGHT
            )
            
            # Connect to entity with crow's foot (ERmany) - exit from bottom center, enter from left
            group_edge_id = get_next_id()
            create_edge(
                root, group_edge_id, entity_id, group_id,
                'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;startArrow=none;startFill=0;endArrow=ERmany;endFill=0;'
            )
            
            # Draw expanded fields (children) to the right
            # Start at the SAME Y position as the field group box
            expanded_y = group_y
            
            for group_field in group_fields:
                field_name = group_field.get('name', 'field')
                is_lookup = group_field.get('isLookup', False)
                group_field_style = get_field_style(group_field)
                # Create expanded field box (add spacingRight for lookup fields to make room for icon)
                expanded_id = get_next_id()
                expanded_style = f'rounded=0;whiteSpace=wrap;html=1;align=left;fillColor={group_field_style["fill"]};strokeColor={group_field_style["stroke"]};'
                if is_lookup:
                    expanded_style += 'spacingRight=20;'
                create_mxcell(
                    root, expanded_id, field_name,
                    expanded_style,
                    EXPANDED_X, expanded_y, EXPANDED_WIDTH, FIELD_HEIGHT
                )
                
                # Connect to field group (from right side of group to left side of expanded)
                expanded_edge_id = get_next_id()
                create_edge(
                    root, expanded_edge_id, group_id, expanded_id,
                    'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;startArrow=none;startFill=0;endArrow=none;endFill=0;exitX=1;exitY=0.5;exitDx=0;exitDy=0;'
                )
                
                # Add lookup icon inside the box (right side)
                if is_lookup:
                    icon_id = get_next_id()
                    icon_x = EXPANDED_X + EXPANDED_WIDTH - LOOKUP_ICON_SIZE - 3
                    icon_y = expanded_y + (FIELD_HEIGHT - LOOKUP_ICON_SIZE) // 2
                    create_lookup_icon(root, icon_id, icon_x, icon_y)
                
                expanded_y += FIELD_SPACING
            
            # Move current_field_y down by the maximum of 1 or number of expanded fields
            # This ensures field groups don't overlap with their expanded children
            current_field_y += max(1, num_expanded) * FIELD_SPACING
    
    # ============================================
    # CONVERT TO XML STRING
    # ============================================
    
    # Use minidom for pretty printing
    xml_str = minidom.parseString(tostring(mxfile)).toprettyxml(indent='    ')
    
    # Remove the XML declaration line that minidom adds
    lines = xml_str.split('\n')
    if lines[0].startswith('<?xml'):
        xml_str = '\n'.join(lines[1:])
    
    return xml_str.strip()


def save_drawio_file(data_model: Dict, output_path: str = "data_model.drawio"):
    """
    Save data model as Draw.io file
    
    Args:
        data_model: Parsed data model dictionary
        output_path: Path to save the .drawio file
    """
    
    xml_content = generate_drawio(data_model)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ Draw.io file saved to: {output_path}")
    print(f"📊 Open this file in Draw.io (https://app.diagrams.net)")


def generate_html_report(data_model: Dict, output_path: str = "data_model_report.html") -> str:
    """
    Generate interactive HTML report with entity details and traceability
    
    Args:
        data_model: Parsed data model dictionary
        output_path: Path to save HTML file
    
    Returns:
        HTML string
    """
    
    metadata = data_model.get('metadata', {})
    reasoning = data_model.get('reasoning', {})
    entities = data_model.get('dataModel', {}).get('entities', [])
    relationships = data_model.get('dataModel', {}).get('relationships', [])
    
    # Get stats
    stats = get_summary_stats(data_model)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Model Report - {metadata.get('generatedDate', 'N/A')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .entity-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 30px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .entity-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .entity-header {{
            background: #667eea;
            color: white;
            padding: 20px 30px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .entity-header h3 {{
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .entity-type-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.7em;
            font-weight: normal;
        }}
        
        .toggle-icon {{
            font-size: 1.5em;
            transition: transform 0.3s;
        }}
        
        .entity-card.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        
        .entity-body {{
            padding: 30px;
            display: block;
        }}
        
        .entity-card.collapsed .entity-body {{
            display: none;
        }}
        
        .entity-description {{
            color: #666;
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .field-name {{
            font-weight: 600;
            color: #333;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .badge-ootb {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-custom {{
            background: #f8cecc;
            color: #b85450;
        }}
        
        tr.custom-field-row {{
            background: #f8cecc !important;
        }}
        
        tr.custom-field-row:hover {{
            background: #f5b8b5 !important;
        }}
        
        .badge-required {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .badge-lookup {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge-group {{
            background: #e7f3ff;
            color: #004085;
        }}
        
        .traceability {{
            margin-top: 15px;
            padding: 10px;
            background: #fffbf0;
            border-left: 3px solid #ffc107;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .traceability-title {{
            font-weight: 600;
            color: #856404;
            margin-bottom: 5px;
        }}
        
        .requirement {{
            color: #666;
            margin-left: 10px;
            display: block;
        }}
        
        .reasoning-section {{
            background: #f0f4ff;
            padding: 25px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .reasoning-title {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .reasoning-text {{
            color: #555;
            line-height: 1.8;
        }}
        
        .brd-reference {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-top: 10px;
            border-left: 3px solid #667eea;
        }}
        
        .brd-reference-title {{
            font-weight: 600;
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .brd-reference-text {{
            color: #666;
            font-style: italic;
        }}
        
        .metadata-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .metadata-item {{
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .metadata-item:last-child {{
            border-bottom: none;
        }}
        
        .metadata-label {{
            font-weight: 600;
            color: #666;
            width: 150px;
        }}
        
        .metadata-value {{
            color: #333;
            flex: 1;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Model Report</h1>
            <p>Generated on {metadata.get('generatedDate', 'N/A')} • Platform: {metadata.get('platform', 'informatica').title()}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <span class="number">{stats['total_entities']}</span>
                <span class="label">Total Entities</span>
            </div>
            <div class="stat-card">
                <span class="number">{stats['business_entities']}</span>
                <span class="label">Business Entities</span>
            </div>
            <div class="stat-card">
                <span class="number">{stats['total_fields']}</span>
                <span class="label">Total Fields</span>
            </div>
            <div class="stat-card">
                <span class="number">{stats['ootb_fields']}</span>
                <span class="label">OOTB Fields</span>
            </div>
            <div class="stat-card">
                <span class="number">{stats['custom_fields']}</span>
                <span class="label">Custom Fields</span>
            </div>
            <div class="stat-card">
                <span class="number">{stats['total_relationships']}</span>
                <span class="label">Relationships</span>
            </div>
        </div>
        
        <div class="content">
            <!-- Metadata Section -->
            <div class="section">
                <h2 class="section-title">📋 Metadata</h2>
                <div class="metadata-section">
                    <div class="metadata-item">
                        <span class="metadata-label">Platform:</span>
                        <span class="metadata-value">{metadata.get('platform', 'informatica').title()}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Generated Date:</span>
                        <span class="metadata-value">{metadata.get('generatedDate', 'N/A')}</span>
                    </div>
                </div>
            </div>
            
            <!-- Reasoning Section -->
            <div class="section">
                <h2 class="section-title">🧠 AI Reasoning</h2>
                <div class="reasoning-section">
                    <div class="reasoning-title">Summary</div>
                    <div class="reasoning-text">{reasoning.get('summary', 'No reasoning provided')}</div>
                </div>
            </div>
            
            <!-- Search -->
            <div class="section">
                <h2 class="section-title">🔍 Entities & Fields</h2>
                <input type="text" class="search-box" id="searchBox" placeholder="Search entities and fields..." onkeyup="filterEntities()">
                <div id="entitiesContainer">
"""
    
    # Generate entity cards
    business_entities = [e for e in entities if e.get('type') == 'BusinessEntity']
    
    for entity in business_entities:
        entity_name = entity.get('name', 'Entity')
        entity_type = entity.get('type', 'BusinessEntity')
        entity_description = entity.get('description', 'No description provided')
        fields = entity.get('fields', [])
        
        # Find entity reasoning
        entity_reasoning = next(
            (er for er in reasoning.get('entityDecisions', []) if er.get('entityName') == entity_name),
            {}
        )
        
        html += f"""
                    <div class="entity-card" data-entity-name="{entity_name.lower()}">
                        <div class="entity-header" onclick="toggleEntity(this)">
                            <h3>
                                {entity_name}
                                <span class="entity-type-badge">{entity_type}</span>
                            </h3>
                            <span class="toggle-icon">▼</span>
                        </div>
                        <div class="entity-body">
                            <div class="entity-description">
                                {entity_description}
                            </div>
"""
        
        # Entity reasoning
        if entity_reasoning:
            html += f"""
                            <div class="reasoning-section">
                                <div class="reasoning-title">Why this entity?</div>
                                <div class="reasoning-text">{entity_reasoning.get('reason', 'N/A')}</div>
                                <div class="brd-reference">
                                    <div class="brd-reference-title">BRD Reference:</div>
                                    <div class="brd-reference-text">"{entity_reasoning.get('brdReference', 'N/A')}"</div>
                                </div>
                            </div>
"""
        
        # Fields table
        html += """
                            <table>
                                <thead>
                                    <tr>
                                        <th>Field Name</th>
                                        <th>Data Type</th>
                                        <th>Field Group</th>
                                        <th>Properties</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
"""
        
        for field in fields:
            field_name = field.get('name', 'field')
            data_type = field.get('dataType', 'N/A')
            field_group = field.get('fieldGroup', '-')
            is_custom = field.get('isCustom', False)
            is_required = field.get('isRequired', False)
            is_lookup = field.get('isLookup', False)
            lookup_entity = field.get('lookupEntity', '')
            description = field.get('description', '')
            requirement_ids = field.get('requirementIds', [])
            source_requirements = field.get('sourceRequirements', [])
            
            # Find field reasoning
            field_reasoning = next(
                (fr for fr in reasoning.get('fieldDecisions', []) 
                 if fr.get('entityName') == entity_name and fr.get('fieldName') == field_name),
                {}
            )
            
            # Build properties badges
            properties = []
            if is_custom:
                properties.append('<span class="badge badge-custom">Custom</span>')
            else:
                properties.append('<span class="badge badge-ootb">OOTB</span>')
            
            if is_required:
                properties.append('<span class="badge badge-required">Required</span>')
            
            if is_lookup:
                properties.append(f'<span class="badge badge-lookup">Lookup → {lookup_entity}</span>')
            
            if field_group and field_group != '-':
                properties.append(f'<span class="badge badge-group">{field_group}</span>')
            
            properties_html = ' '.join(properties)
            row_class = ' class="custom-field-row"' if is_custom else ''
            
            html += f"""
                                    <tr{row_class}>
                                        <td class="field-name">{field_name}</td>
                                        <td>{data_type}</td>
                                        <td>{field_group}</td>
                                        <td>{properties_html}</td>
                                        <td>
                                            {description}
"""
            
            # Traceability
            if requirement_ids or source_requirements:
                html += """
                                            <div class="traceability">
                                                <div class="traceability-title">📎 Requirement Traceability:</div>
"""
                for req_id, req_text in zip(requirement_ids, source_requirements):
                    html += f"""
                                                <span class="requirement"><strong>{req_id}:</strong> {req_text}</span>
"""
                html += """
                                            </div>
"""
            
            # Field reasoning
            if field_reasoning:
                html += f"""
                                            <div class="reasoning-section" style="margin-top: 15px;">
                                                <div class="reasoning-title">Why this field?</div>
                                                <div class="reasoning-text">{field_reasoning.get('reason', 'N/A')}</div>
                                                <div class="brd-reference">
                                                    <div class="brd-reference-title">BRD Reference:</div>
                                                    <div class="brd-reference-text">"{field_reasoning.get('brdReference', 'N/A')}"</div>
                                                </div>
                                                <div style="margin-top: 10px;">
                                                    <strong>Type:</strong> {field_reasoning.get('inferredOrExplicit', 'N/A').title()} | 
                                                    <strong>OOTB/Custom:</strong> {field_reasoning.get('ootbVsCustom', 'N/A')}
                                                </div>
                                            </div>
"""
            
            html += """
                                        </td>
                                    </tr>
"""
        
        html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
"""
    
    # Reference entities
    reference_entities = [e for e in entities if e.get('type') == 'ReferenceEntity']
    
    if reference_entities:
        html += """
                    <h2 class="section-title" style="margin-top: 50px;">📚 Reference Entities (Lookups)</h2>
"""
        
        for entity in reference_entities:
            entity_name = entity.get('name', 'Entity')
            entity_description = entity.get('description', 'No description provided')
            fields = entity.get('fields', [])
            
            html += f"""
                    <div class="entity-card" data-entity-name="{entity_name.lower()}">
                        <div class="entity-header" onclick="toggleEntity(this)" style="background: #28a745;">
                            <h3>
                                {entity_name}
                                <span class="entity-type-badge">Reference Entity</span>
                            </h3>
                            <span class="toggle-icon">▼</span>
                        </div>
                        <div class="entity-body">
                            <div class="entity-description">
                                {entity_description}
                            </div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Field Name</th>
                                        <th>Data Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
"""
            
            for field in fields:
                field_name = field.get('name', 'field')
                data_type = field.get('dataType', 'N/A')
                description = field.get('description', '')
                
                html += f"""
                                    <tr>
                                        <td class="field-name">{field_name}</td>
                                        <td>{data_type}</td>
                                        <td>{description}</td>
                                    </tr>
"""
            
            html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
"""
    
    html += """
                </div>
                <div id="noResults" class="no-results" style="display: none;">
                    No entities or fields match your search.
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function toggleEntity(header) {
            const card = header.parentElement;
            card.classList.toggle('collapsed');
        }
        
        function filterEntities() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const entities = document.querySelectorAll('.entity-card');
            let visibleCount = 0;
            
            entities.forEach(entity => {
                const entityName = entity.getAttribute('data-entity-name');
                const text = entity.textContent.toLowerCase();
                
                if (text.includes(searchTerm)) {
                    entity.style.display = 'block';
                    visibleCount++;
                } else {
                    entity.style.display = 'none';
                }
            });
            
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
        }
    </script>
</body>
</html>
"""
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML report saved to: {output_path}")
    print(f"📄 Open this file in your browser to view the report")
    
    return html


def get_summary_stats(data_model: Dict) -> Dict:
    """
    Get summary statistics about the data model
    
    Args:
        data_model: Parsed data model dictionary
    
    Returns:
        Dictionary with stats
    """
    
    entities = data_model.get('dataModel', {}).get('entities', [])
    
    business_entities = [e for e in entities if e.get('type') == 'BusinessEntity']
    reference_entities = [e for e in entities if e.get('type') == 'ReferenceEntity']
    
    total_fields = sum(len(e.get('fields', [])) for e in entities)
    custom_fields = sum(
        sum(1 for f in e.get('fields', []) if f.get('isCustom', False))
        for e in entities
    )
    
    return {
        'total_entities': len(entities),
        'business_entities': len(business_entities),
        'reference_entities': len(reference_entities),
        'total_fields': total_fields,
        'custom_fields': custom_fields,
        'ootb_fields': total_fields - custom_fields,
        'total_relationships': len(data_model.get('dataModel', {}).get('relationships', []))
    }
"""
Visual Configuration and Styling Specifications
Centralized configuration for Draw.io diagrams and HTML reports
"""

# ============================================================================
# DRAW.IO VISUAL SPECIFICATIONS
# ============================================================================

# Color Scheme
DRAWIO_COLORS = {
    # Entity Colors
    'business_entity': '#66B2FF',      # Blue
    'reference_entity': '#D5E8D4',     # Green
    
    # Field Colors
    'identifier': '#FFE6E6',           # Pink (for _meta fields and fields with 'id' in name)
    'field_group': '#FFF4B3',          # Yellow (for field groups)
    'general_attribute': '#D5E8D4',    # Green (for regular fields)
    
    # Border Colors
    'border': '#000000',
    
    # Legend Colors (same as entity/field colors)
    'legend_business_entity': '#66B2FF',
    'legend_general_attributes': '#D5E8D4',
    'legend_identifiers': '#FFE6E6',
    'legend_field_groups': '#FFF4B3',
}

# Draw.io Layout Constants
DRAWIO_LAYOUT = {
    'legend': {
        'x': 20,
        'y': 20,
        'title_width': 200,
        'title_height': 30,
        'box_width': 160,
        'box_height': 40,
        'x_offset': 400,
        'spacing': 180,
    },
    'entity': {
        'start_y': 100,
        'start_x': 50,
        'spacing_y': 100,
        'width': 200,
        'header_height': 50,
    },
    'field': {
        'height': 35,
        'width': 200,
        'expanded_width': 220,
    },
    'field_group': {
        'offset_x': 400,
    },
    'diagram': {
        'dx': 2000,
        'dy': 1200,
        'grid': 1,
        'gridSize': 10,
        'pageWidth': 2000,
        'pageHeight': 2000,
    },
}

# Draw.io Style Templates
DRAWIO_STYLES = {
    'title': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1',
    'legend_box': 'rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=#000000;',
    'entity_box': 'rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=#000000;fontStyle=1;fontSize=14;',
    'field_box': 'rounded=0;whiteSpace=wrap;html=1;fillColor={color};strokeColor=#000000;align=left;spacingLeft=10;',
    'field_group_header': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF4B3;strokeColor=#000000;fontStyle=1;',
    'field_group_field': 'rounded=0;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#000000;align=left;spacingLeft=10;',
    'relationship_arrow': 'endArrow=classic;html=1;rounded=0;exitX=1;exitY=0.5;exitDx=0;exitDy=0;',
}


# ============================================================================
# HTML REPORT VISUAL SPECIFICATIONS
# ============================================================================

# Color Scheme
HTML_COLORS = {
    # Primary Colors
    'primary': '#667eea',
    'primary_dark': '#764ba2',
    'primary_gradient_start': '#667eea',
    'primary_gradient_end': '#764ba2',
    
    # Text Colors
    'text_primary': '#333',
    'text_secondary': '#666',
    'text_tertiary': '#555',
    'text_muted': '#999',
    
    # Background Colors
    'bg_primary': '#f5f5f5',
    'bg_secondary': '#f8f9fa',
    'bg_white': '#ffffff',
    'bg_light': '#f0f4ff',
    'bg_warning': '#fffbf0',
    
    # Border Colors
    'border_light': '#e0e0e0',
    'border_lighter': '#f0f0f0',
    'border_primary': '#667eea',
    'border_warning': '#ffc107',
    
    # Badge Colors
    'badge_ootb_bg': '#d4edda',
    'badge_ootb_text': '#155724',
    'badge_custom_bg': '#fff3cd',
    'badge_custom_text': '#856404',
    'badge_required_bg': '#f8d7da',
    'badge_required_text': '#721c24',
    'badge_lookup_bg': '#d1ecf1',
    'badge_lookup_text': '#0c5460',
    'badge_group_bg': '#e7f3ff',
    'badge_group_text': '#004085',
    
    # Reference Entity Header
    'ref_entity_header': '#28a745',
}

# Typography
HTML_TYPOGRAPHY = {
    'font_family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif",
    'font_sizes': {
        'h1': '2.5em',
        'h2': '1.8em',
        'h3': '1.5em',
        'body': '1em',
        'small': '0.9em',
        'tiny': '0.85em',
    },
    'line_height': '1.6',
    'line_height_reasoning': '1.8',
}

# Spacing
HTML_SPACING = {
    'container_padding': '20px',
    'content_padding': '40px',
    'section_margin': '50px',
    'card_margin': '30px',
    'field_padding': '12px',
    'header_padding': '40px',
    'entity_header_padding': '20px 30px',
    'entity_body_padding': '30px',
}

# Border Radius
HTML_BORDER_RADIUS = {
    'container': '12px',
    'card': '12px',
    'badge': '12px',
    'button': '8px',
    'input': '8px',
    'small': '4px',
    'badge_small': '20px',
}

# Shadows
HTML_SHADOWS = {
    'container': '0 2px 8px rgba(0,0,0,0.1)',
    'card': '0 2px 4px rgba(0,0,0,0.05)',
    'card_hover': '0 4px 12px rgba(0,0,0,0.15)',
}

# Layout
HTML_LAYOUT = {
    'container_max_width': '1400px',
    'stats_grid': 'repeat(auto-fit, minmax(200px, 1fr))',
    'stats_gap': '20px',
}

# Transitions
HTML_TRANSITIONS = {
    'card_hover': 'transform 0.2s, box-shadow 0.2s',
    'toggle_icon': 'transform 0.3s',
    'border': 'border-color 0.3s',
}

# ============================================================================
# HTML CSS TEMPLATES
# ============================================================================

def get_html_css():
    """Generate complete CSS for HTML report"""
    return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {HTML_TYPOGRAPHY['font_family']};
            line-height: {HTML_TYPOGRAPHY['line_height']};
            color: {HTML_COLORS['text_primary']};
            background: {HTML_COLORS['bg_primary']};
            padding: {HTML_SPACING['container_padding']};
        }}
        
        .container {{
            max-width: {HTML_LAYOUT['container_max_width']};
            margin: 0 auto;
            background: {HTML_COLORS['bg_white']};
            border-radius: {HTML_BORDER_RADIUS['container']};
            box-shadow: {HTML_SHADOWS['container']};
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, {HTML_COLORS['primary_gradient_start']} 0%, {HTML_COLORS['primary_gradient_end']} 100%);
            color: white;
            padding: {HTML_SPACING['header_padding']};
        }}
        
        .header h1 {{
            font-size: {HTML_TYPOGRAPHY['font_sizes']['h1']};
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: {HTML_LAYOUT['stats_grid']};
            gap: {HTML_LAYOUT['stats_gap']};
            padding: {HTML_SPACING['content_padding']};
            background: {HTML_COLORS['bg_secondary']};
            border-bottom: 1px solid {HTML_COLORS['border_light']};
        }}
        
        .stat-card {{
            background: {HTML_COLORS['bg_white']};
            padding: {HTML_SPACING['content_padding']};
            border-radius: {HTML_BORDER_RADIUS['card']};
            box-shadow: {HTML_SHADOWS['card']};
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: {HTML_COLORS['primary']};
            display: block;
        }}
        
        .stat-card .label {{
            color: {HTML_COLORS['text_secondary']};
            font-size: {HTML_TYPOGRAPHY['font_sizes']['small']};
            margin-top: 5px;
        }}
        
        .content {{
            padding: {HTML_SPACING['content_padding']};
        }}
        
        .section {{
            margin-bottom: {HTML_SPACING['section_margin']};
        }}
        
        .section-title {{
            font-size: {HTML_TYPOGRAPHY['font_sizes']['h2']};
            margin-bottom: 20px;
            color: {HTML_COLORS['text_primary']};
            border-bottom: 3px solid {HTML_COLORS['primary']};
            padding-bottom: 10px;
        }}
        
        .entity-card {{
            background: {HTML_COLORS['bg_white']};
            border: 2px solid {HTML_COLORS['border_light']};
            border-radius: {HTML_BORDER_RADIUS['card']};
            margin-bottom: {HTML_SPACING['card_margin']};
            overflow: hidden;
            transition: {HTML_TRANSITIONS['card_hover']};
        }}
        
        .entity-card:hover {{
            transform: translateY(-2px);
            box-shadow: {HTML_SHADOWS['card_hover']};
        }}
        
        .entity-header {{
            background: {HTML_COLORS['primary']};
            color: white;
            padding: {HTML_SPACING['entity_header_padding']};
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .entity-header h3 {{
            font-size: {HTML_TYPOGRAPHY['font_sizes']['h3']};
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .entity-type-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: {HTML_BORDER_RADIUS['badge_small']};
            font-size: 0.7em;
            font-weight: normal;
        }}
        
        .toggle-icon {{
            font-size: {HTML_TYPOGRAPHY['font_sizes']['h3']};
            transition: {HTML_TRANSITIONS['toggle_icon']};
        }}
        
        .entity-card.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        
        .entity-body {{
            padding: {HTML_SPACING['entity_body_padding']};
            display: block;
        }}
        
        .entity-card.collapsed .entity-body {{
            display: none;
        }}
        
        .entity-description {{
            color: {HTML_COLORS['text_secondary']};
            margin-bottom: 25px;
            padding: 15px;
            background: {HTML_COLORS['bg_secondary']};
            border-left: 4px solid {HTML_COLORS['primary']};
            border-radius: {HTML_BORDER_RADIUS['small']};
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: {HTML_COLORS['bg_secondary']};
            padding: {HTML_SPACING['field_padding']};
            text-align: left;
            font-weight: 600;
            color: {HTML_COLORS['text_primary']};
            border-bottom: 2px solid {HTML_COLORS['border_light']};
        }}
        
        td {{
            padding: {HTML_SPACING['field_padding']};
            border-bottom: 1px solid {HTML_COLORS['border_lighter']};
        }}
        
        tr:hover {{
            background: {HTML_COLORS['bg_secondary']};
        }}
        
        .field-name {{
            font-weight: 600;
            color: {HTML_COLORS['text_primary']};
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: {HTML_BORDER_RADIUS['badge']};
            font-size: {HTML_TYPOGRAPHY['font_sizes']['tiny']};
            font-weight: 500;
        }}
        
        .badge-ootb {{
            background: {HTML_COLORS['badge_ootb_bg']};
            color: {HTML_COLORS['badge_ootb_text']};
        }}
        
        .badge-custom {{
            background: {HTML_COLORS['badge_custom_bg']};
            color: {HTML_COLORS['badge_custom_text']};
        }}
        
        .badge-required {{
            background: {HTML_COLORS['badge_required_bg']};
            color: {HTML_COLORS['badge_required_text']};
        }}
        
        .badge-lookup {{
            background: {HTML_COLORS['badge_lookup_bg']};
            color: {HTML_COLORS['badge_lookup_text']};
        }}
        
        .badge-group {{
            background: {HTML_COLORS['badge_group_bg']};
            color: {HTML_COLORS['badge_group_text']};
        }}
        
        .traceability {{
            margin-top: 15px;
            padding: 10px;
            background: {HTML_COLORS['bg_warning']};
            border-left: 3px solid {HTML_COLORS['border_warning']};
            border-radius: {HTML_BORDER_RADIUS['small']};
            font-size: {HTML_TYPOGRAPHY['font_sizes']['small']};
        }}
        
        .traceability-title {{
            font-weight: 600;
            color: {HTML_COLORS['badge_custom_text']};
            margin-bottom: 5px;
        }}
        
        .requirement {{
            color: {HTML_COLORS['text_secondary']};
            margin-left: 10px;
            display: block;
        }}
        
        .reasoning-section {{
            background: {HTML_COLORS['bg_light']};
            padding: 25px;
            border-radius: {HTML_BORDER_RADIUS['button']};
            margin-top: 20px;
        }}
        
        .reasoning-title {{
            font-weight: 600;
            color: {HTML_COLORS['primary']};
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .reasoning-text {{
            color: {HTML_COLORS['text_tertiary']};
            line-height: {HTML_TYPOGRAPHY['line_height_reasoning']};
        }}
        
        .brd-reference {{
            background: {HTML_COLORS['bg_white']};
            padding: 15px;
            border-radius: {HTML_BORDER_RADIUS['button']};
            margin-top: 10px;
            border-left: 3px solid {HTML_COLORS['primary']};
        }}
        
        .brd-reference-title {{
            font-weight: 600;
            color: {HTML_COLORS['primary']};
            font-size: {HTML_TYPOGRAPHY['font_sizes']['small']};
            margin-bottom: 5px;
        }}
        
        .brd-reference-text {{
            color: {HTML_COLORS['text_secondary']};
            font-style: italic;
        }}
        
        .metadata-section {{
            background: {HTML_COLORS['bg_secondary']};
            padding: {HTML_SPACING['content_padding']};
            border-radius: {HTML_BORDER_RADIUS['button']};
            margin-bottom: {HTML_SPACING['card_margin']};
        }}
        
        .metadata-item {{
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid {HTML_COLORS['border_light']};
        }}
        
        .metadata-item:last-child {{
            border-bottom: none;
        }}
        
        .metadata-label {{
            font-weight: 600;
            color: {HTML_COLORS['text_secondary']};
            width: 150px;
        }}
        
        .metadata-value {{
            color: {HTML_COLORS['text_primary']};
            flex: 1;
        }}
        
        .search-box {{
            width: 100%;
            padding: {HTML_SPACING['field_padding']} 20px;
            border: 2px solid {HTML_COLORS['border_light']};
            border-radius: {HTML_BORDER_RADIUS['input']};
            font-size: {HTML_TYPOGRAPHY['font_sizes']['body']};
            margin-bottom: 20px;
            transition: {HTML_TRANSITIONS['border']};
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: {HTML_COLORS['primary']};
        }}
        
        .no-results {{
            text-align: center;
            padding: {HTML_SPACING['content_padding']};
            color: {HTML_COLORS['text_muted']};
            font-size: 1.2em;
        }}
    """


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_field_color(field, color_scheme=DRAWIO_COLORS):
    """Determine field color based on field properties"""
    field_group = field.get('fieldGroup')
    field_name = field.get('name', '').lower()
    
    # Identifiers (pink) - _meta fields or fields with 'id' in name
    if field_group == '_meta' or 'id' in field_name:
        return color_scheme['identifier']
    
    # Field groups (yellow)
    if field_group and field_group != '_meta':
        return color_scheme['field_group']
    
    # General attributes (green)
    return color_scheme['general_attribute']


def get_entity_color(entity, color_scheme=DRAWIO_COLORS):
    """Determine entity color based on entity type"""
    entity_type = entity.get('type', '')
    if entity_type == 'BusinessEntity':
        return color_scheme['business_entity']
    return color_scheme['reference_entity']


"""Parser for Unity serialized MonoBehaviour data structures."""
import copy
from typing import Dict, Any, List, Optional, Tuple, Union


class DataParser:
    """Parses and edits Unity serialized MonoBehaviour data."""
    
    @staticmethod
    def _safe_get_array(obj: Any, default: list = None) -> list:
        """
        Safely get an array from Unity data structure.
        Handles both dict with 'Array' key and direct list.
        """
        if default is None:
            default = []
        
        if obj is None:
            return default
        
        # If it's already a list, return it
        if isinstance(obj, list):
            return obj
        
        # If it's a dict, try to get 'Array' key
        if isinstance(obj, dict):
            return obj.get('Array', default)
        
        return default
    
    @staticmethod
    def _safe_get_dict(obj: Any, default: dict = None) -> dict:
        """
        Safely get a dictionary from Unity data structure.
        """
        if default is None:
            default = {}
        
        if obj is None:
            return default
        
        if isinstance(obj, dict):
            return obj
        
        return default
    
    @staticmethod
    def _clean_for_unitypy(data: Any) -> Any:
        """
        Clean data structure to ensure it's compatible with UnityPy.
        Converts any non-standard types to proper dict/list structures.
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                cleaned[key] = DataParser._clean_for_unitypy(value)
            return cleaned
        elif isinstance(data, list):
            return [DataParser._clean_for_unitypy(item) for item in data]
        else:
            # Return primitive types as-is
            return data
    
    @staticmethod
    def _validate_mvalues_structure(data: Dict[str, Any]) -> bool:
        """
        Validate that all m_Values.Array entries are dictionaries.
        Returns True if valid, False otherwise.
        """
        m_rules = data.get('m_Rules')
        rules = DataParser._safe_get_array(m_rules)
        for rule in rules:
            if isinstance(rule, dict):
                m_props = rule.get('m_Properties')
                props = DataParser._safe_get_array(m_props)
                for prop in props:
                    if isinstance(prop, dict) and prop.get('m_Name') == 'color':
                        m_vals = prop.get('m_Values')
                        if isinstance(m_vals, dict):
                            vals_array = DataParser._safe_get_array(m_vals.get('Array'))
                            for v in vals_array:
                                if not isinstance(v, dict):
                                    return False
        return True
    
    @staticmethod
    def _clean_structure_recursive(obj: Any) -> Any:
        """
        Recursively clean structure to ensure all arrays contain only dicts where expected.
        This helps prevent UnityPy errors from strings in arrays.
        """
        if isinstance(obj, dict):
            cleaned = {}
            for key, value in obj.items():
                # Special handling for m_Values.Array - must contain only dicts
                if key == 'm_Values' and isinstance(value, dict):
                    array_val = DataParser._safe_get_array(value.get('Array'))
                    # Filter to only dicts with m_ValueType
                    cleaned_array = [v for v in array_val if isinstance(v, dict) and 'm_ValueType' in v]
                    cleaned[key] = {'Array': cleaned_array}
                else:
                    cleaned[key] = DataParser._clean_structure_recursive(value)
            return cleaned
        elif isinstance(obj, list):
            return [DataParser._clean_structure_recursive(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def parse_attribute_data_collection(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse AttributeDataCollection to extract thresholds and style classes.
        
        Returns:
            Dictionary with 'thresholds' (list of ints) and 'style_classes' (list of strings)
        """
        result = {
            'thresholds': [],
            'style_classes': []
        }
        
        # Find the Key column (IntDataSet)
        references_data = DataParser._safe_get_dict(data.get('references', {}))
        references = DataParser._safe_get_array(references_data.get('RefIds'))
        
        key_column_rid = None
        style_column_rid = None
        
        # Get column RIDs from m_columns
        m_columns = data.get('m_columns')
        columns = DataParser._safe_get_array(m_columns)
        if len(columns) >= 2:
            # Handle both dict with 'rid' key and direct dict
            col0 = columns[0]
            col1 = columns[1]
            if isinstance(col0, dict):
                key_column_rid = col0.get('rid')
            if isinstance(col1, dict):
                style_column_rid = col1.get('rid')
        
        # Extract data from references
        for ref in references:
            if not isinstance(ref, dict):
                continue
                
            rid = ref.get('rid')
            ref_type_data = DataParser._safe_get_dict(ref.get('type', {}))
            ref_type = ref_type_data.get('class', '')
            ref_data = DataParser._safe_get_dict(ref.get('data', {}))
            
            if rid == key_column_rid and ref_type == 'IntDataSet':
                # Extract thresholds
                m_rows = ref_data.get('m_rows')
                rows = DataParser._safe_get_array(m_rows)
                result['thresholds'] = rows
            
            elif rid == style_column_rid and ref_type == 'StringDataSet':
                # Extract style classes
                m_rows = ref_data.get('m_rows')
                rows = DataParser._safe_get_array(m_rows)
                result['style_classes'] = rows
        
        return result
    
    @staticmethod
    def update_attribute_data_collection(data: Dict[str, Any], thresholds: List[int], 
                                        style_classes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update AttributeDataCollection with new thresholds.
        
        Args:
            data: Original data dictionary
            thresholds: New threshold values
            style_classes: Optional new style class names
            
        Returns:
            Updated data dictionary
        """
        # Create a deep copy
        updated_data = data.copy()
        references_orig = data.get('references', {})
        updated_data['references'] = DataParser._safe_get_dict(references_orig).copy()
        ref_ids = DataParser._safe_get_array(references_orig.get('RefIds'))
        updated_data['references']['RefIds'] = [ref.copy() if isinstance(ref, dict) else ref for ref in ref_ids]
        
        # Get column RIDs
        m_columns = updated_data.get('m_columns')
        columns = DataParser._safe_get_array(m_columns)
        if len(columns) >= 2:
            col0 = columns[0]
            col1 = columns[1]
            key_column_rid = col0.get('rid') if isinstance(col0, dict) else None
            style_column_rid = col1.get('rid') if isinstance(col1, dict) else None
            
            # Update references
            for ref in updated_data['references']['RefIds']:
                if not isinstance(ref, dict):
                    continue
                rid = ref.get('rid')
                ref_type_data = DataParser._safe_get_dict(ref.get('type', {}))
                ref_type = ref_type_data.get('class', '')
                ref_data = DataParser._safe_get_dict(ref.get('data', {}))
                
                if rid == key_column_rid and ref_type == 'IntDataSet':
                    # Update thresholds - preserve structure format
                    ref['data'] = ref_data.copy()
                    m_rows_orig = ref_data.get('m_rows')
                    if isinstance(m_rows_orig, dict) and 'Array' in m_rows_orig:
                        ref['data']['m_rows'] = {'Array': thresholds}
                    else:
                        ref['data']['m_rows'] = thresholds
                
                elif rid == style_column_rid and ref_type == 'StringDataSet' and style_classes:
                    # Update style classes - preserve structure format
                    ref['data'] = ref_data.copy()
                    m_rows_orig = ref_data.get('m_rows')
                    if isinstance(m_rows_orig, dict) and 'Array' in m_rows_orig:
                        ref['data']['m_rows'] = {'Array': style_classes}
                    else:
                        ref['data']['m_rows'] = style_classes
            
            # Update row count
            updated_data['m_rows'] = len(thresholds)
        
        return updated_data
    
    @staticmethod
    def parse_attribute_highlight_collection(data: Dict[str, Any]) -> List[str]:
        """
        Parse AttributeHighlightTypeDataCollection or AttributeHighlightTypeNoBorderDataCollection
        to extract StyleClass values.
        
        Args:
            data: Collection data dictionary
            
        Returns:
            List of StyleClass strings (should be 3 items)
        """
        style_classes = []
        
        # Find the StyleClass column (StringDataSet)
        references_data = DataParser._safe_get_dict(data.get('references', {}))
        references = DataParser._safe_get_array(references_data.get('RefIds'))
        
        style_column_rid = None
        
        # Get column RIDs from m_columns
        m_columns = data.get('m_columns')
        columns = DataParser._safe_get_array(m_columns)
        if len(columns) >= 2:
            col1 = columns[1]
            if isinstance(col1, dict):
                style_column_rid = col1.get('rid')
        
        # Extract data from references
        for ref in references:
            if not isinstance(ref, dict):
                continue
                
            rid = ref.get('rid')
            ref_type_data = DataParser._safe_get_dict(ref.get('type', {}))
            ref_type = ref_type_data.get('class', '')
            ref_data = DataParser._safe_get_dict(ref.get('data', {}))
            
            if rid == style_column_rid and ref_type == 'StringDataSet':
                # Extract style classes
                m_rows = ref_data.get('m_rows')
                rows = DataParser._safe_get_array(m_rows)
                style_classes = rows
                break
        
        return style_classes
    
    @staticmethod
    def update_attribute_highlight_collection(data: Dict[str, Any], enabled: bool, 
                                             is_no_border: bool = False) -> Dict[str, Any]:
        """
        Update AttributeHighlightTypeDataCollection or AttributeHighlightTypeNoBorderDataCollection
        with new StyleClass values.
        
        Args:
            data: Original data dictionary
            enabled: If True, use original unique values; if False, use same value for all
            is_no_border: If True, this is the NoBorder collection
            
        Returns:
            Updated data dictionary
        """
        # Create a deep copy
        updated_data = copy.deepcopy(data)
        references_orig = data.get('references', {})
        updated_data['references'] = DataParser._safe_get_dict(references_orig).copy()
        ref_ids = DataParser._safe_get_array(references_orig.get('RefIds'))
        updated_data['references']['RefIds'] = [ref.copy() if isinstance(ref, dict) else ref for ref in ref_ids]
        
        # Get column RIDs
        m_columns = updated_data.get('m_columns')
        columns = DataParser._safe_get_array(m_columns)
        style_column_rid = None
        if len(columns) >= 2:
            col1 = columns[1]
            if isinstance(col1, dict):
                style_column_rid = col1.get('rid')
        
        # Determine new StyleClass values
        if enabled:
            # Original unique values
            if is_no_border:
                new_style_classes = [
                    "attributes-row-number-no-border",
                    "attributes-row-number-preference-no-border",
                    "attributes-row-number-key-no-border"
                ]
            else:
                new_style_classes = [
                    "attributes-row-number",
                    "attributes-row-number-preference",
                    "attributes-row-number-key"
                ]
        else:
            # All same value
            if is_no_border:
                new_style_classes = [
                    "attributes-row-number-no-border",
                    "attributes-row-number-no-border",
                    "attributes-row-number-no-border"
                ]
            else:
                new_style_classes = [
                    "attributes-row-number",
                    "attributes-row-number",
                    "attributes-row-number"
                ]
        
        # Update references
        for ref in updated_data['references']['RefIds']:
            if not isinstance(ref, dict):
                continue
            rid = ref.get('rid')
            ref_type_data = DataParser._safe_get_dict(ref.get('type', {}))
            ref_type = ref_type_data.get('class', '')
            ref_data = DataParser._safe_get_dict(ref.get('data', {}))
            
            if rid == style_column_rid and ref_type == 'StringDataSet':
                # Update style classes - preserve structure format
                ref['data'] = ref_data.copy()
                m_rows_orig = ref_data.get('m_rows')
                if isinstance(m_rows_orig, dict) and 'Array' in m_rows_orig:
                    ref['data']['m_rows'] = {'Array': new_style_classes}
                else:
                    ref['data']['m_rows'] = new_style_classes
                break
        
        return updated_data
    
    @staticmethod
    def parse_color_preset(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse color preset data to extract color information.
        
        Returns:
            Dictionary with color rules and current colors
        """
        result = {
            'rules': [],
            'colors': [],
            'floats': [],
            'selectors': []
        }
        
        # Extract rules
        m_rules = data.get('m_Rules')
        rules = DataParser._safe_get_array(m_rules)
        result['rules'] = rules
        
        # Extract colors array (may be empty initially)
        colors_data = data.get('colors')
        colors = DataParser._safe_get_array(colors_data)
        result['colors'] = colors
        
        # Extract floats array (RGBA values)
        floats_data = data.get('floats')
        floats = DataParser._safe_get_array(floats_data)
        result['floats'] = floats
        
        # Extract selectors
        m_complex_selectors = data.get('m_ComplexSelectors')
        selectors = DataParser._safe_get_array(m_complex_selectors)
        result['selectors'] = selectors
        
        return result
    
    @staticmethod
    def extract_colors_from_rules(data: Dict[str, Any]) -> List[Tuple[float, float, float, float]]:
        """
        Extract color values from rules.
        
        Returns:
            List of RGBA tuples
        """
        colors = []
        colors_data = data.get('colors')
        colors_array = DataParser._safe_get_array(colors_data)
        m_rules = data.get('m_Rules')
        rules = DataParser._safe_get_array(m_rules)
        
        # Extract from colors array - format is array of objects with r, g, b, a properties
        if colors_array:
            for color_obj in colors_array:
                if isinstance(color_obj, dict):
                    r = color_obj.get('r', 1.0)
                    g = color_obj.get('g', 1.0)
                    b = color_obj.get('b', 1.0)
                    a = color_obj.get('a', 1.0)
                    colors.append((r, g, b, a))
        
        # If colors array is empty or doesn't match rule count, try to extract from rules
        # (fallback for old format or incomplete data)
        if len(colors) != len(rules):
            colors = []
            floats_data = data.get('floats')
            floats = DataParser._safe_get_array(floats_data)
            
            if floats:
                for rule in rules:
                    if not isinstance(rule, dict):
                        continue
                    m_properties = rule.get('m_Properties')
                    properties = DataParser._safe_get_array(m_properties)
                    for prop in properties:
                        if not isinstance(prop, dict):
                            continue
                        if prop.get('m_Name') == 'color':
                            m_values = prop.get('m_Values')
                            values = DataParser._safe_get_array(m_values)
                            # Look for color value (m_ValueType 4) or float value (m_ValueType 2)
                            for val in values:
                                if not isinstance(val, dict):
                                    continue
                                value_type = val.get('m_ValueType')
                                idx = val.get('valueIndex', 0)
                                
                                if value_type == 4:  # Color type - should use colors array
                                    if idx < len(colors_array) and isinstance(colors_array[idx], dict):
                                        color_obj = colors_array[idx]
                                        r = color_obj.get('r', 1.0)
                                        g = color_obj.get('g', 1.0)
                                        b = color_obj.get('b', 1.0)
                                        a = color_obj.get('a', 1.0)
                                        colors.append((r, g, b, a))
                                        break
                                elif value_type == 2:  # Float type (old format)
                                    # Colors are typically 4 floats (RGBA)
                                    if idx < len(floats) - 3:
                                        r = floats[idx]
                                        g = floats[idx + 1] if idx + 1 < len(floats) else 1.0
                                        b = floats[idx + 2] if idx + 2 < len(floats) else 1.0
                                        a = floats[idx + 3] if idx + 3 < len(floats) else 1.0
                                        colors.append((r, g, b, a))
                                        break
        
        # If still no colors found, return default white colors
        if not colors:
            # Return white for each rule
            for _ in rules:
                colors.append((1.0, 1.0, 1.0, 1.0))
        
        return colors
    
    @staticmethod
    def update_color_preset(data: Dict[str, Any], colors: List[Tuple[float, float, float, float]], 
                           style_classes: List[str]) -> Dict[str, Any]:
        """
        Update color preset with new colors.
        
        Args:
            data: Original color preset data
            colors: List of RGBA tuples (r, g, b, a) where values are 0.0-1.0
            style_classes: List of style class names in order
            
        Returns:
            Updated data dictionary
        """
        # Validate inputs
        if not isinstance(style_classes, list):
            raise ValueError(f"style_classes must be a list, got {type(style_classes)}")
        if not isinstance(colors, list):
            raise ValueError(f"colors must be a list, got {type(colors)}")
        if len(style_classes) != len(colors):
            raise ValueError(f"style_classes ({len(style_classes)}) and colors ({len(colors)}) must have the same length")
        
        # Ensure all style_classes are strings
        for idx, sc in enumerate(style_classes):
            if not isinstance(sc, str):
                raise ValueError(f"style_classes[{idx}] must be a string, got {type(sc)}: {sc}")
        
        # Start with a deep copy of the original data to preserve UnityPy's structure
        # This ensures we maintain all the internal structure UnityPy expects
        updated_data = copy.deepcopy(data)
        
        # UnityPy reads m_Rules, m_ComplexSelectors, and colors as DIRECT LISTS, not {"Array": [...]}
        # Check the original format and match it
        original_m_rules = updated_data.get('m_Rules', [])
        original_m_selectors = updated_data.get('m_ComplexSelectors', [])
        original_colors = updated_data.get('colors', [])
        
        # If they're in {"Array": [...]} format, extract the list
        if isinstance(original_m_rules, dict) and 'Array' in original_m_rules:
            original_m_rules = original_m_rules['Array']
        if isinstance(original_m_selectors, dict) and 'Array' in original_m_selectors:
            original_m_selectors = original_m_selectors['Array']
        if isinstance(original_colors, dict) and 'Array' in original_colors:
            original_colors = original_colors['Array']
        
        # Ensure they're lists (UnityPy expects direct lists)
        if not isinstance(original_m_rules, list):
            original_m_rules = []
        if not isinstance(original_m_selectors, list):
            original_m_selectors = []
        if not isinstance(original_colors, list):
            original_colors = []
        
        # Clear existing - we'll rebuild them as direct lists
        updated_data['m_Rules'] = []
        updated_data['m_ComplexSelectors'] = []
        updated_data['colors'] = []
        
        # Convert colors to the format Unity expects: array of color objects with r, g, b, a
        # UnityPy expects a DIRECT LIST, not {"Array": [...]}
        color_objects = []
        for r, g, b, a in colors:
            color_objects.append({
                'r': r,
                'g': g,
                'b': b,
                'a': a
            })
        
        # Update colors array - UnityPy expects direct list
        updated_data['colors'] = color_objects
        
        # Keep floats array as-is (may not be used, but preserve original structure)
        # Don't modify floats array - it's separate from the color values
        
        # Build rules from scratch - don't copy from original to avoid any invalid data
        updated_rules = []
        for i, style_class in enumerate(style_classes):
            # Validate style_class is a string
            if not isinstance(style_class, str):
                raise ValueError(f"style_classes[{i}] is not a string: {type(style_class)} = {style_class}")
            
            # Create rule from scratch based on example format
            # Ensure every value is explicitly a dict, not a string
            # Create the property dict first
            # UnityPy expects m_Values as a DIRECT LIST, not {"Array": [...]}
            property_dict = {
                'm_Name': 'color',
                'm_Line': 3 + (i * 4),
                'm_Values': [
                    {'m_ValueType': 4, 'valueIndex': i}
                ]
            }
            
            # Validate property_dict is a dict
            if not isinstance(property_dict, dict):
                raise ValueError(f"Property dict {i} is not a dictionary: {type(property_dict)}")
            
            # Validate m_Values is a list
            if not isinstance(property_dict.get('m_Values'), list):
                raise ValueError(f"Property dict {i} m_Values is not a list: {type(property_dict.get('m_Values'))}")
            
            # Create the rule dict
            # UnityPy expects m_Properties as a DIRECT LIST, not {"Array": [...]}
            updated_rule = {
                'm_Properties': [property_dict],
                'line': 2 + (i * 4)
            }
            
            # Validate the rule is a dict before adding
            if not isinstance(updated_rule, dict):
                raise ValueError(f"Rule {i} is not a dictionary: {type(updated_rule)}")
            if 'm_Properties' not in updated_rule:
                import json
                rule_str = json.dumps(updated_rule, indent=2, default=str)
                raise ValueError(
                    f"CRITICAL ERROR: Rule {i} missing m_Properties immediately after creation!\n"
                    f"Rule keys: {list(updated_rule.keys())}\n"
                    f"Full rule:\n{rule_str}\n"
                    f"This should be impossible - the rule was just created with m_Properties!"
                )
            # Double-check the structure
            # UnityPy expects m_Properties as a DIRECT LIST
            m_props = updated_rule.get('m_Properties')
            if not isinstance(m_props, list):
                raise ValueError(f"Rule {i} m_Properties is not a list: {type(m_props)}")
            if len(m_props) == 0:
                raise ValueError(f"Rule {i} m_Properties is empty")
            if not isinstance(m_props[0], dict):
                raise ValueError(f"Rule {i} m_Properties[0] is not a dict: {type(m_props[0])}")
            
            # Only append if everything is valid
            updated_rules.append(updated_rule)
        
        # Ensure all rules are dicts and have m_Properties
        for idx, rule in enumerate(updated_rules):
            if not isinstance(rule, dict):
                raise ValueError(f"Rule at index {idx} is not a dict: {type(rule).__name__}")
            if 'm_Properties' not in rule:
                raise ValueError(f"Rule at index {idx} missing m_Properties before adding to updated_data. Keys: {list(rule.keys())}")
        
        # Verify rules before assignment
        for idx, rule in enumerate(updated_rules):
            if not isinstance(rule, dict):
                raise ValueError(f"Rule at index {idx} is not a dict: {type(rule).__name__}")
            if 'm_Properties' not in rule:
                import json
                rule_str = json.dumps(rule, indent=2, default=str)
                raise ValueError(
                    f"CRITICAL: Rule at index {idx} missing m_Properties BEFORE assignment to updated_data!\n"
                    f"Rule keys: {list(rule.keys())}\n"
                    f"Full rule structure:\n{rule_str}\n"
                    f"This should never happen - rule was created with m_Properties"
                )
        
        # UnityPy expects m_Rules as a DIRECT LIST
        updated_data['m_Rules'] = updated_rules
        
        # Double-check after assignment - this should never fail if our code is correct
        # UnityPy expects m_Rules as a DIRECT LIST
        rules_check = updated_data['m_Rules']
        if not isinstance(rules_check, list):
            raise ValueError(f"m_Rules is not a list after assignment: {type(rules_check).__name__}")
        for idx, rule in enumerate(rules_check):
            if not isinstance(rule, dict):
                raise ValueError(f"Rule at index {idx} is not a dict after assignment: {type(rule).__name__}")
            if 'm_Properties' not in rule:
                # This should never happen, but if it does, show what we have
                import json
                rule_str = json.dumps(rule, indent=2, default=str)
                raise ValueError(
                    f"CRITICAL: Rule at index {idx} missing m_Properties AFTER assignment to updated_data!\n"
                    f"Rule keys: {list(rule.keys())}\n"
                    f"Full rule structure:\n{rule_str}\n"
                    f"Something modified the structure between creation and assignment!"
                )
            # Verify m_Properties structure - UnityPy expects DIRECT LIST
            m_props = rule.get('m_Properties')
            if not isinstance(m_props, list):
                raise ValueError(f"Rule {idx} m_Properties is not a list: {type(m_props).__name__}")
            if len(m_props) == 0:
                raise ValueError(f"Rule {idx} m_Properties is empty")
        
        # Build selectors from scratch - don't copy from original
        # UnityPy expects m_ComplexSelectors as a DIRECT LIST
        updated_selectors = []
        for i, style_class in enumerate(style_classes):
            # Create selector from scratch based on example format
            # UnityPy expects m_Selectors and m_Parts as DIRECT LISTS
            updated_selector = {
                'm_Specificity': 11,
                'm_Selectors': [{
                    'm_Parts': [{
                        'm_Value': style_class,
                        'm_Type': 3
                    }],
                    'm_PreviousRelationship': 0
                }],
                'ruleIndex': i
            }
            updated_selectors.append(updated_selector)
        
        # UnityPy expects m_ComplexSelectors as a DIRECT LIST
        updated_data['m_ComplexSelectors'] = updated_selectors
        
        # Final validation: ensure everything is the correct type
        # UnityPy expects m_Rules as a DIRECT LIST
        rules_array = updated_data['m_Rules']
        if not isinstance(rules_array, list):
            raise ValueError(f"m_Rules is not a list: {type(rules_array).__name__}")
        for idx, rule in enumerate(rules_array):
            if not isinstance(rule, dict):
                raise ValueError(f"Rule at index {idx} is not a dict, it's a {type(rule).__name__}: {rule}")
            if 'm_Properties' not in rule:
                raise ValueError(f"Rule at index {idx} missing m_Properties: {rule.keys()}")
            m_props = rule['m_Properties']
            if not isinstance(m_props, list):
                raise ValueError(f"Rule {idx} m_Properties is not a list, it's a {type(m_props).__name__}")
            for prop_idx, prop in enumerate(m_props):
                if not isinstance(prop, dict):
                    raise ValueError(f"Rule {idx} property {prop_idx} is not a dict, it's a {type(prop).__name__}")
        
        # Check selectors too - UnityPy expects m_ComplexSelectors as a DIRECT LIST
        selectors_array = updated_data['m_ComplexSelectors']
        if not isinstance(selectors_array, list):
            raise ValueError(f"m_ComplexSelectors is not a list: {type(selectors_array).__name__}")
        for idx, selector in enumerate(selectors_array):
            if not isinstance(selector, dict):
                raise ValueError(f"Selector at index {idx} is not a dict, it's a {type(selector).__name__}")
        
        # Final comprehensive check before returning
        # UnityPy expects m_Rules as a DIRECT LIST
        final_rules = updated_data.get('m_Rules', [])
        if isinstance(final_rules, dict) and 'Array' in final_rules:
            final_rules = final_rules['Array']
        for idx, rule in enumerate(final_rules):
            if not isinstance(rule, dict):
                import json
                raise ValueError(
                    f"FINAL CHECK FAILED: Rule {idx} is not a dict: {type(rule).__name__}\n"
                    f"Value: {json.dumps(rule, default=str)[:200]}"
                )
            rule_keys = list(rule.keys())
            if 'm_Properties' not in rule_keys:
                import json
                rule_str = json.dumps(rule, indent=2, default=str)
                raise ValueError(
                    f"FINAL CHECK FAILED: Rule {idx} missing m_Properties before returning!\n"
                    f"Rule keys: {rule_keys}\n"
                    f"Expected keys: ['m_Properties', 'line']\n"
                    f"Full rule:\n{rule_str}\n"
                    f"All rules in array: {len(final_rules)} total"
                )
            # Verify m_Properties structure - UnityPy expects DIRECT LIST
            m_props = rule.get('m_Properties')
            if not isinstance(m_props, list):
                raise ValueError(f"FINAL CHECK: Rule {idx} m_Properties is not a list: {type(m_props)}")
            if len(m_props) == 0:
                raise ValueError(f"FINAL CHECK: Rule {idx} m_Properties is empty")
        
        # Create a deep copy to ensure complete isolation from any original data
        # This prevents any potential reference issues
        return copy.deepcopy(updated_data)
    
    @staticmethod
    def rgba_to_hex(r: float, g: float, b: float, a: float = 1.0) -> str:
        """Convert RGBA (0.0-1.0) to hex string with alpha (#RRGGBBAA format)."""
        r_int = int(max(0, min(255, r * 255)))
        g_int = int(max(0, min(255, g * 255)))
        b_int = int(max(0, min(255, b * 255)))
        a_int = int(max(0, min(255, a * 255)))
        return f"#{r_int:02X}{g_int:02X}{b_int:02X}{a_int:02X}"
    
    @staticmethod
    def hex_to_rgba(hex_str: str) -> Tuple[float, float, float, float]:
        """Convert hex string to RGBA (0.0-1.0)."""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            return (r, g, b, 1.0)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            a = int(hex_str[6:8], 16) / 255.0
            return (r, g, b, a)
        return (1.0, 1.0, 1.0, 1.0)


"""Bundle manager for reading and writing Unity bundle files using UnityPy."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import UnityPy


class BundleManager:
    """Manages Unity bundle file operations."""
    
    def __init__(self, fm_install_dir: str):
        """
        Initialize bundle manager.
        
        Args:
            fm_install_dir: Path to FM installation directory
        """
        self.fm_install_dir = Path(fm_install_dir)
        self.bundle_dir = self._get_bundle_directory()
        
    def _get_bundle_directory(self) -> Path:
        """Get the bundle directory based on platform."""
        # Windows path
        bundle_path = self.fm_install_dir / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
        if bundle_path.exists():
            return bundle_path
        
        # Try Linux path
        bundle_path = self.fm_install_dir / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneLinux64"
        if bundle_path.exists():
            return bundle_path
        
        # Try Mac path
        bundle_path = self.fm_install_dir / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneOSX"
        if bundle_path.exists():
            return bundle_path
        
        # Default to Windows path
        return self.fm_install_dir / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
    
    def get_bundle_path(self, bundle_name: str) -> Path:
        """Get full path to a bundle file."""
        return self.bundle_dir / bundle_name
    
    def bundle_exists(self, bundle_name: str) -> bool:
        """Check if a bundle file exists."""
        return self.get_bundle_path(bundle_name).exists()
    
    def read_bundle(self, bundle_name: str) -> Optional[UnityPy.Environment]:
        """
        Read a Unity bundle file.
        
        Args:
            bundle_name: Name of the bundle file
            
        Returns:
            UnityPy Environment object or None if file doesn't exist
        """
        bundle_path = self.get_bundle_path(bundle_name)
        if not bundle_path.exists():
            return None
        
        try:
            return UnityPy.load(str(bundle_path))
        except Exception as e:
            raise Exception(f"Failed to read bundle {bundle_name}: {e}")
    
    def get_object_from_bundle(self, bundle_name: str, object_name: str) -> Optional[Any]:
        """
        Get a specific object from a bundle.
        
        Args:
            bundle_name: Name of the bundle file
            object_name: Name of the object to retrieve
            
        Returns:
            Typetree dictionary or None if not found
        """
        env = self.read_bundle(bundle_name)
        if env is None:
            return None
        
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                # Try to get the serialized data
                try:
                    tree = obj.read_typetree()
                    # Ensure tree is a dictionary
                    if isinstance(tree, dict) and tree.get('m_Name') == object_name:
                        return tree
                except Exception as e:
                    # Log error for debugging if needed
                    pass
        
        return None
    
    def get_unitypy_object_from_bundle(self, bundle_name: str, object_name: str) -> Optional[Any]:
        """
        Get the UnityPy object (not just the typetree) from a bundle.
        
        Args:
            bundle_name: Name of the bundle file
            object_name: Name of the object to retrieve
            
        Returns:
            UnityPy object or None if not found
        """
        env = self.read_bundle(bundle_name)
        if env is None:
            return None
        
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                try:
                    tree = obj.read_typetree()
                    if isinstance(tree, dict) and tree.get('m_Name') == object_name:
                        return obj
                except Exception as e:
                    pass
        
        return None
    
    def get_object_and_env(self, bundle_name: str, object_name: str) -> Optional[tuple]:
        """
        Get both the UnityPy object and environment for writing.
        
        Args:
            bundle_name: Name of the bundle file
            object_name: Name of the object to retrieve
            
        Returns:
            Tuple of (UnityPy object, Environment) or None if not found
        """
        env = self.read_bundle(bundle_name)
        if env is None:
            return None
        
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                try:
                    tree = obj.read_typetree()
                    if tree.get('m_Name') == object_name:
                        return (obj, env)
                except:
                    pass
        
        return None
    
    def write_bundle(self, bundle_name: str, objects: Dict[str, Any]) -> bool:
        """
        Write objects to a bundle file.
        
        Args:
            bundle_name: Name of the bundle file
            objects: Dictionary mapping object names to their updated typetree data
            
        Returns:
            True if successful, False otherwise
        """
        bundle_path = self.get_bundle_path(bundle_name)
        if not bundle_path.exists():
            return False
        
        try:
            # Read existing bundle
            env = UnityPy.load(str(bundle_path))
            
            # Update objects
            for obj in env.objects:
                if obj.type.name == "MonoBehaviour":
                    obj_name = None
                    
                    # Get object name and original tree
                    original_tree = None
                    try:
                        original_tree = obj.read_typetree()
                        if isinstance(original_tree, dict):
                            obj_name = original_tree.get('m_Name')
                    except:
                        pass
                    
                    # Update if in our objects dict
                    if obj_name and obj_name in objects:
                        updated_tree = objects[obj_name]
                        
                        # For color presets, try a different approach: modify the original tree in place
                        # This preserves UnityPy's internal structure and references
                        if obj_name.startswith('AttributeColours') and original_tree:
                            # Instead of replacing the entire tree, modify the original tree in place
                            # This should preserve UnityPy's internal structure
                            import copy
                            # Deep copy to avoid modifying the original
                            modified_tree = copy.deepcopy(original_tree)
                            
                            # Update only the parts we changed
                            if 'm_Rules' in updated_tree:
                                modified_tree['m_Rules'] = copy.deepcopy(updated_tree['m_Rules'])
                            if 'm_ComplexSelectors' in updated_tree:
                                modified_tree['m_ComplexSelectors'] = copy.deepcopy(updated_tree['m_ComplexSelectors'])
                            if 'colors' in updated_tree:
                                modified_tree['colors'] = copy.deepcopy(updated_tree['colors'])
                            
                            updated_tree = modified_tree
                        
                        # Ensure we're passing a dict to save_typetree
                        if isinstance(updated_tree, dict):
                            # Validate structure before saving - check for strings in arrays where they shouldn't be
                            # First, do a quick check on m_Rules if it exists
                            # UnityPy expects m_Rules as a DIRECT LIST, not {"Array": [...]}
                            if 'm_Rules' in updated_tree:
                                m_rules = updated_tree['m_Rules']
                                # Handle both formats for validation
                                if isinstance(m_rules, dict) and 'Array' in m_rules:
                                    rules_array = m_rules['Array']
                                elif isinstance(m_rules, list):
                                    rules_array = m_rules
                                else:
                                    rules_array = []
                                
                                if isinstance(rules_array, list):
                                    for idx, rule in enumerate(rules_array):
                                        if not isinstance(rule, dict):
                                            raise ValueError(
                                                f"CRITICAL: m_Rules[{idx}] is not a dict, it's a {type(rule).__name__}: {str(rule)[:100]}"
                                            )
                                        if 'm_Properties' not in rule:
                                            import json
                                            rule_str = json.dumps(rule, indent=2, default=str)
                                            raise ValueError(
                                                f"CRITICAL: m_Rules[{idx}] missing m_Properties!\n"
                                                f"Rule keys: {list(rule.keys())}\n"
                                                f"Full rule:\n{rule_str}\n"
                                            )
                            
                            def validate_structure(obj, path="root", parent_key=None):
                                """Recursively validate structure - allow strings in StringDataSet.m_rows but not in m_Rules/m_Values"""
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        if key == 'Array' and isinstance(value, list):
                                            # Special handling for critical arrays that must only contain dicts
                                            # Check the parent key to determine which array this is
                                            # When we're at m_Rules.Array, parent_key should be 'm_Rules'
                                            if parent_key == 'm_Rules' or (parent_key is None and 'm_Rules' in path):
                                                # m_Rules.Array must only contain dicts
                                                for idx, item in enumerate(value):
                                                    if not isinstance(item, dict):
                                                        raise ValueError(
                                                            f"Found non-dict in m_Rules.Array at index {idx}: {type(item).__name__} - {str(item)[:50]}"
                                                        )
                                                    if 'm_Properties' not in item:
                                                        raise ValueError(
                                                            f"Rule at index {idx} missing m_Properties. Rule keys: {list(item.keys())}"
                                                        )
                                                    # Pass 'm_Rules' as parent_key to preserve context, not 'Array'
                                                    validate_structure(item, f"{path}.{key}[{idx}]", 'm_Rules')
                                            elif parent_key == 'm_ComplexSelectors' or 'm_ComplexSelectors' in path:
                                                # m_ComplexSelectors.Array must only contain dicts
                                                for idx, item in enumerate(value):
                                                    if not isinstance(item, dict):
                                                        raise ValueError(
                                                            f"Found non-dict in m_ComplexSelectors.Array at index {idx}: {type(item).__name__} - {str(item)[:50]}"
                                                        )
                                                    validate_structure(item, f"{path}.{key}[{idx}]", key)
                                            elif parent_key == 'm_Values' or 'm_Values' in path:
                                                # m_Values.Array must only contain dicts
                                                for idx, item in enumerate(value):
                                                    if not isinstance(item, dict):
                                                        raise ValueError(
                                                            f"Found non-dict in m_Values.Array at index {idx}: {type(item).__name__} - {str(item)[:50]}"
                                                        )
                                                    if 'm_ValueType' not in item:
                                                        raise ValueError(
                                                            f"m_Values.Array[{idx}] missing m_ValueType"
                                                        )
                                                    validate_structure(item, f"{path}.{key}[{idx}]", key)
                                            else:
                                                # Check array contents for other arrays
                                                for idx, item in enumerate(value):
                                                    # Allow strings in StringDataSet.m_rows (style class names)
                                                    if isinstance(item, str):
                                                        # Check if this is a StringDataSet m_rows array - those can have strings
                                                        # Path will be like "root.references.RefIds[1].data.m_rows"
                                                        if 'm_rows' in path:
                                                            # This is OK - StringDataSet rows are strings
                                                            continue
                                                        # Also allow strings in other string arrays (like strings.Array, m_Name, etc.)
                                                        elif 'strings' in path.lower() or key == 'm_Name' or 'm_name' in path.lower():
                                                            continue
                                                        else:
                                                            # Strings not allowed in most arrays
                                                            raise ValueError(
                                                                f"Found string in array at {path}.Array[{idx}]: {item[:50]}"
                                                            )
                                                    validate_structure(item, f"{path}.{key}[{idx}]", key)
                                        else:
                                            validate_structure(value, f"{path}.{key}", key)
                                elif isinstance(obj, list):
                                    for idx, item in enumerate(obj):
                                        # Allow strings in StringDataSet m_rows (direct list format)
                                        if isinstance(item, str):
                                            # Path will be like "root.references.RefIds[1].data.m_rows"
                                            if 'm_rows' in path:
                                                # This is OK - StringDataSet rows are strings
                                                continue
                                            elif 'strings' in path.lower():
                                                continue
                                            else:
                                                raise ValueError(
                                                    f"Found string in list at {path}[{idx}]: {item[:50]}"
                                                )
                                        validate_structure(item, f"{path}[{idx}]", None)
                            
                            # Debug: Check m_Rules structure before validation
                            if 'm_Rules' in updated_tree:
                                m_rules = updated_tree.get('m_Rules', {})
                                if isinstance(m_rules, dict):
                                    rules_array = m_rules.get('Array', [])
                                    if isinstance(rules_array, list) and len(rules_array) > 0:
                                        first_rule = rules_array[0]
                                        if isinstance(first_rule, dict):
                                            rule_keys = list(first_rule.keys())
                                            if 'm_Properties' not in rule_keys:
                                                import json
                                                # Get full structure for debugging
                                                full_structure = json.dumps(updated_tree, indent=2, default=str)
                                                rule_str = json.dumps(first_rule, indent=2, default=str)
                                                raise Exception(
                                                    f"Structure validation failed for {obj_name}: "
                                                    f"Rule at index 0 missing m_Properties.\n"
                                                    f"Rule keys: {rule_keys}\n"
                                                    f"First rule structure:\n{rule_str}\n\n"
                                                    f"Full m_Rules structure:\n{json.dumps(m_rules, indent=2, default=str)}\n\n"
                                                    f"This indicates the property object was placed directly in rules array instead of being wrapped in a rule with m_Properties."
                                                )
                            
                            try:
                                validate_structure(updated_tree)
                            except ValueError as val_err:
                                raise Exception(
                                    f"Structure validation failed for {obj_name}: {val_err}"
                                ) from val_err
                            
                            # Validate structure before saving
                            import json
                            try:
                                # Try to serialize to JSON to catch any structure issues
                                json.dumps(updated_tree)
                            except (TypeError, ValueError) as json_err:
                                raise Exception(
                                    f"Invalid data structure for {obj_name}: {json_err}. "
                                    "Structure contains non-serializable objects."
                                ) from json_err
                            
                            # Final pre-save check - inspect m_Rules structure exactly as UnityPy will see it
                            # UnityPy expects m_Rules as a DIRECT LIST, not {"Array": [...]}
                            if 'm_Rules' in updated_tree:
                                m_rules_final = updated_tree.get('m_Rules', [])
                                # Handle both formats for validation
                                if isinstance(m_rules_final, dict) and 'Array' in m_rules_final:
                                    rules_array_final = m_rules_final['Array']
                                elif isinstance(m_rules_final, list):
                                    rules_array_final = m_rules_final
                                else:
                                    rules_array_final = []
                                
                                if isinstance(rules_array_final, list):
                                    # Check each rule and also check the types of nested structures
                                    for final_idx, final_rule in enumerate(rules_array_final):
                                        if not isinstance(final_rule, dict):
                                            import json
                                            raise Exception(
                                                f"PRE-SAVE: m_Rules[{final_idx}] is {type(final_rule).__name__}, not dict!\n"
                                                f"Value: {final_rule}\n"
                                                f"This is what UnityPy will receive - structure is invalid!"
                                            )
                                        if 'm_Properties' not in final_rule:
                                            import json
                                            rule_dump = json.dumps(final_rule, indent=2, default=str)
                                            raise Exception(
                                                f"PRE-SAVE: m_Rules[{final_idx}] missing m_Properties!\n"
                                                f"Rule type: {type(final_rule)}\n"
                                                f"Rule keys: {list(final_rule.keys())}\n"
                                                f"Rule structure:\n{rule_dump}\n"
                                                f"This is what UnityPy will receive - structure is invalid!"
                                            )
                                        # Check nested structure types - UnityPy expects DIRECT LISTS
                                        m_props_check = final_rule.get('m_Properties', [])
                                        if not isinstance(m_props_check, list):
                                            raise Exception(
                                                f"PRE-SAVE: m_Rules[{final_idx}].m_Properties is {type(m_props_check).__name__}, not list! (UnityPy expects direct list)"
                                            )
                                        for prop_idx, prop in enumerate(m_props_check):
                                            if not isinstance(prop, dict):
                                                raise Exception(
                                                    f"PRE-SAVE: m_Rules[{final_idx}].m_Properties[{prop_idx}] is {type(prop).__name__}, not dict! Value: {prop}"
                                                )
                                            m_vals_check = prop.get('m_Values', [])
                                            if not isinstance(m_vals_check, list):
                                                raise Exception(
                                                    f"PRE-SAVE: m_Rules[{final_idx}].m_Properties[{prop_idx}].m_Values is {type(m_vals_check).__name__}, not list! (UnityPy expects direct list)"
                                                )
                                            for val_idx, val_item in enumerate(m_vals_check):
                                                if not isinstance(val_item, dict):
                                                    raise Exception(
                                                        f"PRE-SAVE: m_Rules[{final_idx}].m_Properties[{prop_idx}].m_Values[{val_idx}] is {type(val_item).__name__}, not dict! Value: {val_item}"
                                                    )
                            
                            try:
                                obj.save_typetree(updated_tree)
                            except AttributeError as e:
                                # If we get an attribute error, it might be a structure issue
                                error_str = str(e)
                                if 'm_Properties' in error_str:
                                    # Dump the structure for debugging
                                    import json
                                    m_rules_debug = updated_tree.get('m_Rules', {})
                                    rules_debug_str = json.dumps(m_rules_debug, indent=2, default=str)
                                    
                                    # Also dump the original structure for comparison
                                    original_rules_debug = original_tree.get('m_Rules', {}) if original_tree else {}
                                    original_rules_str = json.dumps(original_rules_debug, indent=2, default=str)
                                    
                                    raise Exception(
                                        f"UnityPy structure error for {obj_name}: {e}\n\n"
                                        f"Original m_Rules structure (from UnityPy):\n{original_rules_str}\n\n"
                                        f"Updated m_Rules structure (that we're trying to save):\n{rules_debug_str}\n\n"
                                        "A string was found where a dictionary with 'm_Properties' was expected. "
                                        "This usually means a string is in m_Rules.Array or m_ComplexSelectors.Array. "
                                        "Compare the original structure above with the updated structure to see what's different."
                                    ) from e
                                elif 'm_ValueType' in error_str:
                                    raise Exception(
                                        f"UnityPy structure error for {obj_name}: {e}. "
                                        "A string was found in m_Values.Array where a dictionary was expected."
                                    ) from e
                                else:
                                    raise Exception(
                                        f"UnityPy structure error for {obj_name}: {e}. "
                                        "This may indicate incompatible data structure format."
                                    ) from e
            
            # Save bundle
            with open(bundle_path, 'wb') as f:
                f.write(env.file.save())
            
            return True
        except Exception as e:
            raise Exception(f"Failed to write bundle {bundle_name}: {e}")
    
    def get_data_collection_bundle_name(self) -> str:
        """Get the name of the data collection bundle."""
        return "ui-datacollections_assets_all.bundle"
    
    def get_style_bundle_name(self) -> str:
        """Get the name of the style bundle."""
        return "ui-styles_assets_default.bundle"
    
    def get_color_preset_names(self) -> list:
        """Get list of color preset object names."""
        return [
            "AttributeColoursDefault",
            "AttributeColoursAlternative",
            "AttributeColoursBlueOrange",
            "AttributeColoursCyanYellow"
        ]


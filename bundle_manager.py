"""Bundle manager for reading and writing Unity bundle files using UnityPy."""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import UnityPy


class BundleManager:
    """Manages Unity bundle file operations."""
    
    def __init__(self, fm_install_dir: str, bundle_dir_path: Optional[str] = None):
        """
        Initialize bundle manager.
        
        Args:
            fm_install_dir: Path to FM installation directory
            bundle_dir_path: Optional full path to bundle directory (e.g., when auto-scanned).
                           If provided, this will be used directly instead of appending StreamingAssets paths.
        """
        self.fm_install_dir = Path(fm_install_dir)
        if bundle_dir_path:
            self.bundle_dir = Path(bundle_dir_path)
        else:
            self.bundle_dir = self._get_bundle_directory()
        
    def _get_bundle_directory(self) -> Path:
        """Get the bundle directory based on platform by appending StreamingAssets paths."""
        paths_to_try = []
        
        if sys.platform.startswith("win"):
            paths_to_try.extend([
                ("fm_Data", "StandaloneWindows64"),
                ("data", "StandaloneWindows64"),
            ])
            paths_to_try.extend([
                ("fm_Data", "StandaloneLinux64"),
                ("fm_Data", "StandaloneOSX"),
                ("fm_Data", "StandaloneOSXUniversal"),
            ])
        elif sys.platform.startswith("darwin"):
            paths_to_try.extend([
                ("fm_Data", "StandaloneOSXUniversal"),
                ("fm_Data", "StandaloneOSX"),
            ])
            paths_to_try.extend([
                ("fm_Data", "StandaloneWindows64"),
                ("fm_Data", "StandaloneLinux64"),
                ("data", "StandaloneWindows64"),
            ])
        else:
            paths_to_try.extend([
                ("fm_Data", "StandaloneLinux64"),
            ])
            paths_to_try.extend([
                ("fm_Data", "StandaloneWindows64"),
                ("fm_Data", "StandaloneOSX"),
                ("fm_Data", "StandaloneOSXUniversal"),
                ("data", "StandaloneWindows64"),
            ])
        
        for data_dir, platform_dir in paths_to_try:
            bundle_path = self.fm_install_dir / data_dir / "StreamingAssets" / "aa" / platform_dir
            if bundle_path.exists():
                return bundle_path
        
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
                try:
                    tree = obj.read_typetree()
                    if isinstance(tree, dict) and tree.get('m_Name') == object_name:
                        return tree
                except Exception as e:
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
            env = UnityPy.load(str(bundle_path))
            
            for obj in env.objects:
                if obj.type.name == "MonoBehaviour":
                    obj_name = None
                    
                    original_tree = None
                    try:
                        original_tree = obj.read_typetree()
                        if isinstance(original_tree, dict):
                            obj_name = original_tree.get('m_Name')
                    except:
                        pass
                    
                    if obj_name and obj_name in objects:
                        updated_tree = objects[obj_name]
                        
                        if obj_name.startswith('AttributeColours') and original_tree:
                            import copy
                            modified_tree = copy.deepcopy(original_tree)
                            
                            if 'm_Rules' in updated_tree:
                                modified_tree['m_Rules'] = copy.deepcopy(updated_tree['m_Rules'])
                            if 'm_ComplexSelectors' in updated_tree:
                                modified_tree['m_ComplexSelectors'] = copy.deepcopy(updated_tree['m_ComplexSelectors'])
                            if 'colors' in updated_tree:
                                modified_tree['colors'] = copy.deepcopy(updated_tree['colors'])
                            
                            updated_tree = modified_tree
                        
                        if isinstance(updated_tree, dict):
                            if 'm_Rules' in updated_tree:
                                m_rules = updated_tree['m_Rules']
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
                                            if parent_key == 'm_Rules' or (parent_key is None and 'm_Rules' in path):
                                                for idx, item in enumerate(value):
                                                    if not isinstance(item, dict):
                                                        raise ValueError(
                                                            f"Found non-dict in m_Rules.Array at index {idx}: {type(item).__name__} - {str(item)[:50]}"
                                                        )
                                                    if 'm_Properties' not in item:
                                                        raise ValueError(
                                                            f"Rule at index {idx} missing m_Properties. Rule keys: {list(item.keys())}"
                                                        )
                                                    validate_structure(item, f"{path}.{key}[{idx}]", 'm_Rules')
                                            elif parent_key == 'm_ComplexSelectors' or 'm_ComplexSelectors' in path:
                                                for idx, item in enumerate(value):
                                                    if not isinstance(item, dict):
                                                        raise ValueError(
                                                            f"Found non-dict in m_ComplexSelectors.Array at index {idx}: {type(item).__name__} - {str(item)[:50]}"
                                                        )
                                                    validate_structure(item, f"{path}.{key}[{idx}]", key)
                                            elif parent_key == 'm_Values' or 'm_Values' in path:
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
                                                for idx, item in enumerate(value):
                                                    if isinstance(item, str):
                                                        if 'm_rows' in path:
                                                            continue
                                                        elif 'strings' in path.lower() or key == 'm_Name' or 'm_name' in path.lower():
                                                            continue
                                                        else:
                                                            raise ValueError(
                                                                f"Found string in array at {path}.Array[{idx}]: {item[:50]}"
                                                            )
                                                    validate_structure(item, f"{path}.{key}[{idx}]", key)
                                        else:
                                            validate_structure(value, f"{path}.{key}", key)
                                elif isinstance(obj, list):
                                    for idx, item in enumerate(obj):
                                        if isinstance(item, str):
                                            if 'm_rows' in path:
                                                continue
                                            elif 'strings' in path.lower():
                                                continue
                                            else:
                                                raise ValueError(
                                                    f"Found string in list at {path}[{idx}]: {item[:50]}"
                                                )
                                        validate_structure(item, f"{path}[{idx}]", None)
                            
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
                            
                            import json
                            try:
                                json.dumps(updated_tree)
                            except (TypeError, ValueError) as json_err:
                                raise Exception(
                                    f"Invalid data structure for {obj_name}: {json_err}. "
                                    "Structure contains non-serializable objects."
                                ) from json_err
                            
                            if 'm_Rules' in updated_tree:
                                m_rules_final = updated_tree.get('m_Rules', [])
                                if isinstance(m_rules_final, dict) and 'Array' in m_rules_final:
                                    rules_array_final = m_rules_final['Array']
                                elif isinstance(m_rules_final, list):
                                    rules_array_final = m_rules_final
                                else:
                                    rules_array_final = []
                                
                                if isinstance(rules_array_final, list):
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
                                error_str = str(e)
                                if 'm_Properties' in error_str:
                                    import json
                                    m_rules_debug = updated_tree.get('m_Rules', {})
                                    rules_debug_str = json.dumps(m_rules_debug, indent=2, default=str)
                                    
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
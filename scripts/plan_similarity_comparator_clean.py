"""
plan_similarity_comparator_clean.py

A tool to compare the similarity of two PostgreSQL execution plans in JSON format.
It evaluates structure similarity (40%) and operator similarity (60%).
This version has the `generate_difference_report` removed.
"""

from __future__ import annotations

import sys
import json
import difflib
from typing import Any, Optional

# Ensure stdout and stderr use utf-8 encoding to avoid Windows encoding errors when printing Unicode tree structures
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

STRUCTURE_WEIGHT = 0.40
OPERATOR_WEIGHT = 0.60

# Operator weights mapping query plan importance
OPERATOR_WEIGHTS: dict[str, int] = {
    "Hash Join": 15,
    "Merge Join": 15,
    "Nested Loop": 15,

    "Index Scan": 12,
    "Index Only Scan": 12,

    "Bitmap Heap Scan": 10,
    "Bitmap Index Scan": 10,

    "Seq Scan": 8,

    "Aggregate": 8,
    "Hash": 8,

    "Sort": 5,

    "Materialize": 3,
    "Memoize": 3
}

# Fallback weight for any PostgreSQL operator not explicitly listed
DEFAULT_OPERATOR_WEIGHT: int = 5


def _normalize_plan_node(plan: Any) -> Optional[dict[str, Any]]:
    """
    Robustly extract the core plan dictionary from standard PostgreSQL EXPLAIN formats.
    Handles:
    - Lists of execution plans (e.g. [{"Plan": {...}}])
    - Dictionaries containing the top-level Plan key
    - Dictionaries containing a query structure wrapper (e.g., {"plan": ...} or {"Plan": ...})
    - Dictionaries using plural "Plans" as top-level wrapper (e.g. {"Plans": [...], "Planning Time": ...})
    - Directly nested plan node dictionaries
    """
    if isinstance(plan, list):
        if not plan:
            return None
        plan = plan[0]
    
    if isinstance(plan, dict):
        if "Plan" in plan:
            inner = plan["Plan"]
            return inner if isinstance(inner, dict) else None
        if "plan" in plan:
            inner = plan["plan"]
            if isinstance(inner, list) and inner:
                inner = inner[0]
            if isinstance(inner, dict):
                if "Plan" in inner:
                    inner_plan = inner["Plan"]
                    return inner_plan if isinstance(inner_plan, dict) else None
                return inner
        if "Plans" in plan and "Node Type" not in plan:
            inner_list = plan["Plans"]
            if isinstance(inner_list, list) and inner_list:
                inner = inner_list[0]
                if isinstance(inner, dict):
                    return inner
        return plan
    
    return None


def extract_structure_signature(plan: Any) -> list[str]:
    """
    Traverse the plan recursively and generate a structural signature using preorder
    representation and LISP-style bracket boundaries.
    Ignores operator names and node types to focus solely on tree shape,
    parent-child relationships, depth, and branching factor.
    
    Example:
    ["(", "NODE", "(", "NODE", ")", "(", "NODE", ")", ")"]
    """
    if plan is not None and not isinstance(plan, (dict, list)):
        return ["(", "NODE", ")"]
        
    node = _normalize_plan_node(plan)
    if not node or not isinstance(node, dict):
        return []
    
    children = node.get("Plans", [])
    if not isinstance(children, list):
        children = []
    
    sig = ["(", "NODE"]
    for child in children:
        sig.extend(extract_structure_signature(child))
    sig.append(")")
    
    return sig


def compute_structure_similarity(plan1: Any, plan2: Any) -> float:
    """
    Compare structure signatures using SequenceMatcher to calculate a tree similarity score.
    Returns a score between 0.0 and 100.0.
    """
    sig1 = extract_structure_signature(plan1)
    sig2 = extract_structure_signature(plan2)
    
    if not sig1 and not sig2:
        return 100.0
    if not sig1 or not sig2:
        return 0.0
        
    matcher = difflib.SequenceMatcher(None, sig1, sig2)
    return matcher.ratio() * 100.0


def extract_preorder_operators(plan: Any) -> list[str]:
    """
    Traverse the plan recursively to extract preorder operator occurrences.
    """
    node = _normalize_plan_node(plan)
    if not node or not isinstance(node, dict):
        return []
    ops = []
    def _walk(curr: Any) -> None:
        if not isinstance(curr, dict):
            return
        op = curr.get("Node Type")
        if op and isinstance(op, str):
            ops.append(op)
        children = curr.get("Plans", [])
        if isinstance(children, list):
            for child in children:
                _walk(child)
    _walk(node)
    return ops


def compute_operator_similarity(plan1: Any, plan2: Any) -> float:
    """
    Compare execution operators using weighted sequence alignment.
    Returns a score between 0.0 and 100.0.
    """
    ops1 = extract_preorder_operators(plan1)
    ops2 = extract_preorder_operators(plan2)
    
    if not ops1 and not ops2:
        return 100.0
    if not ops1 or not ops2:
        return 0.0

    matcher = difflib.SequenceMatcher(None, ops1, ops2)
    matching_blocks = matcher.get_matching_blocks()
    
    matched_weight = 0.0
    for block in matching_blocks:
        for i in range(block.size):
            op = ops1[block.a + i]
            matched_weight += OPERATOR_WEIGHTS.get(op, DEFAULT_OPERATOR_WEIGHT)
            
    total_weight1 = sum(OPERATOR_WEIGHTS.get(op, DEFAULT_OPERATOR_WEIGHT) for op in ops1)
    total_weight2 = sum(OPERATOR_WEIGHTS.get(op, DEFAULT_OPERATOR_WEIGHT) for op in ops2)
    max_weight = max(total_weight1, total_weight2)
    
    if max_weight == 0.0:
        return 100.0
        
    return (matched_weight / max_weight) * 100.0


def compare_plans(plan1: Any, plan2: Any) -> dict[str, Any]:
    """
    Compare two execution plans and return structured metrics.
    The final score consists of 40% structure similarity and 60% operator similarity.
    """
    structure_score = compute_structure_similarity(plan1, plan2)
    operator_score = compute_operator_similarity(plan1, plan2)
    
    final_similarity = STRUCTURE_WEIGHT * structure_score + OPERATOR_WEIGHT * operator_score
    
    return {
        "overall_similarity": final_similarity,
        "structure_score": structure_score,
        "operator_score": operator_score
    }


def print_plan_tree(plan: Any) -> None:
    """
    Print the given plan formatted as a hierarchical text tree, displaying
    PostgreSQL optimizer statistics and optional EXPLAIN ANALYZE runtime metrics.
    """
    node = _normalize_plan_node(plan)
    if not node or not isinstance(node, dict):
        print("Empty or invalid plan.")
        return
        
    def _format_node(n: dict[str, Any]) -> str:
        if not isinstance(n, dict):
            return "?"
        nt = n.get("Node Type")
        if not nt or not isinstance(nt, str):
            nt = "?"
        extras: list[str] = []
        if "Relation Name" in n and isinstance(n["Relation Name"], str) and n["Relation Name"]:
            extras.append(f"on {n['Relation Name']}")
        if "Index Name" in n and isinstance(n["Index Name"], str) and n["Index Name"]:
            extras.append(f"using {n['Index Name']}")
        if extras:
            return f"{nt} {' '.join(extras)}"
        return nt

    def _format_stats(n: dict[str, Any], next_prefix: str) -> list[str]:
        if not isinstance(n, dict):
            return []
        est_lines = []
        if "Startup Cost" in n and "Total Cost" in n:
            est_lines.append(f"{next_prefix}(cost={n['Startup Cost']}..{n['Total Cost']})")
        if "Plan Rows" in n:
            plan_rows = n["Plan Rows"]
            if isinstance(plan_rows, (int, float)):
                if isinstance(plan_rows, float) and plan_rows.is_integer():
                    plan_rows = int(plan_rows)
            est_lines.append(f"{next_prefix}(rows={plan_rows})")
            
        act_lines = []
        if "Actual Rows" in n:
            actual_rows = n["Actual Rows"]
            if isinstance(actual_rows, (int, float)):
                if isinstance(actual_rows, float) and actual_rows.is_integer():
                    actual_rows = int(actual_rows)
            act_lines.append(f"{next_prefix}(actual rows={actual_rows})")
        if "Actual Startup Time" in n and "Actual Total Time" in n:
            act_lines.append(f"{next_prefix}(actual time={n['Actual Startup Time']}..{n['Actual Total Time']})")
            
        stats_lines = []
        if est_lines:
            stats_lines.extend(est_lines)
        if est_lines and act_lines:
            stats_lines.append(next_prefix.rstrip())
        if act_lines:
            stats_lines.extend(act_lines)
            
        return stats_lines

    def _build_lines(n: Any, prefix: str = "", is_last: bool = True, is_root: bool = False) -> list[str]:
        if not isinstance(n, dict):
            label = "?"
            if is_root:
                line = label
            else:
                connector = "└── " if is_last else "├── "
                line = f"{prefix}{connector}{label}"
            return [line]
            
        label = _format_node(n)
        if is_root:
            line = label
        else:
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{label}"
            
        lines = [line]
        children = n.get("Plans", [])
        if not isinstance(children, list):
            children = []
        
        # Determine next indentation prefix
        if is_root:
            next_prefix = ""
        else:
            next_prefix = prefix + ("    " if is_last else "│   ")
            
        # Append node statistics
        stats = _format_stats(n, next_prefix)
        lines.extend(stats)
        
        # Add visual separator lines
        if not is_root and not is_last:
            lines.append(next_prefix.rstrip())
        elif is_root and children:
            lines.append("")
            
        for i, child in enumerate(children):
            lines.extend(_build_lines(child, next_prefix, i == len(children) - 1, is_root=False))
        return lines

    lines = _build_lines(node, is_root=True)
    print("\n".join(lines))


def select_file_via_gui(title: str) -> Optional[str]:
    """
    Open a graphical file picker dialog to let the user select a JSON plan file.
    Hides the Tkinter root window and forces focus to the dialog.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()  # Hide root window
        
        # Force window focus and bring it to topmost
        root.lift()
        root.attributes("-topmost", True)
        
        file_path = filedialog.askopenfilename(
            parent=root,
            title=title,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        root.destroy()
        return file_path if file_path else None
    except Exception:
        return None


def is_list_of_plans(data: Any) -> bool:
    """
    Check if the loaded JSON data is a list of multiple PostgreSQL plan instances
    rather than a single explain execution plan.
    """
    if not isinstance(data, list):
        return False
    if not data:
        return False
        
    if isinstance(data[0], list):
        return True
        
    resolved_count = 0
    for item in data:
        if isinstance(item, dict):
            if "Plan" in item or "Node Type" in item or "plan" in item or "Plans" in item:
                resolved_count += 1
    if resolved_count == len(data):
        return True
            
    return False


def is_multiple_plans(data: Any) -> bool:
    """
    Backward-compatible alias for is_list_of_plans.
    """
    return is_list_of_plans(data)


def is_map_of_plans(data: Any) -> bool:
    """
    Check if the loaded JSON data is a dictionary mapping query names
    to execution plans.
    """
    if not isinstance(data, dict):
        return False
    if not data:
        return False
        
    if "Node Type" in data:
        return False
        
    if "Plan" in data:
        return False
        
    if "plan" in data:
        other_plan_keys = 0
        for k, val in data.items():
            if k == "plan":
                continue
            if k in ("Planning Time", "Execution Time", "PlanningTime", "ExecutionTime", "Trigger Plans", "Query Text", "Params"):
                continue
            normalized = _normalize_plan_node(val)
            if normalized is not None and "Node Type" in normalized:
                other_plan_keys += 1
        if other_plan_keys == 0:
            return False
            
    for val in data.values():
        normalized = _normalize_plan_node(val)
        if normalized is not None and "Node Type" in normalized:
            return True
            
    return False


def natural_sort_key(s: str) -> list[Any]:
    """
    Generate a sort key for sorting strings containing numbers in natural order.
    """
    import re
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def main() -> None:
    """
    CLI main function for comparing two execution plan JSON files.
    If no arguments are provided, prompts for files via a GUI picker.
    """
    file1_path: Optional[str] = None
    file2_path: Optional[str] = None

    if len(sys.argv) >= 3:
        file1_path = sys.argv[1]
        file2_path = sys.argv[2]
    else:
        print("No command-line arguments provided. Attempting to open GUI file picker...")
        file1_path = select_file_via_gui("Select PostgreSQL Plan File 1")
        if file1_path:
            print(f"Selected Plan 1: {file1_path}")
            file2_path = select_file_via_gui("Select PostgreSQL Plan File 2")
            if file2_path:
                print(f"Selected Plan 2: {file2_path}")

    if not file1_path or not file2_path:
        print("\nError: Two plan files must be specified.")
        print("Usage (CLI): python plan_similarity_comparator_clean.py <plan_file1.json> <plan_file2.json>")
        sys.exit(1)
    
    try:
        with open(file1_path, "r", encoding="utf-8") as f:
            plan1 = json.load(f)
    except Exception as e:
        print(f"Error loading {file1_path}: {e}")
        sys.exit(1)
        
    try:
        with open(file2_path, "r", encoding="utf-8") as f:
            plan2 = json.load(f)
    except Exception as e:
        print(f"Error loading {file2_path}: {e}")
        sys.exit(1)

    if isinstance(plan1, list) and len(plan1) == 1 and not (isinstance(plan2, list) and len(plan2) > 1):
        plan1 = plan1[0]
    if isinstance(plan2, list) and len(plan2) == 1 and not (isinstance(plan1, list) and len(plan1) > 1):
        plan2 = plan2[0]

    # Check if we have multiple plans comparison (lists vs lists)
    if is_list_of_plans(plan1) and is_list_of_plans(plan2):
        len1 = len(plan1)
        len2 = len(plan2)
        common_len = min(len1, len2)
        print(f"\nDetected multiple plan instances: Plan 1 has {len1} instances, Plan 2 has {len2} instances.")
        print(f"Comparing the first {common_len} corresponding instances...\n")
        
        overall_scores = []
        structure_scores = []
        operator_scores = []
        
        for idx in range(common_len):
            inst1 = plan1[idx]
            inst2 = plan2[idx]
            result = compare_plans(inst1, inst2)
            
            overall_scores.append(result["overall_similarity"])
            structure_scores.append(result["structure_score"])
            operator_scores.append(result["operator_score"])
            
            print(f"--- Instance {idx + 1} Comparison ---")
            print(f"Overall Similarity : {result['overall_similarity']:.1f}%")
            print(f"Structure Score    : {result['structure_score']:.1f}%")
            print(f"Operator Score     : {result['operator_score']:.1f}%")
            print()
            
        # Print summary statistics across all compared instances
        avg_overall = sum(overall_scores) / common_len
        avg_struct = sum(structure_scores) / common_len
        avg_op = sum(operator_scores) / common_len
        
        print("=====================================")
        print("MULTIPLE PLANS COMPARISON SUMMARY")
        print(f"Compared Instances : {common_len}")
        print(f"Average Similarity : {avg_overall:.1f}%")
        print(f"Average Structure  : {avg_struct:.1f}%")
        print(f"Average Operator   : {avg_op:.1f}%")
        print("=====================================\n")
        return

    # Check if we have map of plans comparison (dict vs dict query catalog)
    elif is_map_of_plans(plan1) and is_map_of_plans(plan2):
        raw_common_keys = sorted(list(set(plan1.keys()) & set(plan2.keys())), key=natural_sort_key)
        
        common_keys = []
        for key in raw_common_keys:
            v1 = plan1[key]
            v2 = plan2[key]
            n1 = _normalize_plan_node(v1[0] if isinstance(v1, list) and v1 else v1)
            n2 = _normalize_plan_node(v2[0] if isinstance(v2, list) and v2 else v2)
            
            if (n1 is not None and "Node Type" in n1) or (n2 is not None and "Node Type" in n2):
                common_keys.append(key)
                
        len1 = len([k for k, v in plan1.items() if _normalize_plan_node(v[0] if isinstance(v, list) and v else v) and "Node Type" in _normalize_plan_node(v[0] if isinstance(v, list) and v else v)])
        len2 = len([k for k, v in plan2.items() if _normalize_plan_node(v[0] if isinstance(v, list) and v else v) and "Node Type" in _normalize_plan_node(v[0] if isinstance(v, list) and v else v)])
        
        print(f"\nDetected query plan catalog maps: Plan 1 has {len1} valid queries, Plan 2 has {len2} valid queries.")
        
        if not common_keys:
            print("\nError: No common queries found between the two query plan catalogs.")
            print(f"Plan 1 keys: {', '.join(sorted(plan1.keys(), key=natural_sort_key))}")
            print(f"Plan 2 keys: {', '.join(sorted(plan2.keys(), key=natural_sort_key))}")
            sys.exit(1)
            
        print(f"Comparing the {len(common_keys)} corresponding query plans...\n")
        
        overall_scores = []
        structure_scores = []
        operator_scores = []
        
        for key in common_keys:
            inst1 = plan1[key]
            inst2 = plan2[key]

            inst1_runs = inst1 if (isinstance(inst1, list) and len(inst1) > 1) else [inst1]
            inst2_runs = inst2 if (isinstance(inst2, list) and len(inst2) > 1) else [inst2]

            if len(inst1_runs) > 1 or len(inst2_runs) > 1:
                run_count = min(len(inst1_runs), len(inst2_runs))
                if len(inst1_runs) != len(inst2_runs):
                    print(f"  [Note] Query '{key}': file 1 has {len(inst1_runs)} run(s), "
                          f"file 2 has {len(inst2_runs)} run(s). Comparing the first {run_count} run(s).")

                run_overall, run_struct, run_op = [], [], []
                for run_idx in range(run_count):
                    r = compare_plans(inst1_runs[run_idx], inst2_runs[run_idx])
                    run_overall.append(r["overall_similarity"])
                    run_struct.append(r["structure_score"])
                    run_op.append(r["operator_score"])
                    print(f"--- Query '{key}' Run {run_idx + 1} Comparison ---")
                    print(f"Overall Similarity : {r['overall_similarity']:.1f}%")
                    print(f"Structure Score    : {r['structure_score']:.1f}%")
                    print(f"Operator Score     : {r['operator_score']:.1f}%")
                    print()

                q_overall = sum(run_overall) / run_count
                q_struct  = sum(run_struct)  / run_count
                q_op      = sum(run_op)      / run_count
                print(f"  → Query '{key}' average across {run_count} run(s): "
                      f"Overall {q_overall:.1f}% | Structure {q_struct:.1f}% | Operator {q_op:.1f}%")
                print()
            else:
                result = compare_plans(inst1, inst2)
                q_overall = result["overall_similarity"]
                q_struct  = result["structure_score"]
                q_op      = result["operator_score"]
                print(f"--- Query '{key}' Comparison ---")
                print(f"Overall Similarity : {q_overall:.1f}%")
                print(f"Structure Score    : {q_struct:.1f}%")
                print(f"Operator Score     : {q_op:.1f}%")
                print()

            overall_scores.append(q_overall)
            structure_scores.append(q_struct)
            operator_scores.append(q_op)
            
        # Print summary statistics across all compared queries
        avg_overall = sum(overall_scores) / len(common_keys)
        avg_struct = sum(structure_scores) / len(common_keys)
        avg_op = sum(operator_scores) / len(common_keys)
        
        print("=====================================")
        print("MULTIPLE PLANS COMPARISON SUMMARY")
        print(f"Compared Queries   : {len(common_keys)}")
        print(f"Average Similarity : {avg_overall:.1f}%")
        print(f"Average Structure  : {avg_struct:.1f}%")
        print(f"Average Operator   : {avg_op:.1f}%")
        print("=====================================\n")
        return
        
    elif is_list_of_plans(plan1) or is_list_of_plans(plan2) or is_map_of_plans(plan1) or is_map_of_plans(plan2):
        print("\nError: Mismatched input formats.")
        print("Ensure both files contain single plans, both contain lists, or both contain query catalogs.")
        sys.exit(1)

    # Output plan trees for visual comparison
    print("\nPLAN 1 TREE:")
    print_plan_tree(plan1)
    
    print("\nPLAN 2 TREE:")
    print_plan_tree(plan2)
    
    # Compute similarity and print report
    result = compare_plans(plan1, plan2)
    
    print("\n=====================================")
    print("PLAN SIMILARITY REPORT")
    print(f"Overall Similarity : {result['overall_similarity']:.1f}%")
    print(f"Structure Score    : {result['structure_score']:.1f}%")
    print(f"Operator Score     : {result['operator_score']:.1f}%")
    print("=====================================\n")


if __name__ == "__main__":
    main()

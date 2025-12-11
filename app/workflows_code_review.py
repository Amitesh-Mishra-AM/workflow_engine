from typing import Any, Dict, List, Tuple, Optional
import time


State = Dict[str, Any]


def _get_code_and_init_state(state: State) -> State:
    code = state.get("code", "")
    state.setdefault("lines", code.splitlines())
    state.setdefault("functions", [])
    state.setdefault("complexity_score", 0)
    state.setdefault("issue_count", 0)
    state.setdefault("suggestions", [])
    state.setdefault("quality_score", 0)
    state.setdefault("threshold", 80)
    state.setdefault("loop_count", 0)
    state.setdefault("max_loops", 5)
    return state


def node_extract_functions(state: State) -> State:
    state = _get_code_and_init_state(state)
    functions: List[str] = []
    for line in state["lines"]:
        stripped = line.strip()
        if stripped.startswith("def ") and "(" in stripped and ")" in stripped:
            name = stripped.split("def ", 1)[1].split("(", 1)[0].strip()
            functions.append(name)
    state["functions"] = functions
    return state

def node_check_complexity(state: State) -> State:
    state = _get_code_and_init_state(state)
    num_lines = len(state["lines"])
    num_funcs = len(state["functions"])

    complexity = num_lines + num_funcs * 5
    state["complexity_score"] = complexity
    return state


def node_detect_issues(state: State) -> State:
    state = _get_code_and_init_state(state)
    time.sleep(2) # adding a fake sleep time to show a fake delay 
    issues = 0

    for line in state["lines"]:
        if len(line) > 80:
            issues += 1
        if "TODO" in line:
            issues += 1
        if "print(" in line:
            issues += 1

    state["issue_count"] = issues
    return state


def node_suggest_improvements(state: State) -> State:
    state = _get_code_and_init_state(state)
    suggestions: List[str] = []

    complexity = state.get("complexity_score", 0)
    issues = state.get("issue_count", 0)

    if complexity > 100:
        suggestions.append("Reduce function sizes or split logic into smaller helpers.")
    if issues > 0:
        suggestions.append("Fix code smells such as long lines, TODOs, and print statements.")
    if not suggestions:
        suggestions.append("Code looks good. Minor refactoring only if needed.")

    quality = 100
    quality -= max(0, complexity - 50) // 2
    quality -= issues * 5

    loop_count = state.get("loop_count", 0)
    quality += loop_count * 3

    quality = max(0, min(100, quality))

    state["suggestions"] = suggestions
    state["quality_score"] = quality
    return state


def node_evaluate_quality(state: State) -> Tuple[State, Optional[str]]:
    state = _get_code_and_init_state(state)
    threshold = state.get("threshold", 80)
    quality = state.get("quality_score", 0)
    loop_count = state.get("loop_count", 0)
    max_loops = state.get("max_loops", 5)

    if quality < threshold and loop_count < max_loops:
        state["loop_count"] = loop_count + 1
        next_node = "suggest_improvements"
    else:
        next_node = "finish"

    return state, next_node


def node_finish(state: State) -> State:
    # Final node – just returns state.
    return state

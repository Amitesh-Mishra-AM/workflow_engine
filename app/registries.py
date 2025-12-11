from typing import Any, Callable, Dict

from .workflows_code_review import(
    node_extract_functions,
    node_check_complexity,
    node_detect_issues,
    node_suggest_improvements,
    node_evaluate_quality,
    node_finish,
)

State=Dict[str, Any]
NodeFunc=Callable[..., Any]

NODE_REGISTRY:Dict[str, NodeFunc]={
    "extract_functions":node_extract_functions,
    "check_complexity":node_check_complexity,
    "detect_issues":node_detect_issues,
    "suggest_improvements":node_suggest_improvements,
    "evaluate_quality":node_evaluate_quality,
    "finish":node_finish,
}

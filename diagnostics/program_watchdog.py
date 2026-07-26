from diagnostics.program_error_recorder import record_error


def report_missing_resource(module: str, resource_type: str, path: str):
    message = f"Missing {resource_type}: {path}"
    record_error(
        module=module,
        function="resource_check",
        line=0,
        error_type="MissingResource",
        message=message,
        traceback=None,
        severity="warning",
    )


def report_runaway_loop(module: str, function: str, line: int):
    message = "Runaway loop detected — fail-safe triggered"
    record_error(
        module=module,
        function=function,
        line=line,
        error_type="RunawayLoop",
        message=message,
        traceback=None,
        severity="critical",
    )

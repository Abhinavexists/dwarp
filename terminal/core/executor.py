import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ResponseType(Enum):
    SHELL_COMMAND = "shell_command"
    GENERAL_QUERY = "general_query"
    CODE_GENERATION = "code_generation"
    EXPLANATION = "explanation"

@dataclass
class CommandResponse:
    command: str
    explanation: str
    response_type: ResponseType = ResponseType.SHELL_COMMAND

@dataclass
class GeneralResponse:
    content: str
    response_type: ResponseType = ResponseType.GENERAL_QUERY
    action_required: bool = False
    suggested_command: Optional[str] = None

def run_command(command: str, cwd: str | None = None) -> tuple[str, bool]:
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            cwd=cwd,
            capture_output=True
        )
        return result.stdout if result.stdout else "Command executed successfully", True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else f"Command failed with exit code {e.returncode}"
        return error_msg, False
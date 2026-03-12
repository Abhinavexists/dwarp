import os
import re

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from terminal.core.executor import CommandResponse, GeneralResponse, run_command
from terminal.core.agent import process_request
from terminal.safety import check_command_safety
from terminal.commands import check_shell_command
from terminal.utils.loading import LoadingAnimation

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import FuzzyWordCompleter

console = Console()

HISTORY_FILE = os.path.expanduser("~/.dwarp_history")
_OLD_HISTORY_FILE = os.path.expanduser("~/.terminal_history") # Legacy history file from older versions

if os.path.exists(_OLD_HISTORY_FILE) and not os.path.exists(HISTORY_FILE):
    os.rename(_OLD_HISTORY_FILE, HISTORY_FILE)


def load_previous_commands():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as file:
        return list(set([line.strip() for line in file if line.strip()]))


def save_command(cmd: str):
    with open(HISTORY_FILE, "a") as file:
        file.write(cmd + "\n")


PLACEHOLDER_PATTERNS = [
    r"<[^>]+>",
    r"\b(old|new)[-_]?(file|filename|path|dir)\b",
    r"\b(source|destination)[-_ ]?(file|directory|dir|path)\b",
    r"\bYOUR[_-]?(FILE|PATH|DIR|BRANCH|REPO)\b",
]


def placeholders(cmd: str) -> bool:
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, cmd, flags=re.IGNORECASE):
            return True
    return False


def edit_command(suggested: str) -> str:
    print(f"[cyan]Current command:[/cyan] {suggested}")
    print("[magenta]Edit the command (press Enter to keep as is):[/magenta]")
    edited = input("> ").strip()
    return edited if edited else suggested


def handle_cd(command: str, current_dir: str) -> tuple[bool, str]:
    parts = command.strip().split()
    if not parts or parts[0] != "cd":
        return False, current_dir

    target = parts[1] if len(parts) > 1 else os.path.expanduser("~")
    target = os.path.expanduser(target)

    if not os.path.isabs(target):
        target = os.path.normpath(os.path.join(current_dir, target))

    if not os.path.isdir(target):
        print(f"[red]cd: no such directory: {target}[/red]")
        return True, current_dir

    return True, target


def handle_shell_command(result: CommandResponse, current_dir: str) -> str:
    """Handle shell command responses."""
    print(f"\n[cyan]Command:[/cyan] {result.command}")
    print(f"[yellow]Explanation:[/yellow] {result.explanation}")

    final_cmd = result.command

    # Special-case clear/cls to avoid printing raw ANSI sequences
    if final_cmd.strip().lower() in {"clear", "cls"}:
        console.clear()
        return current_dir

    if placeholders(final_cmd):
        print("[yellow]Please edit before execution:[/yellow]")
        final_cmd = edit_command(final_cmd)
    else:
        opt = input("Edit command before executing? [y/N]: ").strip().lower()
        if opt == "y":
            final_cmd = edit_command(final_cmd)

    if check_command_safety(final_cmd):
        print("\n[green]Command approved! Executing...[/green]")
        output, success = run_command(final_cmd, cwd=current_dir)
        print(output)
        if success:
            save_command(final_cmd)
        else:
            print("[red]Command failed to execute[/red]")
        return current_dir
    else:
        print("[blue]Command rejected by user[/blue]")
        return current_dir


def handle_general_response(result: GeneralResponse):
    """Handle general query responses."""
    print("\n[bold blue]Response:[/bold blue]")

    if "```" in result.content or "**" in result.content or "##" in result.content:
        console.print(Markdown(result.content))
    else:
        print(result.content)

    if result.action_required and result.suggested_command:
        print(f"\n[cyan]Suggested Command:[/cyan] {result.suggested_command}")
        opt = input("Execute this command? [y/N]: ").strip().lower()
        if opt == "y":
            return result.suggested_command
    return None


def main():
    print("[bold green]dwarp[/bold green]")
    print("Type your request (type 'exit' to quit)")
    print("Examples: 'install docker', 'what is Python?', 'write a hello world script'\n")

    history = FileHistory(HISTORY_FILE)
    previous_cmds = load_previous_commands()
    session = PromptSession(history=history)

    current_dir = os.getcwd()

    while True:
        completer = FuzzyWordCompleter(previous_cmds)
        try:
            user_input = session.prompt(f"{current_dir} > ", completer=completer).strip()
        except KeyboardInterrupt:
            print("\n[blue]Use 'exit' to quit[/blue]")
            continue
        except EOFError:
            break

        if user_input.lower() in {"exit", "quit"}:
            break

        if not user_input:
            continue

        handled, current_dir = handle_cd(user_input, current_dir)
        if handled:
            continue

        # Special-case clear/cls entered directly by the user
        if user_input.strip().lower() in {"clear", "cls"}:
            console.clear()
            previous_cmds.append(user_input)
            save_command(user_input)
            continue

        if check_shell_command(user_input):
            output, success = run_command(user_input, cwd=current_dir)
            if success:
                print(output)
                save_command(user_input)
                previous_cmds.append(user_input)
            continue

        try:
            loading_animation = LoadingAnimation("Thinking")
            loading_animation.start()
            try:
                result = process_request(user_input, current_dir)
            finally:
                loading_animation.stop()

            if isinstance(result, CommandResponse):
                current_dir = handle_shell_command(result, current_dir)
            elif isinstance(result, GeneralResponse):
                suggested_cmd = handle_general_response(result)
                if suggested_cmd:
                    output, success = run_command(suggested_cmd, cwd=current_dir)
                    print("\n[green]Executing suggested command...[/green]")
                    print(output)
                    if success:
                        save_command(suggested_cmd)
                        previous_cmds.append(suggested_cmd)

        except Exception as e:
            print(f"[red]Error generating response:[/red] {e}")
            print("[yellow]Try rephrasing your request[/yellow]")


if __name__ == "__main__":
    main()

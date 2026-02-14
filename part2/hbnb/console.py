"""Simple command-line console for HBNB Part 2.

Usage:
  python3 -m hbnb.console

Commands:
  create <ClassName> <json_payload?>   Create an instance, prints id
  show <ClassName> <id>                Show instance JSON
  destroy <ClassName> <id>             Delete instance
  all [ClassName]                      List instances
  update <ClassName> <id> <json|key=value>  Update instance
  count <ClassName>                    Count instances
  quit / EOF                           Exit
"""
from __future__ import annotations

import cmd
import shlex
import json
from typing import Any

from .persistence.in_memory_repository import InMemoryRepository
from .business.facade import HBNBFacade, NotFoundError, ValidationError


class HBNBCommand(cmd.Cmd):
    intro = "Welcome to HBNB console. Type help or ? to list commands."
    prompt = "(hbnb) "

    def __init__(self):
        super().__init__()
        self._repo = InMemoryRepository()
        self._facade = HBNBFacade(self._repo)

    def do_create(self, arg: str) -> None:
        """create <ClassName> [json_payload] -- create an instance and print id"""
        if not arg:
            print("** class name missing **")
            return
        parts = shlex.split(arg, posix=True)
        cls = parts[0]
        payload = {}
        if len(parts) > 1:
            rest = arg[len(cls) :].strip()
            try:
                payload = json.loads(rest)
            except Exception:
                print("** payload must be valid JSON object **")
                return
        obj = self._facade.create(cls, payload)
        print(obj.get("id"))

    def do_show(self, arg: str) -> None:
        """show <ClassName> <id> -- display an instance"""
        parts = shlex.split(arg)
        if len(parts) < 2:
            print("** class name or id missing **")
            return
        cls, obj_id = parts[0], parts[1]
        try:
            obj = self._facade.get(cls, obj_id)
            print(json.dumps(obj, indent=2))
        except NotFoundError as e:
            print(f"** {e} **")

    def do_destroy(self, arg: str) -> None:
        """destroy <ClassName> <id> -- delete an instance"""
        parts = shlex.split(arg)
        if len(parts) < 2:
            print("** class name or id missing **")
            return
        cls, obj_id = parts[0], parts[1]
        try:
            self._facade.delete(cls, obj_id)
        except NotFoundError as e:
            print(f"** {e} **")

    def do_all(self, arg: str) -> None:
        """all [ClassName] -- list all instances or instances of ClassName"""
        parts = shlex.split(arg)
        if parts:
            items = self._facade.list(parts[0])
            print(json.dumps(items, indent=2))
            return
        all_items = self._facade.list_all()
        print(json.dumps(all_items, indent=2))

    def do_update(self, arg: str) -> None:
        """update <ClassName> <id> <json|key=value> -- update an instance"""
        parts = shlex.split(arg)
        if len(parts) < 3:
            print("** class name, id or attributes missing **")
            return
        cls, obj_id = parts[0], parts[1]
        rest = arg.split(None, 2)[2]
        updates: dict[str, Any] = {}
        # try JSON first
        try:
            updates = json.loads(rest)
        except Exception:
            # parse key=value pairs
            try:
                for token in shlex.split(rest):
                    if "=" in token:
                        k, v = token.split("=", 1)
                        # strip quotes
                        if v.startswith("\"") and v.endswith("\""):
                            v = v[1:-1]
                        updates[k] = v
            except Exception:
                print("** attributes must be JSON or key=value pairs **")
                return
        try:
            obj = self._facade.update(cls, obj_id, updates)
            print(json.dumps(obj, indent=2))
        except NotFoundError as e:
            print(f"** {e} **")
        except ValidationError as e:
            print(f"** {e} **")

    def do_count(self, arg: str) -> None:
        """count <ClassName> -- return number of instances for ClassName"""
        parts = shlex.split(arg)
        if not parts:
            print("** class name missing **")
            return
        print(self._facade.count(parts[0]))

    def do_quit(self, arg: str) -> bool:
        """Quit the console."""
        return True

    def do_EOF(self, arg: str) -> bool:
        print()
        return True


def main() -> None:
    HBNBCommand().cmdloop()


if __name__ == "__main__":
    main()

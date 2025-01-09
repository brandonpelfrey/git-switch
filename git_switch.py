#!/usr/bin/env python3

import argparse
import dataclasses
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, List

@dataclass
class Persona:
    persona_name: str
    commit_name: str
    email: str
    ssh_key_path: str

@dataclass
class Config:
    current_persona: str
    personas: Dict[str, Persona]

class Manager:
    '''
    Config is a class that manages the personas configuration file. Config
    is serialized to json and stored in the user's home local config directory.
    '''
    config: Config

    def __init__(self, config_file_path: Path):
        self.config_file_path = config_file_path

    def has_persona(self, persona_name: str) -> bool:
        return persona_name in self.config.personas

    def get_persona(self, persona_name: str) -> Persona:
        return self.config.personas[persona_name]

    def set_persona(self, persona: Persona):
        self.config.personas[persona.persona_name] = persona

    def switch_persona(self, persona_name: str, _global: bool = False):
        if persona_name not in self.config.personas:
            raise ValueError(f'Persona {persona_name} not found')
        self.config.current_persona = persona_name
        persona = self.config.personas[persona_name]
        
        import os
        _global = '--global' if _global else ''
        os.system(f'git config {_global} user.name "{persona.commit_name}"')
        os.system(f'git config {_global} user.email "{persona.email}"')
        os.system(f'git config {_global} core.sshCommand "ssh -i {persona.ssh_key_path}"')

    def get_current_persona(self) -> Persona | None:
        if not self.config.current_persona:
            return None
        return self.config.personas[self.config.current_persona]
    
    def rename_persona(self, old_name: str, new_name: str):
        persona = self.config.personas[old_name]
        del self.config.personas[old_name]
        persona.persona_name = new_name
        self.config.personas[new_name] = persona

    def remove_persona(self, persona_name: str):
        del self.config.personas[persona_name]
    
    def list_personas(self) -> List[Persona]:
        return sorted(list(self.config.personas.values()), key=lambda p: p.persona_name)

    def __enter__(self):
        # Catch all errors print general message
        try:
            with self.config_file_path.open() as f:
                _dict = json.load(f)
                self.config = Config(_dict['current_persona'], {})
                for persona_dict in _dict['personas'].values():
                    persona = Persona(**persona_dict)
                    self.config.personas[persona.persona_name] = persona
        except Exception as e:
            self.config = Config(None, {})
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_file_path.open('w') as f:
            json.dump(dataclasses.asdict(self.config), f, indent=2)

def main():
    '''
    git-switch is a tool for managing git personas. It allows you to easily switch
    between different SSH keys, usernames, and email addresses. It has the following
    sub-commands:
      --add
      --list
      --remove

    By default, with no sub-command, it will list the current persona.
    By default, with a persona provided, it will switch to that persona.
    '''

    parser = argparse.ArgumentParser(description='Manage git personas')

    # add/list/remove are subcommands, not -- options
    subparsers = parser.add_subparsers(dest='subcommand', required=False)
    subparsers.add_parser('add', help='Add a new persona')
    subparsers.add_parser('list', help='List all personas')
    subparsers.add_parser('remove', help='Remove a persona')

    become_parser = subparsers.add_parser('become', help='Switch to another persona')
    become_parser.add_argument('persona', help='The persona to switch to')
    become_parser.add_argument('--global', dest='_global', action='store_true', help='Set the persona globally')

    rename_parser = subparsers.add_parser('rename', help='Rename a persona')
    rename_parser.add_argument('old_name', help='The old name of the persona')
    rename_parser.add_argument('new_name', help='The new name of the persona')

    args = parser.parse_args()

    config_path = Path.home() / '.config' / 'git-switch.json'
    with Manager(config_path) as manager:
        if args.subcommand == 'add':
            print('Adding a new persona ...')
            persona_name = input('Persona name: ')
            commit_name = input('Commit Author name: ')
            email = input('Commit Author Email address: ')
            ssh_key_path = input('SSH key path: ')
            
            persona = Persona(persona_name, commit_name, email, ssh_key_path)
            manager.set_persona(persona)
            print('Persona added')

        elif args.subcommand == 'list':
            for persona in manager.list_personas():
                print(f'{persona.persona_name}: {persona.commit_name} <{persona.email}>')

        elif args.subcommand == 'remove':
            persona_name = input('Persona name: ')
            if not manager.has_persona(persona_name):
                print(f"Persona '{persona_name}' not found")
                return
            manager.remove_persona(persona_name)
            print(f"Removed persona '{persona_name}'")
        
        elif args.subcommand == 'rename':
            old_name = input('Old persona name: ')
            new_name = input('New persona name: ')

            if not manager.has_persona(old_name):
                print(f"Persona '{old_name}' not found")
                return
            manager.rename_persona(old_name, new_name)
            print(f"Renamed persona '{old_name}' to '{new_name}'")

        elif args.subcommand == 'become':
            try:
                manager.switch_persona(args.persona, _global=args._global)
                print(f'Switched to persona {args.persona}')
            except ValueError:
                print(f'Persona {args.persona} not found')

        else:
            current = manager.get_current_persona()
            if current and manager.has_persona(current.persona_name):
                print('Currently using persona:', current.persona_name)
            else:
                print('No persona set')

if __name__ == '__main__':
    main()

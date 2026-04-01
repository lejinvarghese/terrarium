#!/usr/bin/env python3
"""Landscape management CLI"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.landscapes import list_landscapes, list_active_landscapes


def cmd_list():
    """List all landscapes"""
    landscapes = list_landscapes()
    if not landscapes:
        print('No landscapes found.')
        return

    print('\n🌿 Terrarium Landscapes\n')

    for lid, config in landscapes.items():
        active = '✓' if config.get('active', False) else ' '
        print(f'[{active}] {lid}')
        print(f'    Name: {config["name"]}')
        print(f'    Culture: {config["culture"]}')
        if 'aesthetic' in config:
            print(f'    Aesthetic: {config["aesthetic"]}')
        if 'priorities' in config:
            priorities = ', '.join(config['priorities'])
            print(f'    Priorities: {priorities}')
        print()


def cmd_status():
    """Show active landscapes with details"""
    active = list_active_landscapes()
    if not active:
        print('No active landscapes.')
        return

    print(f'\n🌱 Active Landscapes: {len(active)}\n')

    for lid, config in active.items():
        print(f'{lid}')
        print(f'  Path: {config["path"]}')

        # Check for bots
        bots_path = config['path'] / 'bots'
        if bots_path.exists():
            bot_files = list(bots_path.glob('*.md'))
            print(f'  Bots: {len(bot_files)}')

        # Check for incubator
        incubator_path = config['path'] / 'incubator'
        if incubator_path.exists():
            print(f'  Incubator: ✓')

        print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: landscapes.py {list|status}')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        cmd_list()
    elif command == 'status':
        cmd_status()
    else:
        print(f'Unknown command: {command}')
        print('Usage: landscapes.py {list|status}')
        sys.exit(1)

# Study Time

**A College Student's Final Exam Dream RPG**

## Description

Study Time is an action RPG roguelike where you play as a college student who fell asleep while studying for finals. In your dream, you must fight through 10 floors of nightmarish challenges, battling personifications of academic concepts from your hardest classes.

## Storyline

You are a college student cramming for your final exams. Exhausted, you fall asleep at your desk... and find yourself in a dream world where academic principles have come to life as fearsome enemies. Fight your way through this nightmare to wake up!

## Gameplay Features

### Classes & Difficulty
- **Select 2-4 subjects** from: Math, Computer Science, Physics, Chemistry, Biology, History
- **Choose difficulty**: Freshman → Sophomore → Junior → Senior → Graduate
- Higher difficulties multiply enemy health and damage
- Later floors (7-9) have 1.5x multiplier
- Final boss has 2x multiplier

### Player Abilities
- **Movement**: WASD keys
- **Attack**: Space bar - Melee attacks with combo system
- **Dash**: Shift - Quick dodge with invulnerability frames
- **Parry**: C - Perfectly timed blocks reflect damage
- **Ultimate**: Q - Berserk mode with massive damage boost

### Combat Systems
- **Combo Counter**: Chain hits together for bonus damage
- **Critical Hits**: Random chance for 2x damage
- **Poison Debuff**: Some enemies apply damage-over-time
- **Enemy Variety**: Melee, ranged, and magic enemy types

### Progression
- **10 Floors**: Navigate through halls, classrooms, and boss rooms
- **Floor 5**: Mini-boss checkpoint
- **Floor 6**: Rest stop to heal and upgrade
- **Floor 10**: Final exam boss battle
- **Upgrades**: Increase damage and movement speed at rest stops

## Enemies

### Math Enemies
- **Swordsman**: Melee fighter with linear blade that grows in power
- **Archer**: Ranged attacker with defensive shield

### Computer Science Enemies
- **Binary Blade**: Fast melee with consecutive hit bonuses
- **Bug Swarm**: Ranged with homing projectiles

### Physics Enemies
- **Kinetic Brute**: Tank that absorbs and releases damage
- **Gravity Manipulator**: Shoots orbiting projectiles

### Chemistry Enemies
- **Acidic Alchemist**: Applies poison debuff on hit

### Biology Enemies (NEW!)
- **Poison Mite**: Small, fast melee that applies poison damage-over-time
- **Bio Engineer**: Ranged support that shoots poison projectiles

### History Enemies (NEW!)
- **Ancient Warrior**: Heavily armored with shield bash stun ability
- **Artillery Commander**: Long-range cannon fire attacks

## Controls

- **WASD**: Move
- **Space**: Attack
- **Shift**: Dash
- **C**: Parry
- **Q**: Ultimate Ability
- **E**: Interact (doors, upgrades)
- **ESC**: Pause/Exit

## Requirements

- Python 3.7+
- pygame 2.5.2+

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Planned Features

- 9 more enemy class types (Astronomy, Business, Geology, Music, Health, Psychology, Engineering, Art, Communication)
- Player class system (Procrastinator, Early Bird, Befriender, Cheater)
- Weapon variety and rarity system
- Enhanced debuff system (stun, slow, confusion, etc.)
- Loot drops and equipment upgrades
- Sound effects and music

## Recent Improvements (v0.2)

- Fixed critical memory leak with projectile cleanup
- Fixed float comparison issues causing timer bugs
- Cached fonts for better performance
- Applied difficulty scaling properly to all enemies
- Added Biology enemy class with poison mechanics
- Added History enemy class with armor and cannons
- Enhanced HUD with poison status display
- Improved class selection UI to support 6 classes

## Development

This game is actively being developed and improved. Check the Gameplan.txt for the full design vision!

## Credits

Created as a college dream simulator RPG.

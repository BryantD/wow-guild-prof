# WoW Guild Professions List

This is a quick and dirty Python script to generate a professions list
for a guild site. It produces Markdown intended for use with
[Hugo](https://gohugo.io); if you know some python you could tweak it to
produce something else. Or you could send me a merge request that adds
Jinja templates!

## Requirements

* Python 3 (python-blizzardapi)

## Installation 

1. Download this repo to somewhere convenient 
    1. git clone https://github.com/BryantD/wow-guild-prof.git
    1. Or just snag it manually, whatever
1. Install dependencies
    1. pip3 install -r requirements.txt
1. Generate a set of Blizzard API tokens [here](https://develop.battle.net/access/clients) (you must have a Blizzard account)
1. Copy wow-guild-example.conf to wow-guild.conf
1. Edit wow-guild.conf to include your API tokens, your guild name, and anything else you want to change 

## Usage

wow-guild-prof.py [-h] [-c CONFIG] [-o OUTPUT]

All arguments are optional. By default, wow-guild-prof.py looks for a config file 
in the working directory called wow-guild.conf and prints output to stdout.

## Example

Our crafting list is [here](https://wow.distancinglikepros.com/posts/shadowlands-crafting/).

## Potential Improvements

This script doesn't know about item tiers (e.g., Shadowlands legendaries).
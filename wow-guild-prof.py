#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3

# The MIT License (MIT)
#
# Copyright (c) 2021 Bryant Durrell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from blizzardapi import BlizzardApi
from datetime import datetime
import configparser
import argparse
import sys
import pprint


def get_config(config_name):
    sections_expected = ["api", "general", "professions", "exclude"]
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = lambda option: option
    try:
        config.read(config_name)
    except:
        raise SystemExit(f"Config error: unable to parse {config_name}")

    for section in sections_expected:
        if not section in config.sections():
            raise SystemExit(f"Config error: {section} section not found")

    # Little bit of text munging because people will inevitably miss the way you
    # need to format names.

    for token in ["guild", "server"]:
        config["general"][token] = config["general"][token].replace(" ", "-").lower()

    return config


def get_arguments():
    parser = argparse.ArgumentParser()

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        dest="config",
        default="wow-guild.conf",
        help="Config file",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output",
        help="Output file (stdout if not specified)",
    )

    args = parser.parse_args()
    return args


def get_item_from_recipe(api_client, config, recipe_id):
    item_data = api_client.wow.game_data.get_recipe(
        config["general"]["region"], config["general"]["locale"], recipe_id
    )
    return item_data["crafted_item"]["id"]


def get_profession_data(api_client, config, guild_profession_data, character_slug):
    character_profession_data = (
        api_client.wow.profile.get_character_professions_summary(
            config["general"]["region"],
            config["general"]["locale"],
            config["general"]["server"],
            character_slug,
        )
    )

    if "primaries" in character_profession_data.keys():
        for profession in character_profession_data["primaries"]:
            for tier in profession["tiers"]:
                tier_name = tier["tier"]["name"]
                if tier_name in guild_profession_data.keys():
                    for recipe in tier["known_recipes"]:
                        if recipe["name"] not in guild_profession_data[tier_name].keys():

                            if "Enchanting" in tier_name:
                                item_id = recipe["id"]
                            else:
                                item_id = get_item_from_recipe(
                                    api_client, config, recipe["id"]
                                )
                            guild_profession_data[tier_name][recipe["name"]] = {
                                "id": item_id,
                                "chars": [],
                            }
                        guild_profession_data[tier_name][recipe["name"]]["chars"].append(
                            character_slug
                        )

    return guild_profession_data


def print_profession_table(profession_data, exclude_list):

    base_url = "https://www.wowhead.com/item="
    base_enchanting_url = "https://www.wowhead.com/recipe/"

    for profession in profession_data:
        if profession_data[profession]:
            print(f"## {profession}")
            print(f"Recipe |Crafters  |")
            print(f":------|:---------|")

            for recipe in sorted(profession_data[profession].keys()):
                if not recipe in exclude_list:
                    crafters = [
                        char.capitalize()
                        for char in profession_data[profession][recipe]["chars"]
                    ]
                    crafters.sort()
                    if "Enchanting" in profession:
                        item_url = f'{base_enchanting_url}{profession_data[profession][recipe]["id"]}'
                    else:
                        item_url = (
                            f'{base_url}{profession_data[profession][recipe]["id"]}'
                        )
                    print(f'[{recipe}]({item_url}) |{", ".join(crafters)} |')

            print(f"")


def print_header(config):
    title = config["general"]["page_title"]
    summary = config["general"]["page_summary"]

    print(f"---")
    print(f'title: "{title}"')
    print(f"draft: false")
    print(f"date: {datetime.now()}")
    print(f"summary: {summary}")
    print(f"---")
    print(f"")


def main():
    args = get_arguments()
    if args.output:
        try:
            output_file = open(args.output, mode="w")
        except:
            raise SystemExit(f"File error: couldn't open {args.output} for writing")
        sys.stdout = output_file

    config = get_config(args.config)

    exclude_list = config.options("exclude")
    guild_profession_data = {}
    for profession_tier in config.options("professions"):
        guild_profession_data[profession_tier] = {}

    api_client = BlizzardApi(config["api"]["client_id"], config["api"]["client_secret"])
    # Failed API initialization doesn't throw an exception, so we catch this when we
    # try to get guild info

    try:
        guild_data = api_client.wow.profile.get_guild_roster(
            config["general"]["region"],
            config["general"]["locale"],
            config["general"]["server"],
            config["general"]["guild"],
        )
    except KeyError:
        raise SystemExit(
            f"API error: couldn't retrieve guild data using configuration keys"
        )

    if not "members" in guild_data:
        raise SystemExit(
            f"Data error: couldn't find guild {config['general']['guild']}"
        )

    for character in guild_data["members"]:
        if character["character"]["level"] > int(config["general"]["char_min_level"]):
            guild_profession_data = get_profession_data(
                api_client,
                config,
                guild_profession_data,
                character["character"]["name"].lower(),
            )

    print_header(config)
    print_profession_table(guild_profession_data, exclude_list)


if __name__ == "__main__":
    main()

import os
from ConfigParser import ConfigParser


def self_heal(conf_file, heal_dict):
    heal_config = get_config(conf_file)
    for heal_item in heal_dict:
        section, section_value = heal_item.iteritems().next()
        if not heal_config.has_section(section):
            heal_config.add_section(section)
        if type(section_value) == dict:
            for item, value in section_value.items():
                if not heal_config.has_option(section, item):
                    heal_config.set(section, item, value)
        else:
            if len(heal_config.items(section)) != 1:
                for r_item, r_value in heal_config.items(section):
                    heal_config.remove_option(section, r_item)
                heal_config.set(section, section_value)

    heal_config.write(open(conf_file, 'w'))
    return heal_config


def get_config(conf_file):
    dir_name = os.path.dirname(conf_file)
    if not os.path.exists(dir_name):
        os.makedirs(os.path.dirname(conf_file))

    heal_config = ConfigParser(allow_no_value=True)
    if os.path.exists(conf_file):
        heal_config.read(conf_file)
    return heal_config

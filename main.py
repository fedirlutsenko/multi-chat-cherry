# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-
# Copyright (C) 2016   CzT/Vladislav Ivanov
import os
import imp
import Queue
import messaging
import logging
import logging.config
import semantic_version
from collections import OrderedDict
from modules.helper.parser import load_from_config_file
from modules.helper.system import load_translations_keys, PYTHON_FOLDER, CONF_FOLDER, MAIN_CONF_FILE, MODULE_FOLDER, \
    LOG_FOLDER, GUI_TAG, TRANSLATION_FOLDER, LOG_FILE, LOG_FORMAT, get_language, get_update, ModuleLoadException
from modules.helper.module import BaseModule

VERSION = '0.3.5'
SEM_VERSION = semantic_version.Version(VERSION)


def init():
    def close():
        for l_module, l_module_dict in loaded_modules.iteritems():
            l_module_dict['class'].apply_settings(system_exit=True)

        if window:
            window.gui.on_close('Closing Program from console')
        else:
            os._exit(0)
    # For system compatibility, loading chats
    loaded_modules = OrderedDict()
    gui_settings = {}
    window = None

    # Creating dict with folder settings
    main_config = {'root_folder': PYTHON_FOLDER,
                   'conf_folder': CONF_FOLDER,
                   'main_conf_file': MAIN_CONF_FILE,
                   'main_conf_file_loc': MAIN_CONF_FILE,
                   'main_conf_file_name': ''.join(os.path.basename(MAIN_CONF_FILE).split('.')[:-1]),
                   'update': False}

    if not os.path.isdir(MODULE_FOLDER):
        logging.error("Was not able to find modules folder, check you installation")
        exit()

    # Trying to load config file.
    # Create folder if doesn't exist
    if not os.path.isdir(CONF_FOLDER):
        log.error("Could not find {0} folder".format(CONF_FOLDER))
        try:
            os.mkdir(CONF_FOLDER)
        except:
            log.error("Was unable to create {0} folder.".format(CONF_FOLDER))
            exit()

    log.info("Loading basic configuration")
    main_config_dict = OrderedDict()
    main_config_dict['gui_information'] = OrderedDict()
    main_config_dict['gui_information']['category'] = 'main'
    main_config_dict['gui_information']['width'] = '450'
    main_config_dict['gui_information']['height'] = '500'
    main_config_dict['gui'] = OrderedDict()
    main_config_dict['gui']['show_hidden'] = False
    main_config_dict['gui']['gui'] = True
    main_config_dict['gui']['on_top'] = True
    main_config_dict['gui']['show_browser'] = True
    main_config_dict['gui']['show_counters'] = True
    main_config_dict['gui']['reload'] = None
    main_config_dict['language'] = get_language()

    main_config_gui = {
        'language': {
            'view': 'choose_single',
            'check_type': 'dir',
            'check': 'translations'
        },
        'non_dynamic': ['language.list_box', 'gui.*']
    }
    config = load_from_config_file(MAIN_CONF_FILE, main_config_dict)
    # Adding config for main module
    main_class = BaseModule(
        conf_params={
            'folder': CONF_FOLDER,
            'file': main_config['main_conf_file_loc'],
            'filename': main_config['main_conf_file_name'],
            'parser': config,
            'root_folder': main_config['root_folder'],
            'logs_folder': LOG_FOLDER,
            'config': main_config_dict,
            'gui': main_config_gui
        }
    )
    loaded_modules['main'] = main_class.conf_params()

    gui_settings['gui'] = main_config_dict[GUI_TAG].get('gui')
    gui_settings['on_top'] = main_config_dict[GUI_TAG].get('on_top')
    gui_settings['language'] = main_config_dict.get('language')
    gui_settings['show_hidden'] = main_config_dict[GUI_TAG].get('show_hidden')
    gui_settings['size'] = (int(main_config_dict['gui_information'].get('width')),
                            int(main_config_dict['gui_information'].get('height')))
    gui_settings['show_browser'] = main_config_dict['gui'].get('show_browser')

    # Checking updates
    log.info("Checking for updates")
    loaded_modules['main']['update'], loaded_modules['main']['update_url'] = get_update(SEM_VERSION)
    if loaded_modules['main']['update']:
        log.info("There is new update, please update!")

    # Starting modules
    log.info("Loading Messaging Handler")
    log.info("Loading Queue for message handling")

    # Creating queues for messaging transfer between chat threads
    queue = Queue.Queue()
    # Loading module for message processing...
    msg = messaging.Message(queue)
    loaded_modules.update(msg.load_modules(main_config, loaded_modules['main']))
    msg.start()

    log.info("Loading Chats")
    # Trying to dynamically load chats that are in config file.
    chat_modules = os.path.join(CONF_FOLDER, "chat_modules.cfg")
    chat_location = os.path.join(MODULE_FOLDER, "chat")
    chat_conf_dict = OrderedDict()
    chat_conf_dict['gui_information'] = {'category': 'chat'}
    chat_conf_dict['chats'] = {}

    chat_conf_gui = {
        'chats': {
            'view': 'choose_multiple',
            'check_type': 'files',
            'check': os.path.sep.join(['modules', 'chat']),
            'file_extension': False},
        'non_dynamic': ['chats.list_box']}
    chat_config = load_from_config_file(chat_modules, chat_conf_dict)

    chat_module = BaseModule(
        conf_params={
            'folder': CONF_FOLDER, 'file': chat_modules,
            'filename': ''.join(os.path.basename(chat_modules).split('.')[:-1]),
            'parser': chat_config,
            'config': chat_conf_dict,
            'gui': chat_conf_gui
        }
    )
    loaded_modules['chat'] = chat_module.conf_params()

    for module in chat_conf_dict['chats']:
        log.info("Loading chat module: {0}".format(module))
        module_location = os.path.join(chat_location, module + ".py")
        if os.path.isfile(module_location):
            log.info("found {0}".format(module))
            # After module is find, we are initializing it.
            # Class should be named as in config
            # Also passing core folder to module so it can load it's own
            #  configuration correctly

            tmp = imp.load_source(module, module_location)
            chat_init = getattr(tmp, module)
            class_module = chat_init(queue, PYTHON_FOLDER,
                                     conf_folder=CONF_FOLDER,
                                     conf_file=os.path.join(CONF_FOLDER, '{0}.cfg'.format(module)))
            loaded_modules[module] = class_module.conf_params()
        else:
            log.error("Unable to find {0} module")

    # Actually loading modules
    for f_module, f_config in loaded_modules.iteritems():
        if 'class' in f_config:
            try:
                f_config['class'].load_module(main_settings=main_config, loaded_modules=loaded_modules,
                                              queue=queue)
            except ModuleLoadException:
                msg.modules.remove(loaded_modules[f_module]['class'])
                loaded_modules.pop(f_module)

    try:
        load_translations_keys(TRANSLATION_FOLDER, gui_settings['language'])
    except:
        log.exception("Failed loading translations")

    if gui_settings['gui']:
        import gui
        log.info("Loading GUI Interface")
        window = gui.GuiThread(gui_settings=gui_settings,
                               main_config=loaded_modules['main'],
                               loaded_modules=loaded_modules,
                               queue=queue)
        loaded_modules['gui'] = window.conf_params()
        window.start()
    try:
        while True:
            console = raw_input("> ")
            log.info(console)
            if console == "exit":
                log.info("Exiting now!")
                close()
            else:
                log.info("Incorrect Command")
    except (KeyboardInterrupt, SystemExit):
        log.info("Exiting now!")
        close()
    except Exception as exc:
        log.info(exc)

if __name__ == '__main__':
    root_logger = logging.getLogger()
    # Logging level
    root_logger.setLevel(level=logging.DEBUG)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(LOG_FORMAT)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LOG_FORMAT)
    root_logger.addHandler(console_handler)
    logging.getLogger('requests').setLevel(logging.ERROR)

    log = logging.getLogger('main')
    init()

import pygame

BOUND_EVENT = pygame.event.custom_type()

eventtype_to_string = {
    # normal events
    pygame.QUIT: lambda x: 'quit',
    pygame.ACTIVEEVENT: lambda x: f'active-event {x.gain} {x.state}',
    pygame.KEYDOWN: lambda x: f'keydown {x.key} {x.mod}',
    pygame.KEYUP: lambda x: f'keyup {x.key} {x.mod}',
    pygame.MOUSEMOTION: lambda x: 'mouse-motion',
    pygame.MOUSEBUTTONUP: lambda x: f'mouse-button-up {x.button}',
    pygame.MOUSEBUTTONDOWN: lambda x: f'mouse-button-down {x.button}',
    pygame.JOYAXISMOTION: lambda x: 'joydevice-axis-motion',
    pygame.JOYBALLMOTION: lambda x: 'joydevice-ball-motion',
    pygame.JOYHATMOTION: lambda x: 'joydevice-hat-motion',
    pygame.JOYBUTTONUP: lambda x: 'joydevice-button-up',
    pygame.JOYBUTTONDOWN: lambda x: 'joydevice-button-down',
    pygame.VIDEORESIZE: lambda x: 'resize',
    pygame.VIDEOEXPOSE: lambda x: 'video=-expose',
    pygame.USEREVENT: lambda x: 'user-event',
    # extra when compiled with SDL2
    pygame.AUDIODEVICEADDED: lambda x: 'audio-device-added',
    pygame.AUDIODEVICEREMOVED: lambda x: 'audio-device-removed',
    pygame.FINGERMOTION: lambda x: 'finger-motion',
    pygame.FINGERDOWN: lambda x: 'finger-down',
    pygame.FINGERUP: lambda x: 'finger-up',
    pygame.MOUSEWHEEL: lambda x: 'mousewheel',
    pygame.MULTIGESTURE: lambda x: 'multigesture',
    pygame.TEXTEDITING: lambda x: 'text-editing',
    pygame.TEXTINPUT: lambda x: 'text-input',
    # controller hot-plugging
    pygame.DROPFILE: lambda x: 'drop-file',
    pygame.DROPBEGIN: lambda x: 'drop-begin',
    pygame.DROPCOMPLETE: lambda x: 'drop-complete',
    pygame.DROPTEXT: lambda x: 'drop-text',
    pygame.MIDIIN: lambda x: 'midi-in',
    pygame.MIDIOUT: lambda x: 'midi-out',
    pygame.CONTROLLERDEVICEADDED: lambda x: 'controller-added',
    pygame.JOYDEVICEADDED: lambda x: 'joydevice-added',
    pygame.CONTROLLERDEVICEREMOVED: lambda x: 'controller-removed',
    pygame.JOYDEVICEREMOVED: lambda x: 'joydevice-removed',
    pygame.CONTROLLERDEVICEREMAPPED: lambda x: 'controller-remapped',
    # window events
    pygame.WINDOWSHOWN: lambda x: 'window-shown',
    pygame.WINDOWHIDDEN: lambda x: 'window-hidden',
    pygame.WINDOWEXPOSED: lambda x: 'window-exposed',
    pygame.WINDOWMOVED: lambda x: 'window-moved',
    pygame.WINDOWRESIZED: lambda x: 'window-resized',
    pygame.WINDOWSIZECHANGED: lambda x: 'window-size-changed',
    pygame.WINDOWMINIMIZED: lambda x: 'window-minimized',
    pygame.WINDOWMAXIMIZED: lambda x: 'window-maximized',
    pygame.WINDOWRESTORED: lambda x: 'window-restored',
    pygame.WINDOWENTER: lambda x: 'window-enter',
    pygame.WINDOWLEAVE: lambda x: 'window-leave',
    pygame.WINDOWFOCUSGAINED: lambda x: 'window-focus-gained',
    pygame.WINDOWFOCUSLOST: lambda x: 'window-focus-lost',
    pygame.WINDOWCLOSE: lambda x: 'window-close',
    pygame.WINDOWTAKEFOCUS: lambda x: 'window-take-focus',
    pygame.WINDOWHITTEST: lambda x: 'window-hit-test',
    "generic": lambda x: 'unknown-event'
}

def get_string_id(event):
    # all pygame events from pygame 2.1.2 (SDL 2.0.16)
    return eventtype_to_string[event.type](event)


class EventHandler:
    def __init__(self, bindings={}):
        self.bindings = bindings

    def update_bindings(self, bindings):
        self.bindings.update(bindings)

    def process_event(self, event):
        ...

glob_event = EventHandler()
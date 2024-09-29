from transitions import Machine


# Состояния конечного автомата
user_states = ["START", "REGISTER", "USERNAME", "PASSWORD", "TASK_MENU"]
task_states = ["show_menu", "get_title", "get_description", "delete"]

# Переходы
user_transitions = [
    {"trigger": "start", "source": "START", "dest": "REGISTER"},
    {"trigger": "REGISTER", "source": "REGISTER", "dest": "USERNAME"},
    {"trigger": "USERNAME", "source": "USERNAME", "dest": "PASSWORD"},
    {"trigger": "PASSWORD", "source": "PASSWORD", "dest": "show_menu"},
    {"trigger": "show_menu", "source": "*", "dest": "TASK_MENU"},
]

task_transitions = [
    {"trigger": "show_menu", "source": "*", "dest": "show_menu"},
    {"trigger": "create_task", "source": "show_menu", "dest": "get_title"},
    {"trigger": "set_title", "source": "get_title", "dest": "get_description"},
    {"trigger": "set_description", "source": "get_description", "dest": "show_menu"},
]


class UserFSM:
    """FSM для регистрации пользователя"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.username = None
        self.password = None
        self.machine = Machine(
            model=self,
            states=user_states,
            transitions=user_transitions,
            initial="START",
        )


class TaskFSM:
    """FSM для работы с задачами"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.task = None
        self.machine = Machine(
            model=self,
            states=task_states,
            transitions=task_transitions,
            initial="start",
        )


user_fsm = {}
task_fsm = {}

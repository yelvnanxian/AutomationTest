"""作用：封装user db相关的项目公共业务能力。"""


from base.sqlite_opt.demoProject.demo_project_sessions import DemoProject_Sessions
from common_projects.sqlite_opt.base_db import Base_DB
from models.demoProject.user import User

class User_DB(Base_DB):
    def __init__(self) -> None:
        self.db_demoProject_session=DemoProject_Sessions().db_demoProject_session
        super(User_DB,self).__init__(self.db_demoProject_session,User)

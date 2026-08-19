from __future__ import annotations

from pathlib import Path
import threading
import sys

from PySide6.QtCore import QObject,Signal,Slot
from PySide6.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QFrame,QLabel,QPushButton,QStackedWidget,QMessageBox

from ..api import ApiClient
from ..environment import MinecraftRLEnv
from ..agent import DQNAgent
from ..encoder import ObservationEncoder
from ..trainer import Trainer,TrainingConfig
from ..settings import SettingsStore
from ..core.metrics import EpisodeMetric,MetricHistory
from ..update.github import GitHubReleaseClient,UpdateError
from ..update.models import BuildChannel
from ..server.installer import bundled_plugin_candidates,install_plugin
from ..version import display_version
from ..i18n import Translator
from ..profiles import get_profile
from ..learning import ProgressStore,TutorialEngine,default_tutorials
from .screens.dashboard import DashboardScreen
from .screens.connection import ConnectionScreen
from .screens.goals import GoalsScreen
from .screens.observation import ObservationScreen
from .screens.history import HistoryScreen
from .screens.updates import UpdatesScreen
from .screens.manual import ManualScreen
from .screens.models import ModelsScreen
from .screens.settings_screen import SettingsScreen
from .screens.learning import LearningScreen


class Bridge(QObject):
    event=Signal(dict); error=Signal(str); connected=Signal(object); update=Signal(object)


class MainWindow(QMainWindow):
    def __init__(self,settings_store:SettingsStore|None=None,settings=None)->None:
        super().__init__(); self.setWindowTitle(display_version()); self.resize(1320,820); self.setMinimumSize(1024,680)
        self.bridge=Bridge(); self.bridge.event.connect(self._on_training_event); self.bridge.error.connect(self._show_error); self.bridge.connected.connect(self._finish_connect); self.bridge.update.connect(self._finish_update)
        self.settings_store=settings_store or SettingsStore(); self.settings=settings or self.settings_store.load(); self.tr=Translator(self.settings.language); self.profile=get_profile(self.settings.experience_mode)
        self.env=None; self.agent=None; self.trainer=None; self.training_thread=None; self.metrics=MetricHistory(); self.current_goal="WOODEN_SWORD"
        self.progress_store=ProgressStore(); self.tutorial_engine=TutorialEngine(default_tutorials(),self.progress_store); self.active_tutorial=None
        self._build_ui(); self._wire(); self._load_settings()

    def _build_ui(self)->None:
        host=QWidget(); self.setCentralWidget(host); outer=QHBoxLayout(host); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0); side=QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(220); sl=QVBoxLayout(side); sl.setContentsMargins(14,18,14,16); sl.setSpacing(6); title=QLabel("🧠  "+self.tr("app.name")); title.setObjectName("AppTitle"); sl.addWidget(title); version=QLabel(display_version()); version.setObjectName("Subtitle"); version.setWordWrap(True); sl.addWidget(version); sl.addSpacing(15)
        self.dashboard=DashboardScreen(tr=self.tr); self.connection=ConnectionScreen(tr=self.tr); self.goals=GoalsScreen(tr=self.tr); self.manual=ManualScreen(tr=self.tr); self.observation=ObservationScreen(tr=self.tr); self.history=HistoryScreen(tr=self.tr); self.models=ModelsScreen(tr=self.tr); self.updates=UpdatesScreen(tr=self.tr); self.learning=LearningScreen(tr=self.tr,progress_store=self.progress_store); self.settings_screen=SettingsScreen(tr=self.tr)
        entries=[("nav.dashboard",self.dashboard),("nav.server",self.connection),("nav.goals",self.goals),("nav.learning",self.learning)]
        if self.profile.show_manual_actions:entries.append(("nav.manual",self.manual))
        if self.profile.show_raw_observations:entries.append(("nav.observations",self.observation))
        entries.append(("nav.history",self.history))
        if self.profile.show_model_internals:entries.append(("nav.models",self.models))
        entries.extend((("nav.updates",self.updates),("nav.settings",self.settings_screen)))
        self.stack=QStackedWidget(); self.nav=[]
        for index,(key,screen) in enumerate(entries):
            button=QPushButton(self.tr(key)); button.setObjectName("Nav"); button.setCheckable(True); button.clicked.connect(lambda _=False,i=index:self._switch(i)); sl.addWidget(button); self.nav.append(button); self.stack.addWidget(screen)
        sl.addStretch(1); mode=QLabel(self.tr(self.profile.title_key)); mode.setObjectName("Subtitle"); mode.setWordWrap(True); sl.addWidget(mode); outer.addWidget(side); outer.addWidget(self.stack,1); self._switch(0)

    def _wire(self)->None:
        self.connection.connect_button.clicked.connect(self.connect); self.connection.install_button.clicked.connect(self.install_bundled_plugin); self.goals.goal_changed.connect(self._set_goal); self.dashboard.start_button.clicked.connect(self.start_training); self.dashboard.stop_button.clicked.connect(self.stop_training); self.updates.check_requested.connect(self.check_updates); self.manual.step_requested.connect(self.manual_step); self.models.save_requested.connect(self.save_model); self.models.load_requested.connect(self.load_model); self.settings_screen.save_requested.connect(self.save_settings); self.learning.tutorial_requested.connect(self.start_tutorial); self.learning.demo_requested.connect(self._learning_demo_note); self.learning.tutorial_next_requested.connect(self._tutorial_next)

    def _load_settings(self)->None:
        self.connection.host.setText(self.settings.host); self.connection.port.setValue(self.settings.port); self.connection.player.setText(self.settings.player); idx=self.updates.channel.findText(self.settings.update_channel)
        if idx>=0:self.updates.channel.setCurrentIndex(idx)
        self.settings_screen.owner.setText(self.settings.github_owner); self.settings_screen.repo.setText(self.settings.github_repo); idx2=self.settings_screen.channel.findText(self.settings.update_channel)
        if idx2>=0:self.settings_screen.channel.setCurrentIndex(idx2)
        self.settings_screen.auto.setChecked(self.settings.auto_check_updates); self.settings_screen.set_language(self.settings.language); self.settings_screen.set_mode(self.settings.experience_mode); self.settings_screen.kid_name.setText(self.settings.kid_name)

    def _switch(self,index:int)->None:
        self.stack.setCurrentIndex(index)
        for i,button in enumerate(self.nav):button.setChecked(i==index)

    @Slot(str)
    def _set_goal(self,goal:str)->None:
        self.current_goal=goal; self._tutorial_event("goal."+goal)

    def connect(self)->None:
        self.connection.status.set_state(self.tr("status.connecting"),"info")
        def work():
            try:
                api=ApiClient(self.connection.host.text(),self.connection.port.value(),self.connection.token.text()); api.health(); api.info(); player=self.connection.player.text().strip();
                if player:api.bind(player)
                self.bridge.connected.emit(MinecraftRLEnv(api))
            except Exception as exc:self.bridge.error.emit(str(exc))
        threading.Thread(target=work,daemon=True,name="connect").start()

    @Slot(object)
    def _finish_connect(self,env)->None:
        self.env=env; self.connection.status.set_state(self.tr("status.connected"),"good"); self.manual.set_actions(list(env.actions)); self.settings.host=self.connection.host.text(); self.settings.port=self.connection.port.value(); self.settings.player=self.connection.player.text(); self.settings_store.save(self.settings); self._tutorial_event("server.connected")

    def start_training(self)->None:
        if self.env is None:self._show_error(self.tr("error.connect_first")); return
        if self.training_thread and self.training_thread.is_alive():return
        try:self.agent=DQNAgent(ObservationEncoder.FEATURE_SIZE,len(self.env.actions))
        except Exception as exc:self._show_error(str(exc)); return
        self.trainer=Trainer(self.env,self.agent,on_event=self.bridge.event.emit); config=TrainingConfig(self.current_goal,self.goals.profile.currentText(),episodes=self.dashboard.episodes.value(),episode_offset=self.dashboard.episode_offset.value()); self.training_thread=threading.Thread(target=self.trainer.run,args=(config,),daemon=True,name="rl-training"); self.training_thread.start(); self.dashboard.start_button.setEnabled(False); self.dashboard.stop_button.setEnabled(True); self._tutorial_event("training.started")

    def stop_training(self)->None:
        if self.trainer:self.trainer.stop()

    @Slot(dict)
    def _on_training_event(self,event:dict)->None:
        kind=event.get("type"); obs=event.get("observation")
        if isinstance(obs,dict):self.observation.set_observation(obs)
        if kind=="step":
            self.dashboard.cards["episode"].set_value(event.get("episode",0)); self.dashboard.cards["reward"].set_value(f"{event.get('episode_reward',0):.3f}"); self.dashboard.cards["epsilon"].set_value(f"{event.get('epsilon',0):.3f}"); loss=event.get("loss"); self.dashboard.cards["loss"].set_value("—" if loss is None else f"{loss:.5f}"); self.dashboard.last_action.setText(self.tr("dashboard.last_action",action=event.get("action","—")))
            if abs(float(event.get("reward",0.0)))>0:self._tutorial_event("training.reward")
        elif kind=="episode":
            metric=EpisodeMetric(int(event.get("episode",0)),int(event.get("steps",0)),float(event.get("reward",0)),bool(event.get("success",False)),str(event.get("terminal_reason",""))); self.metrics.add(metric); self.history.add_metric(metric); self.dashboard.push_reward(metric.reward); self.dashboard.cards["success"].set_value(f"{self.metrics.success_rate*100:.0f}%"); self.dashboard.cards["best"].set_value(f"{self.metrics.best_reward:.3f}"); self._tutorial_event("episode.completed")
        elif kind in ("training_finished","training_stopped"):
            self.dashboard.start_button.setEnabled(True); self.dashboard.stop_button.setEnabled(False)

    def install_bundled_plugin(self)->None:
        server=self.connection.server_path.text().strip()
        if not server:self._show_error(self.tr("server.choose_folder")); return
        roots=[Path.cwd(),Path(sys.executable).resolve().parent,Path(__file__).resolve().parents[3]]; candidates=[]
        for root in roots:candidates.extend(bundled_plugin_candidates(root))
        if not candidates:self._show_error(self.tr("error.plugin_missing")); return
        try:
            result=install_plugin(server,candidates[-1]); self.connection.install_status.setText(self.tr("server.plugin_installed",path=result.destination))
        except Exception as exc:self._show_error(str(exc))

    def manual_step(self,action:str)->None:
        if self.env is None:self._show_error(self.tr("error.connect_first")); return
        if self.training_thread and self.training_thread.is_alive():self._show_error(self.tr("error.stop_training_manual")); return
        try:index=self.env.actions.index(action)
        except ValueError:self._show_error(self.tr("error.action_unavailable")); return
        def work():
            try:
                result=self.env.step(index); event={"type":"step","episode":0,"step":1,"action":action,"reward":result.reward,"episode_reward":result.reward,"done":result.done,"success":result.success,"terminal_reason":result.terminal_reason,"loss":None,"epsilon":self.agent.epsilon if self.agent else 1.0,"observation":result.observation}; self.bridge.event.emit(event)
            except Exception as exc:self.bridge.error.emit(str(exc))
        threading.Thread(target=work,daemon=True,name="manual-step").start()

    def save_model(self,path:str)->None:
        if self.agent is None:self._show_error(self.tr("error.no_model")); return
        try:self.agent.save(path); self.models.info.setText(self.tr("models.saved",path=path))
        except Exception as exc:self._show_error(str(exc))

    def load_model(self,path:str)->None:
        if self.env is None:self._show_error(self.tr("error.connect_action_space")); return
        try:
            if self.agent is None:self.agent=DQNAgent(ObservationEncoder.FEATURE_SIZE,len(self.env.actions))
            self.agent.load(path); self.models.info.setText(self.tr("models.loaded",path=path))
        except Exception as exc:self._show_error(str(exc))

    @Slot(dict)
    def save_settings(self,values:dict)->None:
        self.settings.github_owner=str(values.get("github_owner",self.settings.github_owner)); self.settings.github_repo=str(values.get("github_repo",self.settings.github_repo)); self.settings.update_channel=str(values.get("update_channel",self.settings.update_channel)); self.settings.auto_check_updates=bool(values.get("auto_check_updates",self.settings.auto_check_updates)); self.settings.language=str(values.get("language",self.settings.language)); self.settings.experience_mode=str(values.get("experience_mode",self.settings.experience_mode)); self.settings.kid_name=str(values.get("kid_name",self.settings.kid_name)); self.settings_store.save(self.settings); idx=self.updates.channel.findText(self.settings.update_channel)
        if idx>=0:self.updates.channel.setCurrentIndex(idx)
        QMessageBox.information(self,self.tr("nav.settings"),self.tr("app.restart_required"))

    @Slot(str)
    def check_updates(self,channel:str)->None:
        self.updates.status.set_state(self.tr("updates.checking"),"info")
        def work():
            try:client=GitHubReleaseClient(self.settings.github_owner,self.settings.github_repo); release=client.newest(BuildChannel(channel)); self.bridge.update.emit(release)
            except UpdateError as exc:self.bridge.error.emit(str(exc))
        threading.Thread(target=work,daemon=True,name="update-check").start()

    @Slot(object)
    def _finish_update(self,release)->None:
        if release is None:self.updates.status.set_state(self.tr("updates.no_build"),"muted"); return
        self.updates.set_release(release.name,release.tag,release.verification.value,release.published_at)

    @Slot(str)
    def start_tutorial(self,tutorial_id:str)->None:
        if tutorial_id not in self.tutorial_engine.tutorials:return
        self.active_tutorial=tutorial_id; self._show_tutorial_step()

    def _tutorial_event(self,event:str)->None:
        if not self.active_tutorial:return
        tutorial=self.tutorial_engine.tutorials[self.active_tutorial]
        if self.tutorial_engine.handle_event(self.active_tutorial,event):
            self.learning.refresh(); done,total=self.tutorial_engine.completion(self.active_tutorial)
            if done>=total:self.learning.show_step(self.tr(tutorial.title_key),self.tr("learning.completed"),done,total,False); self.active_tutorial=None
            else:self._show_tutorial_step()

    def _tutorial_next(self)->None:
        if not self.active_tutorial:return
        tutorial=self.tutorial_engine.tutorials[self.active_tutorial]
        if self.tutorial_engine.next(self.active_tutorial):
            self.learning.refresh(); done,total=self.tutorial_engine.completion(self.active_tutorial)
            if done>=total:self.learning.show_step(self.tr(tutorial.title_key),self.tr("learning.completed"),done,total,False); self.active_tutorial=None
            else:self._show_tutorial_step()

    def _show_tutorial_step(self)->None:
        if not self.active_tutorial:return
        tutorial=self.tutorial_engine.tutorials[self.active_tutorial]; done,total=self.tutorial_engine.completion(self.active_tutorial); step=self.tutorial_engine.current_step(self.active_tutorial); body=self.tr(step.body_key); manual=step.event is None
        if not manual: body += "\n\n"+self.tr("tutorial.wait_action")
        self.learning.show_step(self.tr(tutorial.title_key),body,done,total,manual)

    def _learning_demo_note(self,tutorial_id:str)->None:
        tutorial=self.tutorial_engine.tutorials.get(tutorial_id)
        if tutorial:QMessageBox.information(self,self.tr("kids.demo_badge"),self.tr(tutorial.description_key)+"\n\n"+self.tr("kids.tip"))

    @Slot(str)
    def _show_error(self,message:str)->None:
        self.connection.status.set_state(self.tr("status.error"),"bad"); QMessageBox.critical(self,self.tr("app.name"),message)

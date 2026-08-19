from __future__ import annotations

from pathlib import Path
import sys
import threading

from PySide6.QtCore import QObject,QTimer,Signal,Slot
from PySide6.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QFrame,QLabel,QPushButton,QStackedWidget,QMessageBox

from ...agent import DQNAgent
from ...api import ApiClient
from ...encoder import ObservationEncoder
from ...environment import MinecraftRLEnv
from ...i18n import Translator
from ...learning import ProgressStore,TutorialEngine,default_tutorials
from ...learning.achievements import AchievementTracker
from ...learning.demo_environment import DemoEnvironment
from ...profiles.kids_content import kids_goal_cards
from ...profiles.kids_session import KidsSessionModel
from ...server.installer import bundled_plugin_candidates,install_plugin
from ...trainer import Trainer,TrainingConfig
from ...version import display_version
from ..theme_kids import KIDS_STYLESHEET
from .home import KidsHomeScreen
from .learn import KidsLearnScreen
from .missions import KidsMissionsScreen
from .progress import KidsProgressScreen
from .server import KidsServerScreen
from .settings import KidsSettingsScreen


class KidsBridge(QObject):
    event=Signal(dict)
    error=Signal(str)
    connected=Signal(object)


class KidsMainWindow(QMainWindow):
    def __init__(self,settings_store,settings)->None:
        super().__init__(); self.settings_store=settings_store; self.settings=settings; self.tr=Translator(settings.language); self.setStyleSheet(KIDS_STYLESHEET); self.setWindowTitle(display_version()+" • Kids"); self.resize(1180,760); self.setMinimumSize(960,650)
        self.bridge=KidsBridge(); self.bridge.event.connect(self._on_training_event); self.bridge.error.connect(self._show_error); self.bridge.connected.connect(self._finish_connect)
        self.env=None; self.agent=None; self.trainer=None; self.training_thread=None; self.current_goal="WOODEN_SWORD"; self.demo=DemoEnvironment(seed=17); self.demo_running=False
        self.progress_store=ProgressStore(); self.tutorial_engine=TutorialEngine(default_tutorials(),self.progress_store); progress=self.progress_store.load(); self.session=KidsSessionModel(set(progress.unlocked_achievements)); self.active_tutorial=None
        self._build_ui(); self._wire(); self._load_settings(); self._refresh_progress()

    def _build_ui(self)->None:
        host=QWidget(); self.setCentralWidget(host); outer=QHBoxLayout(host); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        side=QFrame(); side.setObjectName("KidsSidebar"); side.setFixedWidth(245); sl=QVBoxLayout(side); sl.setContentsMargins(16,22,16,18); sl.setSpacing(8); brand=QLabel("🧠  Minecraft\n     RL Lab"); brand.setObjectName("KidsCardTitle"); sl.addWidget(brand); version=QLabel(display_version()); version.setObjectName("KidsTiny"); sl.addWidget(version); sl.addSpacing(16)
        self.stack=QStackedWidget(); self.home=KidsHomeScreen(self.tr,self.settings.kid_name); self.missions=KidsMissionsScreen(self.tr); self.learn=KidsLearnScreen(self.tr,self.tutorial_engine); self.progress=KidsProgressScreen(self.tr,self.progress_store); self.server=KidsServerScreen(self.tr); self.kids_settings=KidsSettingsScreen(self.tr,self.settings); self.screens=[self.home,self.missions,self.learn,self.progress,self.server,self.kids_settings]
        nav_specs=(("🏠", "kids.home"),("🎯","kids.missions"),("📚","kids.learn"),("🏆","kids.progress"),("⛏️","kids.server"),("⚙️","nav.settings")); self.nav=[]
        for index,(emoji,key) in enumerate(nav_specs):
            button=QPushButton(f"{emoji}  {self.tr(key)}"); button.setObjectName("KidsNav"); button.setCheckable(True); button.clicked.connect(lambda _=False,i=index:self._switch(i)); sl.addWidget(button); self.nav.append(button)
        sl.addStretch(1); mode=QLabel("✨ "+self.tr("mode.kids.title")); mode.setObjectName("KidsTiny"); mode.setWordWrap(True); sl.addWidget(mode); outer.addWidget(side); outer.addWidget(self.stack,1)
        for screen in self.screens:self.stack.addWidget(screen)
        self._switch(0)

    def _wire(self)->None:
        self.missions.goal_changed.connect(self._select_goal); self.home.start_requested.connect(self.start_training); self.home.stop_requested.connect(self.stop_training); self.home.demo_requested.connect(self.start_demo); self.server.connect_requested.connect(self.connect_server); self.server.install_requested.connect(self.install_bundled_plugin); self.learn.tutorial_selected.connect(self.start_tutorial); self.home.coach.next_requested.connect(self._tutorial_next); self.kids_settings.save_requested.connect(self.save_kids_settings)

    def _load_settings(self)->None:
        self.server.host.setText(self.settings.host); self.server.port.setValue(self.settings.port); self.server.player.setText(self.settings.player)

    def _switch(self,index:int)->None:
        self.stack.setCurrentIndex(index)
        for i,button in enumerate(self.nav):button.setChecked(i==index)
        if index==2:self.learn.refresh()
        if index==3:self.progress.refresh()

    @Slot(str)
    def _select_goal(self,goal:str)->None:
        self.current_goal=goal; self.session.select_goal(goal); card=next(item for item in kids_goal_cards(self.tr) if item.goal==goal); self.home.set_goal(card.emoji,card.title); self._tutorial_event("goal."+goal)

    def connect_server(self)->None:
        self.server.status.setText("🟡  "+self.tr("status.connecting"))
        def work():
            try:
                api=ApiClient(self.server.host.text(),self.server.port.value(),self.server.token.text()); api.health(); api.info(); player=self.server.player.text().strip();
                if player:api.bind(player)
                self.bridge.connected.emit(MinecraftRLEnv(api))
            except Exception as exc:self.bridge.error.emit(str(exc))
        threading.Thread(target=work,daemon=True,name="kids-connect").start()

    @Slot(object)
    def _finish_connect(self,env)->None:
        self.env=env; self.home.set_connected(True); self.server.set_connected(True); self.settings.host=self.server.host.text(); self.settings.port=self.server.port.value(); self.settings.player=self.server.player.text(); self.settings_store.save(self.settings); self._tutorial_event("server.connected")

    def start_training(self)->None:
        if self.env is None:
            self._switch(4); self._show_error(self.tr("kids.not_connected")); return
        if self.training_thread and self.training_thread.is_alive():return
        try:self.agent=DQNAgent(ObservationEncoder.FEATURE_SIZE,len(self.env.actions))
        except Exception as exc:self._show_error(str(exc)); return
        self.trainer=Trainer(self.env,self.agent,on_event=self.bridge.event.emit); config=TrainingConfig(self.current_goal,"CURRICULUM",episodes=10,episode_offset=0); self.training_thread=threading.Thread(target=self.trainer.run,args=(config,),daemon=True,name="kids-training"); self.training_thread.start(); self.home.set_training(True); self._tutorial_event("training.started")

    def stop_training(self)->None:
        if self.trainer:self.trainer.stop()

    @Slot(dict)
    def _on_training_event(self,event:dict)->None:
        kind=event.get("type"); result=self.session.consume_training_event(event)
        if kind=="step":
            self.home.reward.setText(f"{float(event.get('episode_reward',0.0)):.2f}")
            if abs(float(event.get("reward",0.0)))>0:self._tutorial_event("training.reward")
        elif kind=="episode":
            self.home.reward.setText(f"{float(event.get('reward',0.0)):.2f}"); self._save_new_achievements(result.unlocked); self._tutorial_event("episode.completed"); self._refresh_progress()
        elif kind in ("training_finished","training_stopped"):
            self.home.set_training(False)

    def _save_new_achievements(self,achievement_ids:list[str])->None:
        if not achievement_ids:return
        progress=self.progress_store.load(); changed=False
        for aid in achievement_ids:
            if aid not in progress.unlocked_achievements:
                progress.unlocked_achievements.append(aid); progress.stars+=3; changed=True
        if changed:self.progress_store.save(progress)

    @Slot(str)
    def start_tutorial(self,tutorial_id:str)->None:
        if tutorial_id not in self.tutorial_engine.tutorials:return
        self.active_tutorial=tutorial_id; self._show_current_tutorial_step(); self._switch(0)

    def _tutorial_event(self,event:str)->None:
        if not self.active_tutorial:return
        tutorial=self.tutorial_engine.tutorials[self.active_tutorial]; before=self.tutorial_engine.current_index(self.active_tutorial)
        if self.tutorial_engine.handle_event(self.active_tutorial,event):
            after=self.tutorial_engine.current_index(self.active_tutorial); self.learn.refresh(); self._refresh_progress()
            if after>=len(tutorial.steps) and before<len(tutorial.steps):
                progress=self.progress_store.load(); tracker=AchievementTracker(set(progress.unlocked_achievements)); new=tracker.consume("tutorial.completed",{"tutorial":self.active_tutorial}); self._save_new_achievements(new); self.home.coach.show_step("🎉 "+self.tr("learning.completed"),self.tr(tutorial.title_key)); self.active_tutorial=None
            else:self._show_current_tutorial_step()

    def _tutorial_next(self)->None:
        if not self.active_tutorial:return
        tutorial=self.tutorial_engine.tutorials[self.active_tutorial]
        if self.tutorial_engine.next(self.active_tutorial):
            self.learn.refresh(); self._refresh_progress(); done,total=self.tutorial_engine.completion(self.active_tutorial)
            if done>=total:
                progress=self.progress_store.load(); tracker=AchievementTracker(set(progress.unlocked_achievements)); self._save_new_achievements(tracker.consume("tutorial.completed",{"tutorial":self.active_tutorial})); self.home.coach.show_step("🎉 "+self.tr("learning.completed"),self.tr(tutorial.title_key),False,self.tr("common.next")); self.active_tutorial=None
            else:self._show_current_tutorial_step()

    def _show_current_tutorial_step(self)->None:
        if not self.active_tutorial:return
        tutorial=self.tutorial_engine.tutorials[self.active_tutorial]; done,total=self.tutorial_engine.completion(self.active_tutorial)
        if done>=total:return
        step=self.tutorial_engine.current_step(self.active_tutorial); body=self.tr(step.body_key); manual=step.event is None
        if not manual:body += "\n\n"+self.tr("tutorial.wait_action")
        self.home.coach.show_step(self.tr(tutorial.title_key),body,manual,self.tr("common.next"))

    def start_demo(self)->None:
        if self.demo_running:return
        self.demo.reset(self.current_goal); self.demo_running=True; self.home.coach.show_step(self.tr("kids.demo_badge"),self.tr("kids.tip"),False,self.tr("common.next")); self._demo_tick()

    def _demo_tick(self)->None:
        if not self.demo_running:return
        event=self.demo.step(); self.home.reward.setText(f"{event['total_reward']:.2f}"); self.home.coach.show_step(self.tr("kids.demo_badge"),f"{event['action']}  →  +{event['reward']:.2f} ⭐",False,self.tr("common.next"))
        if event["done"]:
            self.demo_running=False; return
        QTimer.singleShot(550,self._demo_tick)

    def install_bundled_plugin(self)->None:
        server_path=self.server.server_path.text().strip()
        if not server_path:self._show_error(self.tr("server.choose_folder")); return
        roots=[Path.cwd(),Path(sys.executable).resolve().parent,Path(__file__).resolve().parents[4]]; candidates=[]
        for root in roots:candidates.extend(bundled_plugin_candidates(root))
        if not candidates:self._show_error(self.tr("error.plugin_missing")); return
        try:
            result=install_plugin(server_path,candidates[-1]); self.server.install_status.setText(self.tr("server.plugin_installed",path=result.destination))
        except Exception as exc:self._show_error(str(exc))

    def _refresh_progress(self)->None:
        progress=self.progress_store.load(); self.home.stars.setText(str(progress.stars)); self.progress.refresh(); self.learn.refresh()


    @Slot(dict)
    def save_kids_settings(self,values:dict)->None:
        self.settings.language=str(values.get("language",self.settings.language)); self.settings.experience_mode=str(values.get("experience_mode",self.settings.experience_mode)); self.settings.kid_name=str(values.get("kid_name",self.settings.kid_name)); self.settings_store.save(self.settings); QMessageBox.information(self,self.tr("nav.settings"),self.tr("app.restart_required"))

    @Slot(str)
    def _show_error(self,message:str)->None:
        self.home.set_connected(False if self.env is None else True); self.server.set_connected(False if self.env is None else True); QMessageBox.critical(self,self.tr("app.name"),message)

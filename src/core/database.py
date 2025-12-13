"""Shared database models for observations across all landscapes"""

from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import click

Base = declarative_base()


class Agent(Base):
    """Agent persona definitions"""

    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    persona = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Agent {self.agent_id}: {self.name}>"


class Observation(Base):
    """Individual agent observations"""

    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    episode_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    observation_text = Column(Text)
    screenshot_path = Column(String)
    action_code = Column(Text)
    outcome = Column(Text)
    reward = Column(Float, default=0.0)
    model_checkpoint = Column(String, default="base")

    def __repr__(self):
        return f"<Observation {self.id}: {self.agent_id} @ {self.timestamp}>"


class DatabaseManager:
    """Manages database connections for a landscape"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        click.secho(f"[Database] Initialized: {db_path}", fg="green")

    def get_session(self):
        """Get database session"""
        return self.Session()

    def add_agent(self, agent_id: str, name: str, persona: str, system_prompt: str):
        """Add or update agent definition"""
        session = self.get_session()
        agent = session.query(Agent).filter_by(agent_id=agent_id).first()

        if agent:
            agent.name = name
            agent.persona = persona
            agent.system_prompt = system_prompt
            click.secho(f"[Database] Updated agent: {agent_id}", fg="yellow")
        else:
            agent = Agent(
                agent_id=agent_id,
                name=name,
                persona=persona,
                system_prompt=system_prompt,
            )
            session.add(agent)
            click.secho(f"[Database] Created agent: {agent_id}", fg="green")

        session.commit()
        session.close()
        return agent

    def add_observation(
        self,
        agent_id: str,
        episode_id: str,
        observation_text: str,
        action_code: str,
        outcome: str,
        reward: float,
        screenshot_path: str = None,
        model_checkpoint: str = "base",
    ):
        """Store observation"""
        session = self.get_session()
        obs = Observation(
            agent_id=agent_id,
            episode_id=episode_id,
            observation_text=observation_text,
            screenshot_path=screenshot_path,
            action_code=action_code,
            outcome=outcome,
            reward=reward,
            model_checkpoint=model_checkpoint,
        )
        session.add(obs)
        session.commit()
        click.secho(
            f"[Database] Observation stored: {agent_id} | reward={reward:.2f}",
            fg="green" if reward > 0 else "red",
        )
        session.close()
        return obs

    def get_agent_observations(self, agent_id: str, min_reward: float = None):
        """Get observations for specific agent"""
        session = self.get_session()
        query = session.query(Observation).filter_by(agent_id=agent_id)

        if min_reward is not None:
            query = query.filter(Observation.reward >= min_reward)

        observations = query.order_by(Observation.timestamp.desc()).all()
        session.close()
        return observations

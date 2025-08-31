from sqlalchemy.orm import Session
from app.models.session import Session as SessionModel, Chat as ChatModel, Keyframe as KeyframeModel
from app.schemas.session import SessionBase, ChatBase, KeyframeBase

def create_session(db: Session, session: SessionBase):
    db_session = SessionModel(user_id=session.user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def create_chat(db: Session, chat: ChatBase, session_id: int):
    db_chat = ChatModel(**chat.dict(), session_id=session_id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def create_keyframe(db: Session, keyframe: KeyframeBase):
    db_keyframe = KeyframeModel(**keyframe.dict())
    db.add(db_keyframe)
    db.commit()
    db.refresh(db_keyframe)
    return db_keyframe

def get_session(db: Session, session_id: int):
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()

def get_chats_by_session(db: Session, session_id: int):
    return db.query(ChatModel).filter(ChatModel.session_id == session_id).all()

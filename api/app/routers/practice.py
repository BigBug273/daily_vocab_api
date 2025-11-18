from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Word, PracticeSession
from app.schemas import ValidateSentenceRequest, ValidateSentenceResponse
from app.utils import mock_ai_validation

router = APIRouter()


@router.post("/validate-sentence", response_model=ValidateSentenceResponse)
def validate_sentence(
    request: ValidateSentenceRequest,
    db: Session = Depends(get_db)
):
    # Look for word
    word = db.query(Word).filter(Word.id == request.word_id).first()
    if word is None:
        raise HTTPException(status_code=404, detail="Word not found")

    # Mock AI validation
    result = mock_ai_validation(
        request.sentence,  
        word.word,
        word.difficulty_level
    )

    new_record = PracticeSession(
        word_id=request.word_id,
        user_sentence=request.sentence,
        score=result["score"],
        feedback=result["suggestion"],
        corrected_sentence=result["corrected_sentence"]
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return result

from pydantic import BaseModel


class TurtleSoupStory(BaseModel):
    brief_story: str
    full_story: str


class TurtleSoupEvaluation(BaseModel):
    evaluation: str


class TurtleSoupJudge(BaseModel):
    judge: str


class TurtleSoupGuess(BaseModel):
    guess: str

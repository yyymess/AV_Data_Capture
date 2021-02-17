'''用于储存单个评分数据。'''
from dataclasses import dataclass

@dataclass
class Rating:
    '''
    用于存储单个评分。包含分数，票数，最大值，以及来源。
    '''
    rating: float = 0.0
    max_rating: float = 10.0
    source: str = 'nfo'
    votes: int = 0
    
    def is_valid(self) -> bool:
        '''
        返回本条数据中的数值是否合理。
        '''
        if self.rating < 0:
            return False

        if self.rating == 0 and self.votes == 0:
            return False

        if self.max_rating < self.rating:
            return False

        return True

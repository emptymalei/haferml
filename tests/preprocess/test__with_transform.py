from haferml.data.preprocessing.ingredients import attributes
from haferml.data.preprocessing.ingredients import with_transforms
from loguru import logger


class AGoodClass:
    def __init__(self):
        pass

    @attributes(rank=1)
    def first_good_member(self, new):
        return f"{new} - appended first good member"

    @attributes(rank=2)
    def second_good_member(self, new):
        return f"{new} - appended second good member"

    @with_transforms(attr="rank")
    def bench(self, name):
        logger.info(name)
        logger.info(self.transforms)
        for t in self.transforms:
            name = self.transforms[t](name)
            logger.info(f"transformation {t} is done. Got strings: {name}")


a = AGoodClass()

a.bench("a name")

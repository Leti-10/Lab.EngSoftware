from dataclasses import dataclass, field

from src.domain.enums.enums import ReportTarget

@dataclass
class Report:
    id: int | None = field(init=False, default=None)
    description: str = field(init=True)
    user_id: int = field(init=True)
    target_entity: ReportTarget = field(init=True)
    target_id: int = field(init=True)

    def __post_init__(self):
        if not self.description.strip():
            raise ValueError("description não pode ser vazio")

        if len(self.description.strip()) <= 10:
            raise ValueError("description deve ter pelo menos 10 caracteres")

        if self.user_id <= 0:
            raise ValueError("user_id deve ser maior que 0")

        if not isinstance(self.target_entity, ReportTarget):
            try:
                self.target_entity = ReportTarget(self.target_entity)
            except ValueError:
                raise ValueError("Não é possível criar um report para esse target")

        if self.target_id <= 0:
            raise ValueError("target_id deve ser maior que 0")

if __name__ == "__main__":
    report = Report(
        description="As informações desse livro estão incorretas",
        user_id=1,
        target_entity="books",
        target_id=1
    )

    bad_report = Report(
        description="descrição haha",
        user_id=1,
        target_entity="chat",
        target_id=1
    )
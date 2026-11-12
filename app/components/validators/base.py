from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """Thông tin về một vấn đề được phát hiện khi kiểm tra dữ liệu."""

    name: str
    message: str
    severity: str = "error"
    details: dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Tổng hợp kết quả kiểm tra dataset."""

    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(
        self,
        name: str,
        message: str,
        severity: str = "error",
        details: dict | None = None,
    ):
        self.issues.append(
            ValidationIssue(
                name=name,
                message=message,
                severity=severity,
                details=details or {},
            )
        )

    @property
    def is_valid(self) -> bool:
        return not any(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def errors(self) -> list[ValidationIssue]:
        return [
            issue for issue in self.issues
            if issue.severity == "error"
        ]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [
            issue for issue in self.issues
            if issue.severity == "warning"
        ]
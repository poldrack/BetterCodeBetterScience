"""Execution logging for stateless workflow.

Tracks execution details including timing, parameters, and status for each step.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class StepRecord:
    """Record of a single workflow step execution."""

    step_number: int
    step_name: str
    start_time: str
    end_time: str | None = None
    duration_seconds: float | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    from_cache: bool = False
    status: str = "running"
    checkpoint_file: str | None = None
    error_message: str | None = None


@dataclass
class ExecutionLog:
    """Complete execution log for a workflow run."""

    workflow_name: str
    run_id: str
    start_time: str
    end_time: str | None = None
    total_duration_seconds: float | None = None
    status: str = "running"
    steps: list[StepRecord] = field(default_factory=list)
    workflow_parameters: dict[str, Any] = field(default_factory=dict)

    def add_step(
        self,
        step_number: int,
        step_name: str,
        parameters: dict[str, Any] | None = None,
        checkpoint_file: str | None = None,
    ) -> StepRecord:
        """Add a new step record and return it."""
        record = StepRecord(
            step_number=step_number,
            step_name=step_name,
            start_time=datetime.now().isoformat(),
            parameters=parameters or {},
            checkpoint_file=checkpoint_file,
        )
        self.steps.append(record)
        return record

    def complete_step(
        self,
        record: StepRecord,
        from_cache: bool = False,
        error_message: str | None = None,
    ) -> None:
        """Mark a step as completed."""
        record.end_time = datetime.now().isoformat()
        start = datetime.fromisoformat(record.start_time)
        end = datetime.fromisoformat(record.end_time)
        record.duration_seconds = (end - start).total_seconds()
        record.from_cache = from_cache
        record.status = "completed" if error_message is None else "failed"
        record.error_message = error_message

    def complete(self, error_message: str | None = None) -> None:
        """Mark the entire workflow as completed."""
        self.end_time = datetime.now().isoformat()
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        self.total_duration_seconds = (end - start).total_seconds()
        self.status = "completed" if error_message is None else "failed"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "workflow_name": self.workflow_name,
            "run_id": self.run_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_seconds": self.total_duration_seconds,
            "status": self.status,
            "workflow_parameters": self.workflow_parameters,
            "steps": [asdict(step) for step in self.steps],
        }

    def save(self, log_dir: Path) -> Path:
        """Save execution log to a date-stamped JSON file.

        Parameters
        ----------
        log_dir : Path
            Directory to save the log file

        Returns
        -------
        Path
            Path to the saved log file
        """
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"execution_log_{timestamp}.json"

        with open(log_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        return log_file

    def print_summary(self) -> None:
        """Print a summary of the execution."""
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Workflow: {self.workflow_name}")
        print(f"Run ID: {self.run_id}")
        print(f"Status: {self.status}")
        if self.total_duration_seconds is not None:
            print(f"Total Duration: {self.total_duration_seconds:.1f} seconds")

        print("\nStep Details:")
        print("-" * 60)
        for step in self.steps:
            cache_indicator = " [cached]" if step.from_cache else ""
            duration = (
                f"{step.duration_seconds:.1f}s"
                if step.duration_seconds is not None
                else "N/A"
            )
            status_icon = "✓" if step.status == "completed" else "✗"
            print(
                f"  {status_icon} Step {step.step_number}: {step.step_name:<25} "
                f"{duration:>8}{cache_indicator}"
            )
        print("-" * 60)


def create_execution_log(
    workflow_name: str,
    workflow_parameters: dict[str, Any] | None = None,
) -> ExecutionLog:
    """Create a new execution log.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow
    workflow_parameters : dict, optional
        Parameters passed to the workflow

    Returns
    -------
    ExecutionLog
        New execution log instance
    """
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return ExecutionLog(
        workflow_name=workflow_name,
        run_id=run_id,
        start_time=datetime.now().isoformat(),
        workflow_parameters=workflow_parameters or {},
    )


def serialize_parameters(**kwargs) -> dict[str, Any]:
    """Convert parameters to JSON-serializable format.

    Handles common non-serializable types like Path objects.

    Parameters
    ----------
    **kwargs
        Parameters to serialize

    Returns
    -------
    dict
        Serialized parameters
    """
    result = {}
    for key, value in kwargs.items():
        if isinstance(value, Path):
            result[key] = str(value)
        elif hasattr(value, "tolist"):  # numpy arrays
            result[key] = value.tolist()
        elif hasattr(value, "__dict__"):  # objects
            result[key] = str(type(value).__name__)
        else:
            try:
                json.dumps(value)
                result[key] = value
            except (TypeError, ValueError):
                result[key] = str(value)
    return result

from typing import Optional
from dataclasses import dataclass


@dataclass
class Measurement:
    mtype: str
    target: str
    # probes: Optional[List[str]] = None
    probes: Optional[str] = None
    mid: Optional[int] = None
    key: Optional[str] = None
    project: Optional[str] = None
    ripe_params: Optional[str] = None
    last_updated: Optional[int] = None

    def command(self) -> str:
        cmd = f"python ripe-atlas.py measure {self.mtype} --target={self.target} --no-report "
        if self.probes:
            cmd += f"--from-probes={self.probes} "
        if self.key:
            cmd += f"--auth={self.key} "
        if self.project:
            cmd += f"--description={self.description()} "
        if self.ripe_params:
            cmd += self.ripe_params
        return cmd

    def description(self) -> str:
        if self.project:
            return f"{self.project}-{self.target}"
        return f"era-2-{self.target}"

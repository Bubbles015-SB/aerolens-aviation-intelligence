"""Engineering technical records / evidence traceability quality gate.

Supports synthetic portfolio exercises or user-owned compliance CSVs.
NOT a regulatory certification decision or substitute for responsible engineers.
"""
from __future__ import annotations
from datetime import date
from collections import Counter
from dataclasses import dataclass

@dataclass(frozen=True)
class Evidence:
    id:str; requirement:str; revision:int; approved_revision:int; approved:bool; due_date:date; artifact_url:str; criticality:str='medium'
    def validate(self):
        if not self.id or not self.requirement or not self.artifact_url:raise ValueError('Evidence must have identifier, requirement, and artifact reference')
        if self.revision<1 or self.approved_revision<0:raise ValueError('Invalid revision')
        if self.approved_revision>self.revision:raise ValueError('Approval for future revision')
        if self.criticality not in ('low','medium','high','critical'):raise ValueError('Unknown criticality')
        return self


def audit(evidence, as_of:date):
    seen=set();items=[];counter=Counter()
    for row in evidence:
        row.validate()
        if row.id in seen:raise ValueError('Duplicate evidence ID')
        seen.add(row.id)
        issues=[]
        if not row.approved:issues.append('not_approved')
        if row.approved_revision!=row.revision:issues.append('revision_gap')
        if row.due_date<as_of and issues:issues.append('overdue')
        status='ready' if not issues else 'blocked'
        counter[status]+=1
        items.append(dict(id=row.id,requirement=row.requirement,criticality=row.criticality,
                          current_revision=row.revision,approved_revision=row.approved_revision,status=status,
                          issues=issues,due_date=row.due_date.isoformat()))
    critical_blocked=sum(r['status']=='blocked' and r['criticality'] in ('high','critical') for r in items)
    return dict(as_of=as_of.isoformat(),records=len(items),ready=counter['ready'],blocked=counter['blocked'],
                critical_blocked=critical_blocked,readiness_pct=round(100*counter['ready']/len(items),1) if items else None,
                release_gate='REVIEW_REQUIRED' if counter['blocked'] else ('EVIDENCE_READY' if items else 'EMPTY'),
                note='Documentation readiness only. Does NOT confer technical certification or authority approval.',records_detail=items)

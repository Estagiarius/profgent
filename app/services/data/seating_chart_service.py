# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
from app.models.seating_chart import SeatingChart, SeatAssignment
from app.models.student import Student
from app.models.class_enrollment import ClassEnrollment
from .base_service import BaseDataService


class SeatingChartService(BaseDataService):
    def create_seating_chart(self, class_id: int, name: str, rows: int, cols: int, layout_config: str = "{}") -> dict:
        with self._get_db() as db:
            chart = SeatingChart(
                class_id=class_id,
                name=name,
                rows=rows,
                columns=cols,
                layout_config=layout_config
            )
            db.add(chart)
            db.flush()
            db.refresh(chart)
            return {
                "id": chart.id,
                "class_id": chart.class_id,
                "name": chart.name,
                "rows": chart.rows,
                "columns": chart.columns,
                "layout_config": chart.layout_config,
                "created_at": chart.created_at,
            }

    def get_seating_charts_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            charts = db.query(SeatingChart).filter(SeatingChart.class_id == class_id).all()
            return [{"id": c.id, "name": c.name, "rows": c.rows, "columns": c.columns, "created_at": c.created_at} for c in charts]

    def get_seating_chart_details(self, chart_id: int) -> dict | None:
        with self._get_db() as db:
            chart = db.query(SeatingChart).filter(SeatingChart.id == chart_id).first()
            if not chart:
                return None

            assignments_query = (
                db.query(
                    SeatAssignment,
                    Student.first_name,
                    Student.last_name,
                    ClassEnrollment.call_number
                )
                .join(Student, SeatAssignment.student_id == Student.id)
                .outerjoin(ClassEnrollment, (ClassEnrollment.student_id == Student.id) & (ClassEnrollment.class_id == chart.class_id))
                .filter(SeatAssignment.chart_id == chart_id)
                .all()
            )

            assignments_data = []
            for a, fname, lname, call_num in assignments_query:
                assignments_data.append({
                    "id": a.id,
                    "student_id": a.student_id,
                    "student_name": f"{fname} {lname}",
                    "call_number": call_num,
                    "row_index": a.row_index,
                    "col_index": a.col_index
                })

            return {
                "id": chart.id,
                "name": chart.name,
                "rows": chart.rows,
                "columns": chart.columns,
                "layout_config": chart.layout_config,
                "assignments": assignments_data
            }

    def update_seating_chart_layout(self, chart_id: int, layout_config: str):
        with self._get_db() as db:
            chart = db.query(SeatingChart).filter(SeatingChart.id == chart_id).first()
            if chart:
                chart.layout_config = layout_config
                db.flush()

    def save_seat_assignments(self, chart_id: int, assignments: list[dict]):
        """
        Substitui todas as alocações de assento de um mapa de sala pela nova lista.
        assignments: lista de dicts {student_id, row_index, col_index}
        """
        with self._get_db() as db:
            db.query(SeatAssignment).filter(SeatAssignment.chart_id == chart_id).delete()
            db.flush()

            new_assignments = [
                SeatAssignment(
                    chart_id=chart_id,
                    student_id=a['student_id'],
                    row_index=a['row_index'],
                    col_index=a['col_index']
                ) for a in assignments
            ]
            if new_assignments:
                db.bulk_save_objects(new_assignments)
            db.flush()

    def delete_seating_chart(self, chart_id: int):
        with self._get_db() as db:
            chart = db.query(SeatingChart).filter(SeatingChart.id == chart_id).first()
            if chart:
                db.delete(chart)
                db.flush()

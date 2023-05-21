# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import logging


_logger = logging.getLogger(__name__) #Información que obtiene del fichero de configuración

class task(models.Model):
    _name = 'manage.task'
    _description = 'manage.task'

    code = fields.Char(compute="_get_code")
    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre") #Name
    description = fields.Text()
    creation_date = fields.Date()
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    is_paused = fields.Boolean()
    sprint = fields.Many2one("manage.sprint", ondelete="set null", help="Sprint relacionado")
    technologies = fields.Many2many(comodel_name="manage.technology",
                                    relation="technologies_tasks",
                                    column1="task_id",
                                    column2="technology_id")
    #@api.one
    def _get_code(self):
        for task in self:
            if len(task.sprint) == 0:
                task.code = "TSK_"+str(task.id)
            else:
                task.code = str(task.sprint.name).upper()+"_"+str(task.id)

class sprint(models.Model):
    _name = 'manage.sprint'
    _description = 'manage.sprint'

    name = fields.Char()
    description = fields.Text()
    duration = fields.Integer()
    start_date = fields.Datetime()
    end_date = fields.Datetime(compute="_get_end_date", store=True)
    tasks = fields.One2many(string="Tareas", comodel_name="manage.task", inverse_name='sprint')

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for sprint in self:
            if isinstance(sprint.start_date, datetime.datetime) and sprint.duration > 0:
                sprint.end_date = sprint.start_date + datetime.timedelta(days=sprint.duration)
            else:
                sprint.end_date = sprint.start_date


class technology(models.Model):
    _name = 'manage.technology'
    _description = 'manage.technology'

    name = fields.Char()
    description = fields.Text()

    photo = fields.Image(max_width=200, max_height=200)
    tasks = fields.Many2many(comodel_name="manage.task",
                             relation="technologies_tasks",
                             column1="technology_id",
                             column2="task_id")


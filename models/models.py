# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import datetime
import logging


_logger = logging.getLogger(__name__) #Información que obtiene del fichero de configuración

class developer(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_dev = fields.Boolean()
    
    technologies = fields.Many2many('manage.technology',
                                    relation='developer_technologies',
                                    column1='developer_id',
                                    column2='technologies_id')
    
    @api.onchange('is_dev')
    def _onchange_is_dev(self):
        categories = self.env['res.partner.category'].search([('name','=','Devs')])
        if len(categories) > 0:
            category = categories[0]
        else:
            category = self.env['res.partner.category'].create({'name':'Devs'})
        self.category_id = [(4, category.id)]    
    

class project(models.Model):
    _name = 'manage.project'
    _description = 'manage.project'
    
    name = fields.Char()
    description = fields.Text()
    histories = fields.One2many(comodel_name="manage.history", inverse_name="project")

class history(models.Model):
    _name = 'manage.history'
    _description = 'manage.history'
    
    name = fields.Char()
    description = fields.Text()
    project = fields.Many2one("manage.project", ondelete="set null")
    tasks = fields.One2many(string="Tareas", comodel_name="manage.task", inverse_name="history")
    used_technologies = fields.Many2many("manage.technology", compute="_get_used_technologies")

    def _get_used_technologies(self):
        for history in self:
            technologies = None
            for task in history.tasks:
                if not technologies:
                    technologies = task.technologies
                else:
                    technologies = technologies + task.technologies
            history.used_technologies = technologies   


class task(models.Model):
    _name = 'manage.task'
    _description = 'manage.task'

    project = fields.Many2one('manage.project', related='history.project', readonly=True)
    code = fields.Char(compute="_get_code")
    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre") #Name
    history = fields.Many2one("manage.history", ondelete="set null", help="Historia relacionada")
    description = fields.Text()
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    is_paused = fields.Boolean()
    sprint = fields.Many2one("manage.sprint", compute="_get_sprint", store=True)
    technologies = fields.Many2many(comodel_name="manage.technology",
                                    relation="technologies_tasks",
                                    column1="task_id",
                                    column2="technology_id")
    developer = fields.Many2one('res.partner')

    #@api.one
    def _get_code(self):
        for task in self:
            try:
                task.code = "TSK_"+str(task.id)
                _logger.info("Código generado: "+task.code)
            except:
                raise ValidationError(_("Generación de código errónea"))
            
    @api.depends('code')
    def _get_sprint(self):
        for task in self:
            sprints = self.env['manage.sprint'].search([('project.id', '=', task.history.project.id)])
            found = False
            for sprint in sprints:
                if isinstance(sprint.end_date, datetime.datetime) and sprint.end_date > datetime.datetime.now():
                    task.sprint = sprint.id
                    found = True
            if not found:
                task.sprint = False

    # def _get_definition_date(self):
    #     return datetime.datetime.now()

    # definition_date = fields.Datetime(default=_get_definition_date)
    
    definition_date = fields.Datetime(default=lambda p: datetime.datetime.now())

class sprint(models.Model):
    _name = 'manage.sprint'
    _description = 'manage.sprint'

    project = fields.Many2one("manage.project")
    name = fields.Char()
    description = fields.Text()

    duration = fields.Integer(default=15)
    
    start_date = fields.Datetime()
    end_date = fields.Datetime(compute="_get_end_date", store=True)
    tasks = fields.One2many(string="Tareas", comodel_name="manage.task", inverse_name='sprint')
    
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for sprint in self:
            try:
                if isinstance(sprint.start_date, datetime.datetime) and sprint.duration > 0:
                    sprint.end_date = sprint.start_date + datetime.timedelta(days=sprint.duration)
                else:
                    sprint.end_date = sprint.start_date
                _logger.debug("Fecha final de sprint creada")
            except:
                raise ValidationError(_("Generación de fecha errónea"))

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


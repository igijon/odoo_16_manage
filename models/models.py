# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import datetime
import logging
import re


_logger = logging.getLogger(__name__) #Información que obtiene del fichero de configuración

class developer(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_dev = fields.Boolean()
    access_code = fields.Char()
    last_login = fields.Date()

    technologies = fields.Many2many('manage.technology',
                                    relation='developer_technologies',
                                    column1='developer_id',
                                    column2='technologies_id')
    
    tasks = fields.Many2many('manage.task',
                                    relation='developer_tasks',
                                    column1='developer_id',
                                    column2='task_id')
 
    bugs = fields.Many2many('manage.bug',
                                    relation='developer_bugs',
                                    column1='developer_id',
                                    column2='bug_id')
    
    
    improvements = fields.Many2many('manage.improvement',
                                    relation='developer_improvements',
                                    column1='developer_id',
                                    column2='improvement_id')
    

    @api.constrains('access_code')
    def _check_code(self):
        regex = re.compile('^[0-9]{8}[a-z]', re.I)
        for dev in self:
            if regex.match(dev.access_code):
                _logger.info('Código de acceso generado correctamente')
            else:
                raise ValidationError('Formato de código de acceso incorrecto')
            
    _sql_constraints = [('access_code_unique', 'unique(access_code)', 'Access code ya existente.')]

    
    @api.onchange('is_dev')
    def _onchange_is_dev(self):
        categories = self.env['res.partner.category'].search([('name','=','Devs')])
        if len(categories) > 0:
            category = categories[0]
        else:
            category = self.env['res.partner.category'].create({'name':'Devs'})
        self.category_id = [(4, category.id)]    
    
    @api.constrains('is_dev')
    def _check_is_dev(self):
        for dev in self:
            if dev.is_dev:
                categories = self.env['res.partner.category'].search([('name','=','Devs')])
                if len(categories) > 0:
                    category = categories[0]
                else:
                    category = self.env['res.partner.category'].create({'name':'Devs'})
                dev.category_id = [(4, category.id)]  
        

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

    definition_date = fields.Datetime(default=lambda p: datetime.datetime.now())
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
            # sprints = self.env['manage.sprint'].search([('project.id', '=', task.history.project.id)])
            if isinstance(task.history.project.id, models.NewId):
                id_project = int(task.history.project.id.origin)
            else:
                id_project = task.history.project.id
            sprints = self.env['manage.sprint'].search([('project.id','=', id_project)])
            found = False
            for sprint in sprints:
                if isinstance(sprint.end_date, datetime.datetime) and sprint.end_date > datetime.datetime.now():
                    task.sprint = sprint.id
                    found = True
            if not found:
                task.sprint = False

    def _get_default_dev(self):
        dev = self.browse(self._context.get('current_developer'))
        if dev:
            return [dev.id]
        else:
            return []

    developers = fields.Many2many(comodel_name='res.partner',
                                  relation='developers_tasks',
                                  column1='task_id',
                                  column2='developer_id',
                                  default=_get_default_dev)

class bug(models.Model):
    _name = 'manage.bug'
    _description = 'manage.bug'
    _inherit = 'manage.task'

    technologies = fields.Many2many(comodel_name="manage.technology",
                                    relation="technologies_bugs",
                                    column1="bug_id",
                                    column2="technology_id")
    
    tasks_linked = fields.Many2many(comodel_name="manage.task",
                                    relation="tasks_bugs",
                                    column1="bug_id",
                                    column2="task_id")
    
    bugs_linked = fields.Many2many(comodel_name="manage.bug",
                                    relation="bugs_bugs",
                                    column1="bug1_id",
                                    column2="bug2_id")
    
    improvements_linked = fields.Many2many(comodel_name="manage.improvement",
                                    relation="improvements_bugs",
                                    column1="bug_id",
                                    column2="improvement_id")
    

    developers = fields.Many2many(comodel_name="res.partner",
                                    relation="developers_bugs",
                                    column1="bug_id",
                                    column2="developer_id")

class improvement(models.Model):
    _name = 'manage.improvement'
    _description = 'manage.improvement'
    _inherit = 'manage.task'

    technologies = fields.Many2many(comodel_name="manage.technology",
                                    relation="technologies_improvements",
                                    column1="improvement_id",
                                    column2="technology_id")
    
    histories_linked = fields.Many2many('manage.history')

    developers = fields.Many2many(comodel_name="res.partner",
                                    relation="developers_improvements",
                                    column1="improvement_id",
                                    column2="developer_id")


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


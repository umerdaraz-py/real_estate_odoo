from odoo import fields, models


class EstatePropertiesType(models.Model):
    _name = "estate.property.type"
    _description = "Model for Real-Estate Property Types"

    name = fields.Char(string="Name", required=True)

    # _sql_constraints = [('unique_type', 'UNIQUE(name)', 'A property type name must be unique')]
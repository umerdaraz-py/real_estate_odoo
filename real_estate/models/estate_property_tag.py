from odoo import fields, models


class EstatePropertiesTag(models.Model):
    _name = "estate.property.tag"
    _description = "Model for Real-Estate Property Types"

    name = fields.Char(string="Name", required=True)